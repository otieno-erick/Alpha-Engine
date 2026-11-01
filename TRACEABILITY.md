from app.db import get_cached_alphas, init_db
from app.services.audit import AuditLog
from app.services.hash_cache import HashCache
from app.services.quota import QuotaGuard
from app.services.rules import load_rules
from app.services.scheduler import Scheduler


def test_scheduler_stop_all_stops_running_tasks():
    scheduler = Scheduler(load_rules())
    scheduler.submit("alpha-a", "LLM", 2)
    scheduler.submit("alpha-b", "Evolution", 3)
    scheduler.submit("alpha-c", "LLM", 2)

    stopped = scheduler.stop_all(within_seconds=10)
    assert len(stopped) == 3
    assert all(task["status"] == "stopped" for task in stopped)
    assert all(task.get("stopped_within_seconds") == 10 for task in stopped)


# existing tests remain below


def test_rules_loader_loads_yaml():
    rules = load_rules()
    assert "quota.reserve" in rules
    assert rules["quota.reserve"]["value"] == 10
    assert "source" in rules["quota.reserve"]
    assert "last_verified" in rules["quota.reserve"]


def test_hash_cache_detects_duplicate_config():
    cache = HashCache()
    config = {"region": "USA", "universe": "TOP3000", "delay": 1, "regular": "rank(x)"}
    first = cache.check_and_store(config)
    second = cache.check_and_store(config)
    assert first["hit"] is False
    assert second["hit"] is True
    assert second["saved"] is True


def test_hash_changes_when_any_setting_changes():
    cache = HashCache()
    left = {"region": "USA", "universe": "TOP3000", "delay": 1, "regular": "rank(x)"}
    right = {"region": "USA", "universe": "TOP3000", "delay": 1, "regular": "rank(x) + 1"}
    assert cache._hash_config(left) != cache._hash_config(right)


def test_quota_guard_blocks_zero_remaining():
    rules = load_rules()
    guard = QuotaGuard(rules)
    guard.set_remaining(0)
    assert guard.can_send({"X-Ratelimit-Remaining": "0"}, requested=1) is False


def test_quota_guard_respects_reserve():
    rules = load_rules()
    guard = QuotaGuard(rules)
    guard.set_remaining(10)
    assert guard.can_send({"X-Ratelimit-Remaining": "10"}, requested=1) is False


def test_quota_reads_x_ratelimit_remaining():
    rules = load_rules()
    guard = QuotaGuard(rules)
    assert guard.can_send({"X-Ratelimit-Remaining": "50"}, requested=1) is True


def test_scheduler_uses_shared_slot_limit():
    rules = load_rules()
    scheduler = Scheduler(rules)
    result_a = scheduler.submit("alpha-a", "LLM", 5)
    result_b = scheduler.submit("alpha-b", "Evolution", 6)
    assert result_a["status"] == "running"
    assert result_b["status"] == "queued"


def test_scheduler_enforces_source_budget():
    rules = load_rules()
    scheduler = Scheduler(rules)
    first = scheduler.submit("task-a", "LLM", 6)
    second = scheduler.submit("task-b", "LLM", 5)
    assert first["status"] == "running"
    assert second["status"] == "queued"


def test_audit_log_records_user_actions():
    audit = AuditLog()
    entry = audit.log("simulation_sent", {"count": 1})
    assert entry["action"] == "simulation_sent"
    assert "count" in entry["detail"]


def test_app_loads_cached_alphas_offline(tmp_path, monkeypatch):
    db_path = tmp_path / "alpha_engine.db"
    monkeypatch.setattr("app.db.DB_PATH", db_path)
    init_db()

    conn = __import__("sqlite3").connect(db_path)
    conn.execute(
        "INSERT INTO alpha_cache (alpha_id, dataset, status, expression, created_at) VALUES (?, ?, ?, ?, datetime('now'))",
        ("A-100", "USA_EQ", "pending", "rank(x)"),
    )
    conn.commit()
    conn.close()

    rows = get_cached_alphas()
    assert len(rows) == 1
    assert rows[0]["alpha_id"] == "A-100"
    assert rows[0]["dataset"] == "USA_EQ"
    assert rows[0]["status"] == "pending"
