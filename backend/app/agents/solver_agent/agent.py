import json
from typing import Dict, Any, List, Optional
from datetime import datetime, date, timedelta, timezone

from app.config import settings
from app.services.groq_service import groq_service
from app.services.calendar_service import calendar_service
from app.agents.reader_agent.schemas import OmniChannelMessage
from app.agents.analyzer_agent.schemas import ClinicalAnalysis
from app.agents.solver_agent.schemas import (
    SolverResponse,
    Treatment,
    GeneralFAQ,
    ClinicCatalog,
    TriageResult
)
from app.agents.solver_agent.memory import SolverMemory

# Load and validate clinic knowledge base with Pydantic
DATA_FILE = settings.BASE_DIR / "app" / "data" / "clinic_info.json"
try:
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        raw_json = json.load(f)
    CLINIC_CATALOG = ClinicCatalog.model_validate(raw_json)
except Exception as e:
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


class DentalFAQAgent:
    """Answers patient questions regarding dental treatments, pricing, and clinic policies with ethical constraints."""

    def __init__(self) -> None:
        self.kb_context = json.dumps(CLINIC_CATALOG.model_dump(), ensure_ascii=False, indent=2)

    def generate_response(
        self,
        user_message: str,
        triage_data: TriageResult,
        context: List[Dict[str, str]],
        rag_knowledge: Optional[List[str]] = None,
        patient_memories: Optional[List[str]] = None
    ) -> str:
        # Check for medication or prescription inquiry
        msg_lower = user_message.lower()
        if any(w in msg_lower for w in ["receta", "medicamento", "pastilla", "amoxicilina", "ibuprofeno", "que tomo", "qué puedo tomar"]):
            return (
                f"⚠️ Por normativas médicas y éticas de {settings.clinic_name}, ningún profesional puede recetar "
                f"medicamentos sin una valoración física previa en el consultorio.\n\n"
                f"Si estás con dolor agudo o inflamación, te recomendamos acudir de inmediato a nuestra clínica en "
                f"{settings.clinic_address} o indicarnos si deseas un turno de urgencia hoy mismo."
            )

        rag_section = ""
        if rag_knowledge:
            rag_section += "\n\nCONOCIMIENTO CLÍNICO RAG RELEVANTE (Neon pgvector):\n" + "\n---\n".join(rag_knowledge)
        if patient_memories:
            rag_section += "\n\nANTECEDENTES DEL PACIENTE:\n" + "\n---\n".join(patient_memories)

        system_prompt = f"""Eres el Asistente Clínico Odontológico de {settings.clinic_name}.
Ubicación: {settings.clinic_address}
Teléfono: {settings.clinic_phone}
Horario de Atención: {settings.business_hours_start}:00 a {settings.business_hours_end}:00

BASE DE CONOCIMIENTO DE TRATAMIENTOS Y PRECIOS:
{self.kb_context}{rag_section}

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
        target_date = date.today() + timedelta(days=1)
        extracted_date = triage_data.extracted_date

        if extracted_date:
            try:
                target_date = datetime.strptime(extracted_date, "%Y-%m-%d").date()
            except Exception:
                target_date = date.today() + timedelta(days=1)

        available_slots = calendar_service.get_available_slots(target_date)
        extracted_time = triage_data.extracted_time
        patient_name = triage_data.extracted_name or "Paciente"
        treatment = triage_data.extracted_treatment or "Evaluación Odontológica General"

        if extracted_time and not any(extracted_time in slot for slot in available_slots):
            slots_text = ", ".join(available_slots[:5]) if available_slots else "Sin horarios disponibles"
            return (
                f"⚠️ El horario solicitado (**{extracted_time}**) ya se encuentra reservado para el día **{target_date.strftime('%Y-%m-%d')}**.\n\n"
                f"Te ofrecemos las siguientes alternativas disponibles en ese día:\n"
                f"👉 **{slots_text}**\n\n"
                f"Por favor indícame cuál te queda más cómodo para confirmarte la reserva."
            )

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

        slots_text = ", ".join(available_slots[:5]) if available_slots else "Sin horarios disponibles"
        return (
            f"📅 Para el día **{target_date.strftime('%Y-%m-%d')}** tenemos los siguientes horarios disponibles:\n"
            f"👉 **{slots_text}**\n\n"
            f"Por favor indícame cuál de estos horarios prefieres y tu nombre completo para confirmarte la reserva en el calendario."
        )


class SolverAgent:
    """Agent 3: Formulates the final empathetic solution based on diagnosis and channel."""

    def __init__(self, memory: Optional[Any] = None, memory_service: Optional[Any] = None) -> None:
        self.faq_agent = DentalFAQAgent()
        self.appointment_agent = AppointmentAgent()
        self.memory = memory or memory_service or SolverMemory()

    def solve(
        self,
        message: OmniChannelMessage,
        analysis: ClinicalAnalysis,
        context: List[Dict[str, str]]
    ) -> SolverResponse:
        intent = analysis.intent
        channel = message.channel
        sender_id = message.sender_id
        user_text = message.raw_text

        triage_bridge = TriageResult(
            intent=analysis.intent,
            extracted_name=analysis.extracted_name or message.sender_name,
            extracted_treatment=analysis.extracted_treatment,
            extracted_date=analysis.extracted_date,
            extracted_time=analysis.extracted_time,
            urgency=analysis.urgency,
            summary=analysis.summary
        )

        rag_knowledge = analysis.rag_knowledge_context
        patient_memories = analysis.patient_memory_context

        action_taken = "responded"
        responding_agent_name = "SolverAgent"

        if intent == "BOOK_APPOINTMENT":
            reply_text = self.appointment_agent.handle(user_text, triage_bridge, sender_id, channel)
            action_taken = "calendar_booked" if "confirmada con éxito" in reply_text else "slots_proposed"
            responding_agent_name = "SolverAgent (Calendar)"
        elif intent == "EMERGENCY_OR_PAIN":
            reply_text = self.faq_agent.generate_response(user_text, triage_bridge, context, rag_knowledge=rag_knowledge, patient_memories=patient_memories)
            action_taken = "emergency_diverted"
            responding_agent_name = "SolverAgent (Emergency)"
        elif intent in ("INQUIRE_PRICE_OR_TREATMENT", "GENERAL_FAQ"):
            reply_text = self.faq_agent.generate_response(user_text, triage_bridge, context, rag_knowledge=rag_knowledge, patient_memories=patient_memories)
            action_taken = "faq_answered"
            responding_agent_name = "SolverAgent (Clinical Catalog)"
        else:  # GREETING
            reply_text = self.faq_agent.generate_response(user_text, triage_bridge, context, rag_knowledge=rag_knowledge, patient_memories=patient_memories)
            action_taken = "greeting_provided"
            responding_agent_name = "SolverAgent (Welcome)"

        # 1. Log conversation turns in short-term memory
        self.memory.add_turn(channel=channel, sender_id=sender_id, role="user", content=user_text)
        self.memory.add_turn(channel=channel, sender_id=sender_id, role="assistant", content=reply_text)

        # 2. Extract and vectorize long-term patient memories
        patient_name = analysis.extracted_name or (message.sender_name if message.sender_name not in ("Paciente", "unknown") else None)
        if analysis.extracted_treatment:
            self.memory.add_patient_memory(
                sender_id=sender_id,
                patient_name=patient_name,
                memory_text=f"Interés en tratamiento: {analysis.extracted_treatment}"
            )
        if analysis.urgency == "high":
            self.memory.add_patient_memory(
                sender_id=sender_id,
                patient_name=patient_name,
                memory_text=f"Reportó dolor o urgencia dental: {analysis.detected_problem}"
            )
        if analysis.intent == "BOOK_APPOINTMENT" and (analysis.extracted_date or analysis.extracted_time):
            self.memory.add_patient_memory(
                sender_id=sender_id,
                patient_name=patient_name,
                memory_text=f"Agendó o consultó turno para {analysis.extracted_date or 'fecha próxima'} {analysis.extracted_time or ''}".strip()
            )

        return SolverResponse(
            reply=reply_text,
            channel=channel,
            sender_id=sender_id,
            intent=intent,
            agent=responding_agent_name,
            action_taken=action_taken,
            timestamp=datetime.now(timezone.utc).isoformat()
        )
