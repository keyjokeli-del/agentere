from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

from app.models.dental_models import AgentResponse
from app.agents.reader_agent import ReaderAgent, OmniChannelMessage
from app.agents.analyzer_agent import AnalyzerAgent, ClinicalAnalysis
from app.agents.solver_agent import (
    SolverAgent,
    SolverResponse,
    TriageResult,
    DentalFAQAgent,
    AppointmentAgent,
    CLINIC_CATALOG
)


class TriageAgent:
    """Legacy wrapper delegating triage and clinical analysis to ReaderAgent and AnalyzerAgent."""

    def __init__(
        self,
        reader: Optional[ReaderAgent] = None,
        analyzer: Optional[AnalyzerAgent] = None,
        memory_service: Optional[Any] = None
    ) -> None:
        self.reader = reader or ReaderAgent()
        self.analyzer = analyzer or AnalyzerAgent()

    def process(self, message: str, context: List[Dict[str, str]]) -> TriageResult:
        omni_msg = self.reader.from_text(message)
        analysis = self.analyzer.analyze(omni_msg, context)
        return TriageResult(
            intent=analysis.intent,
            extracted_name=analysis.extracted_name,
            extracted_treatment=analysis.extracted_treatment,
            extracted_date=analysis.extracted_date,
            extracted_time=analysis.extracted_time,
            urgency=analysis.urgency,
            summary=analysis.summary
        )


class OmniChannelPipeline:
    """Centralized orchestrator running the sequential 3-agent critical pipeline:
    ReaderAgent -> AnalyzerAgent -> SolverAgent
    with Hybrid Memory and Neon PostgreSQL pgvector.
    """

    def __init__(
        self,
        reader: Optional[ReaderAgent] = None,
        analyzer: Optional[AnalyzerAgent] = None,
        solver: Optional[SolverAgent] = None,
        memory_service: Optional[Any] = None
    ) -> None:
        self.reader = reader or ReaderAgent(memory_service=memory_service)
        self.analyzer = analyzer or AnalyzerAgent(memory_service=memory_service)
        self.solver = solver or SolverAgent(memory_service=memory_service)
        self.sessions: Dict[str, List[Dict[str, str]]] = {}

    def get_or_create_session(self, session_id: str) -> List[Dict[str, str]]:
        if session_id not in self.sessions:
            self.sessions[session_id] = []
        return self.sessions[session_id]

    def process_message(self, message: OmniChannelMessage) -> SolverResponse:
        session_id = f"{message.channel}:{message.sender_id}"
        history = self.get_or_create_session(session_id)

        # Ingest short-term memory if empty
        if not message.recent_history:
            message.recent_history = self.reader.memory.get_recent_turns(message.channel, message.sender_id, limit=4)

        combined_history = history if history else message.recent_history

        # 1. AnalyzerAgent (with RAG retrieval)
        analysis = self.analyzer.analyze(message, combined_history)

        # 2. SolverAgent (solves, logs turns, extracts patient memory)
        solution = self.solver.solve(message, analysis, combined_history)

        # 3. Update session cache
        history.append({"role": "user", "content": message.raw_text})
        history.append({"role": "assistant", "content": solution.reply})

        return solution

    def process_incoming_message(
        self,
        message: str,
        sender_id: str,
        channel: str = "web",
        sender_name: str = "Paciente",
        payload: Optional[Dict[str, Any]] = None
    ) -> AgentResponse:
        """Backward-compatible entrypoint matching legacy DentalAgentCoordinator."""
        if payload:
            omni_msg = self.reader.read(payload, channel=channel, default_sender=sender_id)
        else:
            omni_msg = self.reader.from_text(
                text=message,
                channel=channel,
                sender_id=sender_id,
                sender_name=sender_name
            )

        solution = self.process_message(omni_msg)

        return AgentResponse(
            reply=solution.reply,
            channel=solution.channel,
            sender_id=solution.sender_id,
            intent=solution.intent,
            agent=solution.agent,
            timestamp=solution.timestamp
        )


pipeline = OmniChannelPipeline()
coordinator = pipeline
DentalAgentCoordinator = OmniChannelPipeline

__all__ = [
    "OmniChannelPipeline",
    "TriageAgent",
    "pipeline",
    "coordinator",
    "DentalAgentCoordinator",
    "ReaderAgent",
    "AnalyzerAgent",
    "SolverAgent",
    "DentalFAQAgent",
    "AppointmentAgent",
    "CLINIC_CATALOG"
]
