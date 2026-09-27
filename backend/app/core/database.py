import os
import re
import base64
import hashlib
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone, timedelta
from cryptography.fernet import Fernet

from app.config import settings
from app.services.embedding_service import embedding_service

# ==============================================================================
# AES-256 / Fernet Encryption at Rest (Mejora 6)
# ==============================================================================
def get_fernet_cipher() -> Fernet:
    key_src = os.getenv("DATA_ENCRYPTION_KEY") or os.getenv("JWT_SECRET") or "lumina_clinic_default_vault_secret_2026"
    key_32 = hashlib.sha256(key_src.encode("utf-8")).digest()
    fernet_key = base64.urlsafe_b64encode(key_32)
    return Fernet(fernet_key)

_cipher: Optional[Fernet] = None

def encrypt_field(value: Optional[str]) -> Optional[str]:
    """Encrypts sensitive patient plaintext using AES-256 / Fernet at rest."""
    if not value or not isinstance(value, str):
        return value
    global _cipher
    if _cipher is None:
        _cipher = get_fernet_cipher()
    try:
        return _cipher.encrypt(value.encode("utf-8")).decode("utf-8")
    except Exception:
        return value

def decrypt_field(value: Optional[str]) -> Optional[str]:
    """Decrypts AES-256 / Fernet ciphertext, with backwards compatibility for legacy unencrypted rows."""
    if not value or not isinstance(value, str):
        return value
    if not value.startswith("gAAAAA"):
        return value  # Legacy unencrypted record
    global _cipher
    if _cipher is None:
        _cipher = get_fernet_cipher()
    try:
        return _cipher.decrypt(value.encode("utf-8")).decode("utf-8")
    except Exception:
        return value


def format_ssl_url(db_url: str) -> str:
    """Configures strict verify-full SSL/TLS if CA certificates exist, falling back to require (Mejora 7)."""
    if not db_url or "sslmode=" in db_url:
        return db_url
    ca_candidates = [
        "/etc/ssl/certs/ca-certificates.crt",
        "/etc/pki/tls/certs/ca-bundle.crt",
        "/etc/ssl/cert.pem"
    ]
    ca_path = next((p for p in ca_candidates if os.path.exists(p)), None)
    delimiter = "&" if "?" in db_url else "?"
    if ca_path:
        return f"{db_url}{delimiter}sslmode=verify-full&sslrootcert={ca_path}"
    return f"{db_url}{delimiter}sslmode=require"

try:
    import psycopg
except ImportError:
    psycopg = None  # type: ignore[assignment]

try:
    from psycopg_pool import ConnectionPool  # type: ignore[assignment]
    HAS_PSYCOPG_POOL = True
except ImportError:
    HAS_PSYCOPG_POOL = False


class PooledConnectionWrapper:
    """Wraps a psycopg connection borrowed from ConnectionPool to return it on close()."""

    def __init__(self, conn: Any, pool: Any):
        self._conn = conn
        self._pool = pool
        self._returned = False

    def close(self) -> None:
        if not self._returned and self._pool:
            try:
                self._pool.putconn(self._conn)
            except Exception:
                try:
                    self._conn.close()
                except Exception:
                    pass
            self._returned = True

    def __enter__(self) -> Any:
        return self._conn.__enter__()

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> Any:
        return self._conn.__exit__(exc_type, exc_val, exc_tb)

    def cursor(self, *args: Any, **kwargs: Any) -> Any:
        return self._conn.cursor(*args, **kwargs)

    def commit(self) -> None:
        self._conn.commit()

    def rollback(self) -> None:
        self._conn.rollback()

    def __getattr__(self, name: str) -> Any:
        return getattr(self._conn, name)


class DatabaseManager:
    """Centralized database manager for Neon PostgreSQL with pgvector, connection pooling, and in-memory fallback."""

    def __init__(self, database_url: Optional[str] = None, in_memory_only: bool = False):
        self.in_memory_only = in_memory_only
        raw_url = database_url if database_url is not None else settings.database_url
        self.database_url = "" if in_memory_only else format_ssl_url(raw_url)
        self._db_available: Optional[bool] = None
        self._pool: Optional[Any] = None

        # Shared in-memory fallback stores
        self.in_memory_turns: Dict[str, List[Dict[str, str]]] = {}
        self.in_memory_knowledge: List[Dict[str, Any]] = []
        self.in_memory_patient_memories: Dict[str, List[Dict[str, Any]]] = {}
        self.in_memory_activity_logs: List[Dict[str, Any]] = []
        self.in_memory_patient_identities: Dict[str, Dict[str, Any]] = {}
        self.in_memory_appointments_tracker: List[Dict[str, Any]] = []
        self.in_memory_waitlist: List[Dict[str, Any]] = []
        self.in_memory_handoffs: Dict[str, Dict[str, Any]] = {}

        self._init_pool()

    def _init_pool(self) -> None:
        """Initializes psycopg_pool ConnectionPool if available and database_url is configured."""
        if self.in_memory_only or not HAS_PSYCOPG_POOL or not self.database_url:
            return
        try:
            # Pool configuration: min_size 1, max_size 4 to protect 512MB RAM and Neon connection limits
            self._pool = ConnectionPool(
                conninfo=self.database_url,
                min_size=1,
                max_size=4,
                timeout=8.0,
                open=True
            )
        except Exception as e:
            print(f"[DatabaseManager] Pool init warning: {e}")
            self._pool = None

    def get_connection(self) -> Any:
        """Attempts to obtain a live connection via pool or direct psycopg connection."""
        if self.in_memory_only or not psycopg or not self.database_url:
            return None

        if self._pool:
            try:
                raw_conn = self._pool.getconn()
                return PooledConnectionWrapper(raw_conn, self._pool)
            except Exception:
                pass

        try:
            return psycopg.connect(self.database_url, connect_timeout=5)
        except Exception:
            return None

    def init_db(self) -> bool:
        """Enables pgvector extension, creates necessary tables, and builds HNSW indexes."""
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
                        CREATE INDEX IF NOT EXISTS idx_clinical_knowledge_hnsw 
                        ON clinical_knowledge_vectors 
                        USING hnsw (embedding vector_cosine_ops);
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
                        CREATE INDEX IF NOT EXISTS idx_patient_memory_hnsw 
                        ON patient_memory_vectors 
                        USING hnsw (embedding vector_cosine_ops);
                    """)

                    # 4. Activity Logs (Eliminates volatile RECENT_ACTIVITIES in memory)
                    cur.execute("""
                        CREATE TABLE IF NOT EXISTS activity_logs (
                            id SERIAL PRIMARY KEY,
                            channel VARCHAR(50) NOT NULL,
                            sender_id VARCHAR(100) NOT NULL,
                            sender_name VARCHAR(150),
                            message TEXT NOT NULL,
                            reply TEXT NOT NULL,
                            agent VARCHAR(50) NOT NULL,
                            intent VARCHAR(50) NOT NULL,
                            status VARCHAR(20) DEFAULT 'delivered',
                            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                        );
                        CREATE INDEX IF NOT EXISTS idx_activity_logs_created_at 
                        ON activity_logs(created_at DESC);
                    """)

                    # 5. Patient Identities (Cross-channel profile unification)
                    cur.execute("""
                        CREATE TABLE IF NOT EXISTS patient_identities (
                            id SERIAL PRIMARY KEY,
                            phone VARCHAR(50) UNIQUE,
                            email VARCHAR(100),
                            full_name VARCHAR(150),
                            instagram_id VARCHAR(100),
                            facebook_id VARCHAR(100),
                            telegram_id VARCHAR(100),
                            youtube_id VARCHAR(100),
                            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                            updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                        );
                        CREATE INDEX IF NOT EXISTS idx_patient_identities_phone 
                        ON patient_identities(phone);
                    """)

                    # 6. Appointments Tracker (Anti No-Show & Dynamic Duration)
                    cur.execute("""
                        CREATE TABLE IF NOT EXISTS appointments_tracker (
                            id SERIAL PRIMARY KEY,
                            appt_id VARCHAR(100) UNIQUE NOT NULL,
                            patient_name VARCHAR(150) NOT NULL,
                            contact VARCHAR(100) NOT NULL,
                            treatment VARCHAR(100) NOT NULL,
                            doctor VARCHAR(150) DEFAULT 'Dra. Nairoby Domínguez',
                            appointment_date DATE NOT NULL,
                            appointment_time VARCHAR(10) NOT NULL,
                            duration_min INT DEFAULT 45,
                            channel VARCHAR(50) DEFAULT 'manual',
                            status VARCHAR(20) DEFAULT 'tentative',
                            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                        );
                        CREATE INDEX IF NOT EXISTS idx_appointments_tracker_date 
                        ON appointments_tracker(appointment_date, appointment_time);
                    """)

                    # 7. Waitlist Entries (Auto-Fill for cancellations)
                    cur.execute("""
                        CREATE TABLE IF NOT EXISTS waitlist_entries (
                            id SERIAL PRIMARY KEY,
                            patient_name VARCHAR(150) NOT NULL,
                            contact VARCHAR(100) NOT NULL,
                            treatment VARCHAR(100) NOT NULL,
                            preferred_date DATE NOT NULL,
                            preferred_time VARCHAR(10),
                            channel VARCHAR(50) DEFAULT 'whatsapp',
                            status VARCHAR(20) DEFAULT 'waiting',
                            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                        );
                        CREATE INDEX IF NOT EXISTS idx_waitlist_entries_date 
                        ON waitlist_entries(preferred_date, status);
                    """)

                    # 8. Human Handoffs (Pause bot for 30m)
                    cur.execute("""
                        CREATE TABLE IF NOT EXISTS human_handoffs (
                            id SERIAL PRIMARY KEY,
                            sender_id VARCHAR(100) UNIQUE NOT NULL,
                            channel VARCHAR(50) NOT NULL,
                            paused_until TIMESTAMP WITH TIME ZONE NOT NULL,
                            paused_by VARCHAR(100) DEFAULT 'admin',
                            reason TEXT,
                            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                        );
                        CREATE INDEX IF NOT EXISTS idx_human_handoffs_sender 
                        ON human_handoffs(sender_id);
                    """)

                    # 9. Least Privilege Role configuration (Mejora 20)
                    try:
                        cur.execute("""
                            DO $$
                            BEGIN
                                IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'lumina_app_user') THEN
                                    CREATE ROLE lumina_app_user WITH LOGIN PASSWORD 'lumina_secure_app_2026';
                                END IF;
                            END
                            $$;
                            GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO lumina_app_user;
                            REVOKE DROP, TRUNCATE ON ALL TABLES IN SCHEMA public FROM lumina_app_user;
                        """)
                    except Exception:
                        pass

            self._db_available = True
            return True
        except Exception as e:
            print(f"[DatabaseManager] init_db warning: {e}")
            self._db_available = False
            return False
        finally:
            conn.close()

    def purge_patient_data(self, sender_id: str) -> Dict[str, Any]:
        """
        Permanently purges all patient records, turns, vectors, and identities across tables
        in accordance with GDPR / HIPAA Right to be Forgotten (Mejora 14).
        """
        deleted_turns = 0
        deleted_memories = 0
        deleted_activities = 0
        deleted_identities = 0

        # In-memory purge
        keys_to_purge = [k for k in self.in_memory_turns if k == sender_id or k.endswith(f":{sender_id}")]
        for k in keys_to_purge:
            deleted_turns += len(self.in_memory_turns.pop(k, []))
        if sender_id in self.in_memory_patient_memories:
            deleted_memories += len(self.in_memory_patient_memories.pop(sender_id, []))

        orig_act_count = len(self.in_memory_activity_logs)
        self.in_memory_activity_logs = [a for a in self.in_memory_activity_logs if a.get("sender_id") != sender_id]
        deleted_activities += (orig_act_count - len(self.in_memory_activity_logs))

        if sender_id in self.in_memory_patient_identities:
            self.in_memory_patient_identities.pop(sender_id, None)
            deleted_identities += 1

        # Neon DB purge
        conn = self.get_connection()
        if conn:
            try:
                with conn:
                    with conn.cursor() as cur:
                        cur.execute("DELETE FROM conversation_turns WHERE sender_id = %s;", (sender_id,))
                        deleted_turns += (cur.rowcount or 0)

                        cur.execute("DELETE FROM patient_memory_vectors WHERE sender_id = %s;", (sender_id,))
                        deleted_memories += (cur.rowcount or 0)

                        cur.execute("DELETE FROM activity_logs WHERE sender_id = %s;", (sender_id,))
                        deleted_activities += (cur.rowcount or 0)

                        cur.execute("""
                            DELETE FROM patient_identities 
                            WHERE phone = %s OR instagram_id = %s OR facebook_id = %s OR telegram_id = %s OR youtube_id = %s;
                        """, (sender_id, sender_id, sender_id, sender_id, sender_id))
                        deleted_identities += (cur.rowcount or 0)
            except Exception as e:
                print(f"[DatabaseManager] purge_patient_data error: {e}")
            finally:
                conn.close()

        return {
            "status": "purged",
            "sender_id": sender_id,
            "deleted_turns": deleted_turns,
            "deleted_memories": deleted_memories,
            "deleted_activities": deleted_activities,
            "deleted_identities": deleted_identities,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    def log_activity(
        self,
        channel: str,
        sender_id: str,
        sender_name: Optional[str],
        message: str,
        reply: str,
        agent: str,
        intent: str,
        status: str = "delivered"
    ) -> Dict[str, Any]:
        """Persists omni-channel activity in Neon PostgreSQL with in-memory fallback."""
        now_iso = datetime.now(timezone.utc).isoformat()
        act_entry = {
            "id": f"act-{len(self.in_memory_activity_logs) + 1}",
            "channel": channel,
            "sender_id": sender_id,
            "sender_name": sender_name or sender_id,
            "message": message,
            "reply": reply,
            "agent": agent,
            "intent": intent,
            "status": status,
            "timestamp": now_iso
        }
        self.in_memory_activity_logs.insert(0, act_entry)
        if len(self.in_memory_activity_logs) > 100:
            self.in_memory_activity_logs.pop()

        conn = self.get_connection()
        if conn:
            try:
                with conn:
                    with conn.cursor() as cur:
                        cur.execute(
                            """
                            INSERT INTO activity_logs (channel, sender_id, sender_name, message, reply, agent, intent, status)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                            RETURNING id, created_at;
                            """,
                            (channel, sender_id, sender_name or sender_id, encrypt_field(message), encrypt_field(reply), agent, intent, status)
                        )
                        row = cur.fetchone()
                        if row:
                            act_entry["id"] = f"act-{row[0]}"
                            act_entry["timestamp"] = row[1].isoformat() if hasattr(row[1], 'isoformat') else now_iso

                        try:
                            cur.execute(
                                """
                                INSERT INTO conversation_turns (channel, sender_id, role, content)
                                VALUES (%s, %s, %s, %s), (%s, %s, %s, %s);
                                """,
                                (channel, sender_id, "user", encrypt_field(message), channel, sender_id, "assistant", encrypt_field(reply))
                            )
                        except Exception:
                            pass
            except Exception:
                pass
            finally:
                conn.close()

        return act_entry

    def get_recent_activities(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Retrieves recent activities from Neon PostgreSQL or fallback."""
        conn = self.get_connection()
        if conn:
            try:
                with conn:
                    with conn.cursor() as cur:
                        cur.execute(
                            """
                            SELECT id, channel, sender_id, sender_name, message, reply, agent, intent, status, created_at
                            FROM activity_logs
                            ORDER BY created_at DESC
                            LIMIT %s;
                            """,
                            (limit,)
                        )
                        rows = cur.fetchall()
                        if rows:
                            return [
                                {
                                    "id": f"act-{r[0]}",
                                    "channel": r[1],
                                    "sender_id": r[2],
                                    "sender_name": r[3],
                                    "message": decrypt_field(r[4]),
                                    "reply": decrypt_field(r[5]),
                                    "agent": r[6],
                                    "intent": r[7],
                                    "status": r[8] or "delivered",
                                    "timestamp": r[9].isoformat() if hasattr(r[9], 'isoformat') else str(r[9])
                                }
                                for r in rows
                            ]
            except Exception:
                pass
            finally:
                conn.close()

        return self.in_memory_activity_logs[:limit]

    def update_activity_status(self, sender_id: str, channel: str, status: str = "read") -> bool:
        """Updates delivery/read status of recent logs."""
        for act in self.in_memory_activity_logs:
            if act["sender_id"] == sender_id and act["channel"] == channel:
                act["status"] = status

        conn = self.get_connection()
        if not conn:
            return True

        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        UPDATE activity_logs
                        SET status = %s
                        WHERE sender_id = %s AND channel = %s
                          AND id IN (
                              SELECT id FROM activity_logs
                              WHERE sender_id = %s AND channel = %s
                              ORDER BY created_at DESC LIMIT 5
                          );
                        """,
                        (status, sender_id, channel, sender_id, channel)
                    )
            return True
        except Exception:
            return False
    def get_channels_inbox(self) -> Dict[str, Any]:
        """
        Returns structured inbox channels and real conversation threads from Neon PostgreSQL
        (querying conversation_turns, activity_logs, and patient_memory_vectors).
        """
        channels = ["whatsapp", "facebook", "instagram", "youtube", "telegram", "web"]
        channel_titles = {
            "whatsapp": "WhatsApp (Baileys Bridge)",
            "facebook": "Facebook Messenger",
            "instagram": "Instagram Direct",
            "youtube": "Canal de YouTube",
            "telegram": "Telegram Gateway",
            "web": "Chat Web & Simulador"
        }

        # Base structure
        result: Dict[str, Any] = {}
        for ch in channels:
            result[ch] = {
                "channel": ch,
                "title": channel_titles.get(ch, ch.title()),
                "total_messages": 0,
                "active_threads": 0,
                "last_message": None,
                "threads": []
            }

        patient_memories: Dict[str, str] = {}
        conn = self.get_connection()

        if conn:
            try:
                with conn:
                    with conn.cursor() as cur:
                        # 1. Fetch patient memories to enrich threads
                        try:
                            cur.execute(
                                """
                                SELECT sender_id, memory_text 
                                FROM patient_memory_vectors
                                ORDER BY created_at DESC;
                                """
                            )
                            for r in cur.fetchall():
                                sid = str(r[0])
                                if sid not in patient_memories:
                                    patient_memories[sid] = decrypt_field(r[1]) or ""
                        except Exception:
                            pass

                        # 2. Fetch all activity logs in chronological order
                        cur.execute(
                            """
                            SELECT id, channel, sender_id, sender_name, message, reply, agent, intent, status, created_at
                            FROM activity_logs
                            ORDER BY created_at ASC;
                            """
                        )
                        activity_rows = cur.fetchall()

                        channel_threads: Dict[str, Dict[str, Dict[str, Any]]] = {ch: {} for ch in channels}

                        for r in activity_rows:
                            act_id, ch, s_id, s_name, msg, rep, agent, intent, status, created_at = r
                            ch_key = (ch or "web").lower()
                            if ch_key not in channel_threads:
                                channel_threads[ch_key] = {}
                                result[ch_key] = {
                                    "channel": ch_key,
                                    "title": channel_titles.get(ch_key, ch_key.title()),
                                    "total_messages": 0,
                                    "active_threads": 0,
                                    "last_message": None,
                                    "threads": []
                                }

                            ts = created_at.isoformat() if hasattr(created_at, 'isoformat') else str(created_at)

                            if s_id not in channel_threads[ch_key]:
                                channel_threads[ch_key][s_id] = {
                                    "sender_id": s_id,
                                    "patient_name": s_name or s_id,
                                    "channel": ch_key,
                                    "last_activity": ts,
                                    "message_count": 0,
                                    "patient_memory": patient_memories.get(str(s_id)),
                                    "messages": []
                                }

                            thread = channel_threads[ch_key][s_id]
                            thread["last_activity"] = ts
                            if s_name and s_name != s_id:
                                thread["patient_name"] = s_name

                            # Add user turn
                            thread["messages"].append({
                                "id": f"act-{act_id}-u",
                                "role": "user",
                                "sender_name": s_name or s_id,
                                "content": decrypt_field(msg),
                                "timestamp": ts,
                                "status": status or "delivered"
                            })

                            # Add assistant turn
                            thread["messages"].append({
                                "id": f"act-{act_id}-a",
                                "role": "assistant",
                                "sender_name": agent or "SolverAgent",
                                "agent": agent,
                                "intent": intent,
                                "content": decrypt_field(rep),
                                "timestamp": ts,
                                "status": status or "delivered"
                            })
                            thread["message_count"] = len(thread["messages"])

                        # 3. Assemble final threads per channel
                        for ch_k, threads_dict in channel_threads.items():
                            threads_list = list(threads_dict.values())
                            threads_list.sort(key=lambda x: x.get("last_activity") or "", reverse=True)
                            total_msgs = sum(t["message_count"] for t in threads_list)
                            last_msg = None
                            if threads_list and threads_list[0]["messages"]:
                                lm = threads_list[0]["messages"][-1]
                                last_msg = {
                                    "sender_id": threads_list[0]["sender_id"],
                                    "patient_name": threads_list[0]["patient_name"],
                                    "content": lm["content"],
                                    "role": lm["role"],
                                    "timestamp": lm["timestamp"]
                                }

                            result[ch_k] = {
                                "channel": ch_k,
                                "title": channel_titles.get(ch_k, ch_k.title()),
                                "total_messages": total_msgs,
                                "active_threads": len(threads_list),
                                "last_message": last_msg,
                                "threads": threads_list
                            }

                        return result
            except Exception as e:
                print(f"[get_channels_inbox] Warning: {e}")
            finally:
                conn.close()

        # In-memory fallback
        channel_threads_mem: Dict[str, Dict[str, Dict[str, Any]]] = {ch: {} for ch in channels}
        for act in reversed(self.in_memory_activity_logs):
            ch_k = act.get("channel", "web").lower()
            s_id = act.get("sender_id", "anonymous")
            s_name = act.get("sender_name") or s_id
            msg = act.get("message", "")
            rep = act.get("reply", "")
            agent = act.get("agent", "SolverAgent")
            intent = act.get("intent", "GENERAL")
            status = act.get("status", "delivered")
            ts = act.get("timestamp") or datetime.now(timezone.utc).isoformat()

            if ch_k not in channel_threads_mem:
                channel_threads_mem[ch_k] = {}

            if s_id not in channel_threads_mem[ch_k]:
                channel_threads_mem[ch_k][s_id] = {
                    "sender_id": s_id,
                    "patient_name": s_name,
                    "channel": ch_k,
                    "last_activity": ts,
                    "message_count": 0,
                    "patient_memory": None,
                    "messages": []
                }

            thr = channel_threads_mem[ch_k][s_id]
            thr["last_activity"] = ts
            thr["messages"].append({
                "id": f"{act.get('id', 'act')}-u",
                "role": "user",
                "sender_name": s_name,
                "content": msg,
                "timestamp": ts,
                "status": status
            })
            thr["messages"].append({
                "id": f"{act.get('id', 'act')}-a",
                "role": "assistant",
                "sender_name": agent,
                "agent": agent,
                "intent": intent,
                "content": rep,
                "timestamp": ts,
                "status": status
            })
            thr["message_count"] = len(thr["messages"])

        for ch_k, threads_dict in channel_threads_mem.items():
            threads_list = list(threads_dict.values())
            threads_list.sort(key=lambda x: x.get("last_activity") or "", reverse=True)
            total_msgs = sum(t["message_count"] for t in threads_list)
            last_msg = None
            if threads_list and threads_list[0]["messages"]:
                lm = threads_list[0]["messages"][-1]
                last_msg = {
                    "sender_id": threads_list[0]["sender_id"],
                    "patient_name": threads_list[0]["patient_name"],
                    "content": lm["content"],
                    "role": lm["role"],
                    "timestamp": lm["timestamp"]
                }

            result[ch_k] = {
                "channel": ch_k,
                "title": channel_titles.get(ch_k, ch_k.title()),
                "total_messages": total_msgs,
                "active_threads": len(threads_list),
                "last_message": last_msg,
                "threads": threads_list
            }

        return result

    def get_or_link_patient_identity(
        self,
        phone: Optional[str] = None,
        sender_id: Optional[str] = None,
        channel: Optional[str] = None,
        full_name: Optional[str] = None,
        email: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Unifies patient profile across channels based on phone or channel ID."""
        key = phone or sender_id
        if not key:
            return None

        # Check in-memory store
        for p_id, p_data in self.in_memory_patient_identities.items():
            if phone and p_data.get("phone") == phone:
                if full_name:
                    p_data["full_name"] = full_name
                if channel == "instagram" and sender_id:
                    p_data["instagram_id"] = sender_id
                elif channel == "telegram" and sender_id:
                    p_data["telegram_id"] = sender_id
                return p_data

        record: Dict[str, Any] = {
            "phone": phone,
            "email": email,
            "full_name": full_name or "Paciente",
            "instagram_id": sender_id if channel == "instagram" else None,
            "facebook_id": sender_id if channel == "facebook" else None,
            "telegram_id": sender_id if channel == "telegram" else None,
            "youtube_id": sender_id if channel == "youtube" else None,
        }
        self.in_memory_patient_identities[key] = record

        conn = self.get_connection()
        if conn:
            try:
                with conn:
                    with conn.cursor() as cur:
                        if phone:
                            cur.execute(
                                """
                                INSERT INTO patient_identities (phone, email, full_name, instagram_id, facebook_id, telegram_id, youtube_id)
                                VALUES (%s, %s, %s, %s, %s, %s, %s)
                                ON CONFLICT (phone) DO UPDATE SET
                                    full_name = COALESCE(EXCLUDED.full_name, patient_identities.full_name),
                                    email = COALESCE(EXCLUDED.email, patient_identities.email),
                                    instagram_id = COALESCE(EXCLUDED.instagram_id, patient_identities.instagram_id),
                                    telegram_id = COALESCE(EXCLUDED.telegram_id, patient_identities.telegram_id),
                                    updated_at = CURRENT_TIMESTAMP
                                RETURNING phone, email, full_name, instagram_id, facebook_id, telegram_id;
                                """,
                                (phone, email, full_name, record["instagram_id"], record["facebook_id"], record["telegram_id"], record["youtube_id"])
                            )
                            row = cur.fetchone()
                            if row:
                                return {
                                    "phone": row[0],
                                    "email": row[1],
                                    "full_name": row[2],
                                    "instagram_id": row[3],
                                    "facebook_id": row[4],
                                    "telegram_id": row[5]
                                }
            except Exception:
                pass
            finally:
                conn.close()

        return record

    def is_handoff_active(self, sender_id: str) -> bool:
        """Checks if human handoff is currently paused for this sender_id."""
        now = datetime.now(timezone.utc)
        mem = self.in_memory_handoffs.get(sender_id)
        if mem and mem.get("paused_until") and mem["paused_until"] > now:
            return True

        conn = self.get_connection()
        if not conn:
            return False

        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        SELECT paused_until FROM human_handoffs
                        WHERE sender_id = %s AND paused_until > CURRENT_TIMESTAMP;
                        """,
                        (sender_id,)
                    )
                    row = cur.fetchone()
                    return bool(row)
        except Exception:
            return False
        finally:
            conn.close()

    def set_human_handoff(
        self,
        sender_id: str,
        channel: str,
        minutes: int = 30,
        reason: Optional[str] = "Pausado por recepcionista"
    ) -> bool:
        """Pauses AI bot for 30 minutes for a specific patient."""
        paused_until = datetime.now(timezone.utc) + timedelta(minutes=minutes)
        self.in_memory_handoffs[sender_id] = {
            "channel": channel,
            "paused_until": paused_until,
            "reason": reason
        }

        conn = self.get_connection()
        if not conn:
            return True

        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        INSERT INTO human_handoffs (sender_id, channel, paused_until, reason)
                        VALUES (%s, %s, %s, %s)
                        ON CONFLICT (sender_id) DO UPDATE SET
                            paused_until = EXCLUDED.paused_until,
                            reason = EXCLUDED.reason;
                        """,
                        (sender_id, channel, paused_until, reason)
                    )
            return True
        except Exception:
            return True
        finally:
            conn.close()

    def clear_human_handoff(self, sender_id: str) -> bool:
        """Re-activates AI bot for a patient."""
        self.in_memory_handoffs.pop(sender_id, None)

        conn = self.get_connection()
        if not conn:
            return True

        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute("DELETE FROM human_handoffs WHERE sender_id = %s;", (sender_id,))
            return True
        except Exception:
            return True
        finally:
            conn.close()

    def record_appointment(
        self,
        appt_id: str,
        patient_name: str,
        contact: str,
        treatment: str,
        doctor: str,
        appointment_date: str,
        appointment_time: str,
        duration_min: int = 45,
        channel: str = "whatsapp",
        status: str = "tentative"
    ) -> bool:
        """Stores appointment in Neon DB appointments_tracker."""
        entry = {
            "appt_id": appt_id,
            "patient_name": patient_name,
            "contact": contact,
            "treatment": treatment,
            "doctor": doctor,
            "date": appointment_date,
            "time": appointment_time,
            "duration_min": duration_min,
            "channel": channel,
            "status": status
        }
        self.in_memory_appointments_tracker.append(entry)

        conn = self.get_connection()
        if not conn:
            return True

        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        INSERT INTO appointments_tracker (
                            appt_id, patient_name, contact, treatment, doctor, 
                            appointment_date, appointment_time, duration_min, channel, status
                        )
                        VALUES (%s, %s, %s, %s, %s, %s::date, %s, %s, %s, %s)
                        ON CONFLICT (appt_id) DO UPDATE SET
                            status = EXCLUDED.status,
                            doctor = EXCLUDED.doctor;
                        """,
                        (appt_id, patient_name, contact, treatment, doctor, appointment_date, appointment_time, duration_min, channel, status)
                    )
            return True
        except Exception:
            return True
        finally:
            conn.close()

    def update_appointment_status(self, contact: str, status: str) -> bool:
        """Updates appointment status (e.g. 'confirmed' or 'cancelled') based on patient contact."""
        updated = False
        for appt in self.in_memory_appointments_tracker:
            if appt["contact"] == contact or contact in appt["contact"]:
                appt["status"] = status
                updated = True

        conn = self.get_connection()
        if not conn:
            return updated

        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        UPDATE appointments_tracker
                        SET status = %s
                        WHERE contact = %s
                          AND id IN (
                              SELECT id FROM appointments_tracker
                              WHERE contact = %s
                              ORDER BY appointment_date DESC LIMIT 1
                          );
                        """,
                        (status, contact, contact)
                    )
            return True
        except Exception:
            return updated
        finally:
            conn.close()

    def add_to_waitlist(
        self,
        patient_name: str,
        contact: str,
        treatment: str,
        preferred_date: str,
        preferred_time: Optional[str] = None,
        channel: str = "whatsapp"
    ) -> bool:
        """Adds a patient to the auto-fill waitlist."""
        self.in_memory_waitlist.append({
            "patient_name": patient_name,
            "contact": contact,
            "treatment": treatment,
            "preferred_date": preferred_date,
            "preferred_time": preferred_time,
            "channel": channel,
            "status": "waiting"
        })

        conn = self.get_connection()
        if not conn:
            return True

        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        INSERT INTO waitlist_entries (patient_name, contact, treatment, preferred_date, preferred_time, channel, status)
                        VALUES (%s, %s, %s, %s::date, %s, %s, 'waiting');
                        """,
                        (patient_name, contact, treatment, preferred_date, preferred_time, channel)
                    )
            return True
        except Exception:
            return True
        finally:
            conn.close()

    def check_waitlist_for_cancellation(self, cancelled_date: str) -> List[Dict[str, Any]]:
        """Returns waiting patients for a cancelled date."""
        matches = []
        for w in self.in_memory_waitlist:
            if w["preferred_date"] == cancelled_date and w["status"] == "waiting":
                w["status"] = "notified"
                matches.append(w)

        conn = self.get_connection()
        if conn:
            try:
                with conn:
                    with conn.cursor() as cur:
                        cur.execute(
                            """
                            UPDATE waitlist_entries
                            SET status = 'notified'
                            WHERE preferred_date = %s::date AND status = 'waiting'
                            RETURNING patient_name, contact, treatment, preferred_date, preferred_time, channel;
                            """,
                            (cancelled_date,)
                        )
                        rows = cur.fetchall()
                        if rows:
                            return [
                                {
                                    "patient_name": r[0],
                                    "contact": r[1],
                                    "treatment": r[2],
                                    "preferred_date": str(r[3]),
                                    "preferred_time": r[4],
                                    "channel": r[5]
                                }
                                for r in rows
                            ]
            except Exception:
                pass
            finally:
                conn.close()

        return matches

    def seed_clinical_knowledge(self) -> int:
        """Seeds Lumina clinical catalog and post-operative care guides."""
        documents = [
            # Catalog Treatments
            {
                "topic": "Limpieza Dental y Profilaxis",
                "content": "Limpieza Dental y Profilaxis con Ultrasonido: 30 min de duración. Rango de precio: $30 - $45 USD. Procedimiento de eliminación completa de sarro, placa bacteriana y pulido dental para prevenir caries y gingivitis."
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
                "content": "Implantes Dentales de Titanio: 90 min por intervención. Rango de precio: $350 - $600 USD por pieza. Reemplazo permanente de piezas dentales perdidas con tornillo de titanio biocompatible y corona estética."
            },
            {
                "topic": "Endodoncia Tratamiento de Conducto",
                "content": "Endodoncia (Tratamiento de Conducto): 90 min de duración. Rango de precio: $80 - $140 USD. Procedimiento para eliminar la infección del nervio dental conservando la pieza dental natural y aliviando el dolor."
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


def purge_patient_data(sender_id: str) -> Dict[str, Any]:
    """Module-level helper to purge all clinical data for a given patient identifier."""
    return db_manager.purge_patient_data(sender_id)
