import hmac
import hashlib
import json
from typing import Optional, Dict, Any
from fastapi import APIRouter, Request, HTTPException, Query, Header
import httpx

from app.config import settings
from app.agents import pipeline
from app.models.dental_models import SolverResponse

router = APIRouter(tags=["Meta Social Gateway"])

def verify_meta_signature(raw_body: bytes, signature_header: Optional[str], app_secret: str) -> bool:
    """Verifies the X-Hub-Signature-256 header sent by Meta using HMAC-SHA256."""
    if not app_secret:
        # Dev / fallback mode when secret is not configured
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

async def dispatch_meta_graph_reply(recipient_id: str, reply_text: str, access_token: str) -> Dict[str, Any]:
    """Dispatches outgoing reply via Meta Graph API (Messenger / Instagram Direct)."""
    if not access_token:
        print(f"[Meta Gateway] Simulación: Mensaje listo para {recipient_id} (META_ACCESS_TOKEN no configurado).")
        return {"status": "simulated", "recipient_id": recipient_id}

    url = "https://graph.facebook.com/v19.0/me/messages"
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
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(url, json=payload, headers=headers)
            if resp.is_success:
                print(f"[Meta Gateway] Respuesta entregada a Meta Graph API para {recipient_id}.")
                return resp.json()
            else:
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
    x_hub_signature_256: Optional[str] = Header(None, alias="X-Hub-Signature-256")
):
    """Receives Facebook Messenger & Instagram Direct events, verified with HMAC-SHA256."""
    raw_body = await request.body()

    # Verify cryptographic signature
    if settings.meta_app_secret:
        if not verify_meta_signature(raw_body, x_hub_signature_256, settings.meta_app_secret):
            print("[Meta Gateway] ❌ Firma X-Hub-Signature-256 inválida o adulterada.")
            raise HTTPException(status_code=403, detail="Invalid X-Hub-Signature-256 signature")
    else:
        print("[Meta Gateway] Aviso: META_APP_SECRET no configurado, omitiendo validación estricta de firma.")

    try:
        payload = json.loads(raw_body.decode("utf-8"))
    except Exception:
        payload = {}

    # Ingest through ReaderAgent
    omni_msg = pipeline.reader.from_meta(payload)

    if not omni_msg.raw_text:
        return {"status": "ignored_empty_or_non_message_event"}

    print(f"[Meta Gateway] Ingestando mensaje [{omni_msg.channel.upper()}] de {omni_msg.sender_id}: '{omni_msg.raw_text}'")

    # Critical 3-agent pipeline: Reader -> Analyzer -> Solver
    solution: SolverResponse = pipeline.process_message(omni_msg)

    # Dispatch to Graph API
    await dispatch_meta_graph_reply(
        recipient_id=omni_msg.sender_id,
        reply_text=solution.reply,
        access_token=settings.meta_access_token
    )

    return solution.model_dump()
