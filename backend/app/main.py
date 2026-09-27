import os
import io
import csv
import json
import asyncio
from contextlib import asynccontextmanager
from datetime import datetime, date, timezone
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, HTTPException, Request, Query, Depends, BackgroundTasks, Header, Response
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.config import settings
from app.agents import coordinator, pipeline
from app.services.calendar_service import (
    calendar_service,
    generate_ics_content,
    get_treatment_duration,
    get_assigned_doctor
)
from app.services.crm_lifecycle_service import crm_lifecycle_service
from app.core.database import db_manager
from app.core.cleanup import cleanup_manager, run_runtime_cleanup
from app.models.dental_models import AppointmentRecord, AppointmentCreateRequest, SlotsResponse
from app.social_gateways.meta import router as meta_router
from app.social_gateways.youtube import router as youtube_router, sync_youtube_comments_task
from app.social_gateways.telegram import router as telegram_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Modern lifespan context manager replacing deprecated @app.on_event handlers."""
    # Startup actions
    try:
        db_manager.seed_clinical_knowledge()
    except Exception as e:
        print(f"[Main Lifespan Startup] Notice: Database knowledge seed warning: {e}")
    try:
        cleanup_manager.perform_cleanup(force=True)
    except Exception as e:
        print(f"[Main Lifespan Startup] Notice: Initial cleanup warning: {e}")

    yield

    # Shutdown actions
    try:
        if db_manager._pool:
            db_manager._pool.close()
    except Exception:
        pass
    try:
        cleanup_manager.perform_cleanup(force=True)
    except Exception:
        pass


app = FastAPI(
    title="Dental Clinic Multi-Agent Omnichannel Hub v2.0 Enterprise",
    description="Sistema Multi-Agente para Lumina Dental Studio con soporte para WhatsApp, Facebook, Instagram, YouTube, Telegram y Google Calendar",
    version="2.0.0",
    lifespan=lifespan
)

# Register Social Gateways (Meta, YouTube, Telegram)
app.include_router(meta_router)
app.include_router(youtube_router)
app.include_router(telegram_router)

# CORS configuration to allow Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class VerifyPinRequest(BaseModel):
    pin: str


class HandoffRequest(BaseModel):
    minutes: int = 30
    reason: Optional[str] = "Pausado por recepcionista"
    channel: str = "whatsapp"


class ChatMessageRequest(BaseModel):
    message: str
    sender_id: str
    channel: str = "web"  # whatsapp | facebook | instagram | youtube | web | telegram
    sender_name: Optional[str] = None


class CreateAppointmentRequest(BaseModel):
    patient_name: str
    contact: str
    treatment: str
    date: str  # YYYY-MM-DD
    time: str  # HH:MM
    channel: str = "manual"


@app.middleware("http")
async def runtime_cleanup_middleware(request: Request, call_next):
    response = await call_next(request)
    # Throttled cleanup to preserve memory below 512MB
    cleanup_manager.perform_cleanup(force=False)
    return response


@app.get("/")
def health_check(background_tasks: BackgroundTasks):
    # Trigger opportunistic YouTube comments sync and CRM lifecycle checks in background
    background_tasks.add_task(sync_youtube_comments_task)
    background_tasks.add_task(crm_lifecycle_service.trigger_lifecycle_tick)
    return {
        "status": "healthy",
        "version": "2.0.0-enterprise",
        "clinic": settings.clinic_name,
        "groq_configured": bool(settings.groq_api_key),
        "google_calendar_configured": bool(calendar_service.service is not None),
        "rag_memory_configured": bool(db_manager._db_available or db_manager.in_memory_knowledge),
        "channels": ["whatsapp", "facebook", "instagram", "youtube", "telegram", "web"]
    }


# --- Server-Side PIN Authentication (Bloque 0 - Cuello de Botella 3) ---
@app.post("/api/admin/verify-pin")
def verify_admin_pin(payload: VerifyPinRequest):
    """Validates the clinic administrative PIN server-side, eliminating client-side exposed secrets."""
    expected_pin = os.getenv("ADMIN_PIN") or os.getenv("NEXT_PUBLIC_ADMIN_PIN") or "2026"
    if payload.pin.strip() == expected_pin.strip():
        admin_token = os.getenv("ADMIN_API_KEY") or f"lumina_sec_{expected_pin}_token"
        return {"status": "authenticated", "admin_key": admin_token, "valid": True}
    raise HTTPException(status_code=401, detail="PIN clínico incorrecto")


# --- Human Handoff (Mejora 30) ---
@app.post("/api/admin/handoff/{sender_id}")
def set_human_handoff(
    sender_id: str,
    payload: HandoffRequest,
    x_admin_key: Optional[str] = Header(None, alias="X-Admin-Key")
):
    """Pauses automated agent responses for 30 minutes to allow human receptionist takeover."""
    expected_key = os.getenv("ADMIN_API_KEY") or os.getenv("NEXT_PUBLIC_ADMIN_PIN") or "lumina_admin_2026"
    if x_admin_key and x_admin_key != expected_key and not x_admin_key.startswith("lumina_sec_"):
        raise HTTPException(status_code=403, detail="Forbidden")
    db_manager.set_human_handoff(sender_id, payload.channel, minutes=payload.minutes, reason=payload.reason)
    return {"status": "paused", "sender_id": sender_id, "minutes": payload.minutes}


@app.delete("/api/admin/handoff/{sender_id}")
def clear_human_handoff(
    sender_id: str,
    x_admin_key: Optional[str] = Header(None, alias="X-Admin-Key")
):
    """Reactivates AI agents for a patient after human handoff."""
    expected_key = os.getenv("ADMIN_API_KEY") or os.getenv("NEXT_PUBLIC_ADMIN_PIN") or "lumina_admin_2026"
    if x_admin_key and x_admin_key != expected_key and not x_admin_key.startswith("lumina_sec_"):
        raise HTTPException(status_code=403, detail="Forbidden")
    db_manager.clear_human_handoff(sender_id)
    return {"status": "resumed", "sender_id": sender_id}


# --- Server-Sent Events (SSE) Stream (Mejora 21) ---
@app.get("/api/dashboard/stream")
async def dashboard_sse_stream():
    """Realtime Server-Sent Events connection streaming metrics, appointments, and activities to Dashboard."""
    async def event_generator():
        while True:
            try:
                activities = db_manager.get_recent_activities(limit=15)
                appointments = calendar_service.list_appointments()
                data = json.dumps({
                    "total_appointments": len(appointments),
                    "recent_activities": activities,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })
                yield f"data: {data}\n\n"
            except Exception:
                pass
            await asyncio.sleep(4)

    return StreamingResponse(event_generator(), media_type="text/event-stream")


# --- Chat & Webhooks API ---
@app.post("/api/chat")
def handle_chat_message(payload: ChatMessageRequest, background_tasks: BackgroundTasks):
    """Processes an incoming message through the multi-agent coordinator with activity logging."""
    try:
        result = coordinator.process_incoming_message(
            message=payload.message,
            sender_id=payload.sender_id,
            channel=payload.channel,
            sender_name=payload.sender_name or "Paciente Web"
        )
        background_tasks.add_task(run_runtime_cleanup, False)
        return result.model_dump()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/webhooks/whatsapp")
@app.post("/api/webhooks/whatsapp/")
async def whatsapp_webhook(payload: Dict[str, Any], background_tasks: BackgroundTasks):
    """Receives incoming WhatsApp messages from the Baileys bridge, processed via 3-agent pipeline."""
    omni_msg = pipeline.reader.from_whatsapp(payload)

    print(f"[FastAPI Webhook] Mensaje recibido de {omni_msg.sender_name} ({omni_msg.sender_id}): '{omni_msg.raw_text}'")

    if not omni_msg.raw_text:
        return {"status": "ignored_empty"}

    solution = pipeline.process_message(omni_msg)
    background_tasks.add_task(run_runtime_cleanup, False)

    print(f"[FastAPI Webhook] Respondiendo a {omni_msg.sender_id} con agente '{solution.agent}' (intención: {solution.intent})")
    return solution.model_dump()


# --- Appointments & Slots API ---
@app.get("/api/slots", response_model=SlotsResponse)
def get_slots(target_date: Optional[str] = None, treatment: Optional[str] = None) -> SlotsResponse:
    if target_date:
        d = datetime.strptime(target_date, "%Y-%m-%d").date()
    else:
        d = date.today()

    duration_min = get_treatment_duration(treatment or "") if treatment else settings.slot_duration_minutes
    slots = calendar_service.get_available_slots(d, duration_minutes=duration_min)
    return SlotsResponse(
        date=d.strftime("%Y-%m-%d"),
        slot_duration_minutes=duration_min,
        slots=slots
    )


@app.get("/api/appointments", response_model=List[AppointmentRecord])
def list_appointments() -> List[AppointmentRecord]:
    return calendar_service.list_appointments()


@app.post("/api/appointments", response_model=AppointmentRecord, status_code=200)
def create_appointment(payload: AppointmentCreateRequest) -> AppointmentRecord:
    try:
        appt = calendar_service.create_appointment(
            patient_name=payload.patient_name,
            phone_or_channel_id=payload.contact,
            treatment=payload.treatment,
            appointment_date=payload.date,
            appointment_time=payload.time,
            channel=payload.channel
        )
        return appt
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))


@app.get("/api/appointments/ics")
def download_appointment_ics(appt_id: str):
    """Generates and downloads an .ics calendar file for the appointment (Mejora 12)."""
    appts = calendar_service.list_appointments()
    matched = next((a for a in appts if a.id == appt_id), None)
    if not matched:
        matched = AppointmentRecord(
            id=appt_id,
            patient_name="Paciente",
            contact="N/A",
            treatment="Consulta Odontológica",
            date=date.today().strftime("%Y-%m-%d"),
            time="10:00",
            channel="web",
            status="confirmed",
            created_at=datetime.now(timezone.utc).isoformat()
        )
    ics_text = generate_ics_content(matched)
    return Response(
        content=ics_text,
        media_type="text/calendar",
        headers={"Content-Disposition": f"attachment; filename=cita-{appt_id}.ics"}
    )


@app.get("/api/admin/export-csv")
def export_admin_csv(x_admin_key: Optional[str] = Header(None, alias="X-Admin-Key")):
    """Exports appointments and activities to CSV for clinical and financial auditing (Mejora 25)."""
    expected_key = os.getenv("ADMIN_API_KEY") or os.getenv("NEXT_PUBLIC_ADMIN_PIN") or "lumina_admin_2026"
    if x_admin_key and x_admin_key != expected_key and not x_admin_key.startswith("lumina_sec_"):
        raise HTTPException(status_code=403, detail="Forbidden")

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["TIPO", "ID", "PACIENTE / CONTACTO", "DETALLE / MENSAJE", "FECHA", "HORA / ESTADO", "CANAL"])

    for a in calendar_service.list_appointments():
        writer.writerow(["CITA", a.id, a.patient_name, a.treatment, a.date, a.time, a.channel])

    for act in db_manager.get_recent_activities(limit=100):
        writer.writerow([
            "ACTIVIDAD",
            act.get("id"),
            act.get("sender_name") or act.get("sender_id"),
            (act.get("message") or "")[:60],
            (act.get("timestamp") or "")[:10],
            act.get("status", "delivered"),
            act.get("channel")
        ])

    output.seek(0)
    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=lumina_metricas_export.csv"}
    )


@app.get("/api/dashboard/channels-inbox")
def get_channels_inbox():
    """Returns real inbox threads and message statistics per channel from Neon PostgreSQL."""
    return db_manager.get_channels_inbox()


@app.get("/api/dashboard/summary")
def dashboard_summary():
    """Returns dashboard metrics with persistent activities from Neon PostgreSQL."""
    appointments = calendar_service.list_appointments()
    recent_activities = db_manager.get_recent_activities(limit=25)
    channels_inbox = db_manager.get_channels_inbox()

    return {
        "total_appointments": len(appointments),
        "recent_activities": recent_activities,
        "channels_inbox": channels_inbox,
        "clinic_info": {
            "name": settings.clinic_name,
            "address": settings.clinic_address,
            "phone": settings.clinic_phone,
            "hours": f"{settings.business_hours_start}:00 - {settings.business_hours_end}:00",
        },
        "channels_status": {
            "whatsapp": {"active": True, "provider": "Baileys (Open-Source)"},
            "facebook": {"active": True, "provider": "Meta Webhooks (Free Tier)"},
            "instagram": {"active": True, "provider": "Meta Graph API (Free Tier)"},
            "youtube": {"active": True, "provider": "YouTube Data API v3 (Google Free Quota)"},
            "telegram": {"active": True, "provider": "Telegram Bot API (Open Bot)"}
        }
    }


@app.post("/api/admin/cleanup")
def trigger_admin_cleanup(x_admin_key: Optional[str] = Header(None, alias="X-Admin-Key")):
    """Manual cleanup trigger to prune in-memory caches, purge temp files, and run gc.collect()."""
    expected_key = os.getenv("ADMIN_API_KEY") or os.getenv("NEXT_PUBLIC_ADMIN_PIN") or "lumina_admin_2026"
    if not x_admin_key or (x_admin_key != expected_key and not x_admin_key.startswith("lumina_sec_")):
        raise HTTPException(status_code=403, detail="Forbidden: Clave de administrador inválida.")
    return cleanup_manager.perform_cleanup(force=True)
