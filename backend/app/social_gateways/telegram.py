import os
from typing import Dict, Any, Optional
from fastapi import APIRouter, Request, HTTPException, Header
import httpx

from app.config import settings
from app.agents import pipeline
from app.models.dental_models import SolverResponse

router = APIRouter(tags=["Telegram Social Gateway"])


async def dispatch_telegram_reply(chat_id: str, reply_text: str, bot_token: Optional[str] = None) -> Dict[str, Any]:
    """Dispatches outgoing message to Telegram Bot API."""
    token = bot_token or os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        print(f"[Telegram Gateway] Simulación: Mensaje listo para {chat_id} (TELEGRAM_BOT_TOKEN no configurado).")
        return {"status": "simulated", "chat_id": chat_id}

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": reply_text,
        "parse_mode": "Markdown"
    }

    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            resp = await client.post(url, json=payload)
            if resp.is_success:
                print(f"[Telegram Gateway] Mensaje entregado a Telegram para {chat_id}.")
                return resp.json()
            else:
                # Retry in plain text if markdown formatting failed
                payload.pop("parse_mode", None)
                resp_plain = await client.post(url, json=payload)
                return resp_plain.json() if resp_plain.is_success else {"status": "error", "code": resp.status_code}
    except Exception as e:
        print(f"[Telegram Gateway] Error conectando a Telegram Bot API: {e}")
        return {"status": "network_error", "detail": str(e)}


@router.post("/api/webhooks/telegram")
@router.post("/api/webhooks/telegram/")
async def telegram_webhook_event(request: Request):
    """Receives inbound Telegram Bot events and routes through 3-agent pipeline."""
    try:
        payload = await request.json()
    except Exception:
        payload = {}

    omni_msg = pipeline.reader.from_telegram(payload)
    if not omni_msg.raw_text:
        return {"status": "ignored_empty_or_non_text_update"}

    print(f"[Telegram Gateway] Mensaje recibido de {omni_msg.sender_name} ({omni_msg.sender_id}): '{omni_msg.raw_text}'")

    solution: SolverResponse = pipeline.process_message(omni_msg)

    # Dispatch reply back to patient on Telegram
    await dispatch_telegram_reply(
        chat_id=omni_msg.sender_id,
        reply_text=solution.reply
    )

    return solution.model_dump()
