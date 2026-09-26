import re
from typing import List, Dict, Any, Optional
from app.core.database import db_manager, DatabaseManager
from app.services.embedding_service import embedding_service, EmbeddingService


class AnalyzerMemory:
    """AnalyzerAgent Memory: searches clinical knowledge and patient history using pgvector cosine distance."""

    def __init__(
        self,
        db: Optional[DatabaseManager] = None,
        embedder: Optional[EmbeddingService] = None
    ) -> None:
        self.db = db or db_manager
        self.embedder = embedder or embedding_service

    def search_clinical_knowledge(self, query_text: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Searches clinical knowledge vectors using cosine distance (<=>)."""
        query_vec = self.embedder.embed_text(query_text)
        vec_literal = self.embedder.format_pgvector(query_vec)

        conn = self.db.get_connection()
        if conn:
            try:
                with conn:
                    with conn.cursor() as cur:
                        cur.execute(
                            """
                            SELECT topic, content, (1 - (embedding <=> %s::vector)) AS similarity
                            FROM clinical_knowledge_vectors
                            ORDER BY embedding <=> %s::vector ASC
                            LIMIT %s;
                            """,
                            (vec_literal, vec_literal, top_k)
                        )
                        rows = cur.fetchall()
                        if rows:
                            return [
                                {
                                    "topic": r[0],
                                    "content": r[1],
                                    "similarity": round(float(r[2]), 4) if r[2] is not None else 0.0
                                }
                                for r in rows
                            ]
            except Exception:
                pass
            finally:
                conn.close()

        # In-memory fallback with cosine similarity & lexical match boost
        if not self.db.in_memory_knowledge:
            self.db.seed_clinical_knowledge()

        results = []
        q_words = set(re.findall(r"\w+", query_text.lower()))

        for item in self.db.in_memory_knowledge:
            item_vec = item["embedding"]
            dot = sum(a * b for a, b in zip(query_vec, item_vec))
            # Lexical keyword boost
            content_lower = item["content"].lower() + " " + item["topic"].lower()
            overlap = sum(1 for w in q_words if w in content_lower)
            score = dot + (overlap * 0.15)
            results.append({
                "topic": item["topic"],
                "content": item["content"],
                "similarity": round(score, 4)
            })

        results.sort(key=lambda x: x["similarity"], reverse=True)
        return results[:top_k]

    def search_patient_memories(self, sender_id: str, query_text: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Retrieves relevant past memories for a specific patient."""
        query_vec = self.embedder.embed_text(query_text)
        vec_literal = self.embedder.format_pgvector(query_vec)

        conn = self.db.get_connection()
        if conn:
            try:
                with conn:
                    with conn.cursor() as cur:
                        cur.execute(
                            """
                            SELECT patient_name, memory_text, (1 - (embedding <=> %s::vector)) AS similarity
                            FROM patient_memory_vectors
                            WHERE sender_id = %s
                            ORDER BY embedding <=> %s::vector ASC
                            LIMIT %s;
                            """,
                            (vec_literal, sender_id, vec_literal, top_k)
                        )
                        rows = cur.fetchall()
                        if rows:
                            return [
                                {
                                    "sender_id": sender_id,
                                    "patient_name": r[0],
                                    "memory_text": r[1],
                                    "similarity": round(float(r[2]), 4) if r[2] is not None else 0.0
                                }
                                for r in rows
                            ]
            except Exception:
                pass
            finally:
                conn.close()

        # In-memory fallback
        memories = self.db.in_memory_patient_memories.get(sender_id, [])
        if not memories:
            return []

        results = []
        q_words = set(re.findall(r"\w+", query_text.lower()))

        for item in memories:
            item_vec = item["embedding"]
            dot = sum(a * b for a, b in zip(query_vec, item_vec))
            mem_lower = item["memory_text"].lower()
            overlap = sum(1 for w in q_words if w in mem_lower)
            score = dot + (overlap * 0.15)
            results.append({
                "sender_id": sender_id,
                "patient_name": item["patient_name"],
                "memory_text": item["memory_text"],
                "similarity": round(score, 4)
            })

        results.sort(key=lambda x: x["similarity"], reverse=True)
        return results[:top_k]
