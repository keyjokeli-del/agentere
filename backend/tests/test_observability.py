import json
import logging
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.core.security import create_access_token
from app.core.observability import (
    JsonLogFormatter,
    sanitize_log_str,
    metrics_tracker,
    track_dependency,
    set_request_context,
    get_request_id,
    get_entry_point
)

client = TestClient(app)


def test_sanitize_log_str_and_pii_redaction():
    """Validates redaction of phone numbers, WhatsApp JIDs, and API keys."""
    raw = "Paciente 5491178296781 con jid 5491178296781@s.whatsapp.net llamó con key=AIzaSySecretKey123"
    sanitized = sanitize_log_str(raw)
    
    # Phone number masked
    assert "5491178296781" not in sanitized
    assert "5491****781" in sanitized or "****" in sanitized
    
    # WhatsApp JID masked
    assert "5491178296781@s.whatsapp.net" not in sanitized
    assert "****" in sanitized
    
    # API key redacted
    assert "AIzaSySecretKey123" not in sanitized
    assert "[REDACTED]" in sanitized


def test_json_formatter_structure():
    """Validates that JsonLogFormatter emits valid single-line JSON with context fields."""
    set_request_context("test-req-abc", "webhook_whatsapp")
    formatter = JsonLogFormatter()
    
    record = logging.LogRecord(
        name="app.test",
        level=logging.INFO,
        pathname="test.py",
        lineno=10,
        msg="Operación completada con éxito",
        args=(),
        exc_info=None
    )
    formatted = formatter.format(record)
    
    # Must be valid JSON
    data = json.loads(formatted)
    assert data["level"] == "INFO"
    assert data["logger"] == "app.test"
    assert data["message"] == "Operación completada con éxito"
    assert data["request_id"] == "test-req-abc"
    assert data["entry_point"] == "webhook_whatsapp"
    assert "timestamp" in data


def test_correlation_id_middleware():
    """Verifies X-Request-ID propagation from caller or automatic generation."""
    # 1. Propagation of incoming X-Request-ID
    res = client.get("/", headers={"X-Request-ID": "custom-trace-uuid-123"})
    assert res.status_code == 200
    assert res.headers.get("X-Request-ID") == "custom-trace-uuid-123"

    # 2. Generation when missing
    res2 = client.get("/")
    assert res2.status_code == 200
    gen_id = res2.headers.get("X-Request-ID")
    assert gen_id is not None
    assert gen_id.startswith("req-")


def test_health_slo_endpoint():
    """Validates public symptom-based SLO health check endpoint."""
    res = client.get("/health/slo")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] in ("healthy", "unhealthy")
    assert "error_rate_5m_pct" in data
    assert "p95_latency_ms" in data
    assert "degraded" in data
    assert "requests_5m_count" in data


def test_health_slo_503_on_error_spike():
    """Verifies SLO trips to HTTP 503 when 5xx error rate exceeds 5% in 5m."""
    # Artificially inject errors into metrics_tracker
    for _ in range(12):
        metrics_tracker.record_request("/api/test-failure", "POST", 500, 150.0)

    is_healthy, status_data = metrics_tracker.check_slo()
    assert is_healthy is False
    assert status_data["status"] == "unhealthy"

    res = client.get("/health/slo")
    assert res.status_code == 503
    data = res.json()
    assert data["status"] == "unhealthy"
    assert "exceeded 5%" in data["reason"]

    # Reset metrics tracker requests to avoid polluting subsequent tests
    with metrics_tracker._lock:
        metrics_tracker._requests_5m.clear()


def test_admin_metrics_endpoint():
    """Verifies protected RED metrics endpoint."""
    # 1. Unauthorized without token
    res_unauth = client.get("/api/admin/metrics")
    assert res_unauth.status_code == 401

    # 2. Authorized with admin JWT
    token = create_access_token({"sub": "admin", "role": "admin"})
    res_auth = client.get("/api/admin/metrics", headers={"Authorization": f"Bearer {token}"})
    assert res_auth.status_code == 200
    data = res_auth.json()

    assert "latency_ms" in data
    assert "requests_5m" in data
    assert "ai_inference_15m" in data
    assert "dependencies" in data
    assert "routes" in data


def test_track_dependency_context_manager():
    """Validates sync and error recording in track_dependency."""
    with track_dependency("test_cloud_service"):
        # Simulated success
        _ = 1 + 1

    summary = metrics_tracker.get_summary()
    assert "test_cloud_service" in summary["dependencies"]
    dep = summary["dependencies"]["test_cloud_service"]
    assert dep["total"] >= 1
    assert dep["success"] >= 1

    # Simulated failure
    with pytest.raises(ValueError):
        with track_dependency("test_cloud_service"):
            raise ValueError("simulated network timeout")

    summary_after = metrics_tracker.get_summary()
    dep_after = summary_after["dependencies"]["test_cloud_service"]
    assert dep_after["error"] >= 1
    assert dep_after["last_error"] == "ValueError"
