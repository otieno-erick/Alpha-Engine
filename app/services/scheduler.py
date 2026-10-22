from __future__ import annotations

from typing import Any


class Scheduler:
    def __init__(self, rules: dict[str, Any] | None = None):
        self.rules = rules or {}
        self.max_slots = int((self.rules.get("scheduler.max_concurrent") or {}).get("value", 10))
        self.tasks: list[dict[str, Any]] = []

    def submit(self, name: str, source: str, slots: int = 1) -> dict[str, Any]:
        if slots < 1:
            raise ValueError("slots must be >= 1")

        active_slots = sum(task["slots"] for task in self.tasks if task["status"] == "running")
        source_slots = sum(
            task["slots"] for task in self.tasks if task["status"] == "running" and task["source"] == source
        )

        if active_slots + slots > self.max_slots:
            queued = {
                "name": name,
                "source": source,
                "slots": slots,
                "status": "queued",
                "reason": "capacity",
            }
            self.tasks.append(queued)
            return queued

        if source_slots + slots > self.max_slots:
            queued = {
                "name": name,
                "source": source,
                "slots": slots,
                "status": "queued",
                "reason": "source_budget",
            }
            self.tasks.append(queued)
            return queued

        task = {
            "name": name,
            "source": source,
            "slots": slots,
            "status": "running",
        }
        self.tasks.append(task)
        return task

    def list_tasks(self) -> list[dict[str, Any]]:
        return self.tasks


class SchedulerBudget:
    def __init__(self, rules: dict[str, Any] | None = None):
        self.max_slots = int((rules or {}).get("scheduler.max_concurrent", {}).get("value", 10))

    def budget_for(self, source: str) -> int:
        return self.max_slots
