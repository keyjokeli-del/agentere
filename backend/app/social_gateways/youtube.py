import json
from typing import Optional, Dict, Any
from fastapi import APIRouter, Request, HTTPException
import httpx

from app.config import settings
from app.agents import pipeline
from app.models.dental_models import SolverResponse

router = APIRouter(tags=["YouTube Social Gateway"])

async def publish_youtube_comment_reply(parent_id: Optional[str], reply_text: str, api_key: str) -> Dict[str, Any]:
    """Publishes a reply to a YouTube comment thread using YouTube Data API v3."""
    if not api_key:
        print(f"[YouTube Gateway] Simulación: Respuesta lista para publicar (YOUTUBE_API_KEY no configurada).")
        return {"status": "simulated", "reply": reply_text}

    if not parent_id:
        print(f"[YouTube Gateway] Advertencia: No se recibió parent_id para responder al comentario.")
        return {"status": "skipped_no_parent_id"}

    url = f"https://www.googleapis.com/youtube/v3/comments?part=snippet&key={api_key}"
    payload = {
        "snippet": {
            "parentId": parent_id,
            "textOriginal": reply_text
        }
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(url, json=payload)
            if resp.is_success:
                print(f"[YouTube Gateway] Comentario publicado con éxito en el hilo {parent_id}.")
                return resp.json()
            else:
                print(f"[YouTube Gateway] Advertencia YouTube Data API ({resp.status_code}): {resp.text}")
                return {"status": "youtube_api_error", "code": resp.status_code, "detail": resp.text}
    except Exception as e:
        print(f"[YouTube Gateway] Error conectando con YouTube Data API: {e}")
        return {"status": "network_error", "detail": str(e)}

@router.post("/api/webhooks/youtube")
@router.post("/api/webhooks/youtube/")
async def youtube_comment_webhook(request: Request):
    """Receives YouTube comment events, routes through 3-agent pipeline, and posts replies."""
    try:
        payload = await request.json()
    except Exception:
        payload = {}

    # Ingest through ReaderAgent
    omni_msg = pipeline.reader.from_youtube(payload)

    if not omni_msg.raw_text:
        return {"status": "ignored_empty_comment"}

    print(f"[YouTube Gateway] Ingestando comentario de {omni_msg.sender_name} ({omni_msg.sender_id}): '{omni_msg.raw_text}'")

    # Critical 3-agent pipeline: Reader -> Analyzer -> Solver
    solution: SolverResponse = pipeline.process_message(omni_msg)

    # Publish reply using YouTube Data API v3 (comments.insert)
    parent_comment_id = omni_msg.metadata.get("comment_id") or omni_msg.metadata.get("parent_id")
    await publish_youtube_comment_reply(
        parent_id=parent_comment_id,
        reply_text=solution.reply,
        api_key=settings.youtube_api_key
    )

    return solution.model_dump()
