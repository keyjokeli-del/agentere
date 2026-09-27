import pytest
from datetime import date, timedelta
from fastapi.testclient import TestClient
from app.main import app
from app.services.calendar_service import calendar_service
from app.agents import coordinator

client = TestClient(app)

def test_health_check():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "channels" in data
    assert "whatsapp" in data["channels"]

def test_chat_faq_flow():
    payload = {
        "message": "¿Cuánto cuesta una limpieza dental y blanqueamiento?",
        "sender_id": "test-user-1",
        "channel": "whatsapp"
    }
    response = client.post("/api/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "reply" in data
    assert len(data["reply"]) > 10
    assert data["channel"] == "whatsapp"

def test_calendar_slots_and_booking():
    tomorrow = None
    slots_data = None
    for offset in range(1, 30):
        candidate = date.today() + timedelta(days=offset)
        if candidate.weekday() == 6:  # Closed on Sunday
            continue
        c_str = candidate.strftime("%Y-%m-%d")
        res = client.get(f"/api/slots?target_date={c_str}")
        if res.status_code == 200:
            data = res.json()
            if len(data.get("slots", [])) > 0:
                tomorrow = c_str
                slots_data = data
                break
    assert tomorrow is not None, "No available slot found in the next 30 days"
    assert slots_data is not None and len(slots_data["slots"]) > 0

    first_slot = slots_data["slots"][0]

    # Book appointment
    book_payload = {
        "patient_name": "Carlos Mendoza",
        "contact": "+5491122334455",
        "treatment": "Limpieza Dental",
        "date": tomorrow,
        "time": first_slot,
        "channel": "whatsapp"
    }
    res_book = client.post("/api/appointments", json=book_payload)
    assert res_book.status_code == 200
    appt = res_book.json()
    assert appt["patient_name"] == "Carlos Mendoza"

    # Verify slot is no longer available
    slots_after = client.get(f"/api/slots?target_date={tomorrow}").json()
    assert first_slot not in slots_after["slots"]

def test_multichannel_webhooks():
    # Test YouTube comment webhook
    yt_payload = {
        "comment": "Tengo dolor en una muela del juicio, ¿atienden urgencias?",
        "author": "Laura Gómez",
        "video_id": "vid_abc123"
    }
    res_yt = client.post("/api/webhooks/youtube", json=yt_payload)
    assert res_yt.status_code == 200
    assert "reply" in res_yt.json()

    # Test WhatsApp webhook
    wa_payload = {
        "sender_id": "5491199887766@s.whatsapp.net",
        "sender_name": "Marcos Diaz",
        "message": "Hola, quisiera agendar un turno para ortodoncia"
    }
    res_wa = client.post("/api/webhooks/whatsapp", json=wa_payload)
    assert res_wa.status_code == 200
    assert "reply" in res_wa.json()
