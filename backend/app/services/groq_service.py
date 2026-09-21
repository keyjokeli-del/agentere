import os
import re
import json
from typing import List, Dict, Any, Optional
from app.config import settings

_DEFAULT_API_KEY = object()

class GroqService:
    def __init__(self, api_key: Any = _DEFAULT_API_KEY) -> None:
        if api_key is _DEFAULT_API_KEY:
            self.api_key = settings.groq_api_key
        else:
            self.api_key = api_key
        self.model = settings.groq_model
        self.client = None
        if self.api_key:
            try:
                from groq import Groq
                self.client = Groq(api_key=self.api_key)
            except Exception as e:
                print(f"[GroqService] Advertencia: No se pudo inicializar cliente Groq: {e}")

    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.3,
        response_format: Optional[Dict[str, str]] = None,
        max_tokens: int = 400
    ) -> str:
        """Sends conversation history to Groq API with robust rate-limit handling and deterministic fallback."""
        if not self.client:
            return self._fallback_response(messages)

        try:
            kwargs: Dict[str, Any] = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
            }
            if response_format:
                kwargs["response_format"] = response_format

            chat_completion = self.client.chat.completions.create(**kwargs)
            return chat_completion.choices[0].message.content or ""
        except Exception as e:
            err_msg = str(e).lower()
            if "rate_limit" in err_msg or "429" in err_msg:
                print("[GroqService] ⚠️ Rate limit detectado en capa gratuita de Groq. Conmutando a fallback determinista inmediato.")
            else:
                print(f"[GroqService] Error en inferencia Groq ({e}). Conmutando a fallback determinista.")
            return self._fallback_response(messages)

    def _fallback_response(self, messages: List[Dict[str, str]]) -> str:
        """Deterministic rule-based response adhering strictly to Pydantic schemas."""
        last_user_msg = ""
        for m in reversed(messages):
            if m.get("role") == "user":
                last_user_msg = m.get("content", "")
                break

        msg_lower = last_user_msg.lower()
        is_json_prompt = any("json" in m.get("content", "").lower() for m in messages if m.get("role") == "system")

        if is_json_prompt:
            # 1. Extract name if present
            name_match = re.search(r'(?:me llamo|soy|mi nombre es)\s+([A-Za-zÁÉÍÓÚáéíóúñ]+)', last_user_msg, re.IGNORECASE)
            extracted_name = name_match.group(1).capitalize() if name_match else None

            # 2. Extract time if present (e.g. 10:00 or a las 10)
            time_match = re.search(r'(\d{1,2}:\d{2})', last_user_msg)
            if time_match:
                extracted_time = time_match.group(1)
            else:
                hour_match = re.search(r'a las\s+(\d{1,2})', msg_lower)
                extracted_time = f"{int(hour_match.group(1)):02d}:00" if hour_match else None

            # 3. Extract treatment keywords
            extracted_treatment = None
            if "limpieza" in msg_lower or "profilaxis" in msg_lower:
                extracted_treatment = "Limpieza Dental y Profilaxis"
            elif "blanqueamiento" in msg_lower:
                extracted_treatment = "Blanqueamiento Dental LED"
            elif "ortodoncia" in msg_lower or "bracket" in msg_lower:
                extracted_treatment = "Ortodoncia"
            elif "implante" in msg_lower:
                extracted_treatment = "Implantes Dentales"
            elif "conducto" in msg_lower or "endodoncia" in msg_lower:
                extracted_treatment = "Endodoncia"
            elif "extraccion" in msg_lower or "extracción" in msg_lower or "muela" in msg_lower:
                extracted_treatment = "Extracción Dental"

            # 4. Determine intent and urgency
            if any(w in msg_lower for w in ["duel", "dol", "urgencia", "emergencia", "hinch", "sangr", "rot", "quebr"]):
                intent = "EMERGENCY_OR_PAIN"
                urgency = "high"
                summary = "Paciente reporta dolor agudo o urgencia dental."
            elif any(w in msg_lower for w in ["cita", "turno", "agend", "reserv", "hora"]):
                intent = "BOOK_APPOINTMENT"
                urgency = "normal"
                summary = f"Solicitud de turno para {extracted_treatment or 'evaluación general'}."
            elif any(w in msg_lower for w in ["precio", "cuanto", "sale", "cuesta", "costo", "valor"]):
                intent = "INQUIRE_PRICE_OR_TREATMENT"
                urgency = "normal"
                summary = f"Consulta de precios para {extracted_treatment or 'tratamientos dentales'}."
            elif any(w in msg_lower for w in ["hola", "buenos dias", "buenas tardes"]):
                intent = "GREETING"
                urgency = "normal"
                summary = "Saludo inicial del paciente."
            else:
                intent = "GENERAL_FAQ"
                urgency = "normal"
                summary = "Consulta general sobre la clínica."

            return json.dumps({
                "intent": intent,
                "extracted_name": extracted_name,
                "extracted_treatment": extracted_treatment,
                "extracted_date": None,
                "extracted_time": extracted_time,
                "urgency": urgency,
                "summary": summary
            })

        # Conversational text fallback
        if any(w in msg_lower for w in ["receta", "medicamento", "amoxicilina", "ibuprofeno"]):
            return (
                f"⚠️ Por normativas médicas de {settings.clinic_name}, ningún profesional puede recetar "
                f"medicamentos sin una valoración física previa en el consultorio. "
                f"Si presentas dolor agudo, te invitamos a acudir hoy a {settings.clinic_address}."
            )

        if any(w in msg_lower for w in ["precio", "cuanto", "sale", "cuesta"]):
            return (
                f"🦷 En {settings.clinic_name} nuestros tratamientos tienen valores orientativos: "
                f"Limpieza ($30 - $45 USD), Blanqueamiento LED ($90 - $150 USD), Ortodoncia (evaluación inicial sin costo, planes desde $40/mes) "
                f"e Implantes de titanio ($350 - $600 USD). "
                f"El presupuesto definitivo se confirma en tu evaluación presencial. ¿Deseas agendar una cita?"
            )

        return (
            f"¡Hola! Te escribe el asistente de la Clínica Dental {settings.clinic_name} en {settings.clinic_address}. "
            f"Horario de atención: {settings.business_hours_start}:00 a {settings.business_hours_end}:00 hs. "
            f"¿En qué tratamiento te podemos orientar o te gustaría agendar una cita?"
        )

groq_service = GroqService()
