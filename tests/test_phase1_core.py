from app.services.hash_cache import HashCache
from app.services.quota import QuotaGuard
from app.services.scheduler import Scheduler
from app.services.rules import load_rules


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
    from app.services.audit import AuditLog

    audit = AuditLog()
    entry = audit.log("simulation_sent", {"count": 1})
    assert entry["action"] == "simulation_sent"
    assert "count" in entry["detail"]

