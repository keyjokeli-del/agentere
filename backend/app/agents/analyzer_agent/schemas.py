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
    fdi_teeth: List[int] = Field(
        default_factory=list,
        description="Piezas dentales detectadas bajo nomenclatura FDI (11 a 48)"
    )
    sentiment_score: float = Field(
        0.0,
        description="Puntaje de sentimiento del paciente (-1.0 negativo a 1.0 positivo)"
    )
    frustration_detected: bool = Field(
        False,
        description="Indica si el paciente expresa frustración o enojo severo"
    )
    clinical_followup_needed: bool = Field(
        False,
        description="Indica si se deben formular preguntas de seguimiento clínico de seguridad"
    )
    clinical_followup_questions: List[str] = Field(
        default_factory=list,
        description="Preguntas de triaje clínico de seguridad"
    )
    visual_assessment: Optional[str] = Field(
        None,
        description="Evaluación preliminar de imagen dental vía Gemini"
    )
    detected_language: str = Field(
        "es",
        description="Idioma detectado del paciente ('es', 'en', 'pt', 'fr')"
    )
