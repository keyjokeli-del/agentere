import json
from typing import Dict, Any, List, Optional

from app.config import settings
from app.services.groq_service import groq_service
from app.agents.reader_agent.schemas import OmniChannelMessage
from app.agents.analyzer_agent.schemas import ClinicalAnalysis
from app.agents.analyzer_agent.memory import AnalyzerMemory


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

    def __init__(self, memory: Optional[Any] = None, memory_service: Optional[Any] = None) -> None:
        self.memory = memory or memory_service or AnalyzerMemory()

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
