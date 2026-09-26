import os
import time
import tempfile
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.core.database import db_manager
from app.core.cleanup import cleanup_manager, RuntimeCleanupManager

client = TestClient(app)


def test_in_memory_cache_pruning():
    """Validates that in-memory cache pruning prevents unbounded memory growth (>100 users)."""
    manager = RuntimeCleanupManager(max_cached_users=10)

    # Populate 25 user keys in fallback turns and patient memories
    for i in range(25):
        db_manager.in_memory_turns[f"channel_test:user_{i}"] = [{"role": "user", "content": f"msg {i}"}]
        db_manager.in_memory_patient_memories[f"user_{i}"] = [{"memory_text": f"fact {i}"}]

    assert len(db_manager.in_memory_turns) >= 25
    assert len(db_manager.in_memory_patient_memories) >= 25

    # Run pruning
    stats = manager.prune_in_memory_caches()

    assert stats["turns_keys_pruned"] >= 15
    assert stats["memories_keys_pruned"] >= 15
    assert len(db_manager.in_memory_turns) <= 10
    assert len(db_manager.in_memory_patient_memories) <= 10


def test_temp_file_purge():
    """Validates that orphaned temporary files are removed during cleanup."""
    manager = RuntimeCleanupManager(max_temp_file_age_sec=1)
    temp_dir = tempfile.gettempdir()
    dummy_file = os.path.join(temp_dir, "lumina_test_purge.tmp")

    with open(dummy_file, "w") as f:
        f.write("temporary buffer test")

    assert os.path.exists(dummy_file)

    # Artificially age the file
    old_time = time.time() - 100
    os.utime(dummy_file, (old_time, old_time))

    removed = manager.purge_temp_files()
    assert removed >= 1
    assert not os.path.exists(dummy_file)


def test_perform_cleanup_and_gc():
    """Validates full cleanup execution including gc.collect() and cooldown throttling."""
    manager = RuntimeCleanupManager(max_cached_users=50)

    # First run (forced)
    res1 = manager.perform_cleanup(force=True)
    assert res1["status"] == "completed"
    assert "gc_objects_collected" in res1
    assert "pruned_stats" in res1

    # Second immediate run without force should throttle cooldown
    res2 = manager.perform_cleanup(force=False)
    assert res2["status"] == "skipped_interval"


def test_admin_cleanup_endpoint():
    """Validates FastAPI endpoint POST /api/admin/cleanup rejects unauthorized calls and accepts valid keys."""
    # 1. Unauthorized request without header -> 403 Forbidden
    unauthorized_res = client.post("/api/admin/cleanup")
    assert unauthorized_res.status_code == 403
    assert "Forbidden" in unauthorized_res.json()["detail"]

    # 2. Authorized request with valid X-Admin-Key -> 200 OK
    headers = {"X-Admin-Key": "lumina_admin_2026"}
    response = client.post("/api/admin/cleanup", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "completed"
    assert "gc_objects_collected" in data
