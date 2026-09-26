from typing import Optional, List, Literal
from datetime import datetime, timezone
from pydantic import BaseModel, Field


class SolverResponse(BaseModel):
    """Final solution response emitted by SolverAgent."""
    reply: str = Field(..., description="Respuesta empática final redactada para el paciente")
    channel: str = Field(..., description="Canal de destino")
    sender_id: str = Field(..., description="Identificador del destinatario")
    intent: str = Field(..., description="Intención clínica diagnosticada")
    agent: str = Field("SolverAgent", description="Agente resolutor responsable")
    action_taken: str = Field("responded", description="Acción clínica ejecutada")
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="Marca temporal de la respuesta"
    )


class Treatment(BaseModel):
    """Clinical treatment offering with duration, pricing, and scope."""
    name: str = Field(..., description="Nombre del tratamiento odontológico")
    duration_min: int = Field(..., description="Duración estimada en minutos")
    price_range: str = Field(..., description="Rango de precio orientativo")
    description: str = Field(..., description="Descripción clínica básica del procedimiento")


class GeneralFAQ(BaseModel):
    """Clinic policy, schedule, or frequently asked question."""
    question: str = Field(..., description="Pregunta frecuente")
    answer: str = Field(..., description="Respuesta estándar de la clínica")


class ClinicCatalog(BaseModel):
    """Validated catalog of treatments and general clinic FAQs."""
    treatments: List[Treatment]
    general_faqs: List[GeneralFAQ]


class TriageResult(BaseModel):
    """Structured triage data used by sub-agents (appointment and FAQ)."""
    intent: Literal[
        "BOOK_APPOINTMENT",
        "INQUIRE_PRICE_OR_TREATMENT",
        "EMERGENCY_OR_PAIN",
        "GENERAL_FAQ",
        "GREETING"
    ] = Field(..., description="Intención primaria del paciente")
    extracted_name: Optional[str] = Field(None, description="Nombre extraído del paciente")
    extracted_treatment: Optional[str] = Field(None, description="Tratamiento mencionado")
    extracted_date: Optional[str] = Field(None, description="Fecha solicitada (YYYY-MM-DD o relativa)")
    extracted_time: Optional[str] = Field(None, description="Hora solicitada (HH:MM)")
    urgency: Literal["normal", "high"] = Field("normal", description="Nivel de urgencia médica")
    summary: str = Field(..., description="Resumen breve de la necesidad del paciente")
