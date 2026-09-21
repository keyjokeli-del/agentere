import hmac
import hashlib
import json
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.config import settings
from app.services.calendar_service import CalendarService, calendar_service

client = TestClient(app)

@pytest.fixture(autouse=True)
def isolate_calendar(monkeypatch):
    """Ensures deterministic in-memory calendar state for social gateway tests."""
    monkeypatch.setattr(CalendarService, "_init_google_service", lambda self: None)
    monkeypatch.setattr(calendar_service, "service", None)
    calendar_service.local_appointments = []

def test_meta_webhook_verification_handshake():
    # 1. Valid handshake
    token = settings.meta_verify_token
    res_valid = client.get(f"/api/webhooks/meta?hub.mode=subscribe&hub.challenge=115599&hub.verify_token={token}")
    assert res_valid.status_code == 200
    assert res_valid.text == "115599"

    # 2. Invalid handshake token
    res_invalid = client.get("/api/webhooks/meta?hub.mode=subscribe&hub.challenge=115599&hub.verify_token=token_invalido_hacker")
    assert res_invalid.status_code == 403
    assert "Verification token mismatch" in res_invalid.json()["detail"]

def test_meta_webhook_post_hmac_signature_security(monkeypatch):
    # Set app secret
    secret = "meta_test_secret_key_123"
    monkeypatch.setattr(settings, "meta_app_secret", secret)

    payload = {
        "object": "page",
        "entry": [{
            "id": "10001",
            "messaging": [{
                "sender": {"id": "fb-patient-1"},
                "message": {"mid": "mid.test.1", "text": "¿Cuánto cuesta un blanqueamiento?"}
            }]
        }]
    }
    raw_body = json.dumps(payload).encode("utf-8")

    # 1. Tampered / invalid signature -> 403
    headers_bad = {"X-Hub-Signature-256": "sha256=invalid_hash_signature_abcdef"}
    res_bad = client.post("/api/webhooks/meta", content=raw_body, headers=headers_bad)
    assert res_bad.status_code == 403
    assert "Invalid X-Hub-Signature-256" in res_bad.json()["detail"]

    # 2. Authentic HMAC-SHA256 signature -> 200 OK
    valid_signature = "sha256=" + hmac.new(
        key=secret.encode("utf-8"),
        msg=raw_body,
        digestmod=hashlib.sha256
    ).hexdigest()
    headers_good = {"X-Hub-Signature-256": valid_signature, "Content-Type": "application/json"}
    res_good = client.post("/api/webhooks/meta", content=raw_body, headers=headers_good)
    assert res_good.status_code == 200
    data = res_good.json()
    assert data["channel"] == "facebook"
    assert data["sender_id"] == "fb-patient-1"
    assert "Blanqueamiento" in data["reply"] or "$90" in data["reply"] or "Lumina" in data["reply"]

def test_youtube_webhook_comment_processing():
    yt_payload = {
        "snippet": {
            "videoId": "video_dental_tips_01",
            "topLevelComment": {
                "id": "comment_999",
                "snippet": {
                    "textDisplay": "Hola doctor, me duele muchísimo una muela, ¿qué puedo hacer?",
                    "authorDisplayName": "Mariana Lopez",
                    "authorChannelId": {"value": "UC_mariana_789"}
                }
            }
        }
    }
    res = client.post("/api/webhooks/youtube", json=yt_payload)
    assert res.status_code == 200
    data = res.json()
    assert data["channel"] == "youtube"
    assert data["sender_id"] == "UC_mariana_789"
    assert data["intent"] == "EMERGENCY_OR_PAIN"
    assert "recetar" in data["reply"].lower() or "presencial" in data["reply"].lower() or "urgencia" in data["reply"].lower()
