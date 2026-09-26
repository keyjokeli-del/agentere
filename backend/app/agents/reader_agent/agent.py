from typing import Dict, Any, List, Optional
from app.agents.reader_agent.schemas import OmniChannelMessage
from app.agents.reader_agent.memory import ReaderMemory


class ReaderAgent:
    """Agent 1: Ingests raw payloads from diverse social channels and maps to OmniChannelMessage."""

    def __init__(self, memory: Optional[Any] = None, memory_service: Optional[Any] = None) -> None:
        self.memory = memory or memory_service or ReaderMemory()

    def read(self, payload: Any, channel: str = "web", default_sender: str = "unknown") -> OmniChannelMessage:
        """Universal parser dispatching based on detected or specified channel."""
        if channel == "whatsapp":
            return self.from_whatsapp(payload if isinstance(payload, dict) else {"message": str(payload)})
        elif channel in ("facebook", "instagram"):
            return self.from_meta(payload if isinstance(payload, dict) else {"message": str(payload)}, channel=channel)
        elif channel == "youtube":
            return self.from_youtube(payload if isinstance(payload, dict) else {"message": str(payload)})
        elif isinstance(payload, dict):
            return self.from_dict(payload, channel=channel, default_sender=default_sender)
        else:
            return self.from_text(str(payload), channel=channel, sender_id=default_sender)

    def from_whatsapp(self, payload: Dict[str, Any]) -> OmniChannelMessage:
        """Parses WhatsApp payloads (Baileys service format)."""
        sender_id = str(payload.get("sender_id") or "unknown_wa").strip()
        text = str(payload.get("message") or payload.get("raw_text") or "").strip()
        sender_name = str(payload.get("sender_name") or sender_id).strip()
        history = payload.get("recent_history")
        if history is None:
            history = self.memory.get_recent_turns("whatsapp", sender_id, limit=4)
        return OmniChannelMessage(
            channel="whatsapp",
            sender_id=sender_id,
            sender_name=sender_name or "Paciente",
            raw_text=text,
            metadata=payload.get("metadata", {}),
            recent_history=history
        )

    def from_meta(self, payload: Dict[str, Any], channel: str = "facebook") -> OmniChannelMessage:
        """Parses Meta Graph API Webhooks (Messenger and Instagram Direct)."""
        entries = payload.get("entry", [])
        sender_id = "unknown_meta"
        text = ""
        metadata: Dict[str, Any] = {"object": payload.get("object", "page")}

        if payload.get("object") == "instagram":
            channel = "instagram"

        if entries and isinstance(entries, list):
            first_entry = entries[0]
            messaging = first_entry.get("messaging", [])
            if messaging and isinstance(messaging, list):
                event = messaging[0]
                sender_id = str(event.get("sender", {}).get("id") or "unknown_meta")
                msg_obj = event.get("message", {})
                text = str(msg_obj.get("text") or "").strip()
                metadata["mid"] = msg_obj.get("mid")
                metadata["recipient_id"] = event.get("recipient", {}).get("id")

        if not text:
            text = str(payload.get("message") or payload.get("text") or "").strip()
        if sender_id == "unknown_meta" and payload.get("sender_id"):
            sender_id = str(payload.get("sender_id"))

        valid_channel = channel if channel in ("facebook", "instagram") else "facebook"
        history = payload.get("recent_history")
        if history is None:
            history = self.memory.get_recent_turns(valid_channel, sender_id, limit=4)

        return OmniChannelMessage(
            channel=valid_channel,
            sender_id=sender_id,
            sender_name=str(payload.get("sender_name") or "Usuario Meta"),
            raw_text=text,
            metadata=metadata,
            recent_history=history
        )

    def from_youtube(self, payload: Dict[str, Any]) -> OmniChannelMessage:
        """Parses YouTube Comment Webhooks and Data API v3 structures."""
        snippet = payload.get("snippet", {})
        top_level = snippet.get("topLevelComment", {}).get("snippet", snippet)

        text = str(
            top_level.get("textDisplay") or
            top_level.get("textOriginal") or
            payload.get("comment") or
            payload.get("message") or
            payload.get("text") or
            ""
        ).strip()
        sender_name = str(
            top_level.get("authorDisplayName") or
            payload.get("author") or
            payload.get("sender_name") or
            "Comentarista de YouTube"
        ).strip()
        sender_id = str(
            top_level.get("authorChannelId", {}).get("value") or
            payload.get("author") or
            payload.get("sender_id") or
            "unknown_yt"
        ).strip()

        metadata = {
            "video_id": snippet.get("videoId") or payload.get("video_id"),
            "comment_id": payload.get("id") or payload.get("comment_id"),
            "parent_id": snippet.get("parentId") or payload.get("parent_id")
        }

        history = payload.get("recent_history")
        if history is None:
            history = self.memory.get_recent_turns("youtube", sender_id, limit=4)

        return OmniChannelMessage(
            channel="youtube",
            sender_id=sender_id,
            sender_name=sender_name,
            raw_text=text,
            metadata=metadata,
            recent_history=history
        )

    def from_dict(self, payload: Dict[str, Any], channel: str = "web", default_sender: str = "unknown") -> OmniChannelMessage:
        """Parses generic dictionary payloads from Webhooks or internal callers."""
        raw_text = str(payload.get("message") or payload.get("text") or payload.get("raw_text") or "").strip()
        sender_id = str(payload.get("sender_id") or default_sender).strip()
        sender_name = str(payload.get("sender_name") or "Paciente").strip()
        ch = str(payload.get("channel") or channel).lower()
        valid_ch = ch if ch in ("whatsapp", "facebook", "instagram", "youtube", "web") else "web"
        history = payload.get("recent_history")
        if history is None:
            history = self.memory.get_recent_turns(valid_ch, sender_id, limit=4)
        return OmniChannelMessage(
            channel=valid_ch,
            sender_id=sender_id,
            sender_name=sender_name,
            raw_text=raw_text,
            metadata=payload.get("metadata", {}),
            recent_history=history
        )

    def from_text(
        self,
        text: str,
        channel: str = "web",
        sender_id: str = "user-web",
        sender_name: str = "Paciente",
        recent_history: Optional[List[Dict[str, str]]] = None
    ) -> OmniChannelMessage:
        """Convenience factory for plain text messages from frontend or tests."""
        valid_ch = channel if channel in ("whatsapp", "facebook", "instagram", "youtube", "web") else "web"
        history = recent_history
        if history is None:
            history = self.memory.get_recent_turns(valid_ch, sender_id, limit=4)
        return OmniChannelMessage(
            channel=valid_ch,
            sender_id=sender_id,
            sender_name=sender_name,
            raw_text=text.strip(),
            metadata={},
            recent_history=history
        )
