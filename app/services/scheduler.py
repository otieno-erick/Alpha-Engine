import time
from datetime import datetime, timezone
from typing import Any

from app.db import get_connection


class Scheduler:
    def __init__(self, rules: dict[str, Any]):
        self.rules = rules
        self.max_slots = int(rules.get("scheduler.max_concurrent", {}).get("value", 10))
        self.tasks: list[dict] = []

    def submit(self, name: str, source: str, slots: int = 1) -> dict:
        if slots < 1:
            raise ValueError("slots must be >= 1")

        active_slots = sum(item["slots"] for item in self.tasks if item["status"] == "running")
        if active_slots + slots > self.max_slots:
            return {"status": "queued", "name": name, "source": source, "slots": slots, "max_slots": self.max_slots}

        task = {
            "name": name,
            "source": source,
            "slots": slots,
            "status": "running",
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        self.tasks.append(task)
        return task

    def list_tasks(self) -> list[dict]:
        return self.tasks


class SchedulerBudget:
    def __init__(self, rules: dict[str, Any]):
        self.max_slots = int(rules.get("scheduler.max_concurrent", {}).get("value", 10))

    def budget_for(self, source: str) -> int:
        return self.max_slots

