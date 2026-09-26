import os
import re
import json
import math
import hashlib
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

import httpx
from app.config import settings

try:
    import psycopg
except ImportError:
    psycopg = None


class RAGMemoryService:
    """Hybrid Memory Service with Vector RAG in Neon PostgreSQL (pgvector).
    
    Anti-OOM Constraint:
    - 0 MB memory footprint: No PyTorch, sentence-transformers, FAISS or ChromaDB.
    - Embeddings generated via Google Gemini API (models/text-embedding-004, 768 dim).
    - Fully resilient: Deterministic hashing fallback for offline, tests, or missing keys.
    """

    def __init__(
        self,
        database_url: Optional[str] = None,
        gemini_api_key: Optional[str] = None,
        in_memory_only: bool = False
    ):
        self.in_memory_only = in_memory_only
        self.database_url = "" if in_memory_only else (database_url if database_url is not None else settings.database_url)
        self.gemini_api_key = "" if in_memory_only else (gemini_api_key if gemini_api_key is not None else settings.gemini_api_key)
        
        # In-memory stores for ultra-fast fallback & offline tests
        self._in_memory_turns: Dict[str, List[Dict[str, str]]] = {}
        self._in_memory_knowledge: List[Dict[str, Any]] = []
        self._in_memory_patient_memories: Dict[str, List[Dict[str, Any]]] = {}
        
        self._db_initialized = False
        self._db_available: Optional[bool] = None

    def _get_connection(self):
        """Attempts to obtain a live connection to Neon PostgreSQL."""
        if self.in_memory_only or not psycopg or not self.database_url:
            return None
        try:
            conn = psycopg.connect(self.database_url, connect_timeout=5)
            return conn
        except Exception as e:
            return None


    def init_db(self) -> bool:
        """Enables pgvector extension and creates necessary tables in Neon Postgres."""
        conn = self._get_connection()
        if not conn:
            self._db_available = False
            return False

        try:
            with conn:
                with conn.cursor() as cur:
                    # 1. Enable pgvector extension
                    cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")

                    # 2. Conversation turns (short-term memory)
                    cur.execute("""
                        CREATE TABLE IF NOT EXISTS conversation_turns (
                            id SERIAL PRIMARY KEY,
                            channel VARCHAR(50) NOT NULL,
                            sender_id VARCHAR(100) NOT NULL,
                            role VARCHAR(20) NOT NULL,
                            content TEXT NOT NULL,
                            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                        );
                        CREATE INDEX IF NOT EXISTS idx_turns_channel_sender 
                        ON conversation_turns(channel, sender_id, created_at DESC);
                    """)

                    # 3. Clinical knowledge vectors (protocol FAQs, pricing, care guides)
                    cur.execute("""
                        CREATE TABLE IF NOT EXISTS clinical_knowledge_vectors (
                            id SERIAL PRIMARY KEY,
                            topic VARCHAR(150) NOT NULL UNIQUE,
                            content TEXT NOT NULL,
                            embedding vector(768),
                            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                        );
                    """)

                    # 4. Patient memory vectors (long-term patient memory)
                    cur.execute("""
                        CREATE TABLE IF NOT EXISTS patient_memory_vectors (
                            id SERIAL PRIMARY KEY,
                            sender_id VARCHAR(100) NOT NULL,
                            patient_name VARCHAR(150),
                            memory_text TEXT NOT NULL,
                            embedding vector(768),
                            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                        );
                        CREATE INDEX IF NOT EXISTS idx_patient_memories_sender 
                        ON patient_memory_vectors(sender_id, created_at DESC);
                    """)
            self._db_available = True
            self._db_initialized = True
            return True
        except Exception as e:
            self._db_available = False
            return False
        finally:
            conn.close()

    def embed_text(self, text: str) -> List[float]:
        """Generates 768-dim normalized embedding.
        Uses Google Gemini text-embedding-004 API when GEMINI_API_KEY is available.
        Otherwise falls back to deterministic token-hashing embedding.
        """
        clean_text = (text or "").strip()
        if not clean_text:
            return self._deterministic_hash_embedding("empty")

        if self.gemini_api_key:
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/text-embedding-004:embedContent?key={self.gemini_api_key}"
                payload = {
                    "model": "models/text-embedding-004",
                    "content": {"parts": [{"text": clean_text[:2048]}]}
                }
                with httpx.Client(timeout=6.0) as client:
                    resp = client.post(url, json=payload)
                    if resp.status_code == 200:
                        data = resp.json()
                        vals = data.get("embedding", {}).get("values")
                        if vals and len(vals) == 768:
                            return [float(v) for v in vals]
            except Exception:
                pass

        return self._deterministic_hash_embedding(clean_text)

    def _deterministic_hash_embedding(self, text: str, dim: int = 768) -> List[float]:
        """Ultra-fast, deterministic 768-dim normalized vector with 0 MB RAM footprint."""
        vec = [0.0] * dim
        tokens = re.findall(r"\w+", text.lower())
        if not tokens:
            tokens = ["empty"]

        for token in tokens:
            h_sha = int(hashlib.sha256(token.encode("utf-8")).hexdigest()[:8], 16)
            h_md5 = int(hashlib.md5(token.encode("utf-8")).hexdigest()[:8], 16)
            vec[h_sha % dim] += 1.0
            vec[h_md5 % dim] += 0.5
            
            # Subword 3-grams for lexical similarity boost
            if len(token) > 3:
                for i in range(len(token) - 2):
                    ngram = token[i:i+3]
                    h_ng = int(hashlib.md5(ngram.encode("utf-8")).hexdigest()[:6], 16)
                    vec[h_ng % dim] += 0.3

        norm = math.sqrt(sum(x * x for x in vec))
        if norm > 0:
            return [x / norm for x in vec]
        vec[0] = 1.0
        return vec

    def _format_vector(self, embedding: List[float]) -> str:
        """Formats python list as pgvector literal string '[v1,v2,...]'."""
        return "[" + ",".join(f"{x:.6f}" for x in embedding) + "]"

    # --------------------------------------------------------------------------
    # 1. Short-Term Memory: Conversation Turns
    # --------------------------------------------------------------------------
    def add_turn(self, channel: str, sender_id: str, role: str, content: str) -> None:
        """Records a conversation turn in Neon DB and in-memory store."""
        key = f"{channel}:{sender_id}"
        if key not in self._in_memory_turns:
            self._in_memory_turns[key] = []
        self._in_memory_turns[key].append({"role": role, "content": content})

        conn = self._get_connection()
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

    def get_recent_turns(self, channel: str, sender_id: str, limit: int = 4) -> List[Dict[str, str]]:
        """Retrieves the last `limit` conversation turns in chronological order."""
        key = f"{channel}:{sender_id}"
        conn = self._get_connection()
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
                            # Reverse so oldest turns come first chronologically
                            return [{"role": r[0], "content": r[1]} for r in reversed(rows)]
            except Exception:
                pass
            finally:
                conn.close()

        # In-memory fallback
        turns = self._in_memory_turns.get(key, [])
        return turns[-limit:]

    # --------------------------------------------------------------------------
    # 2. Vector RAG: Clinical Knowledge
    # --------------------------------------------------------------------------
    def search_clinical_knowledge(self, query_text: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Searches clinical knowledge vectors using cosine distance (<=>)."""
        query_vec = self.embed_text(query_text)
        vec_literal = self._format_vector(query_vec)

        conn = self._get_connection()
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
        if not self._in_memory_knowledge:
            self.seed_clinical_knowledge()

        results = []
        q_words = set(re.findall(r"\w+", query_text.lower()))

        for item in self._in_memory_knowledge:
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

    # --------------------------------------------------------------------------
    # 3. Vector RAG: Patient Long-Term Memory
    # --------------------------------------------------------------------------
    def add_patient_memory(self, sender_id: str, patient_name: Optional[str], memory_text: str) -> None:
        """Stores a persistent patient memory vectorized with 768 dimensions."""
        if not memory_text.strip():
            return

        embedding = self.embed_text(memory_text)
        vec_literal = self._format_vector(embedding)

        # In-memory store
        if sender_id not in self._in_memory_patient_memories:
            self._in_memory_patient_memories[sender_id] = []
        self._in_memory_patient_memories[sender_id].append({
            "sender_id": sender_id,
            "patient_name": patient_name or "Paciente",
            "memory_text": memory_text,
            "embedding": embedding,
            "created_at": datetime.now(timezone.utc).isoformat()
        })

        conn = self._get_connection()
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

    def search_patient_memories(self, sender_id: str, query_text: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Retrieves relevant past memories for a specific patient."""
        query_vec = self.embed_text(query_text)
        vec_literal = self._format_vector(query_vec)

        conn = self._get_connection()
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
        memories = self._in_memory_patient_memories.get(sender_id, [])
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

    # --------------------------------------------------------------------------
    # 4. Seeding Clinical Knowledge (Catalog + Post-Op Care)
    # --------------------------------------------------------------------------
    def seed_clinical_knowledge(self) -> int:
        """Seeds Lumina clinical treatments, pricing, and post-operative care guides."""
        documents = [
            # Catalog Treatments
            {
                "topic": "Limpieza Dental y Profilaxis",
                "content": "Limpieza Dental y Profilaxis con Ultrasonido: 45 min de duración. Rango de precio: $30 - $45 USD. Procedimiento de eliminación completa de sarro, placa bacteriana y pulido dental para prevenir caries y gingivitis."
            },
            {
                "topic": "Blanqueamiento Dental LED",
                "content": "Blanqueamiento Dental LED: 60 min de duración. Rango de precio: $90 - $150 USD. Procedimiento estético seguro que aclara hasta 4 tonos en una sola sesión sin dañar el esmalte dental."
            },
            {
                "topic": "Ortodoncia Brackets y Alineadores",
                "content": "Ortodoncia (Brackets Metálicos, Estéticos e Invisibles): Duración de consulta: 45 min. Evaluación diagnóstica sin costo inicial. Planes de financiamiento desde $40 USD/mes. Corrección de mordida y alineación dental."
            },
            {
                "topic": "Implantes Dentales de Titanio",
                "content": "Implantes Dentales de Titanio: 60 min por intervención. Rango de precio: $350 - $600 USD por pieza. Reemplazo permanente de piezas dentales perdidas con tornillo de titanio biocompatible y corona estética."
            },
            {
                "topic": "Endodoncia Tratamiento de Conducto",
                "content": "Endodoncia (Tratamiento de Conducto): 60 min de duración. Rango de precio: $80 - $140 USD. Procedimiento para eliminar la infección del nervio dental conservando la pieza dental natural y aliviando el dolor."
            },
            {
                "topic": "Extracción Simple y Muelas del Juicio",
                "content": "Extracción Simple y Muelas del Juicio: 45 min de duración. Rango de precio: $35 - $90 USD. Procedimiento indoloro con anestesia local para retirar piezas muy deterioradas o terceros molares retenidos."
            },
            # Post-Op Care & Emergency Guides
            {
                "topic": "Cuidados Post-Extracción y Muelas del Juicio",
                "content": "Cuidados Postoperatorios de Extracción y Cirugía de Muelas del Juicio: 1) Mantener la gasa estéril mordida firmemente durante 45 minutos. 2) No escupir, no usar popote/sorbete ni enjuagarse la boca las primeras 24 horas para preservar el coágulo y evitar alveolitis. 3) Aplicar hielo indirecto en la mejilla las primeras 24-48 horas. 4) Dieta blanda y fría o templada; evitar irritantes, picantes y semillas. 5) Cero tabaco y alcohol por 7 días."
            },
            {
                "topic": "Cuidados Post-Blanqueamiento Dental",
                "content": "Cuidados Postoperatorios de Blanqueamiento Dental: Seguir una 'dieta blanca' estricta durante 48 a 72 horas. Evitar café, té, mate, vino tinto, salsas con colorantes, refrescos oscuros y tabaco. Si aparece sensibilidad dental transitoria, utilizar pasta desensibilizante y evitar bebidas excesivamente heladas o calientes."
            },
            {
                "topic": "Cuidados Post-Implantes Dentales",
                "content": "Cuidados Postoperatorios de Implantes Dentales: No masticar del lado intervenido durante la primera semana. Cepillado muy suave con cepillo quirúrgico sin tocar directamente los puntos de sutura. Evitar esfuerzos físicos intensos durante 5 a 7 días. Acudir puntualmente al retiro de puntos y revisiones de osteointegración."
            },
            {
                "topic": "Cuidados Post-Endodoncia",
                "content": "Cuidados Postoperatorios de Endodoncia: Es normal una leve molestia a la presión o masticación durante 48 a 72 horas. Evitar masticar alimentos duros o pegajosos con la pieza tratada hasta que tenga colocada su corona o restauración definitiva para prevenir fracturas."
            },
            {
                "topic": "Protocolo de Urgencias y Dolor Agudo",
                "content": "Protocolo de Urgencias y Dolor Agudo: Si el paciente presenta dolor pulsátil intenso, hinchazón facial evidente, sangrado continuo o traumatismo, se considera urgencia prioritaria atendida en el día (09:00 a 19:00). Nunca automedicarse con antibióticos sin diagnóstico presencial en consultorio."
            },
            {
                "topic": "Políticas de Citas y Seguros",
                "content": "Políticas Generales de Citas y Seguros: Atendemos de lunes a sábado de 09:00 a 19:00. Las citas pueden reprogramarse con al menos 4 horas de anticipación sin costo. Trabajamos con las principales aseguradoras médicas y ofrecemos planes en cuotas sin interés."
            }
        ]

        # Sync to in-memory store
        self._in_memory_knowledge = []
        for doc in documents:
            emb = self.embed_text(doc["content"])
            self._in_memory_knowledge.append({
                "topic": doc["topic"],
                "content": doc["content"],
                "embedding": emb
            })

        # Try to seed in Neon PostgreSQL
        conn = self._get_connection()
        count = 0
        if conn:
            try:
                self.init_db()
                with conn:
                    with conn.cursor() as cur:
                        for doc in self._in_memory_knowledge:
                            vec_str = self._format_vector(doc["embedding"])
                            cur.execute(
                                """
                                INSERT INTO clinical_knowledge_vectors (topic, content, embedding)
                                VALUES (%s, %s, %s::vector)
                                ON CONFLICT (topic) 
                                DO UPDATE SET content = EXCLUDED.content, embedding = EXCLUDED.embedding;
                                """,
                                (doc["topic"], doc["content"], vec_str)
                            )
                            count += 1
                return count
            except Exception:
                pass
            finally:
                conn.close()

        return len(self._in_memory_knowledge)


# Global singleton instance
rag_memory_service = RAGMemoryService()
