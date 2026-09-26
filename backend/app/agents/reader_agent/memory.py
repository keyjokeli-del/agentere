from typing import List, Dict, Optional
from app.core.database import db_manager, DatabaseManager


class ReaderMemory:
    """ReaderAgent Memory module: manages sliding window retrieval of conversation turns."""

    def __init__(self, db: Optional[DatabaseManager] = None) -> None:
        self.db = db or db_manager

    def get_recent_turns(
        self,
        channel: str,
        sender_id: Optional[str] = None,
        limit: int = 4,
        sender: Optional[str] = None
    ) -> List[Dict[str, str]]:
        """Retrieves the last `limit` conversation turns in chronological order."""
        target_sender = sender_id if sender_id is not None else (sender or "")
        key = f"{channel}:{target_sender}"
        conn = self.db.get_connection()
        if conn:
            try:
                with conn:
                    with conn.cursor() as cur:
                        cur.execute(
                            """
                            SELECT role, content FROM conversation_turns
                            WHERE channel = %s AND sender_id = %s
                            ORDER BY created_at DESC
                            LIMIT %s;
                            """,
                            (channel, sender_id, limit)
                        )
                        rows = cur.fetchall()
                        if rows:
                            return [{"role": r[0], "content": r[1]} for r in reversed(rows)]
            except Exception:
                pass
            finally:
                conn.close()

        # In-memory fallback
        turns = self.db.in_memory_turns.get(key, [])
        return turns[-limit:]
