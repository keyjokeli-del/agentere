from typing import Optional, List, Literal, Dict, Any
from datetime import datetime, timezone
from pydantic import BaseModel, Field


class OmniChannelMessage(BaseModel):
    """Unified inbound message schema across all communication channels."""
    channel: Literal["whatsapp", "facebook", "instagram", "youtube", "web"] = Field(
        ..., description="Canal de procedencia del mensaje"
    )
    sender_id: str = Field(..., description="Identificador único del remitente en el canal")
    sender_name: str = Field("Paciente", description="Nombre o apodo visible del paciente")
    raw_text: str = Field(..., description="Texto limpio extraído del mensaje")
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Metadatos contextuales (post_id, comment_id, message_id, etc.)"
    )
    recent_history: List[Dict[str, str]] = Field(
        default_factory=list,
        description="Historial reciente de la conversación (últimos turnos)"
    )
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="Marca temporal ISO en UTC"
    )
