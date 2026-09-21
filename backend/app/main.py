import os
from datetime import datetime, date
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, HTTPException, Request, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.config import settings
from app.agents.dental_agents import coordinator
from app.services.calendar_service import calendar_service
from app.models.dental_models import AppointmentRecord, AppointmentCreateRequest, SlotsResponse

app = FastAPI(
    title="Dental Clinic Multi-Agent Omnichannel Hub",
    description="Sistema Multi-Agente para Clínica Dental con soporte para WhatsApp, Facebook, Instagram, YouTube y Google Calendar",
    version="1.0.0"
)

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

@app.get("/")
def health_check():
    return {
        "status": "healthy",
        "clinic": settings.clinic_name,
        "groq_configured": bool(settings.groq_api_key),
        "google_calendar_configured": bool(calendar_service.service is not None),
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
    """Receives incoming WhatsApp messages from the Baileys Node.js bridge."""
    sender_id = payload.get("sender_id", "unknown")
    text = payload.get("message", "")
    sender_name = payload.get("sender_name", sender_id)

    print(f"[FastAPI Webhook] Mensaje recibido de {sender_name} ({sender_id}): '{text}'")

    if not text:
        return {"status": "ignored_empty"}

    response = coordinator.process_incoming_message(
        message=text,
        sender_id=sender_id,
        channel="whatsapp"
    )

    RECENT_ACTIVITIES.insert(0, {
        "id": f"act-{len(RECENT_ACTIVITIES) + 1}",
        "channel": "whatsapp",
        "sender_id": sender_id,
        "sender_name": sender_name,
        "message": text,
        "reply": response.reply,
        "agent": response.agent,
        "intent": response.intent,
        "timestamp": response.timestamp
    })

    print(f"[FastAPI Webhook] Respondiendo a {sender_id} con agente '{response.agent}' (intención: {response.intent})")
    return response.model_dump()

# --- Webhook Meta (Facebook & Instagram) ---
@app.get("/api/webhooks/meta")
def meta_webhook_verification(
    hub_mode: Optional[str] = Query(None, alias="hub.mode"),
    hub_challenge: Optional[str] = Query(None, alias="hub.challenge"),
    hub_verify_token: Optional[str] = Query(None, alias="hub.verify_token")
):
    """Meta Webhook token verification endpoint (free tier)."""
    VERIFY_TOKEN = os.getenv("META_VERIFY_TOKEN", "dental_agent_token_2026")
    if hub_mode == "subscribe" and hub_verify_token == VERIFY_TOKEN:
        return int(hub_challenge) if hub_challenge and hub_challenge.isdigit() else hub_challenge
    raise HTTPException(status_code=403, detail="Verification token mismatch")

@app.post("/api/webhooks/meta")
async def meta_webhook_event(request: Request):
    """Receives Facebook Messenger & Instagram Direct message events."""
    body = await request.json()
    # Simple parser for Meta messages
    entries = body.get("entry", [])
    responses = []
    for entry in entries:
        messaging = entry.get("messaging", [])
        for event in messaging:
            sender_id = event.get("sender", {}).get("id")
            message = event.get("message", {})
            text = message.get("text")
            if text and sender_id:
                # Detect if FB or IG based on entry id or source
                channel = "instagram" if "instagram" in str(entry) else "facebook"
                result = coordinator.process_incoming_message(
                    message=text,
                    sender_id=str(sender_id),
                    channel=channel
                )
                responses.append(result)
    return {"status": "received", "processed": len(responses)}

# --- Webhook YouTube ---
@app.post("/api/webhooks/youtube")
async def youtube_webhook_event(payload: Dict[str, Any]):
    """Receives YouTube video comment events for automated dental response."""
    comment_text = payload.get("comment", "")
    author = payload.get("author", "Usuario de YouTube")
    video_id = payload.get("video_id", "")

    if not comment_text:
        return {"status": "ignored"}

    result = coordinator.process_incoming_message(
        message=comment_text,
        sender_id=author,
        channel="youtube"
    )

    RECENT_ACTIVITIES.insert(0, {
        "id": f"act-{len(RECENT_ACTIVITIES) + 1}",
        "channel": "youtube",
        "sender_id": author,
        "sender_name": f"{author} (Video: {video_id})",
        "message": comment_text,
        "reply": result.reply,
        "agent": result.agent,
        "intent": result.intent,
        "timestamp": result.timestamp
    })

    return result.model_dump()

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
