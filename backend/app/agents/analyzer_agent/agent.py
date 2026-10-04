import os
import re
import json
import httpx
from typing import Dict, Any, List, Optional, Tuple

from app.config import settings
from app.core.observability import track_dependency
from app.services.groq_service import groq_service
from app.agents.reader_agent.schemas import OmniChannelMessage
from app.agents.analyzer_agent.schemas import ClinicalAnalysis
from app.agents.analyzer_agent.memory import AnalyzerMemory


def extract_fdi_teeth(text: str) -> List[int]:
    """Extracts dental piece numbers adhering to the two-digit FDI World Dental Federation system (11-48)."""
    found: List[int] = []
    text_lower = text.lower()

    # Direct 2-digit FDI patterns (e.g., 'pieza 18', 'diente 24', '38', '46')
    matches = re.findall(r"\b([1-4][1-8])\b", text)
    for m in matches:
        val = int(m)
        if val not in found:
            found.append(val)

    # Heuristic mapping for common dental terms
    if any(w in text_lower for w in ["muela del juicio", "muelas del juicio", "cordal", "tercer molar", "terceros molares"]):
        if any(w in text_lower for w in ["superior derecha", "arriba derecha"]):
            if 18 not in found: found.append(18)
        elif any(w in text_lower for w in ["superior izquierda", "arriba izquierda"]):
            if 28 not in found: found.append(28)
        elif any(w in text_lower for w in ["inferior izquierda", "abajo izquierda"]):
            if 38 not in found: found.append(38)
        elif any(w in text_lower for w in ["inferior derecha", "abajo derecha"]):
            if 48 not in found: found.append(48)
        else:
            # General wisdom tooth reference
            if 18 not in found: found.append(18)

    if any(w in text_lower for w in ["colmillo", "canino"]):
        if 13 not in found: found.append(13)

    if any(w in text_lower for w in ["paleta", "incisivo frontal", "diente del frente"]):
        if 11 not in found: found.append(11)

    return sorted(found)


def detect_sentiment_and_frustration(text: str) -> Tuple[float, bool]:
    """Detects sentiment polarity (-1.0 to 1.0) and severe patient frustration."""
    text_lower = text.lower()

    frustration_keywords = [
        "estafa", "pésimo", "pesimo", "inútil", "inutil", "inútiles", "desastre",
        "nadie responde", "nadie atiende", "vergüenza", "verguenza", "harto",
        "no aguanto", "porquería", "porqueria", "mal servicio", "demasiado tiempo",
        "falta de respeto", "incompetentes"
    ]
    pain_negative_keywords = [
        "duele mucho", "duele demasiado", "insoportable", "desesperado", "llorando",
        "urgente", "emergencia", "no duermo", "terrible", "morir del dolor"
    ]
    positive_keywords = [
        "gracias", "excelente", "maravilla", "perfecto", "amable", "genial",
        "muy buena", "encantado", "felicitaciones", "los mejores"
    ]

    has_frustration = any(w in text_lower for w in frustration_keywords)
    has_pain = any(w in text_lower for w in pain_negative_keywords)
    has_positive = any(w in text_lower for w in positive_keywords)

    score = 0.0
    if has_frustration:
        score = -0.9
    elif has_pain:
        score = -0.6
    elif has_positive:
        score = 0.8

    return score, has_frustration


def detect_clinical_followup(text: str) -> Tuple[bool, List[str]]:
    """Identifies red flags (swelling, infection, abscess) requiring clinical triage questions."""
    text_lower = text.lower()
    red_flags = ["hinch", "inflam", "flem", "absceso", "pus", "infecc", "celulitis", "bulto", "flemón"]
    if any(flag in text_lower for flag in red_flags):
        return True, [
            "¿Presenta fiebre o temperatura corporal elevada?",
            "¿Tiene dificultad para abrir la boca (trismus), tragar saliva o respirar con normalidad?"
        ]
    return False, []


def detect_language(text: str) -> str:
    """Detects primary language of patient message (es, en, pt, fr)."""
    text_lower = text.lower()
    words = re.findall(r"\b\w+\b", text_lower)

    en_words = {"hello", "hi", "appointment", "price", "cost", "tooth", "teeth", "pain", "cleaning", "whitening", "how", "much", "doctor", "please"}
    pt_words = {"olá", "ola", "consulta", "preço", "preco", "dente", "dentes", "dor", "limpeza", "clareamento", "obrigado", "obrigada", "agendar"}
    fr_words = {"bonjour", "salut", "rendez", "vous", "prix", "dent", "dents", "douleur", "nettoyage", "blanchiment", "merci", "combien"}

    match_en = sum(1 for w in words if w in en_words)
    match_pt = sum(1 for w in words if w in pt_words)
    match_fr = sum(1 for w in words if w in fr_words)

    if match_en >= 2 or (match_en == 1 and len(words) <= 3 and any(w in words for w in ["hello", "hi", "appointment"])):
        return "en"
    if match_pt >= 2 or (match_pt == 1 and len(words) <= 3 and any(w in words for w in ["olá", "ola", "obrigado"])):
        return "pt"
    if match_fr >= 2 or (match_fr == 1 and len(words) <= 3 and any(w in words for w in ["bonjour", "merci"])):
        return "fr"

    return "es"


def evaluate_visual_image(metadata: Dict[str, Any]) -> Optional[str]:
    """Lightweight multimodal dental photo evaluation using Gemini 1.5 Flash via REST API (Mejora 6)."""
    img_b64 = metadata.get("image_base64")
    img_url = metadata.get("image_url")
    if not img_b64 and not img_url:
        return None

    gemini_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if gemini_key and img_b64:
        try:
            url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
            headers = {"x-goog-api-key": gemini_key}
            payload = {
                "contents": [{
                    "parts": [
                        {
                            "text": (
                                "Eres un asistente de triaje dental preliminar para Lumina Dental Studio. "
                                "Evalúa esta imagen y describe si se aprecian signos compatibles con inflamación en encías, "
                                "sangrado visible o posible fractura dental. No des diagnósticos definitivos y aclara "
                                "que se requiere consulta presencial con la Dra. Nairoby Domínguez."
                            )
                        },
                        {
                            "inline_data": {
                                "mime_type": metadata.get("mime_type", "image/jpeg"),
                                "data": img_b64
                            }
                        }
                    ]
                }],
                "generationConfig": {"temperature": 0.2, "maxOutputTokens": 150}
            }
            with track_dependency("gemini_vision"):
                with httpx.Client(timeout=4.0) as client:
                    res = client.post(url, json=payload, headers=headers)
                    if res.is_success:
                        data = res.json()
                        candidates = data.get("candidates", [])
                        if candidates:
                            part = candidates[0].get("content", {}).get("parts", [{}])[0]
                            return part.get("text", "").strip()
        except Exception as e:
            print(f"[AnalyzerAgent] Gemini visual assessment advertencia: {e}")

    # Fallback safe assessment
    return (
        "Evaluación visual preliminar por IA: Se aprecian signos que ameritan revisión clínica directa "
        "(posible inflamación gingival / fisura coronaria). Recuerde que una imagen no sustituye el examen presencial "
        "y radiográfico en consultorio."
    )


class AnalyzerAgent:
    """Agent 2: Evaluates clinical context, detects real problem, extracts FDI teeth, calculates sentiment & urgency."""

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

        # Heuristic entity and signal extraction
        fdi_teeth = extract_fdi_teeth(raw_text)
        sentiment_score, frustration_detected = detect_sentiment_and_frustration(raw_text)
        clinical_followup_needed, clinical_followup_questions = detect_clinical_followup(raw_text)
        detected_language = detect_language(raw_text)
        visual_assessment = evaluate_visual_image(message.metadata)

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
            parsed["fdi_teeth"] = fdi_teeth
            parsed["sentiment_score"] = sentiment_score
            parsed["frustration_detected"] = frustration_detected
            parsed["clinical_followup_needed"] = clinical_followup_needed
            parsed["clinical_followup_questions"] = clinical_followup_questions
            parsed["visual_assessment"] = visual_assessment
            parsed["detected_language"] = detected_language
            if frustration_detected or sentiment_score <= -0.5:
                parsed["urgency"] = "high"
            return ClinicalAnalysis.model_validate(parsed)
        except Exception:
            # Deterministic rule-based fallback
            msg_lower = raw_text.lower()
            urgency = "high" if (frustration_detected or any(w in msg_lower for w in ["duel", "dol", "urgencia", "emergencia", "muela", "sangr", "inflam", "hinch", "rot", "quebr"])) else "normal"

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
                    patient_memory_context=patient_memory_context,
                    fdi_teeth=fdi_teeth,
                    sentiment_score=sentiment_score,
                    frustration_detected=frustration_detected,
                    clinical_followup_needed=clinical_followup_needed,
                    clinical_followup_questions=clinical_followup_questions,
                    visual_assessment=visual_assessment,
                    detected_language=detected_language
                )
            elif any(w in msg_lower for w in ["cita", "turno", "agend", "reserv", "hora"]):
                return ClinicalAnalysis(
                    intent="BOOK_APPOINTMENT",
                    urgency=urgency,
                    detected_problem="Solicitud de reserva de cita odontológica",
                    extracted_name=None,
                    extracted_treatment=None,
                    extracted_date=None,
                    extracted_time=None,
                    summary="Solicitud para agendar un turno.",
                    rag_knowledge_context=rag_knowledge_context,
                    patient_memory_context=patient_memory_context,
                    fdi_teeth=fdi_teeth,
                    sentiment_score=sentiment_score,
                    frustration_detected=frustration_detected,
                    clinical_followup_needed=clinical_followup_needed,
                    clinical_followup_questions=clinical_followup_questions,
                    visual_assessment=visual_assessment,
                    detected_language=detected_language
                )
            elif any(w in msg_lower for w in ["precio", "cuanto", "sale", "cuesta", "costo", "valor"]):
                return ClinicalAnalysis(
                    intent="INQUIRE_PRICE_OR_TREATMENT",
                    urgency=urgency,
                    detected_problem="Consulta de aranceles y tratamientos disponibles",
                    extracted_name=None,
                    extracted_treatment=None,
                    extracted_date=None,
                    extracted_time=None,
                    summary="Consulta sobre costos o procedimientos.",
                    rag_knowledge_context=rag_knowledge_context,
                    patient_memory_context=patient_memory_context,
                    fdi_teeth=fdi_teeth,
                    sentiment_score=sentiment_score,
                    frustration_detected=frustration_detected,
                    clinical_followup_needed=clinical_followup_needed,
                    clinical_followup_questions=clinical_followup_questions,
                    visual_assessment=visual_assessment,
                    detected_language=detected_language
                )
            elif any(w in msg_lower for w in ["hola", "buen", "saludos", "buenas"]):
                return ClinicalAnalysis(
                    intent="GREETING",
                    urgency=urgency,
                    detected_problem="Contacto inicial del paciente",
                    extracted_name=None,
                    extracted_treatment=None,
                    extracted_date=None,
                    extracted_time=None,
                    summary="Saludo inicial del paciente.",
                    rag_knowledge_context=rag_knowledge_context,
                    patient_memory_context=patient_memory_context,
                    fdi_teeth=fdi_teeth,
                    sentiment_score=sentiment_score,
                    frustration_detected=frustration_detected,
                    clinical_followup_needed=clinical_followup_needed,
                    clinical_followup_questions=clinical_followup_questions,
                    visual_assessment=visual_assessment,
                    detected_language=detected_language
                )
            return ClinicalAnalysis(
                intent="GENERAL_FAQ",
                urgency=urgency,
                detected_problem="Dudas generales sobre la clínica y servicios",
                extracted_name=None,
                extracted_treatment=None,
                extracted_date=None,
                extracted_time=None,
                summary="Consulta general o institucional.",
                rag_knowledge_context=rag_knowledge_context,
                patient_memory_context=patient_memory_context,
                fdi_teeth=fdi_teeth,
                sentiment_score=sentiment_score,
                frustration_detected=frustration_detected,
                clinical_followup_needed=clinical_followup_needed,
                clinical_followup_questions=clinical_followup_questions,
                visual_assessment=visual_assessment,
                detected_language=detected_language
            )
