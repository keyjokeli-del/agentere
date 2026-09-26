import os
import json
import urllib.parse
from datetime import datetime, timedelta, date, time, timezone
from typing import List, Dict, Any, Optional

from app.config import settings
from app.models.dental_models import AppointmentRecord
from app.core.database import db_manager


def get_treatment_duration(treatment: str) -> int:
    """Calculates dynamic appointment duration (minutes) based on procedure complexity (Mejora 9)."""
    t = (treatment or "").lower()
    if any(w in t for w in ["limpieza", "profilaxis"]):
        return 30
    elif any(w in t for w in ["implante", "endodoncia", "conducto", "cirug", "muela del juicio", "extraccion", "extracción"]):
        return 90
    elif any(w in t for w in ["blanqueamiento"]):
        return 60
    return 45


def get_assigned_doctor(treatment: str) -> str:
    """Assigns clinical specialist according to treatment area (Mejora 10)."""
    t = (treatment or "").lower()
    if any(w in t for w in ["implante", "cirug", "muela del juicio", "extraccion", "extracción"]):
        return "Dr. Cirujano Maxilofacial"
    elif any(w in t for w in ["ortodoncia", "bracket", "alineador"]):
        return "Dra. Ortodoncista Especialista"
    return "Dra. Nairoby Domínguez (Directora Médica)"


def generate_google_calendar_url(
    patient_name: str,
    treatment: str,
    appointment_date: str,
    appointment_time: str,
    duration_min: int = 45,
    doctor: str = "Dra. Nairoby Domínguez"
) -> str:
    """Generates direct 1-click Google Calendar booking URL (Mejora 12)."""
    start_dt = datetime.strptime(f"{appointment_date} {appointment_time}", "%Y-%m-%d %H:%M")
    end_dt = start_dt + timedelta(minutes=duration_min)

    fmt = "%Y%m%dT%H%M%SZ"
    dates = f"{start_dt.strftime(fmt)}/{end_dt.strftime(fmt)}"

    title = f"🦷 Cita Odontológica: {treatment} - Lumina Dental Studio"
    details = (
        f"Paciente: {patient_name}\n"
        f"Profesional a cargo: {doctor}\n"
        f"Tratamiento: {treatment}\n"
        f"Dirección: {settings.clinic_address}\n"
        f"Teléfono: {settings.clinic_phone}\n\n"
        f"Por favor presentarse 10 minutos antes con su documento de identidad."
    )
    location = f"{settings.clinic_name}, {settings.clinic_address}"

    params = {
        "action": "TEMPLATE",
        "text": title,
        "dates": dates,
        "details": details,
        "location": location
    }
    return f"https://calendar.google.com/calendar/render?{urllib.parse.urlencode(params)}"


def generate_ics_content(appt: AppointmentRecord, duration_min: int = 45, doctor: str = "Dra. Nairoby Domínguez") -> str:
    """Generates RFC 5545 compliant .ics calendar file format for Apple / Outlook / Google (Mejora 12)."""
    start_dt = datetime.strptime(f"{appt.date} {appt.time}", "%Y-%m-%d %H:%M")
    end_dt = start_dt + timedelta(minutes=duration_min)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    fmt = "%Y%m%dT%H%M%SZ"

    return (
        "BEGIN:VCALENDAR\r\n"
        "VERSION:2.0\r\n"
        "PRODID:-//Lumina Dental Studio//Appointment System v2.0//ES\r\n"
        "CALSCALE:GREGORIAN\r\n"
        "METHOD:PUBLISH\r\n"
        "BEGIN:VEVENT\r\n"
        f"UID:appt-{appt.id}@luminadentalstudio.com\r\n"
        f"DTSTAMP:{stamp}\r\n"
        f"DTSTART:{start_dt.strftime(fmt)}\r\n"
        f"DTEND:{end_dt.strftime(fmt)}\r\n"
        f"SUMMARY:🦷 Cita Odontológica: {appt.treatment} - Lumina Dental Studio\r\n"
        f"DESCRIPTION:Paciente: {appt.patient_name}\\nProfesional: {doctor}\\nTratamiento: {appt.treatment}\\nTel: {settings.clinic_phone}\r\n"
        f"LOCATION:{settings.clinic_name}, {settings.clinic_address}\r\n"
        "STATUS:CONFIRMED\r\n"
        "END:VEVENT\r\n"
        "END:VCALENDAR\r\n"
    )


class CalendarService:
    def __init__(self) -> None:
        self.service = None
        self.local_appointments: List[AppointmentRecord] = []
        self._init_google_service()

    def _init_google_service(self) -> None:
        """Initializes Google Calendar API service if credentials exist via env JSON or local file."""
        creds_json = os.getenv("GOOGLE_CREDENTIALS_JSON")
        if creds_json:
            try:
                from google.oauth2 import service_account
                from googleapiclient.discovery import build
                data = json.loads(creds_json)
                credentials = service_account.Credentials.from_service_account_info(
                    data,
                    scopes=["https://www.googleapis.com/auth/calendar"]
                )
                self.service = build("calendar", "v3", credentials=credentials)
                print("[CalendarService] Google Calendar API conectado con éxito desde GOOGLE_CREDENTIALS_JSON.")
                return
            except Exception as e:
                print(f"[CalendarService] Aviso: Error cargando GOOGLE_CREDENTIALS_JSON ({e}). Probando archivo local...")

        creds_file = settings.google_credentials_file
        candidate_paths = [
            creds_file,
            os.path.join(settings.BASE_DIR, creds_file),
            os.path.join(str(settings.BASE_DIR.parent), creds_file)
        ]
        resolved_file = next((p for p in candidate_paths if os.path.exists(p)), None)
        if resolved_file:
            try:
                from google.oauth2 import service_account
                from googleapiclient.discovery import build
                with open(resolved_file, "r") as f:
                    data = json.load(f)
                if "type" in data and data["type"] == "service_account":
                    credentials = service_account.Credentials.from_service_account_file(
                        resolved_file,
                        scopes=["https://www.googleapis.com/auth/calendar"]
                    )
                    self.service = build("calendar", "v3", credentials=credentials)
                    print(f"[CalendarService] Google Calendar API conectado con éxito desde {resolved_file}.")
            except Exception as e:
                print(f"[CalendarService] Aviso: No se pudo conectar a Google Calendar API ({e}). Usando almacén local.")
        else:
            print("[CalendarService] Sin credenciales de Google Calendar. Operando en modo de calendario local en memoria.")

    def get_available_slots(self, target_date: date, duration_minutes: Optional[int] = None) -> List[str]:
        """Returns a list of available time slots (HH:MM) for a given date with holiday and dynamic duration support."""
        # 1. Closed on Sundays (Mejora 13)
        if target_date.weekday() == 6:
            return []

        booked_times = set()

        if self.service:
            try:
                start_of_day = datetime.combine(target_date, time(0, 0, 0)).isoformat() + "Z"
                end_of_day = datetime.combine(target_date, time(23, 59, 59)).isoformat() + "Z"

                events_result = self.service.events().list(
                    calendarId=settings.google_calendar_id,
                    timeMin=start_of_day,
                    timeMax=end_of_day,
                    singleEvents=True,
                    orderBy="startTime"
                ).execute()

                events = events_result.get("items", [])
                # Check holiday / vacation blocking events (Mejora 13)
                for event in events:
                    summary_lower = (event.get("summary") or "").lower()
                    if any(w in summary_lower for w in ["feriado", "vacaciones", "congreso", "cerrado", "inhabiles"]):
                        return []

                    start_str = event["start"].get("dateTime", event["start"].get("date"))
                    if "T" in start_str:
                        dt = datetime.fromisoformat(start_str.replace("Z", "+00:00"))
                        booked_times.add(dt.strftime("%H:%M"))
            except Exception as e:
                print(f"[CalendarService] Error consultando Google Calendar: {e}")

        # Add locally booked appointments
        target_date_str = target_date.strftime("%Y-%m-%d")
        for appt in self.local_appointments:
            if appt.date == target_date_str and appt.status in ("confirmed", "tentative"):
                booked_times.add(appt.time)

        # Generate dynamic slots during business hours
        available: List[str] = []
        current_dt = datetime.combine(target_date, time(settings.business_hours_start, 0))
        end_dt = datetime.combine(target_date, time(settings.business_hours_end, 0))
        slot_min = duration_minutes if duration_minutes is not None else settings.slot_duration_minutes
        slot_delta = timedelta(minutes=slot_min)

        while current_dt + slot_delta <= end_dt:
            slot_str = current_dt.strftime("%H:%M")
            if slot_str not in booked_times:
                available.append(slot_str)
            current_dt += slot_delta

        return available

    def is_slot_available(self, target_date: date, time_str: str, duration_minutes: Optional[int] = None) -> bool:
        """Checks whether a specific time slot is free."""
        available = self.get_available_slots(target_date, duration_minutes=duration_minutes)
        return any(time_str in s for s in available)

    def create_appointment(
        self,
        patient_name: str,
        phone_or_channel_id: str,
        treatment: str,
        appointment_date: str,  # YYYY-MM-DD
        appointment_time: str,  # HH:MM
        channel: str = "whatsapp"
    ) -> AppointmentRecord:
        """Creates an appointment with dynamic duration, assigned doctor, and Neon persistence."""
        target_d = datetime.strptime(appointment_date, "%Y-%m-%d").date()
        duration_min = get_treatment_duration(treatment)
        doctor = get_assigned_doctor(treatment)

        # Check collision
        available_slots = self.get_available_slots(target_d, duration_minutes=duration_min)
        if not any(appointment_time in s for s in available_slots):
            # Fallback check standard 45-min slots for backward compatibility
            fallback_slots = self.get_available_slots(target_d, duration_minutes=settings.slot_duration_minutes)
            if not any(appointment_time in s for s in fallback_slots):
                raise ValueError(f"El horario {appointment_time} no está disponible para el {appointment_date}.")
            matched_slot = next(s for s in fallback_slots if appointment_time in s)
        else:
            matched_slot = next(s for s in available_slots if appointment_time in s)

        start_dt = datetime.strptime(f"{appointment_date} {matched_slot}", "%Y-%m-%d %H:%M")
        end_dt = start_dt + timedelta(minutes=duration_min)

        event_body = {
            "summary": f"🦷 Cita Dental: {patient_name} - {treatment} ({doctor})",
            "description": (
                f"Paciente: {patient_name}\n"
                f"Contacto: {phone_or_channel_id}\n"
                f"Tratamiento: {treatment}\n"
                f"Especialista: {doctor}\n"
                f"Duración: {duration_min} minutos\n"
                f"Canal de reserva: {channel.upper()}\n"
                f"Agendado automáticamente por el Agente de IA Lumina v2.0"
            ),
            "start": {"dateTime": start_dt.isoformat(), "timeZone": "UTC"},
            "end": {"dateTime": end_dt.isoformat(), "timeZone": "UTC"},
        }

        calendar_event_id = None
        if self.service:
            try:
                created_event = self.service.events().insert(
                    calendarId=settings.google_calendar_id,
                    body=event_body
                ).execute()
                calendar_event_id = created_event.get("id")
            except Exception as e:
                print(f"[CalendarService] Error guardando en Google Calendar: {e}")

        appt_id = calendar_event_id or f"local-{len(self.local_appointments) + 1}"
        appointment_record = AppointmentRecord(
            id=appt_id,
            patient_name=patient_name,
            contact=phone_or_channel_id,
            treatment=treatment,
            date=appointment_date,
            time=matched_slot,
            channel=channel,
            status="confirmed",
            created_at=datetime.now(timezone.utc).isoformat()
        )
        self.local_appointments.append(appointment_record)

        # Persist in Neon appointments_tracker (Mejora 8)
        db_manager.record_appointment(
            appt_id=appt_id,
            patient_name=patient_name,
            contact=phone_or_channel_id,
            treatment=treatment,
            doctor=doctor,
            appointment_date=appointment_date,
            appointment_time=matched_slot,
            duration_min=duration_min,
            channel=channel,
            status="confirmed"
        )

        return appointment_record

    def update_appointment_status(self, contact: str, new_status: str) -> Optional[AppointmentRecord]:
        """Updates appointment status and checks waitlist on cancellation (Mejoras 8 y 11)."""
        target_appt = None
        for appt in reversed(self.local_appointments):
            if appt.contact == contact or contact in appt.contact:
                appt.status = new_status  # type: ignore[assignment]
                target_appt = appt
                break

        db_manager.update_appointment_status(contact, new_status)

        # Waitlist Auto-Fill check on cancellation (Mejora 11)
        if new_status == "cancelled" and target_appt:
            notified_patients = db_manager.check_waitlist_for_cancellation(target_appt.date)
            if notified_patients:
                print(f"[CalendarService] Lista de espera activada para {target_appt.date}: {len(notified_patients)} pacientes notificados.")

        return target_appt

    def list_appointments(self) -> List[AppointmentRecord]:
        """Returns all appointments."""
        return self.local_appointments


calendar_service = CalendarService()
