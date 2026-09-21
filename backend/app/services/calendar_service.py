import os
import json
from datetime import datetime, timedelta, date, time, timezone
from typing import List, Dict, Any, Optional

from app.config import settings
from app.models.dental_models import AppointmentRecord

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

    def get_available_slots(self, target_date: date) -> List[str]:
        """Returns a list of available time slots (HH:MM) for a given date."""
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
                for event in events:
                    start_str = event["start"].get("dateTime", event["start"].get("date"))
                    if "T" in start_str:
                        dt = datetime.fromisoformat(start_str.replace("Z", "+00:00"))
                        booked_times.add(dt.strftime("%H:%M"))
            except Exception as e:
                print(f"[CalendarService] Error consultando Google Calendar: {e}")

        # Add locally booked appointments
        target_date_str = target_date.strftime("%Y-%m-%d")
        for appt in self.local_appointments:
            if appt.date == target_date_str and appt.status == "confirmed":
                booked_times.add(appt.time)

        # Generate dynamic slots (e.g. 45-minute duration) during business hours
        available: List[str] = []
        current_dt = datetime.combine(target_date, time(settings.business_hours_start, 0))
        end_dt = datetime.combine(target_date, time(settings.business_hours_end, 0))
        slot_delta = timedelta(minutes=settings.slot_duration_minutes)

        while current_dt + slot_delta <= end_dt:
            slot_str = current_dt.strftime("%H:%M")
            if slot_str not in booked_times:
                available.append(slot_str)
            current_dt += slot_delta

        return available

    def is_slot_available(self, target_date: date, time_str: str) -> bool:
        """Checks whether a specific time slot is free."""
        available = self.get_available_slots(target_date)
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
        """Creates an appointment in Google Calendar and local store, rejecting collisions."""
        target_d = datetime.strptime(appointment_date, "%Y-%m-%d").date()

        # Check collision
        available_slots = self.get_available_slots(target_d)
        if not any(appointment_time in s for s in available_slots):
            raise ValueError(f"El horario {appointment_time} no está disponible para el {appointment_date}.")

        # Normalize time to HH:00 format
        matched_slot = next(s for s in available_slots if appointment_time in s)

        start_dt = datetime.strptime(f"{appointment_date} {matched_slot}", "%Y-%m-%d %H:%M")
        end_dt = start_dt + timedelta(minutes=settings.slot_duration_minutes)

        event_body = {
            "summary": f"🦷 Cita Dental: {patient_name} - {treatment}",
            "description": (
                f"Paciente: {patient_name}\n"
                f"Contacto: {phone_or_channel_id}\n"
                f"Tratamiento: {treatment}\n"
                f"Canal de reserva: {channel.upper()}\n"
                f"Agendado automáticamente por el Agente de IA"
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

        appointment_record = AppointmentRecord(
            id=calendar_event_id or f"local-{len(self.local_appointments) + 1}",
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
        return appointment_record

    def list_appointments(self) -> List[AppointmentRecord]:
        """Returns all confirmed appointments."""
        return self.local_appointments

calendar_service = CalendarService()
