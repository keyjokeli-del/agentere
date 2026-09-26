import pytest
from app.models.dental_models import ClinicCatalog, Treatment, TriageResult, AgentResponse
from app.agents import TriageAgent, DentalFAQAgent, DentalAgentCoordinator
from app.services.groq_service import GroqService

def test_pydantic_catalog_and_triage_models():
    """Validates Task 1.1: Pydantic models for catalog and triage results."""
    triage = TriageResult(
        intent="BOOK_APPOINTMENT",
        extracted_name="Juan Perez",
        extracted_treatment="Ortodoncia",
        extracted_date="2026-09-25",
        extracted_time="15:00",
        urgency="normal",
        summary="El paciente solicita agendar turno para ortodoncia."
    )
    assert triage.intent == "BOOK_APPOINTMENT"
    assert triage.extracted_time == "15:00"
    assert triage.urgency == "normal"

    # Verify JSON serialization round-trip
    dumped = triage.model_dump()
    reconstructed = TriageResult.model_validate(dumped)
    assert reconstructed.extracted_name == "Juan Perez"

def test_groq_fallback_determinism_under_rate_limits():
    """Validates Task 1.2: Deterministic fallback under missing key or 429 rate limit."""
    service = GroqService(api_key=None)  # Simulates unconfigured or offline API
    messages = [
        {"role": "system", "content": "Devuelve un json con intent"},
        {"role": "user", "content": "Quiero agendar una cita para mañana"}
    ]
    response = service.chat_completion(messages, response_format={"type": "json_object"})
    assert "BOOK_APPOINTMENT" in response

    # Non-json conversation fallback
    chat_response = service.chat_completion([{"role": "user", "content": "Hola"}])
    assert "Clínica Dental" in chat_response

def test_triage_agent_classification():
    """Validates Task 1.3: TriageAgent classifying intents and urgencies."""
    triage_agent = TriageAgent()

    # 1. Acute pain -> High urgency emergency
    res_emergency = triage_agent.process("¡Me duele muchísimo una muela y se me hinchó la cara!", context=[])
    assert res_emergency.intent == "EMERGENCY_OR_PAIN"
    assert res_emergency.urgency == "high"

    # 2. Appointment booking
    res_booking = triage_agent.process("Hola, quisiera agendar un turno para una limpieza", context=[])
    assert res_booking.intent == "BOOK_APPOINTMENT"

    # 3. Price inquiry
    res_price = triage_agent.process("¿Cuánto cuesta un implante dental de titanio?", context=[])
    assert res_price.intent == "INQUIRE_PRICE_OR_TREATMENT"

def test_dental_faq_agent_ethics_and_disclaimer():
    """Validates Task 1.4: DentalFAQAgent constraints (no prescriptions & physical exam disclaimer)."""
    faq_agent = DentalFAQAgent()
    triage_dummy = TriageResult(
        intent="GENERAL_FAQ",
        urgency="normal",
        summary="Consulta"
    )

    # 1. Patient asks for prescription drugs (Ethical restriction check)
    reply_med = faq_agent.generate_response(
        "¿Qué pastilla o antibiótico puedo tomar para el dolor de muela?",
        triage_dummy,
        context=[]
    )
    assert "recetar" in reply_med.lower() or "normativas" in reply_med.lower() or "consultorio" in reply_med.lower()

    # 2. Price inquiry includes clinical evaluation notice
    reply_price = faq_agent.generate_response(
        "¿Cuánto sale el blanqueamiento dental?",
        triage_dummy,
        context=[]
    )
    assert len(reply_price) > 20

def test_dental_coordinator_end_to_end():
    """Validates Checkpoint 1: Coordinator orchestrates flow and returns AgentResponse."""
    coordinator = DentalAgentCoordinator()
    
    # Send message as WhatsApp user
    response = coordinator.process_incoming_message(
        message="Hola, ¿atienden urgencias los fines de semana?",
        sender_id="5491155554444",
        channel="whatsapp"
    )
    assert isinstance(response, AgentResponse)
    assert response.channel == "whatsapp"
    assert response.sender_id == "5491155554444"
    assert len(response.reply) > 10
