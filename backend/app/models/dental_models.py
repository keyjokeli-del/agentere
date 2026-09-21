from typing import Optional, List, Literal
from pydantic import BaseModel, Field

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
