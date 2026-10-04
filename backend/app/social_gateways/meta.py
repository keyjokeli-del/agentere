import os
import time
import hmac
import hashlib
import json
from typing import Optional, Dict, Any
from fastapi import APIRouter, Request, HTTPException, Query, Header, BackgroundTasks
import httpx

from app.config import settings
from app.agents import pipeline
from app.models.dental_models import SolverResponse
from app.core.database import db_manager
from app.core.observability import track_dependency

router = APIRouter(tags=["Meta Social Gateway"])

# In-memory LRU / TTL Anti-Replay Cache (Mejora 4)
_seen_meta_payloads: Dict[str, float] = {}


def check_and_record_replay(raw_body: bytes) -> bool:
    """
    Checks if raw_body SHA-256 hash was seen in the last 15 minutes (900 seconds).
    Returns True if replay attack detected, False otherwise.
    """
    payload_hash = hashlib.sha256(raw_body).hexdigest()
    now = time.time()
    # Prune expired entries older than 15 minutes
    expired = [k for k, t in _seen_meta_payloads.items() if now - t > 900]
    for k in expired:
        _seen_meta_payloads.pop(k, None)

    if payload_hash in _seen_meta_payloads:
        return True
    _seen_meta_payloads[payload_hash] = now
    return False


def verify_meta_signature(raw_body: bytes, signature_header: Optional[str], app_secret: str) -> bool:
    """Verifies the X-Hub-Signature-256 header sent by Meta using HMAC-SHA256."""
    if not app_secret:
        return True
    if not signature_header or not signature_header.startswith("sha256="):
        return False

    expected_hash = hmac.new(
        key=app_secret.encode("utf-8"),
        msg=raw_body,
        digestmod=hashlib.sha256
    ).hexdigest()
    expected_signature = f"sha256={expected_hash}"
    return hmac.compare_digest(expected_signature, signature_header)


async def send_meta_typing_indicator(recipient_id: str, access_token: str) -> None:
    """Sends 'typing_on' sender action to Messenger or Instagram (Mejora 15)."""
    if not access_token:
        return
    url = "https://graph.facebook.com/v21.0/me/messages"
    payload = {"recipient": {"id": recipient_id}, "sender_action": "typing_on"}
    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            await client.post(url, json=payload, headers=headers)
    except Exception:
        pass


async def reply_public_instagram_comment(comment_id: str, reply_text: str, access_token: str) -> Dict[str, Any]:
    """Posts a public reply to an Instagram comment (Mejora 16)."""
    if not access_token or not comment_id:
        return {"status": "simulated", "comment_id": comment_id}
    url = f"https://graph.facebook.com/v21.0/{comment_id}/replies"
    payload = {"message": reply_text}
    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
    try:
        async with track_dependency("meta_graph"):
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.post(url, json=payload, headers=headers)
                return resp.json() if resp.is_success else {"status": "error", "code": resp.status_code}
    except Exception as e:
        return {"status": "network_error", "detail": str(e)}


async def dispatch_meta_graph_reply(recipient_id: str, reply_text: str, access_token: str) -> Dict[str, Any]:
    """Dispatches outgoing reply via Meta Graph API (Messenger / Instagram Direct)."""
    if not access_token:
        print(f"[Meta Gateway] Simulación: Mensaje listo para {recipient_id} (META_ACCESS_TOKEN no configurado).")
        return {"status": "simulated", "recipient_id": recipient_id}

    url = "https://graph.facebook.com/v21.0/me/messages"
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": reply_text},
        "messaging_type": "RESPONSE"
    }
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    try:
        async with track_dependency("meta_graph"):
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(url, json=payload, headers=headers)
                if resp.is_success:
                    print(f"[Meta Gateway] Respuesta entregada a Meta Graph API para {recipient_id}.")
                    return resp.json()
                else:
                    # Fallback to Instagram Graph endpoint
                    ig_url = "https://graph.instagram.com/v21.0/me/messages"
                    resp_ig = await client.post(ig_url, json=payload, headers=headers)
                    if resp_ig.is_success:
                        print(f"[Meta Gateway] Respuesta entregada a Instagram Graph API para {recipient_id}.")
                        return resp_ig.json()
                    print(f"[Meta Gateway] Advertencia Graph API ({resp.status_code}): {resp.text}")
                return {"status": "graph_api_error", "code": resp.status_code, "detail": resp.text}
    except Exception as e:
        print(f"[Meta Gateway] Error de conexión con Graph API: {e}")
        return {"status": "network_error", "detail": str(e)}


@router.get("/api/webhooks/meta")
def meta_webhook_verification(
    hub_mode: Optional[str] = Query(None, alias="hub.mode"),
    hub_challenge: Optional[str] = Query(None, alias="hub.challenge"),
    hub_verify_token: Optional[str] = Query(None, alias="hub.verify_token")
):
    """Meta Webhook token verification endpoint (for Facebook Messenger & Instagram Direct)."""
    expected_token = settings.meta_verify_token or "lumina_agent_token_2026"
    if hub_mode == "subscribe" and hub_verify_token == expected_token:
        print(f"[Meta Gateway] Handshake de verificación de Meta exitoso.")
        return int(hub_challenge) if hub_challenge and hub_challenge.isdigit() else hub_challenge
    raise HTTPException(status_code=403, detail="Verification token mismatch")


@router.post("/api/webhooks/meta")
@router.post("/api/webhooks/meta/")
async def meta_webhook_event(
    request: Request,
    background_tasks: BackgroundTasks,
    x_hub_signature_256: Optional[str] = Header(None, alias="X-Hub-Signature-256")
):
    """Receives Facebook Messenger & Instagram Direct events, verified with HMAC-SHA256."""
    raw_body = await request.body()

    # Verify cryptographic signature
    if settings.meta_app_secret or settings.instagram_app_secret or os.getenv("INSTAGRAM_APP_SECRET"):
        secrets = [s for s in [settings.meta_app_secret, settings.instagram_app_secret, os.getenv("INSTAGRAM_APP_SECRET")] if s]
        valid = any(verify_meta_signature(raw_body, x_hub_signature_256, sec) for sec in secrets)
        if not valid:
            print(f"[Meta Gateway] ❌ Firma X-Hub-Signature-256 inválida o adulterada ({x_hub_signature_256}).")
            raise HTTPException(status_code=403, detail="Invalid X-Hub-Signature-256 signature")
        print("[Meta Gateway] ✅ Firma HMAC-SHA256 verificada exitosamente.")
    else:
        print("[Meta Gateway] Aviso: META_APP_SECRET no configurado, omitiendo validación estricta de firma.")

    # Anti-Replay Attack Check (Mejora 4)
    if check_and_record_replay(raw_body):
        print("[Meta Gateway] ❌ Replay Attack detectado: payload idéntico recibido dentro de la ventana TTL de 15 min.")
        raise HTTPException(status_code=409, detail="Replay attack detected: duplicate webhook payload")

    try:
        payload = json.loads(raw_body.decode("utf-8"))
    except Exception:
        payload = {}

    # Check for delivery / read receipts (Mejora 18)
    for entry in payload.get("entry", []):
        for msg_ev in entry.get("messaging", []):
            if "read" in msg_ev:
                sender_id = str(msg_ev.get("sender", {}).get("id") or "")
                if sender_id:
                    db_manager.update_activity_status(sender_id, "instagram", "read")
                    db_manager.update_activity_status(sender_id, "facebook", "read")
            elif "delivery" in msg_ev:
                sender_id = str(msg_ev.get("sender", {}).get("id") or "")
                if sender_id:
                    db_manager.update_activity_status(sender_id, "instagram", "delivered")
                    db_manager.update_activity_status(sender_id, "facebook", "delivered")

    # Ingest through ReaderAgent
    omni_msg = pipeline.reader.from_meta(payload)

    if not omni_msg.raw_text:
        return {"status": "ignored_empty_or_non_message_event"}

    print(f"[Meta Gateway] Ingestando mensaje [{omni_msg.channel.upper()}] de {omni_msg.sender_id}: '{omni_msg.raw_text}'")

    # Typing indicator (Mejora 15)
    background_tasks.add_task(send_meta_typing_indicator, omni_msg.sender_id, settings.meta_access_token)

    # Critical 3-agent pipeline: Reader -> Analyzer -> Solver
    solution: SolverResponse = pipeline.process_message(omni_msg)

    # Instagram Comment to Public Reply + Private DM (Mejora 16)
    comment_id = omni_msg.metadata.get("comment_id")
    if comment_id:
        public_reply = "¡Hola! Te enviamos los detalles completos y aranceles a tu mensaje directo privado (DM) 🦷✨"
        background_tasks.add_task(reply_public_instagram_comment, comment_id, public_reply, settings.meta_access_token)

    # Dispatch to Graph API
    await dispatch_meta_graph_reply(
        recipient_id=omni_msg.sender_id,
        reply_text=solution.reply,
        access_token=settings.meta_access_token
    )

    return solution.model_dump()
