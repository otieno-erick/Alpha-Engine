from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class Task:
    name: str
    source: str
    core_allocation: int = 1
    status: str = "queued"


@dataclass
class TaskScheduler:
    max_slots: int = 10
    active_tasks: List[Task] = field(default_factory=list)
    task_sources: Dict[str, float] = field(
        default_factory=lambda: {
            "LLM": 0.35,
            "Evolution": 0.25,
            "PowerPool": 0.15,
            "ATOM": 0.10,
            "Template": 0.08,
            "Sampler": 0.04,
            "CorrBreaker": 0.03,
        }
    )

    def register_task(self, task: Task) -> None:
        self.active_tasks.append(task)

    def task_count(self) -> int:
        return len(self.active_tasks)

    def has_capacity(self) -> bool:
        return self.task_count() <= self.max_slots

    def stop_task(self, task_name: str) -> str:
        self.active_tasks = [task for task in self.active_tasks if task.name != task_name]
        return task_name

    def summary(self) -> Dict[str, Any]:
        return {
            "max_slots": self.max_slots,
            "active_tasks": len(self.active_tasks),
            "task_names": [task.name for task in self.active_tasks],
            "task_sources": self.task_sources,
        }


DEFAULT_TASK_SCHEDULER = TaskScheduler()
