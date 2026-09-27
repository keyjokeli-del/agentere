from typing import Optional, List, Literal, Dict, Any
from datetime import datetime, timezone
from pydantic import BaseModel, Field, ConfigDict


class OmniChannelMessage(BaseModel):
    """Unified inbound message schema across all communication channels with Pydantic V2 hardening."""
    model_config = ConfigDict(str_strip_whitespace=True)

    channel: Literal["whatsapp", "facebook", "instagram", "youtube", "web", "telegram"] = Field(
        ..., description="Canal de procedencia del mensaje"
    )
    sender_id: str = Field(..., max_length=150, description="Identificador único del remitente en el canal")
    sender_name: str = Field("Paciente", max_length=150, description="Nombre o apodo visible del paciente")
    raw_text: str = Field(..., max_length=1000, description="Texto limpio extraído del mensaje (máx 1000 caracteres)")
    media_type: Optional[str] = Field(None, max_length=50, description="Tipo de medio si aplica ('audio', 'image', None)")
    is_prompt_injection: bool = Field(
        False,
        description="Indica si se detectó un intento de Jailbreak / Prompt Injection"
    )
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
