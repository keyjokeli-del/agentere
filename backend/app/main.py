import os
from datetime import datetime, date
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, HTTPException, Request, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.config import settings
from app.agents.dental_agents import coordinator, pipeline
from app.services.calendar_service import calendar_service
from app.services.rag_memory_service import rag_memory_service
from app.models.dental_models import AppointmentRecord, AppointmentCreateRequest, SlotsResponse
from app.social_gateways.meta import router as meta_router
from app.social_gateways.youtube import router as youtube_router

app = FastAPI(
    title="Dental Clinic Multi-Agent Omnichannel Hub",
    description="Sistema Multi-Agente para Clínica Dental con soporte para WhatsApp, Facebook, Instagram, YouTube y Google Calendar",
    version="1.0.0"
)

# Register Social Gateways (Meta & YouTube)
app.include_router(meta_router)
app.include_router(youtube_router)

# CORS configuration to allow Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory recent activity log for live dashboard
RECENT_ACTIVITIES: List[Dict[str, Any]] = []

class ChatMessageRequest(BaseModel):
    message: str
    sender_id: str
    channel: str = "web"  # whatsapp | facebook | instagram | youtube | web
    sender_name: Optional[str] = None

class CreateAppointmentRequest(BaseModel):
    patient_name: str
    contact: str
    treatment: str
    date: str  # YYYY-MM-DD
    time: str  # HH:MM
    channel: str = "manual"

@app.on_event("startup")
def on_startup():
    try:
        rag_memory_service.seed_clinical_knowledge()
    except Exception as e:
        print(f"[Main Startup] Notice: RAG memory service init warning: {e}")

@app.get("/")
def health_check():
    return {
        "status": "healthy",
        "clinic": settings.clinic_name,
        "groq_configured": bool(settings.groq_api_key),
        "google_calendar_configured": bool(calendar_service.service is not None),
        "rag_memory_configured": bool(rag_memory_service._db_available or rag_memory_service._in_memory_knowledge),
        "channels": ["whatsapp", "facebook", "instagram", "youtube"]
    }


@app.post("/api/chat")
def handle_chat_message(payload: ChatMessageRequest):
    """Processes an incoming message through the multi-agent coordinator."""
    try:
        result = coordinator.process_incoming_message(
            message=payload.message,
            sender_id=payload.sender_id,
            channel=payload.channel
        )
        
        # Log to recent activities
        activity = {
            "id": f"act-{len(RECENT_ACTIVITIES) + 1}",
            "channel": payload.channel,
            "sender_id": payload.sender_id,
            "sender_name": payload.sender_name or payload.sender_id,
            "message": payload.message,
            "reply": result.reply,
            "agent": result.agent,
            "intent": result.intent,
            "timestamp": result.timestamp
        }
        RECENT_ACTIVITIES.insert(0, activity)
        if len(RECENT_ACTIVITIES) > 50:
            RECENT_ACTIVITIES.pop()

        return result.model_dump()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- Webhook WhatsApp (From Baileys Service) ---
@app.post("/api/webhooks/whatsapp")
@app.post("/api/webhooks/whatsapp/")
async def whatsapp_webhook(payload: Dict[str, Any]):
    """Receives incoming WhatsApp messages from the Baileys Node.js bridge, processed via 3-agent pipeline."""
    omni_msg = pipeline.reader.from_whatsapp(payload)

    print(f"[FastAPI Webhook] Mensaje recibido de {omni_msg.sender_name} ({omni_msg.sender_id}): '{omni_msg.raw_text}'")

    if not omni_msg.raw_text:
        return {"status": "ignored_empty"}

    solution = pipeline.process_message(omni_msg)

    RECENT_ACTIVITIES.insert(0, {
        "id": f"act-{len(RECENT_ACTIVITIES) + 1}",
        "channel": "whatsapp",
        "sender_id": omni_msg.sender_id,
        "sender_name": omni_msg.sender_name,
        "message": omni_msg.raw_text,
        "reply": solution.reply,
        "agent": solution.agent,
        "intent": solution.intent,
        "timestamp": solution.timestamp
    })

    print(f"[FastAPI Webhook] Respondiendo a {omni_msg.sender_id} con agente '{solution.agent}' (intención: {solution.intent})")
    return solution.model_dump()

# --- Appointments & Slots API ---
@app.get("/api/slots", response_model=SlotsResponse)
def get_slots(target_date: Optional[str] = None) -> SlotsResponse:
    if target_date:
        d = datetime.strptime(target_date, "%Y-%m-%d").date()
    else:
        d = date.today()
    slots = calendar_service.get_available_slots(d)
    return SlotsResponse(
        date=d.strftime("%Y-%m-%d"),
        slot_duration_minutes=settings.slot_duration_minutes,
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

@app.get("/api/dashboard/summary")
def dashboard_summary():
    appointments = calendar_service.list_appointments()
    return {
        "total_appointments": len(appointments),
        "recent_activities": RECENT_ACTIVITIES[:15],
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
            "youtube": {"active": True, "provider": "YouTube Data API v3 (Google Free Quota)"}
        }
    }
