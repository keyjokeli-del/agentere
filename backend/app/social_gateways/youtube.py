import time
import json
from typing import Optional, Dict, Any, List, Set
from fastapi import APIRouter, Request, HTTPException, Query, BackgroundTasks
import httpx

from app.config import settings
from app.agents import pipeline
from app.models.dental_models import SolverResponse

router = APIRouter(tags=["YouTube Social Gateway"])

# Global state for automatic polling and quota conservation
YOUTUBE_SYNC_COOLDOWN_SECONDS = 600  # 10 minutes cooldown (conserves Google Cloud Free Quota)
_last_sync_timestamp: float = 0.0
_processed_comment_ids: Set[str] = set()


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


async def sync_youtube_comments(force: bool = False) -> Dict[str, Any]:
    """
    Polls YouTube Data API v3 (commentThreads.list) for new unreplied comments.
    Enforces a strict 10-minute cooldown to respect Google Cloud Free Quota limits.
    Processes new patient inquiries through Reader -> Analyzer -> Solver agents.
    """
    global _last_sync_timestamp, _processed_comment_ids

    now = time.time()
    elapsed = now - _last_sync_timestamp

    if not force and elapsed < YOUTUBE_SYNC_COOLDOWN_SECONDS:
        remaining = int(YOUTUBE_SYNC_COOLDOWN_SECONDS - elapsed)
        return {
            "status": "cooldown_active",
            "seconds_remaining": remaining,
            "message": f"Próxima sincronización permitida en {remaining} segundos."
        }

    api_key = settings.youtube_api_key
    channel_id = settings.youtube_channel_id

    if not api_key or not channel_id:
        return {
            "status": "not_configured",
            "detail": "YOUTUBE_API_KEY o YOUTUBE_CHANNEL_ID no están configurados en el entorno."
        }

    url = "https://www.googleapis.com/youtube/v3/commentThreads"
    params = {
        "part": "snippet,replies",
        "allThreadsRelatedToChannelId": channel_id,
        "key": api_key,
        "maxResults": 20,
        "order": "time"
    }

    processed_count = 0
    errors: List[str] = []

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(url, params=params)

            if resp.status_code != 200:
                print(f"[YouTube Sync] Error consultando commentThreads ({resp.status_code}): {resp.text}")
                return {
                    "status": "api_error",
                    "code": resp.status_code,
                    "detail": resp.text
                }

            data = resp.json()
            items = data.get("items", [])

            for item in items:
                top_level = item.get("snippet", {}).get("topLevelComment", {})
                comment_id = top_level.get("id")
                snippet = top_level.get("snippet", {})

                if not comment_id:
                    continue

                # Ignore comments already processed in this runtime
                if comment_id in _processed_comment_ids:
                    continue

                author_channel = snippet.get("authorChannelId", {}).get("value", "")
                author_name = snippet.get("authorDisplayName", "Paciente YouTube")
                text = snippet.get("textOriginal") or snippet.get("textDisplay") or ""

                # Ignore comments published by the clinic channel itself
                if author_channel and author_channel == channel_id:
                    _processed_comment_ids.add(comment_id)
                    continue

                # Check if the thread already has a reply from the clinic channel
                replies = item.get("replies", {}).get("comments", [])
                already_replied = any(
                    r.get("snippet", {}).get("authorChannelId", {}).get("value") == channel_id
                    for r in replies
                )

                if already_replied:
                    _processed_comment_ids.add(comment_id)
                    continue

                # Build omni-message payload for 3-agent pipeline
                raw_payload = {
                    "snippet": {
                        "videoId": snippet.get("videoId", ""),
                        "topLevelComment": {
                            "id": comment_id,
                            "snippet": {
                                "authorDisplayName": author_name,
                                "authorChannelId": {"value": author_channel or f"yt-{author_name}"},
                                "textDisplay": text
                            }
                        }
                    }
                }

                try:
                    omni_msg = pipeline.reader.from_youtube(raw_payload)
                    if omni_msg.raw_text:
                        solution: SolverResponse = pipeline.process_message(omni_msg)
                        
                        # Post the AI response back to YouTube
                        await publish_youtube_comment_reply(
                            parent_id=comment_id,
                            reply_text=solution.reply,
                            api_key=api_key
                        )
                        processed_count += 1
                    
                    _processed_comment_ids.add(comment_id)
                except Exception as ex:
                    errors.append(f"Error procesando comentario {comment_id}: {str(ex)}")

            # Cap in-memory set to 500 items
            if len(_processed_comment_ids) > 500:
                _processed_comment_ids = set(list(_processed_comment_ids)[-300:])

            _last_sync_timestamp = time.time()
            return {
                "status": "success",
                "processed_new_comments": processed_count,
                "total_threads_checked": len(items),
                "errors": errors
            }

    except Exception as e:
        print(f"[YouTube Sync] Excepción durante la sincronización: {e}")
        return {"status": "network_exception", "detail": str(e)}


async def sync_youtube_comments_task():
    """Background task wrapper triggered opportunistically during health pings."""
    try:
        result = await sync_youtube_comments(force=False)
        if result.get("status") == "success" and result.get("processed_new_comments", 0) > 0:
            print(f"[YouTube Background Sync] {result['processed_new_comments']} comentarios respondidos por los agentes.")
    except Exception as e:
        print(f"[YouTube Background Sync] Warning: {e}")


@router.get("/api/youtube/sync")
async def manual_youtube_sync(force: bool = Query(False)):
    """Triggers or checks YouTube comment sync status."""
    return await sync_youtube_comments(force=force)


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
