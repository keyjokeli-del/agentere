import pytest
from typing import Optional, List, Dict, Any
from app.core.database import DatabaseManager
from app.services.embedding_service import embedding_service
from app.agents import (
    ReaderAgent,
    ReaderMemory,
    AnalyzerAgent,
    AnalyzerMemory,
    SolverAgent,
    SolverMemory,
    OmniChannelPipeline,
    OmniChannelMessage,
    ClinicalAnalysis
)
from app.services.calendar_service import CalendarService, calendar_service


@pytest.fixture
def isolated_memory():
    """Provides an isolated in-memory hybrid memory composed of ReaderMemory, AnalyzerMemory, and SolverMemory."""
    db = DatabaseManager(in_memory_only=True)
    db.seed_clinical_knowledge()
    reader_mem = ReaderMemory(db=db)
    analyzer_mem = AnalyzerMemory(db=db, embedder=embedding_service)
    solver_mem = SolverMemory(db=db, embedder=embedding_service)

    class CombinedMemory:
        def __init__(self):
            self.db = db
            self.reader_memory = reader_mem
            self.analyzer_memory = analyzer_mem
            self.solver_memory = solver_mem

        def embed_text(self, text: str):
            return embedding_service.embed_text(text)

        def add_turn(self, channel: str, sender_id: Optional[str] = None, role: str = "user", content: str = "", sender: Optional[str] = None):
            target = sender_id if sender_id is not None else (sender or "")
            return self.solver_memory.add_turn(channel=channel, sender_id=target, role=role, content=content)

        def get_recent_turns(self, channel: str, sender_id: Optional[str] = None, limit: int = 4, sender: Optional[str] = None):
            target = sender_id if sender_id is not None else (sender or "")
            return self.reader_memory.get_recent_turns(channel=channel, sender_id=target, limit=limit)

        def search_clinical_knowledge(self, query: str, top_k: int = 3):
            return self.analyzer_memory.search_clinical_knowledge(query, top_k=top_k)

        def search_patient_memories(self, sender: str, query: str, top_k: int = 3):
            return self.analyzer_memory.search_patient_memories(sender, query, top_k=top_k)

        def add_patient_memory(self, sender_id: str, patient_name: str, memory_text: str):
            return self.solver_memory.add_patient_memory(sender_id, patient_name, memory_text)

        def init_db(self):
            return self.db.init_db()

        def seed_clinical_knowledge(self):
            return self.db.seed_clinical_knowledge()

    return CombinedMemory()


@pytest.fixture(autouse=True)
def isolate_calendar(monkeypatch):
    """Ensures deterministic calendar state."""
    monkeypatch.setattr(CalendarService, "_init_google_service", lambda self: None)
    monkeypatch.setattr(calendar_service, "service", None)
    calendar_service.local_appointments = []


def test_rag_embedding_dimension_and_normalization(isolated_memory):
    """Verifies that embed_text generates exactly 768-dimensional normalized vectors."""
    text = "Limpieza dental ultrasónica y profilaxis"
    vec = isolated_memory.embed_text(text)
    
    assert isinstance(vec, list)
    assert len(vec) == 768
    # Check normalization: Euclidean norm should be ~1.0
    norm = sum(x * x for x in vec) ** 0.5
    assert pytest.approx(norm, 0.01) == 1.0

    # Determinism: same input generates identical embedding
    vec2 = isolated_memory.embed_text(text)
    assert vec == vec2


def test_short_term_memory_turn_tracking(isolated_memory):
    """Verifies storing and retrieving the last 4 turns in chronological order."""
    channel = "whatsapp"
    sender = "patient_555"

    # Add 6 turns
    for i in range(1, 7):
        role = "user" if i % 2 != 0 else "assistant"
        isolated_memory.add_turn(channel, sender, role, f"Mensaje número {i}")

    # Fetch last 4 turns
    recent_turns = isolated_memory.get_recent_turns(channel, sender, limit=4)
    assert len(recent_turns) == 4
    # Chronological: 3, 4, 5, 6
    assert recent_turns[0]["content"] == "Mensaje número 3"
    assert recent_turns[1]["content"] == "Mensaje número 4"
    assert recent_turns[2]["content"] == "Mensaje número 5"
    assert recent_turns[3]["content"] == "Mensaje número 6"

    # Verify channel/sender isolation
    other_turns = isolated_memory.get_recent_turns("instagram", sender, limit=4)
    assert len(other_turns) == 0


def test_clinical_knowledge_vector_search(isolated_memory):
    """Verifies that RAG searches clinical knowledge vectors and returns relevant chunks."""
    results = isolated_memory.search_clinical_knowledge("cuidados después de extracción muela juicio", top_k=2)
    assert len(results) >= 1
    topics = [r["topic"] for r in results]
    assert any("gasa" in r["content"].lower() or "coágulo" in r["content"].lower() or "hielo" in r["content"].lower() for r in results)


def test_patient_long_term_memory_vector_search(isolated_memory):
    """Verifies saving and retrieving patient's long-term memory across sessions."""
    sender_id = "patient_valeria_99"
    isolated_memory.add_patient_memory(
        sender_id=sender_id,
        patient_name="Valeria",
        memory_text="Paciente alérgica al látex y sensible a la anestesia local"
    )
    isolated_memory.add_patient_memory(
        sender_id=sender_id,
        patient_name="Valeria",
        memory_text="Interesada en colocación de brackets estéticos de zafiro"
    )

    # Search for allergies
    allergy_mem = isolated_memory.search_patient_memories(sender_id, "alergia anestesia", top_k=1)
    assert len(allergy_mem) == 1
    assert "látex" in allergy_mem[0]["memory_text"].lower() or "anestesia" in allergy_mem[0]["memory_text"].lower()
    assert allergy_mem[0]["patient_name"] == "Valeria"

    # Isolation check: other patient has no memories
    other_mem = isolated_memory.search_patient_memories("patient_other", "alergia", top_k=1)
    assert len(other_mem) == 0


def test_reader_agent_injects_recent_history(isolated_memory):
    """Verifies ReaderAgent populates recent_history in OmniChannelMessage."""
    reader = ReaderAgent(memory_service=isolated_memory)
    isolated_memory.add_turn("whatsapp", "user_wa_1", "user", "Hola doctor")
    isolated_memory.add_turn("whatsapp", "user_wa_1", "assistant", "¡Hola! ¿En qué te ayudamos?")

    payload = {
        "sender_id": "user_wa_1",
        "sender_name": "Marcos",
        "message": "Quisiera consultar por implantes"
    }
    msg = reader.from_whatsapp(payload)
    assert msg.channel == "whatsapp"
    assert len(msg.recent_history) == 2
    assert msg.recent_history[0]["content"] == "Hola doctor"


def test_analyzer_agent_retrieves_rag_context(isolated_memory):
    """Verifies AnalyzerAgent attaches RAG knowledge and patient memories to ClinicalAnalysis."""
    analyzer = AnalyzerAgent(memory_service=isolated_memory)
    isolated_memory.add_patient_memory("user_ana_1", "Ana", "Prefiere citas por la tarde")

    msg = OmniChannelMessage(
        channel="web",
        sender_id="user_ana_1",
        sender_name="Ana",
        raw_text="¿Cuánto cuesta el blanqueamiento dental LED?"
    )

    analysis = analyzer.analyze(msg, context=[])
    assert isinstance(analysis, ClinicalAnalysis)
    assert analysis.intent == "INQUIRE_PRICE_OR_TREATMENT"
    assert len(analysis.rag_knowledge_context) > 0
    assert any("Blanqueamiento" in c for c in analysis.rag_knowledge_context)
    assert len(analysis.patient_memory_context) > 0
    assert "tarde" in analysis.patient_memory_context[0].lower()


def test_solver_agent_records_turns_and_memories(isolated_memory):
    """Verifies SolverAgent logs conversation turns and vectorizes patient details."""
    solver = SolverAgent(memory_service=isolated_memory)

    msg = OmniChannelMessage(
        channel="facebook",
        sender_id="fb_user_pedro",
        sender_name="Pedro Gomez",
        raw_text="Me duele muchísimo una muela, es urgente"
    )

    analysis = ClinicalAnalysis(
        intent="EMERGENCY_OR_PAIN",
        urgency="high",
        detected_problem="Dolor agudo en muela",
        extracted_name="Pedro Gomez",
        extracted_treatment="Extracción o Urgencia",
        summary="Paciente con dolor dental agudo.",
        rag_knowledge_context=["Protocolo de Urgencias: atención inmediata en el día."],
        patient_memory_context=[]
    )

    response = solver.solve(msg, analysis, context=[])
    assert response.channel == "facebook"
    assert response.intent == "EMERGENCY_OR_PAIN"

    # Verify conversation turns were logged
    turns = isolated_memory.get_recent_turns("facebook", "fb_user_pedro", limit=4)
    assert len(turns) == 2
    assert turns[0]["role"] == "user"
    assert turns[1]["role"] == "assistant"

    # Verify patient memory was saved
    memories = isolated_memory.search_patient_memories("fb_user_pedro", "dolor", top_k=2)
    assert len(memories) >= 1
    assert "dolor" in memories[0]["memory_text"].lower() or "urgencia" in memories[0]["memory_text"].lower()


def test_omnichannel_pipeline_end_to_end_with_rag(isolated_memory):
    """Verifies complete multi-turn flow with ReaderAgent -> AnalyzerAgent -> SolverAgent & RAG."""
    pipeline = OmniChannelPipeline(memory_service=isolated_memory)

    # Turn 1: Patient asks about extraction post-op care
    msg1 = pipeline.reader.from_text(
        text="Me sacaron una muela ayer y no sé si puedo tomar mate caliente o usar popote",
        channel="whatsapp",
        sender_id="patient_e2e_1",
        sender_name="Lucia"
    )
    res1 = pipeline.process_message(msg1)
    assert res1.channel == "whatsapp"
    assert len(res1.reply) > 20

    # Turn 2: Follow-up question
    msg2 = pipeline.reader.from_text(
        text="¿Y qué hago si me empieza a doler mucho?",
        channel="whatsapp",
        sender_id="patient_e2e_1",
        sender_name="Lucia"
    )
    assert len(msg2.recent_history) >= 2  # Turn 1 user + Turn 1 assistant

    res2 = pipeline.process_message(msg2)
    assert res2.channel == "whatsapp"
    assert len(res2.reply) > 20

    # Verify turns logged
    all_turns = isolated_memory.get_recent_turns("whatsapp", "patient_e2e_1", limit=4)
    assert len(all_turns) == 4


def test_neon_pgvector_database_integration():
    """Verifies that live Neon PostgreSQL supports pgvector and tables when DATABASE_URL is present."""
    from app.config import settings
    from app.core.database import psycopg
    if not settings.database_url or psycopg is None:
        pytest.skip("DATABASE_URL or psycopg driver not available in environment")
    live_db = DatabaseManager(in_memory_only=False)
    ok = live_db.init_db()
    assert ok is True
    seeded = live_db.seed_clinical_knowledge()
    assert seeded >= 6
