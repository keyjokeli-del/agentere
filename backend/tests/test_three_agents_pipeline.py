import pytest
from datetime import date, timedelta
from app.agents.dental_agents import (
    ReaderAgent,
    AnalyzerAgent,
    SolverAgent,
    OmniChannelPipeline,
    pipeline
)
from app.models.dental_models import OmniChannelMessage, ClinicalAnalysis, SolverResponse
from app.services.calendar_service import CalendarService, calendar_service

@pytest.fixture(autouse=True)
def isolate_calendar(monkeypatch):
    """Ensures deterministic in-memory calendar state for 3-agent tests."""
    monkeypatch.setattr(CalendarService, "_init_google_service", lambda self: None)
    monkeypatch.setattr(calendar_service, "service", None)
    calendar_service.local_appointments = []

def test_reader_agent_whatsapp_ingestion():
    reader = ReaderAgent()
    payload = {
        "sender_id": "5491178296781@s.whatsapp.net",
        "sender_name": "Jovam",
        "message": "Hola, necesito saber el costo de una limpieza"
    }
    msg = reader.from_whatsapp(payload)
    assert isinstance(msg, OmniChannelMessage)
    assert msg.channel == "whatsapp"
    assert msg.sender_id == "5491178296781@s.whatsapp.net"
    assert msg.sender_name == "Jovam"
    assert msg.raw_text == "Hola, necesito saber el costo de una limpieza"

def test_reader_agent_meta_facebook_and_instagram():
    reader = ReaderAgent()
    
    # Facebook Messenger payload
    fb_payload = {
        "object": "page",
        "entry": [{
            "id": "page-123",
            "messaging": [{
                "sender": {"id": "fb-user-999"},
                "recipient": {"id": "page-123"},
                "message": {"mid": "mid.123", "text": "Hola, ¿atienden los sábados?"}
            }]
        }]
    }
    fb_msg = reader.from_meta(fb_payload, channel="facebook")
    assert fb_msg.channel == "facebook"
    assert fb_msg.sender_id == "fb-user-999"
    assert fb_msg.raw_text == "Hola, ¿atienden los sábados?"
    assert fb_msg.metadata.get("mid") == "mid.123"

    # Instagram Direct payload
    ig_payload = {
        "object": "instagram",
        "entry": [{
            "id": "ig-page-456",
            "messaging": [{
                "sender": {"id": "ig-user-777"},
                "recipient": {"id": "ig-page-456"},
                "message": {"mid": "mid.456", "text": "Quiero blanqueamiento"}
            }]
        }]
    }
    ig_msg = reader.from_meta(ig_payload, channel="instagram")
    assert ig_msg.channel == "instagram"
    assert ig_msg.sender_id == "ig-user-777"
    assert ig_msg.raw_text == "Quiero blanqueamiento"

def test_reader_agent_youtube_comment():
    reader = ReaderAgent()
    yt_payload = {
        "snippet": {
            "videoId": "vid-101",
            "topLevelComment": {
                "id": "comm-202",
                "snippet": {
                    "textDisplay": "Excelente video doctor, ¿cuánto cuesta ese implante?",
                    "authorDisplayName": "Carlos Gomez",
                    "authorChannelId": {"value": "UC_channel_123"}
                }
            }
        }
    }
    yt_msg = reader.from_youtube(yt_payload)
    assert yt_msg.channel == "youtube"
    assert yt_msg.sender_id == "UC_channel_123"
    assert yt_msg.sender_name == "Carlos Gomez"
    assert "cuánto cuesta ese implante" in yt_msg.raw_text
    assert yt_msg.metadata.get("video_id") == "vid-101"

def test_analyzer_agent_clinical_detection():
    analyzer = AnalyzerAgent()
    
    # Emergency & Pain test
    msg_pain = OmniChannelMessage(
        channel="whatsapp",
        sender_id="user-1",
        sender_name="Mateo",
        raw_text="Tengo un dolor muy fuerte y pulsante en una muela"
    )
    analysis_pain = analyzer.analyze(msg_pain, context=[])
    assert isinstance(analysis_pain, ClinicalAnalysis)
    assert analysis_pain.intent == "EMERGENCY_OR_PAIN"
    assert analysis_pain.urgency == "high"

    # Price inquiry test
    msg_price = OmniChannelMessage(
        channel="facebook",
        sender_id="user-2",
        sender_name="Laura",
        raw_text="¿Cuánto cuesta un blanqueamiento dental?"
    )
    analysis_price = analyzer.analyze(msg_price, context=[])
    assert analysis_price.intent == "INQUIRE_PRICE_OR_TREATMENT"
    assert analysis_price.urgency == "normal"

def test_solver_agent_solution_and_actions():
    solver = SolverAgent()

    # Case 1: Emergency solution must not prescribe drugs
    msg_emergency = OmniChannelMessage(
        channel="instagram",
        sender_id="user-3",
        sender_name="Sofia",
        raw_text="Me duele mucho, ¿puedo tomar amoxicilina o ibuprofeno?"
    )
    analysis_emergency = ClinicalAnalysis(
        intent="EMERGENCY_OR_PAIN",
        urgency="high",
        detected_problem="Dolor agudo con consulta de automedicación",
        summary="Paciente con dolor pregunta por medicamentos"
    )
    solution_emergency = solver.solve(msg_emergency, analysis_emergency, context=[])
    assert isinstance(solution_emergency, SolverResponse)
    assert solution_emergency.action_taken == "emergency_diverted"
    assert "recetar" in solution_emergency.reply.lower() or "prescribir" in solution_emergency.reply.lower() or "valoración física" in solution_emergency.reply.lower()

    # Case 2: Appointment slot proposition
    target_d = (date.today() + timedelta(days=3)).strftime("%Y-%m-%d")
    msg_book = OmniChannelMessage(
        channel="whatsapp",
        sender_id="user-4",
        sender_name="Esteban",
        raw_text="Quiero una cita para ortodoncia"
    )
    analysis_book = ClinicalAnalysis(
        intent="BOOK_APPOINTMENT",
        urgency="normal",
        detected_problem="Solicitud de cita para ortodoncia",
        extracted_treatment="Ortodoncia",
        extracted_date=target_d,
        extracted_time=None,
        summary="Cita para ortodoncia"
    )
    solution_book = solver.solve(msg_book, analysis_book, context=[])
    assert solution_book.action_taken == "slots_proposed"
    assert "horarios disponibles" in solution_book.reply.lower()

def test_omnichannel_pipeline_end_to_end():
    p = OmniChannelPipeline()
    raw_payload = {
        "sender_id": "5491178296781@s.whatsapp.net",
        "sender_name": "Jovam",
        "message": "Hola, ¿cuánto cuesta una limpieza dental?"
    }
    omni_msg = p.reader.from_whatsapp(raw_payload)
    solution = p.process_message(omni_msg)
    
    assert solution.channel == "whatsapp"
    assert solution.sender_id == "5491178296781@s.whatsapp.net"
    assert solution.intent in ("INQUIRE_PRICE_OR_TREATMENT", "GENERAL_FAQ")
    assert "$30" in solution.reply or "Limpieza" in solution.reply
    
    # Verify session memory saved
    session_id = f"whatsapp:{omni_msg.sender_id}"
    history = p.sessions[session_id]
    assert len(history) == 2
    assert history[0]["content"] == omni_msg.raw_text
    assert history[1]["content"] == solution.reply
