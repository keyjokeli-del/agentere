import pytest
from datetime import date, timedelta
from fastapi.testclient import TestClient
from app.main import app
from app.services.calendar_service import CalendarService
from app.agents.dental_agents import AppointmentAgent
from app.models.dental_models import TriageResult

client = TestClient(app)

def test_calendar_service_slots_and_conflict():
    """Validates Task 2.1: Available slots calculation and collision rejection."""
    service = CalendarService()
    test_date = date.today() + timedelta(days=5)
    test_date_str = test_date.strftime("%Y-%m-%d")

    initial_slots = service.get_available_slots(test_date)
    assert len(initial_slots) == 13  # 09:00 to 18:00 with 45-minute slots
    assert initial_slots[:4] == ["09:00", "09:45", "10:30", "11:15"]
    assert "09:00" in initial_slots

    # Book slot at 09:00
    appt = service.create_appointment(
        patient_name="Ana Lopez",
        phone_or_channel_id="whatsapp:+5491112345678",
        treatment="Ortodoncia",
        appointment_date=test_date_str,
        appointment_time="09:00",
        channel="whatsapp"
    )
    assert appt.patient_name == "Ana Lopez"
    assert appt.time == "09:00"
    assert appt.status == "confirmed"

    # Verify slot is no longer available
    slots_after = service.get_available_slots(test_date)
    assert "09:00" not in slots_after
    assert len(slots_after) == 12

    # Collision test: attempt to book the exact same slot must raise ValueError
    with pytest.raises(ValueError) as excinfo:
        service.create_appointment(
            patient_name="Otro Paciente",
            phone_or_channel_id="whatsapp:+5491199998888",
            treatment="Limpieza",
            appointment_date=test_date_str,
            appointment_time="09:00",
            channel="whatsapp"
        )
    assert "no está disponible" in str(excinfo.value)

def test_appointment_agent_conversational_negotiation():
    """Validates Task 2.2: AppointmentAgent handles free slots and occupied slot alternatives."""
    agent = AppointmentAgent()
    target_d = (date.today() + timedelta(days=2)).strftime("%Y-%m-%d")

    # 1. User wants an appointment without specifying time -> Proposes available slots
    triage_no_time = TriageResult(
        intent="BOOK_APPOINTMENT",
        extracted_name="Lucas Rossi",
        extracted_treatment="Limpieza Dental",
        extracted_date=target_d,
        extracted_time=None,
        urgency="normal",
        summary="Pide cita para limpieza"
    )
    reply_propose = agent.handle("Quisiera una cita", triage_no_time, "user-123", "whatsapp")
    assert "horarios disponibles" in reply_propose.lower()

    # 2. User confirms a valid 45-min slot (e.g. 09:45) -> Confirms appointment
    triage_with_time = TriageResult(
        intent="BOOK_APPOINTMENT",
        extracted_name="Lucas Rossi",
        extracted_treatment="Limpieza Dental",
        extracted_date=target_d,
        extracted_time="09:45",
        urgency="normal",
        summary="Confirma a las 09:45"
    )
    reply_confirm = agent.handle("Confirmo a las 09:45", triage_with_time, "user-123", "whatsapp")
    assert "confirmada con éxito" in reply_confirm.lower()
    assert "09:45" in reply_confirm

    # 3. Another user asks for the SAME already occupied slot (09:45) -> Offers alternatives
    triage_busy = TriageResult(
        intent="BOOK_APPOINTMENT",
        extracted_name="Martin Velez",
        extracted_treatment="Extracción",
        extracted_date=target_d,
        extracted_time="09:45",
        urgency="normal",
        summary="Quiere a las 09:45"
    )
    reply_busy = agent.handle("Quiero turno a las 09:45", triage_busy, "user-456", "whatsapp")
    assert "ya se encuentra reservado" in reply_busy.lower() or "ocupado" in reply_busy.lower()
    assert "alternativas" in reply_busy.lower()

def test_fastapi_calendar_endpoints_and_conflict_http_status():
    """Validates Task 2.3: FastAPI REST endpoints, slot query and HTTP 409 Conflict."""
    test_d = (date.today() + timedelta(days=7)).strftime("%Y-%m-%d")

    # 1. Query slots
    res_slots = client.get(f"/api/slots?target_date={test_d}")
    assert res_slots.status_code == 200
    data_slots = res_slots.json()
    assert "slots" in data_slots
    assert len(data_slots["slots"]) > 0

    chosen_slot = data_slots["slots"][0]

    # 2. Create appointment via API
    payload = {
        "patient_name": "Valeria Castro",
        "contact": "+5491177665544",
        "treatment": "Blanqueamiento Dental",
        "date": test_d,
        "time": chosen_slot,
        "channel": "instagram"
    }
    res_create = client.post("/api/appointments", json=payload)
    assert res_create.status_code == 200
    appt_created = res_create.json()
    assert appt_created["patient_name"] == "Valeria Castro"
    assert appt_created["status"] == "confirmed"

    # 3. Duplicate booking attempt on same slot -> Must return 409 Conflict
    res_duplicate = client.post("/api/appointments", json=payload)
    assert res_duplicate.status_code == 409
    assert "no está disponible" in res_duplicate.json()["detail"]

    # 4. List appointments
    res_list = client.get("/api/appointments")
    assert res_list.status_code == 200
    appts = res_list.json()
    assert any(a["patient_name"] == "Valeria Castro" for a in appts)
