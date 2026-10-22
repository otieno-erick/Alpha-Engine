from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Any


@dataclass
class Task:
    name: str
    source: str
    core_allocation: int = 1
    status: str = "queued"


class TaskScheduler:
    def __init__(self, max_slots: int = 10):
        self.max_slots = max_slots
        self.active_tasks: List[Task] = []

    def register_task(self, task: Task) -> None:
        self.active_tasks.append(task)

    def has_capacity(self) -> bool:
        return len(self.active_tasks) <= self.max_slots

    def task_count(self) -> int:
        return len(self.active_tasks)

    def summary(self) -> Dict[str, Any]:
        return {"max_slots": self.max_slots, "active_tasks": len(self.active_tasks), "task_count": len(self.active_tasks)}


DEFAULT_TASK_SCHEDULER = TaskScheduler()
