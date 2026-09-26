import json
from typing import Dict, Any, List, Optional
from datetime import datetime, date, timedelta, timezone

from app.config import settings
from app.services.groq_service import groq_service
from app.services.calendar_service import calendar_service
from app.services.rag_memory_service import rag_memory_service
from app.models.dental_models import (

    ClinicCatalog,
    Treatment,
    GeneralFAQ,
    TriageResult,
    AgentResponse,
    OmniChannelMessage,
    ClinicalAnalysis,
    SolverResponse
)

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


# ==============================================================================
# AGENTE 1: ReaderAgent ("El que lee")
# Ingesta payloads heterogéneos de redes sociales y los mapea a OmniChannelMessage
# ==============================================================================
class ReaderAgent:
    """Agent 1: Ingests raw payloads from diverse social channels and maps to OmniChannelMessage."""

    def __init__(self, memory_service=None) -> None:
        self.memory = memory_service or rag_memory_service

    def read(self, payload: Any, channel: str = "web", default_sender: str = "unknown") -> OmniChannelMessage:
        if channel == "whatsapp":
            return self.from_whatsapp(payload if isinstance(payload, dict) else {"message": str(payload)})
        elif channel in ("facebook", "instagram"):
            return self.from_meta(payload if isinstance(payload, dict) else {"message": str(payload)}, channel=channel)
        elif channel == "youtube":
            return self.from_youtube(payload if isinstance(payload, dict) else {"message": str(payload)})
        elif isinstance(payload, dict):
            return self.from_dict(payload, channel=channel, default_sender=default_sender)
        else:
            return self.from_text(str(payload), channel=channel, sender_id=default_sender)

    def from_whatsapp(self, payload: Dict[str, Any]) -> OmniChannelMessage:
        sender_id = str(payload.get("sender_id") or "unknown_wa").strip()
        text = str(payload.get("message") or payload.get("raw_text") or "").strip()
        sender_name = str(payload.get("sender_name") or sender_id).strip()
        history = payload.get("recent_history")
        if history is None:
            history = self.memory.get_recent_turns("whatsapp", sender_id, limit=4)
        return OmniChannelMessage(
            channel="whatsapp",
            sender_id=sender_id,
            sender_name=sender_name or "Paciente",
            raw_text=text,
            metadata=payload.get("metadata", {}),
            recent_history=history
        )

    def from_meta(self, payload: Dict[str, Any], channel: str = "facebook") -> OmniChannelMessage:
        entries = payload.get("entry", [])
        sender_id = "unknown_meta"
        text = ""
        metadata: Dict[str, Any] = {"object": payload.get("object", "page")}

        if payload.get("object") == "instagram":
            channel = "instagram"

        if entries and isinstance(entries, list):
            first_entry = entries[0]
            messaging = first_entry.get("messaging", [])
            if messaging and isinstance(messaging, list):
                event = messaging[0]
                sender_id = str(event.get("sender", {}).get("id") or "unknown_meta")
                msg_obj = event.get("message", {})
                text = str(msg_obj.get("text") or "").strip()
                metadata["mid"] = msg_obj.get("mid")
                metadata["recipient_id"] = event.get("recipient", {}).get("id")

        if not text:
            text = str(payload.get("message") or payload.get("text") or "").strip()
        if sender_id == "unknown_meta" and payload.get("sender_id"):
            sender_id = str(payload.get("sender_id"))

        valid_channel = channel if channel in ("facebook", "instagram") else "facebook"
        history = payload.get("recent_history")
        if history is None:
            history = self.memory.get_recent_turns(valid_channel, sender_id, limit=4)

        return OmniChannelMessage(
            channel=valid_channel,
            sender_id=sender_id,
            sender_name=str(payload.get("sender_name") or "Usuario Meta"),
            raw_text=text,
            metadata=metadata,
            recent_history=history
        )

    def from_youtube(self, payload: Dict[str, Any]) -> OmniChannelMessage:
        snippet = payload.get("snippet", {})
        top_level = snippet.get("topLevelComment", {}).get("snippet", snippet)

        text = str(
            top_level.get("textDisplay") or
            top_level.get("textOriginal") or
            payload.get("comment") or
            payload.get("message") or
            payload.get("text") or
            ""
        ).strip()
        sender_name = str(
            top_level.get("authorDisplayName") or
            payload.get("author") or
            payload.get("sender_name") or
            "Comentarista de YouTube"
        ).strip()
        sender_id = str(
            top_level.get("authorChannelId", {}).get("value") or
            payload.get("author") or
            payload.get("sender_id") or
            "unknown_yt"
        ).strip()

        metadata = {
            "video_id": snippet.get("videoId") or payload.get("video_id"),
            "comment_id": payload.get("id") or payload.get("comment_id"),
            "parent_id": snippet.get("parentId") or payload.get("parent_id")
        }

        history = payload.get("recent_history")
        if history is None:
            history = self.memory.get_recent_turns("youtube", sender_id, limit=4)

        return OmniChannelMessage(
            channel="youtube",
            sender_id=sender_id,
            sender_name=sender_name,
            raw_text=text,
            metadata=metadata,
            recent_history=history
        )

    def from_dict(self, payload: Dict[str, Any], channel: str = "web", default_sender: str = "unknown") -> OmniChannelMessage:
        raw_text = str(payload.get("message") or payload.get("text") or payload.get("raw_text") or "").strip()
        sender_id = str(payload.get("sender_id") or default_sender).strip()
        sender_name = str(payload.get("sender_name") or "Paciente").strip()
        ch = str(payload.get("channel") or channel).lower()
        valid_ch = ch if ch in ("whatsapp", "facebook", "instagram", "youtube", "web") else "web"
        history = payload.get("recent_history")
        if history is None:
            history = self.memory.get_recent_turns(valid_ch, sender_id, limit=4)
        return OmniChannelMessage(
            channel=valid_ch,
            sender_id=sender_id,
            sender_name=sender_name,
            raw_text=raw_text,
            metadata=payload.get("metadata", {}),
            recent_history=history
        )

    def from_text(self, text: str, channel: str = "web", sender_id: str = "user-web", sender_name: str = "Paciente", recent_history: Optional[List[Dict[str, str]]] = None) -> OmniChannelMessage:
        valid_ch = channel if channel in ("whatsapp", "facebook", "instagram", "youtube", "web") else "web"
        history = recent_history
        if history is None:
            history = self.memory.get_recent_turns(valid_ch, sender_id, limit=4)
        return OmniChannelMessage(
            channel=valid_ch,
            sender_id=sender_id,
            sender_name=sender_name,
            raw_text=text.strip(),
            metadata={},
            recent_history=history
        )



# ==============================================================================
# AGENTE 2: AnalyzerAgent ("El que ve el problema")
# Diagnóstico clínico, extracción de entidades y clasificación de urgencia
# ==============================================================================
class AnalyzerAgent:
    """Agent 2: Evaluates clinical context, detects patient's real problem, extracts entities, and classifies intent."""

    SYSTEM_PROMPT = """Eres el Agente Analizador Clínico de {clinic_name}.
Tu misión es analizar el mensaje del paciente y devolver EXCLUSIVAMENTE un JSON válido:
{{
    "intent": "BOOK_APPOINTMENT" | "INQUIRE_PRICE_OR_TREATMENT" | "EMERGENCY_OR_PAIN" | "GENERAL_FAQ" | "GREETING",
    "urgency": "high" | "normal",
    "detected_problem": "descripción clínica del motivo de consulta o dolor",
    "extracted_name": string or null,
    "extracted_treatment": string or null,
    "extracted_date": string or null,
    "extracted_time": string or null,
    "summary": "resumen breve y estructurado"
}}
No incluyas texto fuera del JSON.
"""

    def __init__(self, memory_service=None) -> None:
        self.memory = memory_service or rag_memory_service

    def analyze(self, message: OmniChannelMessage, context: List[Dict[str, str]]) -> ClinicalAnalysis:
        raw_text = message.raw_text

        # 1. RAG Vectorial: Retrieve top 3 clinical knowledge chunks via cosine distance
        rag_chunks = self.memory.search_clinical_knowledge(raw_text, top_k=3)
        rag_knowledge_context = [c["content"] for c in rag_chunks] if rag_chunks else []

        # 2. RAG Vectorial: Retrieve patient's long-term memory
        patient_mems = self.memory.search_patient_memories(message.sender_id, raw_text, top_k=3)
        patient_memory_context = [m["memory_text"] for m in patient_mems] if patient_mems else []

        effective_context = context if context else message.recent_history

        rag_prompt_section = ""
        if rag_knowledge_context:
            rag_prompt_section += "\n\nCONOCIMIENTO CLÍNICO RAG DISPONIBLE:\n" + "\n".join(f"- {c}" for c in rag_knowledge_context)
        if patient_memory_context:
            rag_prompt_section += "\n\nMEMORIA PREVIA DEL PACIENTE:\n" + "\n".join(f"- {m}" for m in patient_memory_context)

        prompt = self.SYSTEM_PROMPT.format(clinic_name=settings.clinic_name) + rag_prompt_section
        messages = [
            {"role": "system", "content": prompt},
            *effective_context[-4:],
            {"role": "user", "content": f"Mensaje [{message.channel.upper()}] de {message.sender_name}: '{raw_text}'"}
        ]

        response_text = groq_service.chat_completion(messages, temperature=0.1, response_format={"type": "json_object"})

        try:
            parsed = json.loads(response_text)
            parsed["rag_knowledge_context"] = rag_knowledge_context
            parsed["patient_memory_context"] = patient_memory_context
            return ClinicalAnalysis.model_validate(parsed)
        except Exception:
            # Deterministic rule-based fallback
            msg_lower = raw_text.lower()
            if any(w in msg_lower for w in ["duel", "dol", "urgencia", "emergencia", "muela", "sangr", "inflam", "hinch", "rot", "quebr"]):
                return ClinicalAnalysis(
                    intent="EMERGENCY_OR_PAIN",
                    urgency="high",
                    detected_problem="Dolor agudo o urgencia odontológica reportada",
                    extracted_name=None,
                    extracted_treatment="Urgencia Dental",
                    extracted_date=None,
                    extracted_time=None,
                    summary="El paciente reporta dolor o urgencia médica.",
                    rag_knowledge_context=rag_knowledge_context,
                    patient_memory_context=patient_memory_context
                )
            elif any(w in msg_lower for w in ["cita", "turno", "agend", "reserv", "hora"]):
                return ClinicalAnalysis(
                    intent="BOOK_APPOINTMENT",
                    urgency="normal",
                    detected_problem="Solicitud de reserva de cita odontológica",
                    extracted_name=None,
                    extracted_treatment=None,
                    extracted_date=None,
                    extracted_time=None,
                    summary="Solicitud para agendar un turno.",
                    rag_knowledge_context=rag_knowledge_context,
                    patient_memory_context=patient_memory_context
                )
            elif any(w in msg_lower for w in ["precio", "cuanto", "sale", "cuesta", "costo", "valor"]):
                return ClinicalAnalysis(
                    intent="INQUIRE_PRICE_OR_TREATMENT",
                    urgency="normal",
                    detected_problem="Consulta de aranceles y tratamientos disponibles",
                    extracted_name=None,
                    extracted_treatment=None,
                    extracted_date=None,
                    extracted_time=None,
                    summary="Consulta sobre costos o procedimientos.",
                    rag_knowledge_context=rag_knowledge_context,
                    patient_memory_context=patient_memory_context
                )
            elif any(w in msg_lower for w in ["hola", "buen", "saludos", "buenas"]):
                return ClinicalAnalysis(
                    intent="GREETING",
                    urgency="normal",
                    detected_problem="Contacto inicial del paciente",
                    extracted_name=None,
                    extracted_treatment=None,
                    extracted_date=None,
                    extracted_time=None,
                    summary="Saludo inicial del paciente.",
                    rag_knowledge_context=rag_knowledge_context,
                    patient_memory_context=patient_memory_context
                )
            return ClinicalAnalysis(
                intent="GENERAL_FAQ",
                urgency="normal",
                detected_problem="Dudas generales sobre la clínica y servicios",
                extracted_name=None,
                extracted_treatment=None,
                extracted_date=None,
                extracted_time=None,
                summary="Consulta general o institucional.",
                rag_knowledge_context=rag_knowledge_context,
                patient_memory_context=patient_memory_context
            )


# Backward-compatible TriageAgent
class TriageAgent:
    """Legacy wrapper delegating to AnalyzerAgent."""
    def __init__(self, memory_service=None) -> None:
        self.memory = memory_service or rag_memory_service
        self.reader = ReaderAgent(memory_service=self.memory)
        self.analyzer = AnalyzerAgent(memory_service=self.memory)

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


# ==============================================================================
# AGENTE 3: SolverAgent ("El que da la solución")
# Decide la acción resolutiva, consulta agenda o catálogo y redacta la respuesta final
# ==============================================================================
class SolverAgent:
    """Agent 3: Formulates the final empathetic solution based on diagnosis and channel."""

    def __init__(self, memory_service=None) -> None:
        self.faq_agent = DentalFAQAgent()
        self.appointment_agent = AppointmentAgent()
        self.memory = memory_service or rag_memory_service

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

        # 1. Log conversation turns in RAG short-term memory
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


# ==============================================================================
# PIPELINE OMNICANAL CENTRALIZADO (3 Agentes Secuenciales)
# ReaderAgent -> AnalyzerAgent -> SolverAgent
# ==============================================================================
class OmniChannelPipeline:
    """Centralized orchestrator running the sequential 3-agent critical pipeline:
    ReaderAgent -> AnalyzerAgent -> SolverAgent
    with Hybrid Memory and Neon Vector RAG.
    """

    def __init__(self, memory_service=None) -> None:
        self.memory = memory_service or rag_memory_service
        self.reader = ReaderAgent(memory_service=self.memory)
        self.analyzer = AnalyzerAgent(memory_service=self.memory)
        self.solver = SolverAgent(memory_service=self.memory)
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
            message.recent_history = self.memory.get_recent_turns(message.channel, message.sender_id, limit=4)

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

