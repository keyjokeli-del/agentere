"""Tests for Dashboard 50 Improvements (Bidirectional Messaging, RAG Training, KPIs, Calendar & Notes)."""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.security import create_admin_jwt
from app.core.database import db_manager

client = TestClient(app)


@pytest.fixture
def admin_headers():
    token = create_admin_jwt({"sub": "admin", "role": "admin"})
    return {"Authorization": f"Bearer {token}"}


def test_dashboard_reply_and_handoff(admin_headers):
    """Mejora 1: Manual reply sends message, triggers 30m human handoff, and logs activity."""
    payload = {
        "sender_id": "+5491122334455",
        "channel": "whatsapp",
        "message": "Hola, confirmamos que te esperamos este jueves a las 11:00 hs.",
        "sender_name": "Mariana Gómez"
    }
    response = client.post("/api/dashboard/reply", json=payload, headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "sent"
    assert data["handoff_paused_minutes"] == 30
    assert db_manager.is_handoff_active("+5491122334455") is True


def test_dashboard_internal_note(admin_headers):
    """Mejora 8: Internal clinical note saved privately in patient memory vectors."""
    payload = {
        "sender_id": "+5491122334455",
        "channel": "whatsapp",
        "note": "Paciente con fobia a las agujas; usar anestesia tópica profunda previa.",
        "author": "Dra. Domínguez"
    }
    response = client.post("/api/dashboard/internal-note", json=payload, headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "saved"
    assert "fobia a las agujas" in data["note"]


def test_dashboard_train_rag(admin_headers):
    """Mejora 6: Dynamic RAG fine-tuning vector update."""
    payload = {
        "query": "¿El blanqueamiento duele?",
        "corrected_solution": "No duele, se aplica un desensibilizante previo y la lámpara LED fría previene la irritación pulpar.",
        "category": "Estética Dental"
    }
    response = client.post("/api/dashboard/train-rag", json=payload, headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "trained"


def test_dashboard_kpis(admin_headers):
    """Mejora 48: Top executive clinical KPI strip."""
    response = client.get("/api/dashboard/kpis", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert "patients_today" in data
    assert "appointments_confirmed" in data
    assert "urgent_cases" in data
    assert "estimated_pipeline_usd" in data
    assert "avg_sla_seconds" in data
    assert data["estimated_pipeline_usd"] > 0


def test_dashboard_briefing(admin_headers):
    """Mejora 38: Executive 4-line pre-consultation clinical briefing."""
    payload = {
        "patient_name": "Carlos Mendoza",
        "contact": "+5491122334455",
        "treatment": "Endodoncia pieza 24 con molestia",
        "date": "2026-09-30",
        "time": "15:00",
        "channel": "whatsapp"
    }
    response = client.post("/api/dashboard/briefing", json=payload, headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert "briefing_lines" in data
    assert len(data["briefing_lines"]) == 4
    assert any("24" in line for line in data["briefing_lines"])


def test_dashboard_block_calendar_slot(admin_headers):
    """Mejora 35: Block slot for sterilization or surgical emergency."""
    payload = {
        "date": "2026-09-30",
        "time": "12:00",
        "reason": "Esterilización de instrumental quirúrgico autoclave",
        "duration_min": 60
    }
    response = client.post("/api/dashboard/calendar/block-slot", json=payload, headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "blocked"


def test_dashboard_meta_token_health(admin_headers):
    """Mejora 21: Real-time Meta Graph API & YouTube token monitoring."""
    response = client.get("/api/dashboard/meta-token-health", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert "facebook" in data
    assert "instagram" in data
    assert "youtube" in data


def test_dashboard_send_reminder(admin_headers):
    """Mejora 39: Immediate WhatsApp appointment reminder dispatch."""
    payload = {
        "contact": "+5491155556666",
        "patient_name": "Lucía Morales",
        "appointment_date": "2026-10-01",
        "appointment_time": "16:30",
        "treatment": "Limpieza Dental y Profilaxis"
    }
    response = client.post("/api/dashboard/send-reminder", json=payload, headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "reminder_sent"


def test_dashboard_waitlist_invite(admin_headers):
    """Mejora 40: Slot invitation dispatch to waitlist patient."""
    payload = {
        "preferred_date": "2026-10-02",
        "slot_time": "14:00"
    }
    response = client.post("/api/dashboard/waitlist/invite", json=payload, headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "invited"


def test_dashboard_channels_inbox_enriched(admin_headers):
    """Mejoras 2, 9, 13, 24: Enriched threads with FDI teeth, CRM stage, and cross-channel badges."""
    response = client.get("/api/dashboard/channels-inbox", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert "whatsapp" in data
    assert "threads" in data["whatsapp"]
    if data["whatsapp"]["threads"]:
        t = data["whatsapp"]["threads"][0]
        assert "urgency" in t
        assert "crm_stage" in t
        assert "fdi_teeth" in t
        assert "cross_channels" in t
        assert "sla_seconds" in t
