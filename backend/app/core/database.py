import os
import re
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone

from app.config import settings
from app.services.embedding_service import embedding_service

try:
    import psycopg
except ImportError:
    psycopg = None  # type: ignore[assignment]


class DatabaseManager:
    """Centralized database manager for Neon PostgreSQL with pgvector and in-memory fallback."""

    def __init__(self, database_url: Optional[str] = None, in_memory_only: bool = False):
        self.in_memory_only = in_memory_only
        self.database_url = "" if in_memory_only else (database_url if database_url is not None else settings.database_url)
        self._db_available: Optional[bool] = None

        # Shared in-memory fallback stores
        self.in_memory_turns: Dict[str, List[Dict[str, str]]] = {}
        self.in_memory_knowledge: List[Dict[str, Any]] = []
        self.in_memory_patient_memories: Dict[str, List[Dict[str, Any]]] = {}

    def get_connection(self):
        """Attempts to obtain a live connection to Neon PostgreSQL."""
        if self.in_memory_only or not psycopg or not self.database_url:
            return None
        try:
            return psycopg.connect(self.database_url, connect_timeout=5)
        except Exception:
            return None

    def init_db(self) -> bool:
        """Enables pgvector extension and creates necessary tables in Neon Postgres."""
        conn = self.get_connection()
        if not conn:
            self._db_available = False
            return False

        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")

                    # 1. Short-term memory (conversation turns)
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

                    # 2. Clinical knowledge vectors (protocol FAQs, pricing, care guides)
                    cur.execute("""
                        CREATE TABLE IF NOT EXISTS clinical_knowledge_vectors (
                            id SERIAL PRIMARY KEY,
                            topic VARCHAR(150) NOT NULL UNIQUE,
                            content TEXT NOT NULL,
                            embedding vector(768),
                            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                        );
                    """)

                    # 3. Patient long-term memory vectors
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
            return True
        except Exception:
            self._db_available = False
            return False
        finally:
            conn.close()

    def seed_clinical_knowledge(self) -> int:
        """Seeds Lumina clinical catalog and post-operative care guides."""
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

        # Update in-memory fallback list
        self.in_memory_knowledge = []
        for doc in documents:
            emb = embedding_service.embed_text(doc["content"])
            self.in_memory_knowledge.append({
                "topic": doc["topic"],
                "content": doc["content"],
                "embedding": emb
            })

        conn = self.get_connection()
        if not conn:
            return len(self.in_memory_knowledge)

        count = 0
        try:
            self.init_db()
            with conn:
                with conn.cursor() as cur:
                    for doc in self.in_memory_knowledge:
                        vec_str = embedding_service.format_pgvector(doc["embedding"])
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
            return len(self.in_memory_knowledge)
        finally:
            conn.close()


db_manager = DatabaseManager()
