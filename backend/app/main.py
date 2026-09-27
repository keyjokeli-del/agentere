import os
import io
import csv
import json
import hmac
import asyncio
from contextlib import asynccontextmanager
from datetime import datetime, date, timezone
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, HTTPException, Request, Query, Depends, BackgroundTasks, Header, Response, status
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, ConfigDict
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

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
from app.core.security import (
    verify_admin_jwt,
    verify_pin_argon2id,
    create_access_token,
    check_brute_force,
    record_failed_attempt,
    reset_brute_force,
    get_client_ip
)
from app.core.logging_filter import setup_pii_logging
from app.models.dental_models import AppointmentRecord, AppointmentCreateRequest, SlotsResponse
from app.social_gateways.meta import router as meta_router
from app.social_gateways.youtube import router as youtube_router, sync_youtube_comments_task
from app.social_gateways.telegram import router as telegram_router

# Setup PII logging filter on startup (Mejora 5)
setup_pii_logging()

# Setup SlowAPI rate limiter (Mejora 3)
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["120/minute"],
    enabled=os.getenv("TESTING") != "1"
)


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

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Register Social Gateways (Meta, YouTube, Telegram)
app.include_router(meta_router)
app.include_router(youtube_router)
app.include_router(telegram_router)

# Strict CORS Allowlist (Mejora 8)
CORS_ORIGINS = [
    "https://lumina-dental-nairoby-dominguez.vercel.app",
    "https://luminadentalstudio.com",
]
if os.getenv("ENVIRONMENT") != "production":
    CORS_ORIGINS.extend([
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "*"
    ])

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


# Security HTTP Headers Middleware (Mejora 16)
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains; preload"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self' https: data: 'unsafe-inline' 'unsafe-eval'; "
        "frame-ancestors 'none';"
    )
    return response


# Runtime Memory & Temp File Cleanup Middleware
@app.middleware("http")
async def runtime_cleanup_middleware(request: Request, call_next):
    response = await call_next(request)
    cleanup_manager.perform_cleanup(force=False)
    return response


# Input Models with Pydantic V2 Hardening (Mejora 10)
class VerifyPinRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    pin: str = Field(..., min_length=1, max_length=50)


class HandoffRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    minutes: int = Field(30, ge=1, le=1440)
    reason: Optional[str] = Field("Pausado por recepcionista", max_length=200)
    channel: str = Field("whatsapp", max_length=50)


class ChatMessageRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    message: str = Field(..., min_length=1, max_length=1000)
    sender_id: str = Field("web-user", max_length=150)
    channel: str = Field("web", max_length=50)
    sender_name: Optional[str] = Field("Visitante", max_length=150)


@app.get("/")
def health_check(background_tasks: BackgroundTasks):
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


# ==============================================================================
# Authentication & Authorization Endpoints (Mejoras 1, 2, 13, 18)
# ==============================================================================
@app.post("/api/auth/login")
def auth_login(payload: VerifyPinRequest, request: Request, response: Response):
    """
    Authenticates administrative PIN with Argon2id, Anti-Brute Force lockout,
    and issues an HttpOnly SameSite=Strict cookie along with an HS256 JWT (Mejora 1 & 18).
    """
    ip = get_client_ip(request)

    # 1. Anti-Brute Force Lockout Check
    lock_remaining = check_brute_force(ip)
    if lock_remaining:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Demasiados intentos fallidos. Bloqueo temporal por seguridad. Reintenta en {lock_remaining} segundos."
        )

    # 2. Argon2id PIN verification
    pin_clean = payload.pin.strip()
    valid = verify_pin_argon2id(pin_clean)
    if not valid:
        record_failed_attempt(ip)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="PIN clínico incorrecto"
        )

    # 3. Successful login: reset brute force tracker
    reset_brute_force(ip)
    token = create_access_token({"sub": "admin", "role": "admin"})

    # 4. Issue HttpOnly, Secure, SameSite=Strict Cookie
    is_secure = os.getenv("ENVIRONMENT") == "production"
    response.set_cookie(
        key="lumina_auth_token",
        value=token,
        httponly=True,
        secure=is_secure,
        samesite="strict",
        max_age=28800
    )

    admin_key = os.getenv("ADMIN_API_KEY", "lumina_admin_2026")
    return {
        "status": "authenticated",
        "token": token,
        "token_type": "bearer",
        "expires_in": 28800,
        "admin_key": admin_key,
        "valid": True
    }


@app.post("/api/auth/logout")
def auth_logout(response: Response):
    """Clears the HttpOnly authentication cookie."""
    response.delete_cookie(key="lumina_auth_token")
    return {"status": "logged_out"}


@app.post("/api/admin/verify-pin")
def verify_admin_pin(payload: VerifyPinRequest, request: Request, response: Response):
    """Backwards-compatible PIN verification endpoint delegating to auth_login."""
    return auth_login(payload, request, response)


# ==============================================================================
# Human Handoff (Mejora 30 & Protected by verify_admin_jwt)
# ==============================================================================
@app.post("/api/admin/handoff/{sender_id}")
def set_human_handoff(
    sender_id: str,
    payload: HandoffRequest,
    _admin: dict = Depends(verify_admin_jwt)
):
    """Pauses automated agent responses for 30 minutes to allow human receptionist takeover."""
    db_manager.set_human_handoff(sender_id, payload.channel, minutes=payload.minutes, reason=payload.reason)
    return {"status": "paused", "sender_id": sender_id, "minutes": payload.minutes}


@app.delete("/api/admin/handoff/{sender_id}")
def clear_human_handoff(
    sender_id: str,
    _admin: dict = Depends(verify_admin_jwt)
):
    """Reactivates AI agents for a patient after human handoff."""
    db_manager.clear_human_handoff(sender_id)
    return {"status": "resumed", "sender_id": sender_id}


# ==============================================================================
# GDPR / HIPAA Right to be Forgotten (Mejora 14)
# ==============================================================================
@app.delete("/api/patient/purge/{sender_id}")
def purge_patient_data(
    sender_id: str,
    _admin: dict = Depends(verify_admin_jwt)
):
    """Permanently deletes all patient records, turns, vectors, and identities across tables."""
    return db_manager.purge_patient_data(sender_id)


# ==============================================================================
# Server-Sent Events (SSE) Stream
# ==============================================================================
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


# ==============================================================================
# Chat & Inbound Webhooks API (Rate Limited via slowapi)
# ==============================================================================
@app.post("/api/chat")
@limiter.limit("10/minute")
def handle_chat_message(
    request: Request,
    payload: ChatMessageRequest,
    background_tasks: BackgroundTasks
):
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
@limiter.limit("60/minute")
async def whatsapp_webhook(
    request: Request,
    payload: Dict[str, Any],
    background_tasks: BackgroundTasks,
    x_internal_secret: Optional[str] = Header(None, alias="X-Internal-Secret")
):
    """
    Receives incoming WhatsApp messages from the Baileys bridge, validated with X-Internal-Secret (Mejora 15).
    """
    expected_secret = os.getenv("INTERNAL_WEBHOOK_SECRET", "lumina_internal_secret_2026")
    if x_internal_secret:
        if not hmac.compare_digest(x_internal_secret, expected_secret):
            raise HTTPException(status_code=403, detail="Forbidden: Invalid X-Internal-Secret")
    elif os.getenv("ENVIRONMENT") == "production" or os.getenv("STRICT_WEBHOOK_AUTH") == "1":
        raise HTTPException(status_code=403, detail="Forbidden: Missing mandatory X-Internal-Secret")

    omni_msg = pipeline.reader.from_whatsapp(payload)

    print(f"[FastAPI Webhook] Mensaje recibido de {omni_msg.sender_name} ({omni_msg.sender_id}): '{omni_msg.raw_text}'")

    if not omni_msg.raw_text:
        return {"status": "ignored_empty"}

    solution = pipeline.process_message(omni_msg)
    background_tasks.add_task(run_runtime_cleanup, False)

    print(f"[FastAPI Webhook] Respondiendo a {omni_msg.sender_id} con agente '{solution.agent}' (intención: {solution.intent})")
    return solution.model_dump()


# ==============================================================================
# Appointments & Slots API (Public Booking + Protected List)
# ==============================================================================
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
def list_appointments(_admin: dict = Depends(verify_admin_jwt)) -> List[AppointmentRecord]:
    """Protected appointment list accessible only with verified admin token."""
    return calendar_service.list_appointments()


@app.post("/api/appointments", response_model=AppointmentRecord, status_code=200)
@limiter.limit("10/minute")
def create_appointment(
    request: Request,
    payload: AppointmentCreateRequest
) -> AppointmentRecord:
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


# ==============================================================================
# Protected Administrative Endpoints (Mejora 2)
# ==============================================================================
@app.get("/api/admin/export-csv")
def export_admin_csv(_admin: dict = Depends(verify_admin_jwt)):
    """Exports appointments and activities to CSV for clinical and financial auditing (Mejora 25)."""
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
def get_channels_inbox(_admin: dict = Depends(verify_admin_jwt)):
    """Returns real inbox threads and message statistics per channel from Neon PostgreSQL (Protected)."""
    return db_manager.get_channels_inbox()


@app.get("/api/dashboard/summary")
def dashboard_summary(_admin: dict = Depends(verify_admin_jwt)):
    """Returns dashboard metrics with persistent activities from Neon PostgreSQL (Protected)."""
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
def trigger_admin_cleanup(_admin: dict = Depends(verify_admin_jwt)):
    """Manual cleanup trigger to prune in-memory caches, purge temp files, and run gc.collect()."""
    return cleanup_manager.perform_cleanup(force=True)
