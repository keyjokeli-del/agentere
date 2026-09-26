from datetime import datetime, date, timedelta, timezone
from typing import List, Dict, Any, Optional

from app.config import settings
from app.core.database import db_manager
from app.services.calendar_service import calendar_service


class CRMLifecycleService:
    """Manages proactive patient care loops, post-op instructions, NPS surveys, and recalls (Mejoras 26-30)."""

    def __init__(self) -> None:
        self.last_run: Optional[datetime] = None

    def process_post_op_followups(self) -> List[Dict[str, Any]]:
        """Sends care instructions at Day 1, Day 3, and Day 7 following extractions or surgery (Mejora 26)."""
        dispatched: List[Dict[str, Any]] = []
        today = date.today()

        # Check completed appointments from tracker
        appts = calendar_service.list_appointments()
        for appt in appts:
            try:
                appt_d = datetime.strptime(appt.date, "%Y-%m-%d").date()
            except Exception:
                continue

            delta_days = (today - appt_d).days
            treatment_lower = (appt.treatment or "").lower()

            is_surgery = any(w in treatment_lower for w in ["extraccion", "extracción", "muela", "implante", "conducto", "endodoncia", "cirugia", "cirugía"])
            if not is_surgery:
                continue

            msg = None
            if delta_days == 1:
                msg = (
                    f"🦷 Hola {appt.patient_name}, esperamos que estés descansando tras tu {appt.treatment} de ayer. "
                    f"Recuerda: 1) Mantén reposo y dieta blanda y fría. 2) No escupas ni uses popote para cuidar el coágulo. "
                    f"3) Aplica hielo indirecto en la mejilla. ¿Cómo sientes la molestia hoy?"
                )
            elif delta_days == 3:
                msg = (
                    f"👋 Hola {appt.patient_name}, seguimiento de tu 3er día post-tratamiento: "
                    f"A partir de hoy puedes comenzar con enjuagues muy suaves de agua tibia con sal tras las comidas. "
                    f"Si experimentas dolor pulsátil fuerte o aumento de hinchazón, avísanos de inmediato."
                )
            elif delta_days == 7:
                msg = (
                    f"✨ Hola {appt.patient_name}, ha pasado una semana de tu procedimiento de {appt.treatment}. "
                    f"La cicatrización de los tejidos blandos debería estar muy avanzada. "
                    f"Si tienes puntos de sutura pendientes de retiro, por favor avísanos para asignarte un horario breve hoy."
                )

            if msg:
                dispatched.append({
                    "patient_name": appt.patient_name,
                    "contact": appt.contact,
                    "treatment": appt.treatment,
                    "day": delta_days,
                    "message": msg
                })

        return dispatched

    def process_nps_surveys(self) -> List[Dict[str, Any]]:
        """Sends satisfaction survey (1 to 5 stars) post-appointment (Mejora 27)."""
        surveys: List[Dict[str, Any]] = []
        today_str = date.today().strftime("%Y-%m-%d")

        for appt in calendar_service.list_appointments():
            if appt.date == today_str and appt.status in ("confirmed", "completed"):
                survey_text = (
                    f"⭐ Hola {appt.patient_name}, gracias por visitar Lumina Dental Studio hoy con {settings.clinic_name}.\n\n"
                    f"¿Cómo calificarías tu atención del 1 al 5? (Responde con un número del 1 al 5 siendo 5 Excelente)."
                )
                surveys.append({
                    "patient_name": appt.patient_name,
                    "contact": appt.contact,
                    "message": survey_text
                })

        return surveys

    def process_preventive_recalls(self) -> List[Dict[str, Any]]:
        """Generates 6-month preventive checkup / prophylaxis recall alerts (Mejora 29)."""
        recalls: List[Dict[str, Any]] = []
        today = date.today()

        for appt in calendar_service.list_appointments():
            try:
                appt_d = datetime.strptime(appt.date, "%Y-%m-%d").date()
            except Exception:
                continue

            # Approximately 180 days (~6 months)
            if (today - appt_d).days == 180:
                recall_msg = (
                    f"🦷 ¡Hola {appt.patient_name}! Han pasado 6 meses desde tu última atención dental en Lumina Dental Studio.\n\n"
                    f"Para mantener tu sonrisa sana y libre de sarro o caries, la Dra. Nairoby Domínguez recomienda realizar "
                    f"tu limpieza preventiva semestral. ¿Te gustaría agendar una cita para esta semana?"
                )
                recalls.append({
                    "patient_name": appt.patient_name,
                    "contact": appt.contact,
                    "message": recall_msg
                })

        return recalls

    def trigger_lifecycle_tick(self, force: bool = False) -> Dict[str, Any]:
        """Triggered periodically by health check background tasks without blocking requests."""
        now = datetime.now(timezone.utc)
        if not force and self.last_run and (now - self.last_run).total_seconds() < 3600:
            # Enforce 1-hour cooldown between automated lifecycle passes
            return {"status": "cooldown_active"}

        self.last_run = now
        post_ops = self.process_post_op_followups()
        surveys = self.process_nps_surveys()
        recalls = self.process_preventive_recalls()

        return {
            "status": "processed",
            "post_ops_count": len(post_ops),
            "surveys_count": len(surveys),
            "recalls_count": len(recalls)
        }


crm_lifecycle_service = CRMLifecycleService()
