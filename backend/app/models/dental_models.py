from typing import Optional, List, Literal, Dict, Any
from datetime import datetime, timezone
from pydantic import BaseModel, Field

class OmniChannelMessage(BaseModel):
    channel: Literal["whatsapp", "facebook", "instagram", "youtube", "web"] = Field(..., description="Canal de procedencia")
    sender_id: str = Field(..., description="Identificador único del remitente en el canal")
    sender_name: str = Field("Paciente", description="Nombre o apodo visible del paciente")
    raw_text: str = Field(..., description="Texto limpio extraído del mensaje")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadatos contextuales (post_id, comment_id, message_id, etc.)")
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat(), description="Marca temporal ISO en UTC")

class ClinicalAnalysis(BaseModel):
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

class SolverResponse(BaseModel):
    reply: str = Field(..., description="Respuesta empática final redactada para el paciente")
    channel: str = Field(..., description="Canal de destino")
    sender_id: str = Field(..., description="Identificador del destinatario")
    intent: str = Field(..., description="Intención clínica diagnosticada")
    agent: str = Field("SolverAgent", description="Agente resolutor responsable")
    action_taken: str = Field("responded", description="Acción clínica ejecutada")
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat(), description="Marca temporal de la respuesta")

class Treatment(BaseModel):
    name: str = Field(..., description="Nombre del tratamiento odontológico")
    duration_min: int = Field(..., description="Duración estimada en minutos")
    price_range: str = Field(..., description="Rango de precio orientativo")
    description: str = Field(..., description="Descripción clínica básica del procedimiento")

class GeneralFAQ(BaseModel):
    question: str = Field(..., description="Pregunta frecuente")
    answer: str = Field(..., description="Respuesta estándar de la clínica")

class ClinicCatalog(BaseModel):
    treatments: List[Treatment]
    general_faqs: List[GeneralFAQ]

class TriageResult(BaseModel):
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

class AgentResponse(BaseModel):
    reply: str
    channel: str
    sender_id: str
    intent: str
    agent: str
    timestamp: str

class AppointmentRecord(BaseModel):
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
    patient_name: str = Field(..., min_length=2, description="Nombre del paciente")
    contact: str = Field(..., description="Teléfono o ID del canal de mensajería")
    treatment: str = Field(..., description="Tratamiento solicitado")
    date: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$", description="Fecha en formato YYYY-MM-DD")
    time: str = Field(..., pattern=r"^\d{2}:\d{2}$", description="Hora en formato HH:MM")
    channel: str = Field("whatsapp", description="Canal de procedencia")

class SlotsResponse(BaseModel):
    date: str = Field(..., description="Fecha consultada en formato YYYY-MM-DD")
    slot_duration_minutes: int = Field(45, description="Duración de cada franja en minutos")
    slots: List[str] = Field(..., description="Lista de horarios disponibles (HH:MM)")
