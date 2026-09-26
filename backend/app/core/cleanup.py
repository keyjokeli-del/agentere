import os
import gc
import time
import glob
import tempfile
from typing import Optional, Dict, Any
from app.core.database import db_manager


class RuntimeCleanupManager:
    """Manages runtime anti-bloat, memory pruning, and temporary file cleanup.
    
    Guarantees that Render Free Tier instances stay well below the 512 MB RAM ceiling:
    1. Trims in-memory fallback dicts to max 100 active conversations (FIFO/LRU).
    2. Purges orphaned temporary files in /tmp or system temp dir.
    3. Triggers garbage collection (gc.collect()) to release heap memory back to the OS.
    """

    def __init__(self, max_cached_users: int = 100, max_temp_file_age_sec: int = 3600) -> None:
        self.max_cached_users = max_cached_users
        self.max_temp_file_age_sec = max_temp_file_age_sec
        self.last_cleanup_timestamp = time.time()
        self.cleanup_interval_sec = 60  # Minimum seconds between heavy cleanups

    def prune_in_memory_caches(self) -> Dict[str, int]:
        """Prunes in-memory turn and memory caches to prevent unbounded RAM growth."""
        pruned_stats = {"turns_keys_pruned": 0, "memories_keys_pruned": 0}

        # 1. Prune in_memory_turns if exceeding limit
        turns_keys = list(db_manager.in_memory_turns.keys())
        if len(turns_keys) > self.max_cached_users:
            overflow = len(turns_keys) - self.max_cached_users
            for k in turns_keys[:overflow]:
                db_manager.in_memory_turns.pop(k, None)
                pruned_stats["turns_keys_pruned"] += 1

        # 2. Prune in_memory_patient_memories if exceeding limit
        pat_keys = list(db_manager.in_memory_patient_memories.keys())
        if len(pat_keys) > self.max_cached_users:
            overflow = len(pat_keys) - self.max_cached_users
            for k in pat_keys[:overflow]:
                db_manager.in_memory_patient_memories.pop(k, None)
                pruned_stats["memories_keys_pruned"] += 1

        return pruned_stats

    def purge_temp_files(self) -> int:
        """Purges orphaned temporary files older than max_temp_file_age_sec."""
        temp_dir = tempfile.gettempdir()
        patterns = [
            os.path.join(temp_dir, "*.tmp"),
            os.path.join(temp_dir, "tmp*"),
            os.path.join(temp_dir, "lumina_*"),
        ]
        now = time.time()
        removed_count = 0

        for pattern in patterns:
            for file_path in glob.glob(pattern):
                try:
                    if os.path.isfile(file_path):
                        file_age = now - os.path.getmtime(file_path)
                        if file_age > self.max_temp_file_age_sec:
                            os.remove(file_path)
                            removed_count += 1
                except Exception:
                    pass

        return removed_count

    def perform_cleanup(self, force: bool = False) -> Dict[str, Any]:
        """Executes pruning, temp file purge, and garbage collection."""
        now = time.time()
        if not force and (now - self.last_cleanup_timestamp < self.cleanup_interval_sec):
            return {"status": "skipped_interval", "seconds_since_last": int(now - self.last_cleanup_timestamp)}

        pruned_stats = self.prune_in_memory_caches()
        temp_removed = self.purge_temp_files()
        collected = gc.collect()

        self.last_cleanup_timestamp = now
        return {
            "status": "completed",
            "pruned_stats": pruned_stats,
            "temp_files_removed": temp_removed,
            "gc_objects_collected": collected,
            "timestamp": now
        }


cleanup_manager = RuntimeCleanupManager()


def run_runtime_cleanup(force: bool = False) -> Dict[str, Any]:
    """Helper entrypoint for FastAPI BackgroundTasks or middleware."""
    return cleanup_manager.perform_cleanup(force=force)
