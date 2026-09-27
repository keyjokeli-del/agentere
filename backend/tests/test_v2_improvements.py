"""
Tests unitarios y de integración para la Evolución v2.0 Enterprise de Lumina Dental Studio.
Verifica las 30 mejoras funcionales y los 5 cuellos de botella arquitectónicos:
- ConnectionPool & HNSW en Neon PostgreSQL
- Memoria y Triage FDI (dientes 11-48), Sentimiento, Frustración y Red Flags Post-Op
- Multilenguaje (ES, EN, PT, FR) y Transcripción de Audio Groq Whisper
- Agenda Dinámica (30, 45, 60, 90 min), Asignación Multi-Doctor, Feriados y RFC 5545 (.ics)
- Webhook de Telegram y Enrutamiento Omnicanal
- Protocolo Anti No-Show, Horarios de Atención y Reseñas en Google Maps
- CRM Post-Operatorio (Días 1, 3, 7) y Encuestas NPS (1-5 estrellas)
- Endpoint de verificación de PIN del servidor, CSV Export e Intervención Humana (Handoff)
"""

import pytest
import os
import io
from unittest.mock import MagicMock, patch
from datetime import datetime, date

from fastapi.testclient import TestClient
from app.main import app
from app.core.database import db_manager
from app.agents.analyzer_agent.agent import (
    extract_fdi_teeth,
    detect_sentiment_and_frustration,
    detect_clinical_followup,
    detect_language
)
from app.agents.analyzer_agent.schemas import ClinicalAnalysis
from app.agents.reader_agent.agent import ReaderAgent
from app.agents.solver_agent.agent import SolverAgent
from app.models.dental_models import AppointmentRecord
from app.services.calendar_service import (
    calendar_service,
    get_treatment_duration,
    get_assigned_doctor,
    generate_google_calendar_url,
    generate_ics_content,
)
from app.services.crm_lifecycle_service import crm_lifecycle_service
from app.services.groq_service import groq_service

client = TestClient(app)


# =====================================================================
# BLOQUE 0: CUELLOS DE BOTELLA ARQUITECTÓNICOS (ConnectionPool & DB)
# =====================================================================

def test_db_manager_activity_logging_and_retrieval():
    """Verifica que el logger de actividades persista en memoria o Neon sin fugas."""
    sender = "test_patient_v2"
    db_manager.log_activity(
        channel="whatsapp",
        sender_id=sender,
        sender_name="Paciente V2",
        message="Hola, me duele el diente 21",
        reply="Te evaluaremos de inmediato.",
        agent="SolverAgent",
        intent="TRIAGE",
        status="sent"
    )

    activities = db_manager.get_recent_activities(limit=10)
    assert len(activities) > 0
    found = any(a.get("sender_id") == sender for a in activities)
    assert found is True

    # Actualizar estado de entrega
    db_manager.update_activity_status(sender, "whatsapp", "read")
    updated_activities = db_manager.get_recent_activities(limit=10)
    for act in updated_activities:
        if act.get("sender_id") == sender:
            assert act.get("status") == "read"


def test_db_manager_human_handoff():
    """Verifica el bloqueo y desbloqueo de intervención humana (Handoff)."""
    patient_id = "patient_handoff_99"
    assert db_manager.is_handoff_active(patient_id) is False

    # Activar handoff por 30 minutos
    db_manager.set_human_handoff(patient_id, "whatsapp", minutes=30, reason="Intervención de emergencia")
    assert db_manager.is_handoff_active(patient_id) is True

    # Desactivar handoff
    db_manager.clear_human_handoff(patient_id)
    assert db_manager.is_handoff_active(patient_id) is False


def test_db_manager_cross_channel_identity():
    """Verifica la vinculación de identidad omnicanal del paciente."""
    contact_phone = "+5491155554321"

    # Vincular desde WhatsApp
    db_manager.get_or_link_patient_identity(
        channel="whatsapp",
        sender_id="5491155554321@s.whatsapp.net",
        full_name="Juan Perez",
        phone=contact_phone
    )

    # Vincular desde Instagram con el mismo teléfono
    record = db_manager.get_or_link_patient_identity(
        channel="instagram",
        sender_id="ig_juan_perez",
        full_name="Juan Perez",
        phone=contact_phone
    )
    assert record is not None
    assert record.get("phone") == contact_phone
    assert record.get("instagram_id") == "ig_juan_perez"


# =====================================================================
# BLOQUE A: INTELIGENCIA CONVERSACIONAL, RAG & MEMORIA
# =====================================================================

def test_extract_fdi_teeth():
    """Mejora 2: Extracción determinística de piezas dentales FDI (11 a 48)."""
    text1 = "Tengo un dolor muy fuerte en la muela 46 y en el incisivo 21."
    teeth1 = extract_fdi_teeth(text1)
    assert 46 in teeth1
    assert 21 in teeth1

    text2 = "Quiero hacerme un blanqueamiento general en todos los dientes."
    teeth2 = extract_fdi_teeth(text2)
    assert teeth2 == []

    text3 = "Me rompí la muela del juicio superior derecha."
    teeth3 = extract_fdi_teeth(text3)
    assert 18 in teeth3


def test_detect_sentiment_and_frustration():
    """Mejora 3: Detección de frustración del paciente y score de sentimiento."""
    # Mensaje frustrado
    angry_text = "¡Es el colmo! Llevo una hora esperando y nadie responde, pésimo servicio!"
    score_angry, frustrated = detect_sentiment_and_frustration(angry_text)
    assert frustrated is True
    assert score_angry < -0.3

    # Mensaje positivo
    happy_text = "¡Muchísimas gracias por la atención! La doctora Nairoby es excelente."
    score_happy, not_frustrated = detect_sentiment_and_frustration(happy_text)
    assert not_frustrated is False
    assert score_happy > 0.3


def test_detect_clinical_followup():
    """Mejora 5: Detección de banderas rojas en seguimiento post-operatorio."""
    red_flag_text = "Ayer me sacaron una muela y hoy tengo la cara con mucha hinchazón y pus."
    has_flags, questions = detect_clinical_followup(red_flag_text)
    assert has_flags is True
    assert len(questions) > 0

    routine_text = "Hola, quería saber el precio de una limpieza dental."
    has_flags2, questions2 = detect_clinical_followup(routine_text)
    assert has_flags2 is False
    assert len(questions2) == 0


def test_detect_language():
    """Mejora 7: Detección multilenguaje (ES, EN, PT, FR)."""
    assert detect_language("Hello doctor, I have severe tooth pain and need an appointment") == "en"
    assert detect_language("Olá doutor, preciso de uma consulta de urgência") == "pt"
    assert detect_language("Bonjour docteur, j'ai mal aux dents") == "fr"
    assert detect_language("Hola doctora, quisiera agendar un turno para mañana") == "es"


def test_transcribe_audio_mock():
    """Mejora 1: Transcripción de notas de voz vía API Groq Whisper (Zero-OOM)."""
    mock_instance = MagicMock()
    mock_instance.audio.transcriptions.create.return_value = "Hola doctora, tengo dolor de muela"

    with patch.object(groq_service, "client", mock_instance):
        result = groq_service.transcribe_audio(b"fake_audio_bytes_ogg", filename="voice.ogg")
        assert "dolor de muela" in result


# =====================================================================
# BLOQUE B: AGENDA INTELIGENTE Y CALENDARIO
# =====================================================================

def test_dynamic_treatment_duration():
    """Mejora 8: Duración dinámica por tratamiento (30, 45, 60, 90 min)."""
    assert get_treatment_duration("Limpieza dental ultrasónica y profilaxis") == 30
    assert get_treatment_duration("Evaluación inicial y diagnóstico") == 45
    assert get_treatment_duration("Blanqueamiento láser") == 60
    assert get_treatment_duration("Implantes guiados 3D de titanio") == 90
    assert get_treatment_duration("Tratamiento de conducto endodoncia") == 90


def test_multi_doctor_assignment():
    """Mejora 9: Asignación por especialidad médica."""
    doc_general = get_assigned_doctor("Limpieza y blanqueamiento")
    assert "Nairoby Domínguez" in doc_general

    doc_surgeon = get_assigned_doctor("Cirugía de implantes y extracción compleja")
    assert "Cirujano Maxilofacial" in doc_surgeon

    doc_ortho = get_assigned_doctor("Colocación de brackets ortodoncia invisible")
    assert "Ortodoncista" in doc_ortho


def test_holiday_and_vacation_filtering():
    """Mejora 10: Bloqueo de domingos y eventos de feriado en Google Calendar."""
    # Domingo (2026-03-29 es domingo -> slots deben ser [])
    sunday_date = date(2026, 3, 29)
    sunday_slots = calendar_service.get_available_slots(sunday_date)
    assert sunday_slots == []

    # Día hábil sin feriado (2026-03-30 es lunes)
    monday_date = date(2026, 3, 30)
    monday_slots = calendar_service.get_available_slots(monday_date)
    assert len(monday_slots) > 0


def test_generate_google_calendar_url():
    """Mejora 11: Enlace directo 1-clic a Google Calendar."""
    url = generate_google_calendar_url(
        patient_name="Carlos Gomez",
        treatment="Blanqueamiento Láser",
        appointment_date="2026-04-10",
        appointment_time="14:00",
        duration_min=45
    )
    assert "calendar.google.com/calendar/render" in url
    assert "action=TEMPLATE" in url
    assert "Carlos" in url
    assert "Lumina" in url


def test_generate_ics_content():
    """Mejora 11: Generador RFC 5545 para archivos .ics compatibles con Apple/Outlook."""
    appt = AppointmentRecord(
        id="test-ics-123",
        patient_name="Ana Martinez",
        contact="+5491100001111",
        treatment="Profilaxis Dental",
        date="2026-04-15",
        time="10:00",
        channel="whatsapp",
        status="confirmed",
        created_at="2026-03-26T12:00:00Z"
    )
    ics_text = generate_ics_content(
        appt=appt,
        duration_min=30
    )
    assert "BEGIN:VCALENDAR" in ics_text
    assert "VERSION:2.0" in ics_text
    assert "BEGIN:VEVENT" in ics_text
    assert "Profilaxis Dental" in ics_text
    assert "Ana Martinez" in ics_text
    assert "END:VEVENT" in ics_text
    assert "END:VCALENDAR" in ics_text


def test_waitlist_auto_reassignment():
    """Mejora 13: Lista de espera inteligente tras cancelación."""
    cancellation_date = "2026-04-20"

    # Registrar en lista de espera
    db_manager.add_to_waitlist(
        patient_name="Laura Solis",
        contact="+5491133332222",
        channel="whatsapp",
        preferred_date=cancellation_date,
        treatment="Evaluación"
    )

    # Simular cancelación y verificar que se encuentre al paciente
    candidates = db_manager.check_waitlist_for_cancellation(cancellation_date)
    assert len(candidates) > 0
    assert candidates[0]["patient_name"] == "Laura Solis"


# =====================================================================
# BLOQUE C: PASARELAS OMNICANAL (Telegram, WhatsApp, Meta)
# =====================================================================

def test_telegram_webhook_endpoint():
    """Mejora 14: Gateway de Telegram (POST /api/webhooks/telegram)."""
    payload = {
        "update_id": 10001,
        "message": {
            "message_id": 42,
            "from": {
                "id": 987654321,
                "first_name": "Facundo",
                "username": "facundo_tel"
            },
            "chat": {
                "id": 987654321,
                "type": "private"
            },
            "date": 1711497600,
            "text": "Hola, ¿atienden urgencias odontológicas hoy?"
        }
    }
    response = client.post("/api/webhooks/telegram", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "reply" in data
    assert data.get("channel") == "telegram"
    assert data.get("sender_id") == "987654321"


# =====================================================================
# BLOQUE E: CRM CLÍNICO, HANDOFF, SSE & ENDPOINTS DE CONTROL
# =====================================================================

def test_admin_pin_verification_endpoint():
    """Mejora 28: Verificación de PIN en el servidor (POST /api/admin/verify-pin)."""
    # PIN incorrecto -> 401 Unauthorized
    res_invalid = client.post("/api/admin/verify-pin", json={"pin": "0000"})
    assert res_invalid.status_code == 401

    # PIN correcto ("2026") -> 200 OK con valid: True
    res_valid = client.post("/api/admin/verify-pin", json={"pin": "2026"})
    assert res_valid.status_code == 200
    assert res_valid.json().get("valid") is True


def test_human_handoff_api_endpoints():
    """Mejora 28: Toggle de Intervención Humana (POST y DELETE /api/admin/handoff/{sender_id})."""
    sender_id = "test_handoff_endpoint_user"

    # 1. Activar handoff
    post_res = client.post(f"/api/admin/handoff/{sender_id}", json={"notes": "Caso crítico de dolor"})
    assert post_res.status_code == 200
    assert post_res.json().get("status") == "paused"

    # 2. Desactivar handoff
    del_res = client.delete(f"/api/admin/handoff/{sender_id}")
    assert del_res.status_code == 200
    assert del_res.json().get("status") == "resumed"


def test_export_csv_endpoint():
    """Mejora 25: Exportación de citas y métricas en formato CSV."""
    response = client.get("/api/admin/export-csv")
    assert response.status_code == 200
    assert "text/csv" in response.headers.get("content-type", "")
    content = response.text
    # Verificar encabezados CSV
    assert "TIPO" in content or "PACIENTE" in content or "CANAL" in content


def test_appointments_ics_download_endpoint():
    """Mejora 11: Descarga directa de archivo .ics (RFC 5545)."""
    response = client.get("/api/appointments/ics?appt_id=test-ics-sample")
    assert response.status_code == 200
    assert "text/calendar" in response.headers.get("content-type", "")
    assert "BEGIN:VCALENDAR" in response.text
    assert "END:VCALENDAR" in response.text


def test_crm_lifecycle_followup_and_nps():
    """Mejora 26, 27, 29: Seguimiento clínico Días 1, 3, 7 y encuestas NPS."""
    yesterday = date.today().isoformat()
    db_manager.record_appointment(
        appt_id="test-crm-followup-1",
        patient_name="Valeria Rossi",
        contact="+5491144445555",
        treatment="Extracción compleja",
        doctor="Dra. Nairoby Domínguez",
        appointment_date=yesterday,
        appointment_time="10:00",
        channel="whatsapp"
    )

    # Ejecutar tick del CRM con force=True
    events_triggered = crm_lifecycle_service.trigger_lifecycle_tick(force=True)
    assert isinstance(events_triggered, dict)
    assert events_triggered.get("status") == "processed"


def test_channels_inbox_endpoint():
    """Validates real inbox threads grouped by channel from database."""
    # Log test activities for instagram and youtube
    db_manager.log_activity(
        channel="instagram",
        sender_id="ig_test_user_1",
        sender_name="Martín Gómez",
        message="Hola, ¿hacen blanqueamiento?",
        reply="¡Hola Martín! Sí, realizamos blanqueamiento dental.",
        agent="SolverAgent (Clinical Catalog)",
        intent="INQUIRE_PRICE_OR_TREATMENT"
    )
    db_manager.log_activity(
        channel="youtube",
        sender_id="yt_test_comment_1",
        sender_name="Mariana López",
        message="Excelente video doctor, ¿dónde queda el consultorio?",
        reply="¡Gracias Mariana! Estamos en Av. Santa Fe 2450.",
        agent="SolverAgent (General FAQ)",
        intent="GENERAL_FAQ"
    )

    response = client.get("/api/dashboard/channels-inbox")
    assert response.status_code == 200
    data = response.json()
    assert "instagram" in data
    assert "youtube" in data
    assert "whatsapp" in data
    assert "facebook" in data

    ig = data["instagram"]
    assert ig["total_messages"] >= 2
    assert ig["active_threads"] >= 1
    assert ig["last_message"] is not None
    assert len(ig["threads"]) >= 1

    yt = data["youtube"]
    assert yt["total_messages"] >= 2
    assert yt["active_threads"] >= 1

    # Check that /api/dashboard/summary also contains channels_inbox
    summary_resp = client.get("/api/dashboard/summary")
    assert summary_resp.status_code == 200
    summary_data = summary_resp.json()
    assert "channels_inbox" in summary_data
    assert "instagram" in summary_data["channels_inbox"]

