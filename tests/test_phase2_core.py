from alpha_engine.hash_cache import HashCache
from alpha_engine.quota import QuotaLedger
from alpha_engine.scheduler import Task, TaskScheduler


def test_hash_cache_rejects_duplicates():
    cache = HashCache()
    config = {"expression": "alpha_1", "region": "ALL"}
    first = cache.set(config, "alpha-123")
    second = cache.set(config, "alpha-456")
    assert first == second
    assert cache.get(config) == "alpha-123"
    assert cache.has_duplicate(config) is True


def test_quota_respects_reserve():
    quota = QuotaLedger(reserve=5, remaining_quota=10)
    assert quota.can_spend() is True
    assert quota.spend("LLM", 6) is False
    assert quota.remaining_quota == 10


def test_scheduler_slots_are_capped():
    scheduler = TaskScheduler(max_slots=2)
    scheduler.register_task(Task(name="task-1", source="LLM"))
    scheduler.register_task(Task(name="task-2", source="Evolution"))
    assert scheduler.has_capacity() is True
    scheduler.register_task(Task(name="task-3", source="ATOM"))
    assert scheduler.task_count() == 3
    assert scheduler.has_capacity() is False
