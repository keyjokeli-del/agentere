import os
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, date, timedelta, timezone

from app.config import settings
from app.services.groq_service import groq_service
from app.services.calendar_service import (
    calendar_service,
    generate_google_calendar_url,
    get_treatment_duration,
    get_assigned_doctor
)
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
except Exception:
    CLINIC_CATALOG = ClinicCatalog(
        treatments=[
            Treatment(
                name="Limpieza Dental",
                duration_min=30,
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
        patient_memories: Optional[List[str]] = None,
        detected_language: str = "es"
    ) -> str:
        # Check for medication or prescription inquiry (Strict Clinical Ethics)
        msg_lower = user_message.lower()
        if any(w in msg_lower for w in ["receta", "medicamento", "pastilla", "amoxicilina", "ibuprofeno", "que tomo", "qué puedo tomar", "antibiotico", "antibiótico"]):
            if detected_language == "en":
                return (
                    f"⚠️ In accordance with medical ethics and regulations of {settings.clinic_name}, our staff cannot prescribe "
                    f"medications without a prior in-person physical evaluation at the clinic.\n\n"
                    f"If you are experiencing severe pain or swelling, please visit us directly at {settings.clinic_address} "
                    f"or let us know if you need an emergency appointment today."
                )
            elif detected_language == "pt":
                return (
                    f"⚠️ De acordo com as normas médicas e éticas de {settings.clinic_name}, nenhum profissional pode receitar "
                    f"medicamentos sem uma avaliação presencial prévia no consultório.\n\n"
                    f"Se você estiver com dor intensa ou inchaço, recomendamos comparecer imediatamente à nossa clínica em "
                    f"{settings.clinic_address} ou solicitar um horário de emergência hoje."
                )
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

        lang_instruction = "Responde en ESPAÑOL."
        if detected_language == "en":
            lang_instruction = "Respond in fluent, welcoming ENGLISH."
        elif detected_language == "pt":
            lang_instruction = "Responda em PORTUGUÊS com cordialidade e precisão."
        elif detected_language == "fr":
            lang_instruction = "Répondez en FRANÇAIS avec empathie et précision."

        system_prompt = f"""Eres el Asistente Clínico Odontológico de {settings.clinic_name}.
Ubicación: {settings.clinic_address}
Teléfono: {settings.clinic_phone}
Horario de Atención: {settings.business_hours_start}:00 a {settings.business_hours_end}:00

BASE DE CONOCIMIENTO DE TRATAMIENTOS Y PRECIOS:
{self.kb_context}{rag_section}

DIRECTRICES CRÍTICAS:
1. {lang_instruction}
2. Responde de forma empática, clara, concisa y profesional.
3. NUNCA des diagnósticos médicos definitivos. Aclara que el plan de tratamiento y presupuesto final se confirma en la evaluación en el consultorio.
4. Si el paciente siente dolor agudo o urgencia ({triage_data.urgency} == 'high'), prioriza ofrecerle atención inmediata en el día.
5. Invita siempre amablemente al paciente a agendar una cita o evaluación para revisar su caso en detalle.
6. Mantén las respuestas fluidas y directas, óptimas para WhatsApp y redes sociales (párrafos cortos y emojis amigables).
"""
        messages = [
            {"role": "system", "content": system_prompt},
            *context[-4:],
            {"role": "user", "content": user_message}
        ]
        return groq_service.chat_completion(messages, temperature=0.4, max_tokens=350)


class BookingResponse(str):
    """Hybrid String/Dictionary response object ensuring 100% backward and forward compatibility."""
    reply: str
    booked: bool
    appt: Any
    doctor: str
    google_calendar_url: Optional[str]
    ics_url: Optional[str]

    def __new__(
        cls,
        reply: str,
        booked: bool = False,
        appt: Any = None,
        doctor: str = "",
        google_calendar_url: Optional[str] = None,
        ics_url: Optional[str] = None
    ):
        instance = super().__new__(cls, reply)
        instance.reply = reply
        instance.booked = booked
        instance.appt = appt
        instance.doctor = doctor
        instance.google_calendar_url = google_calendar_url
        instance.ics_url = ics_url
        return instance

    def __getitem__(self, key: Any) -> Any:
        if isinstance(key, str):
            if key == "reply": return str(self)
            if key == "booked": return self.booked
            if key == "appt": return self.appt
            if key == "doctor": return self.doctor
            if key == "google_calendar_url": return self.google_calendar_url
            if key == "ics_url": return self.ics_url
        return super().__getitem__(key)

    def get(self, key: str, default: Any = None) -> Any:
        if key == "reply": return str(self)
        if key == "booked": return self.booked
        if key == "appt": return self.appt
        if key == "doctor": return self.doctor
        if key == "google_calendar_url": return self.google_calendar_url
        if key == "ics_url": return self.ics_url
        return default


class AppointmentAgent:
    """Manages slot checking and booking in Google Calendar with dynamic duration and 1-click links."""

    def handle(
        self,
        user_message: str,
        triage_data: TriageResult,
        sender_id: str,
        channel: str,
        detected_language: str = "es"
    ) -> BookingResponse:
        target_date = date.today() + timedelta(days=1)
        extracted_date = triage_data.extracted_date

        if extracted_date:
            try:
                target_date = datetime.strptime(extracted_date, "%Y-%m-%d").date()
            except Exception:
                target_date = date.today() + timedelta(days=1)

        treatment = triage_data.extracted_treatment or "Evaluación Odontológica General"
        duration_min = get_treatment_duration(treatment)
        doctor = get_assigned_doctor(treatment)

        available_slots = calendar_service.get_available_slots(target_date, duration_minutes=duration_min)
        extracted_time = triage_data.extracted_time
        patient_name = triage_data.extracted_name or "Paciente"

        # Check if requested slot matches dynamic duration slots OR standard 45-min slots
        if extracted_time and not any(extracted_time in slot for slot in available_slots):
            fallback_slots = calendar_service.get_available_slots(target_date, duration_minutes=45)
            if any(extracted_time in slot for slot in fallback_slots):
                available_slots = fallback_slots

        # Slot requested but collision
        if extracted_time and not any(extracted_time in slot for slot in available_slots):
            slots_text = ", ".join(available_slots[:5]) if available_slots else "Sin horarios disponibles"
            reply = (
                f"⚠️ El horario solicitado (**{extracted_time}**) ya se encuentra reservado para el día **{target_date.strftime('%Y-%m-%d')}**.\n\n"
                f"Te ofrecemos las siguientes alternativas disponibles ({duration_min} min con {doctor}):\n"
                f"👉 **{slots_text}**\n\n"
                f"Por favor indícame cuál te queda más cómodo para confirmarte la reserva."
            )
            return BookingResponse(reply=reply, booked=False, appt=None, doctor=doctor)

        # Slot requested and available -> Book appointment!
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
            gcal_url = generate_google_calendar_url(
                patient_name=patient_name,
                treatment=treatment,
                appointment_date=appt.date,
                appointment_time=appt.time,
                duration_min=duration_min,
                doctor=doctor
            )
            ics_url = f"/api/appointments/ics?appt_id={appt.id}"

            reply = (
                f"✅ ¡Tu cita ha quedado confirmada con éxito!\n\n"
                f"📅 **Fecha:** {appt.date}\n"
                f"⏰ **Hora:** {appt.time} hs ({duration_min} min)\n"
                f"🦷 **Tratamiento:** {appt.treatment}\n"
                f"👩‍⚕️ **Especialista:** {doctor}\n"
                f"📍 **Lugar:** {settings.clinic_address}\n\n"
                f"📅 [Añadir a Google Calendar en 1 Clic]({gcal_url})\n\n"
                f"Te esperamos unos 5 minutos antes. ¡Que tengas un excelente día!"
            )
            return BookingResponse(
                reply=reply,
                booked=True,
                appt=appt,
                doctor=doctor,
                google_calendar_url=gcal_url,
                ics_url=ics_url
            )

        slots_text = ", ".join(available_slots[:5]) if available_slots else "Sin horarios disponibles"
        reply = (
            f"📅 Para el día **{target_date.strftime('%Y-%m-%d')}** tenemos los siguientes horarios disponibles con {doctor}:\n"
            f"👉 **{slots_text}**\n\n"
            f"Por favor indícame cuál de estos horarios prefieres y tu nombre completo para confirmarte la reserva en el calendario."
        )
        return BookingResponse(reply=reply, booked=False, appt=None, doctor=doctor)


class SolverAgent:
    """Agent 3: Formulates final empathetic response, applies business rules, anti no-show, and CRM triggers."""

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
        user_clean = user_text.strip().lower()

        # 1. Anti No-Show Automation: Check quick replies "1" (confirm) or "2" (reschedule) (Mejora 8)
        if user_clean in ("1", "confirmar", "confirmo", "confirmo cita", "si confirmo", "sí confirmo"):
            appt = calendar_service.update_appointment_status(sender_id, "confirmed")
            if appt:
                reply_text = (
                    f"✅ ¡Muchas gracias {appt.patient_name}! Tu cita para el día **{appt.date}** a las **{appt.time} hs** "
                    f"ha quedado formalmente **CONFIRMADA**.\n\n"
                    f"Te esperamos en {settings.clinic_address}. Recuerda asistir 5 minutos antes."
                )
                return SolverResponse(
                    reply=reply_text,
                    channel=channel,
                    sender_id=sender_id,
                    intent="CONFIRM_APPOINTMENT",
                    agent="SolverAgent (Anti No-Show)",
                    action_taken="appointment_confirmed"
                )

        if user_clean in ("2", "reprogramar", "cancelar", "cancelo", "no puedo ir"):
            appt = calendar_service.update_appointment_status(sender_id, "cancelled")
            reply_text = (
                "🔄 Tu cita ha sido cancelada y liberada para otros pacientes.\n\n"
                "¿Para qué nuevo día y horario te gustaría reprogramar tu consulta? Te ayudamos con gusto."
            )
            return SolverResponse(
                reply=reply_text,
                channel=channel,
                sender_id=sender_id,
                intent="CANCEL_APPOINTMENT",
                agent="SolverAgent (Anti No-Show)",
                action_taken="appointment_cancelled"
            )

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
        google_calendar_url = None
        ics_url = None
        assigned_doctor = None

        if intent == "BOOK_APPOINTMENT":
            booking_res = self.appointment_agent.handle(
                user_text,
                triage_bridge,
                sender_id,
                channel,
                detected_language=analysis.detected_language
            )
            reply_text = booking_res["reply"]
            action_taken = "calendar_booked" if booking_res["booked"] else "slots_proposed"
            responding_agent_name = "SolverAgent (Calendar)"
            google_calendar_url = booking_res.get("google_calendar_url")
            ics_url = booking_res.get("ics_url")
            assigned_doctor = booking_res.get("doctor")
        elif intent == "EMERGENCY_OR_PAIN":
            reply_text = self.faq_agent.generate_response(
                user_text,
                triage_bridge,
                context,
                rag_knowledge=rag_knowledge,
                patient_memories=patient_memories,
                detected_language=analysis.detected_language
            )
            action_taken = "emergency_diverted"
            responding_agent_name = "SolverAgent (Emergency)"
        elif intent in ("INQUIRE_PRICE_OR_TREATMENT", "GENERAL_FAQ"):
            reply_text = self.faq_agent.generate_response(
                user_text,
                triage_bridge,
                context,
                rag_knowledge=rag_knowledge,
                patient_memories=patient_memories,
                detected_language=analysis.detected_language
            )
            action_taken = "faq_answered"
            responding_agent_name = "SolverAgent (Clinical Catalog)"
        else:  # GREETING
            reply_text = self.faq_agent.generate_response(
                user_text,
                triage_bridge,
                context,
                rag_knowledge=rag_knowledge,
                patient_memories=patient_memories,
                detected_language=analysis.detected_language
            )
            action_taken = "greeting_provided"
            responding_agent_name = "SolverAgent (Welcome)"

        # 2. Clinical Red Flag Follow-up Questions (Mejora 5)
        if analysis.clinical_followup_needed and analysis.clinical_followup_questions:
            questions_text = "\n".join(f"- {q}" for q in analysis.clinical_followup_questions)
            reply_text += (
                f"\n\n⚠️ **Preguntas Clínicas de Seguridad:**\n{questions_text}\n"
                f"*(Si presenta dificultad respiratoria o para tragar, acuda inmediatamente a guardia médica física)*"
            )

        # 3. Google Maps Reviews for 5-star or high satisfaction (Mejora 28)
        if any(w in user_clean for w in ["excelente atencion", "excelente atención", "los mejores", "muchas gracias doctora", "maravilloso servicio", "5 estrellas"]):
            reply_text += (
                f"\n\n⭐ **¡Nos alegra muchísimo saberlo!**\n"
                f"¿Podrías dejarnos tu reseña en Google Maps? Nos ayuda enormemente: "
                f"https://maps.google.com/?q=Lumina+Dental+Studio"
            )

        # 4. Outside Operating Hours Notice (Mejora 19)
        now_hour = datetime.now().hour
        if (now_hour < settings.business_hours_start or now_hour >= settings.business_hours_end) and intent != "EMERGENCY_OR_PAIN":
            reply_text = (
                f"🌙 *Nota informativa:* En este momento nuestro consultorio físico se encuentra cerrado "
                f"(atendemos de Lunes a Sábado de {settings.business_hours_start}:00 a {settings.business_hours_end}:00).\n\n"
                f"{reply_text}"
            )

        # 5. Log conversation turns in short-term memory
        self.memory.add_turn(channel=channel, sender_id=sender_id, role="user", content=user_text)
        self.memory.add_turn(channel=channel, sender_id=sender_id, role="assistant", content=reply_text)

        # 6. Extract and vectorize long-term patient memories + FDI teeth (Mejora 3)
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
        if analysis.fdi_teeth:
            self.memory.add_patient_memory(
                sender_id=sender_id,
                patient_name=patient_name,
                memory_text=f"Piezas dentales FDI reportadas: {analysis.fdi_teeth}"
            )

        return SolverResponse(
            reply=reply_text,
            channel=channel,
            sender_id=sender_id,
            intent=intent,
            agent=responding_agent_name,
            action_taken=action_taken,
            google_calendar_url=google_calendar_url,
            ics_url=ics_url,
            assigned_doctor=assigned_doctor,
            fdi_teeth=analysis.fdi_teeth,
            frustration_detected=analysis.frustration_detected,
            detected_language=analysis.detected_language,
            timestamp=datetime.now(timezone.utc).isoformat()
        )
