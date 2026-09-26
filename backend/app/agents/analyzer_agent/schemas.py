from typing import Optional, List, Literal
from pydantic import BaseModel, Field


class ClinicalAnalysis(BaseModel):
    """Clinical diagnosis, entity extraction, and RAG contextual insights."""
    intent: Literal[
        "BOOK_APPOINTMENT",
        "INQUIRE_PRICE_OR_TREATMENT",
        "EMERGENCY_OR_PAIN",
        "GENERAL_FAQ",
        "GREETING"
    ] = Field(..., description="Intención primaria del paciente")
    urgency: Literal["normal", "high"] = Field("normal", description="Nivel de urgencia médica")
    detected_problem: str = Field(..., description="Descripción clínica del problema o consulta")
    extracted_name: Optional[str] = Field(None, description="Nombre del paciente")
    extracted_treatment: Optional[str] = Field(None, description="Tratamiento mencionado")
    extracted_date: Optional[str] = Field(None, description="Fecha solicitada")
    extracted_time: Optional[str] = Field(None, description="Hora solicitada")
    summary: str = Field(..., description="Resumen estructurado")
    rag_knowledge_context: List[str] = Field(
        default_factory=list,
        description="Fragmentos de conocimiento clínico recuperados vía RAG"
    )
    patient_memory_context: List[str] = Field(
        default_factory=list,
        description="Memorias a largo plazo del paciente recuperadas vía RAG"
    )
