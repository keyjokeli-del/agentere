from typing import Optional, List, Literal, Dict, Any
from pydantic import BaseModel, Field

# Re-export domain models from their respective modular agent packages
from app.agents.reader_agent.schemas import OmniChannelMessage
from app.agents.analyzer_agent.schemas import ClinicalAnalysis
from app.agents.solver_agent.schemas import (
    SolverResponse,
    Treatment,
    GeneralFAQ,
    ClinicCatalog,
    TriageResult,
)


class AgentResponse(BaseModel):
    """Normalized response format for legacy API callers and dashboard endpoints."""
    reply: str
    channel: str
    sender_id: str
    intent: str
    agent: str
    timestamp: str


class AppointmentRecord(BaseModel):
    """Calendar appointment entity."""
    id: str
    patient_name: str
    contact: str
    treatment: str
    date: str  # YYYY-MM-DD
    time: str  # HH:MM
    channel: str = "whatsapp"
    status: Literal["confirmed", "cancelled", "completed"] = "confirmed"
    created_at: str


class AppointmentCreateRequest(BaseModel):
    """Input payload to book an appointment."""
    patient_name: str = Field(..., min_length=2, description="Nombre del paciente")
    contact: str = Field(..., description="Teléfono o ID del canal de mensajería")
    treatment: str = Field(..., description="Tratamiento solicitado")
    date: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$", description="Fecha en formato YYYY-MM-DD")
    time: str = Field(..., pattern=r"^\d{2}:\d{2}$", description="Hora en formato HH:MM")
    channel: str = Field("whatsapp", description="Canal de procedencia")


class SlotsResponse(BaseModel):
    """Schedule query response."""
    date: str = Field(..., description="Fecha consultada en formato YYYY-MM-DD")
    slot_duration_minutes: int = Field(45, description="Duración de cada franja en minutos")
    slots: List[str] = Field(..., description="Lista de horarios disponibles (HH:MM)")


__all__ = [
    "OmniChannelMessage",
    "ClinicalAnalysis",
    "SolverResponse",
    "Treatment",
    "GeneralFAQ",
    "ClinicCatalog",
    "TriageResult",
    "AgentResponse",
    "AppointmentRecord",
    "AppointmentCreateRequest",
    "SlotsResponse",
]
