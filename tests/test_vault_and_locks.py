import time
from basic_chan import DaemonlessVault


def test_vault_kv_operations(tmp_path):
    db_path = tmp_path / "vault.db"
    vault = DaemonlessVault(db_path)

    # Set and get
    vault.set("hello", {"msg": "world"})
    assert vault.get("hello") == {"msg": "world"}
    assert vault.get("missing", default=42) == 42

    # Keys listing
    assert "hello" in vault.keys()

    # Deletion
    assert vault.delete("hello") is True
    assert vault.get("hello") is None


def test_vault_ttl_expiration(tmp_path):
    db_path = tmp_path / "vault_ttl.db"
    vault = DaemonlessVault(db_path)

    vault.set("short_lived", "data", ttl_seconds=0.1)
    assert vault.get("short_lived") == "data"

    time.sleep(0.15)
    assert vault.get("short_lived") is None


def test_vault_task_leases(tmp_path):
    db_path = tmp_path / "tasks.db"
    vault = DaemonlessVault(db_path)

    vault.enqueue_task("t1", "test_domain", {"action": "scan"})
    
    # Worker 1 leases task
    task = vault.lease_task("test_domain", "worker-1", lease_seconds=10.0)
    assert task is not None
    assert task["id"] == "t1"
    assert task["payload"]["action"] == "scan"

    # Second worker cannot lease concurrently active task
    task2 = vault.lease_task("test_domain", "worker-2", lease_seconds=10.0)
    assert task2 is None

    # Worker 1 completes task
    vault.complete_task("t1", {"status": "success"})
