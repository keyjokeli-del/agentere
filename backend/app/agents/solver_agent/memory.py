from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from app.core.database import db_manager, DatabaseManager
from app.services.embedding_service import embedding_service, EmbeddingService


class SolverMemory:
    """SolverAgent Memory module: records conversation turns and persists patient clinical memories."""

    def __init__(
        self,
        db: Optional[DatabaseManager] = None,
        embedder: Optional[EmbeddingService] = None
    ) -> None:
        self.db = db or db_manager
        self.embedder = embedder or embedding_service

    def add_turn(
        self,
        channel: str,
        sender_id: Optional[str] = None,
        role: str = "user",
        content: str = "",
        sender: Optional[str] = None
    ) -> None:
        """Records a conversation turn in Neon DB and in-memory store."""
        target_sender = sender_id if sender_id is not None else (sender or "")
        key = f"{channel}:{target_sender}"
        if key not in self.db.in_memory_turns:
            self.db.in_memory_turns[key] = []
        self.db.in_memory_turns[key].append({"role": role, "content": content})

        conn = self.db.get_connection()
        if not conn:
            return

        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        INSERT INTO conversation_turns (channel, sender_id, role, content)
                        VALUES (%s, %s, %s, %s);
                        """,
                        (channel, sender_id, role, content)
                    )
        except Exception:
            pass
        finally:
            conn.close()

    def add_patient_memory(self, sender_id: str, patient_name: Optional[str], memory_text: str) -> None:
        """Stores a persistent patient memory vectorized with 768 dimensions in Neon Postgres."""
        if not memory_text.strip():
            return

        embedding = self.embedder.embed_text(memory_text)
        vec_literal = self.embedder.format_pgvector(embedding)

        # In-memory store
        if sender_id not in self.db.in_memory_patient_memories:
            self.db.in_memory_patient_memories[sender_id] = []
        self.db.in_memory_patient_memories[sender_id].append({
            "sender_id": sender_id,
            "patient_name": patient_name or "Paciente",
            "memory_text": memory_text,
            "embedding": embedding,
            "created_at": datetime.now(timezone.utc).isoformat()
        })

        conn = self.db.get_connection()
        if not conn:
            return

        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        INSERT INTO patient_memory_vectors (sender_id, patient_name, memory_text, embedding)
                        VALUES (%s, %s, %s, %s::vector);
                        """,
                        (sender_id, patient_name or "Paciente", memory_text, vec_literal)
                    )
        except Exception:
            pass
        finally:
            conn.close()
