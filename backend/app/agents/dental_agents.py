import json
from typing import Dict, Any, List, Optional
from datetime import datetime, date, timedelta, timezone

from app.config import settings
from app.services.groq_service import groq_service
from app.services.calendar_service import calendar_service
from app.models.dental_models import ClinicCatalog, Treatment, GeneralFAQ, TriageResult, AgentResponse

# Load and validate clinic knowledge base with Pydantic
DATA_FILE = settings.BASE_DIR / "app" / "data" / "clinic_info.json"
try:
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        raw_json = json.load(f)
    CLINIC_CATALOG = ClinicCatalog.model_validate(raw_json)
except Exception as e:
    print(f"[DentalAgents] Notice: Using fallback catalog ({e})")
    CLINIC_CATALOG = ClinicCatalog(
        treatments=[
            Treatment(
                name="Limpieza Dental",
                duration_min=45,
                price_range="$30 - $45 USD",
                description="Profilaxis ultrasónica completa"
            )
        ],
        general_faqs=[]
    )


class TriageAgent:
    """Classifies user intent and extracts clinical and booking entities with Pydantic validation."""

    SYSTEM_PROMPT = """Eres el Agente de Triage y Recepción de {clinic_name}.
Tu misión es clasificar el mensaje del paciente y extraer entidades clave.
Devuelve EXCLUSIVAMENTE un objeto JSON válido con la siguiente estructura:
{{
    "intent": "BOOK_APPOINTMENT" | "INQUIRE_PRICE_OR_TREATMENT" | "EMERGENCY_OR_PAIN" | "GENERAL_FAQ" | "GREETING",
    "extracted_name": string or null,
    "extracted_treatment": string or null,
    "extracted_date": string or null (formato YYYY-MM-DD si es identificable, o relativo como 'mañana', 'lunes', etc.),
    "extracted_time": string or null (formato HH:MM si es identificable),
    "urgency": "high" | "normal",
    "summary": "resumen breve de lo que necesita el paciente"
}}
No incluyas texto fuera del JSON.
"""

    def process(self, message: str, context: List[Dict[str, str]]) -> TriageResult:
        prompt = self.SYSTEM_PROMPT.format(clinic_name=settings.clinic_name)
        messages = [
            {"role": "system", "content": prompt},
            *context[-4:],  # Last few turns for context
            {"role": "user", "content": f"Mensaje del paciente: '{message}'"}
        ]
        response_text = groq_service.chat_completion(messages, temperature=0.1, response_format={"type": "json_object"})
        
        try:
            parsed = json.loads(response_text)
            return TriageResult.model_validate(parsed)
        except Exception:
            # Deterministic rule-based fallback
            msg_lower = message.lower()
            if any(w in msg_lower for w in ["duel", "dol", "urgencia", "emergencia", "muela", "sangr", "inflam", "hinch", "rot", "quebr"]):
                return TriageResult(
                    intent="EMERGENCY_OR_PAIN",
                    extracted_name=None,
                    extracted_treatment=None,
                    extracted_date=None,
                    extracted_time=None,
                    urgency="high",
                    summary="El paciente reporta dolor o urgencia dental."
                )
            elif any(w in msg_lower for w in ["cita", "turno", "agend", "reserv", "hora"]):
                return TriageResult(
                    intent="BOOK_APPOINTMENT",
                    extracted_name=None,
                    extracted_treatment=None,
                    extracted_date=None,
                    extracted_time=None,
                    urgency="normal",
                    summary="Solicitud para agendar un turno."
                )
            elif any(w in msg_lower for w in ["precio", "cuanto", "sale", "cuesta", "costo", "valor"]):
                return TriageResult(
                    intent="INQUIRE_PRICE_OR_TREATMENT",
                    extracted_name=None,
                    extracted_treatment=None,
                    extracted_date=None,
                    extracted_time=None,
                    urgency="normal",
                    summary="Consulta sobre costos o procedimientos."
                )
            return TriageResult(
                intent="GENERAL_FAQ",
                extracted_name=None,
                extracted_treatment=None,
                extracted_date=None,
                extracted_time=None,
                urgency="normal",
                summary="Consulta general o saludo."
            )


class DentalFAQAgent:
    """Answers patient questions regarding dental treatments, pricing, and clinic policies with ethical constraints."""

    def __init__(self) -> None:
        self.kb_context = json.dumps(CLINIC_CATALOG.model_dump(), ensure_ascii=False, indent=2)

    def generate_response(self, user_message: str, triage_data: TriageResult, context: List[Dict[str, str]]) -> str:
        # Check for medication or prescription inquiry
        msg_lower = user_message.lower()
        if any(w in msg_lower for w in ["receta", "medicamento", "pastilla", "amoxicilina", "ibuprofeno", "que tomo", "qué puedo tomar"]):
            return (
                f"⚠️ Por normativas médicas y éticas de {settings.clinic_name}, ningún profesional puede recetar "
                f"medicamentos sin una valoración física previa en el consultorio.\n\n"
                f"Si estás con dolor agudo o inflamación, te recomendamos acudir de inmediato a nuestra clínica en "
                f"{settings.clinic_address} o indicarnos si deseas un turno de urgencia hoy mismo."
            )

        system_prompt = f"""Eres el Asistente Clínico Odontológico de {settings.clinic_name}.
Ubicación: {settings.clinic_address}
Teléfono: {settings.clinic_phone}
Horario de Atención: {settings.business_hours_start}:00 a {settings.business_hours_end}:00

BASE DE CONOCIMIENTO DE TRATAMIENTOS Y PRECIOS:
{self.kb_context}

DIRECTRICES CRÍTICAS:
1. Responde de forma empática, clara, concisa y profesional.
2. NUNCA des diagnósticos médicos definitivos. Aclara que el plan de tratamiento y presupuesto final se confirma en la evaluación en el consultorio.
3. Si el paciente siente dolor agudo o urgencia ({triage_data.urgency} == 'high'), prioriza ofrecerle atención inmediata en el día.
4. Invita siempre amablemente al paciente a agendar una cita o evaluación para revisar su caso en detalle.
5. Mantén las respuestas fluidas y directas, óptimas para WhatsApp y redes sociales (párrafos cortos y emojis amigables).
"""
        messages = [
            {"role": "system", "content": system_prompt},
            *context[-4:],
            {"role": "user", "content": user_message}
        ]
        return groq_service.chat_completion(messages, temperature=0.4, max_tokens=350)


class AppointmentAgent:
    """Manages slot checking and booking in Google Calendar."""

    def handle(self, user_message: str, triage_data: TriageResult, sender_id: str, channel: str) -> str:
        # Determine target date
        target_date = date.today() + timedelta(days=1)  # Default: tomorrow
        extracted_date = triage_data.extracted_date
        
        # Check if user specified a date
        if extracted_date:
            try:
                target_date = datetime.strptime(extracted_date, "%Y-%m-%d").date()
            except Exception:
                target_date = date.today() + timedelta(days=1)

        available_slots = calendar_service.get_available_slots(target_date)
        extracted_time = triage_data.extracted_time
        patient_name = triage_data.extracted_name or "Paciente"
        treatment = triage_data.extracted_treatment or "Evaluación Odontológica General"

        # If user selected a specific time that is busy
        if extracted_time and not any(extracted_time in slot for slot in available_slots):
            slots_text = ", ".join(available_slots[:5]) if available_slots else "Sin horarios disponibles"
            return (
                f"⚠️ El horario solicitado (**{extracted_time}**) ya se encuentra reservado para el día **{target_date.strftime('%Y-%m-%d')}**.\n\n"
                f"Te ofrecemos las siguientes alternativas disponibles en ese día:\n"
                f"👉 **{slots_text}**\n\n"
                f"Por favor indícame cuál te queda más cómodo para confirmarte la reserva."
            )

        # If user selected a specific valid slot and confirmed
        if extracted_time and any(extracted_time in slot for slot in available_slots):
            match_slot = next(slot for slot in available_slots if extracted_time in slot)
            appt = calendar_service.create_appointment(
                patient_name=patient_name,
                phone_or_channel_id=sender_id,
                treatment=treatment,
                appointment_date=target_date.strftime("%Y-%m-%d"),
                appointment_time=match_slot,
                channel=channel
            )
            return (
                f"✅ ¡Tu cita ha quedado confirmada con éxito!\n\n"
                f"📅 **Fecha:** {appt.date}\n"
                f"⏰ **Hora:** {appt.time} hs\n"
                f"🦷 **Tratamiento:** {appt.treatment}\n"
                f"📍 **Lugar:** {settings.clinic_address}\n"
                f"🗓️ **Google Calendar:** Registrado en la agenda de la clínica.\n\n"
                f"Te esperamos unos 5 minutos antes. ¡Que tengas un excelente día!"
            )

        # Propose slots
        slots_text = ", ".join(available_slots[:5]) if available_slots else "Sin horarios disponibles"
        return (
            f"📅 Para el día **{target_date.strftime('%Y-%m-%d')}** tenemos los siguientes horarios disponibles:\n"
            f"👉 **{slots_text}**\n\n"
            f"Por favor indícame cuál de estos horarios prefieres y tu nombre completo para confirmarte la reserva en el calendario."
        )


class DentalAgentCoordinator:
    """Coordinates Triage, FAQ and Appointment agents, maintaining per-session memory."""

    def __init__(self) -> None:
        self.triage = TriageAgent()
        self.faq = DentalFAQAgent()
        self.appointment = AppointmentAgent()
        self.sessions: Dict[str, List[Dict[str, str]]] = {}

    def get_or_create_session(self, session_id: str) -> List[Dict[str, str]]:
        if session_id not in self.sessions:
            self.sessions[session_id] = []
        return self.sessions[session_id]

    def process_incoming_message(self, message: str, sender_id: str, channel: str) -> AgentResponse:
        session_id = f"{channel}:{sender_id}"
        history = self.get_or_create_session(session_id)

        # Step 1: Triage
        triage_result = self.triage.process(message, history)
        intent = triage_result.intent

        # Step 2: Routing to specialized agent
        if intent == "BOOK_APPOINTMENT":
            reply_text = self.appointment.handle(message, triage_result, sender_id, channel)
            responding_agent = "Appointment & Calendar Agent"
        else:
            reply_text = self.faq.generate_response(message, triage_result, history)
            responding_agent = "Dental FAQ & Clinical Agent"

        # Update history
        history.append({"role": "user", "content": message})
        history.append({"role": "assistant", "content": reply_text})

        return AgentResponse(
            reply=reply_text,
            channel=channel,
            sender_id=sender_id,
            intent=intent,
            agent=responding_agent,
            timestamp=datetime.now(timezone.utc).isoformat()
        )

coordinator = DentalAgentCoordinator()
