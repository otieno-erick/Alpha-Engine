from __future__ import annotations

from typing import Any


class BatchSplitter:
    def __init__(self, max_batch_size: int = 10):
        self.max_batch_size = max_batch_size

    def split(self, items: list[dict[str, Any]]) -> list[list[dict[str, Any]]]:
        return [items[i : i + self.max_batch_size] for i in range(0, len(items), self.max_batch_size)]

    def split_by_settings(self, items: list[dict[str, Any]]) -> list[list[dict[str, Any]]]:
        grouped: list[list[dict[str, Any]]] = []
        current: list[dict[str, Any]] = []
        current_key: tuple[Any, ...] | None = None

        for item in items:
            item_key = (
                item.get("region"),
                item.get("delay"),
                item.get("language"),
                item.get("instrumentType"),
            )
            if current and (item_key != current_key or len(current) >= self.max_batch_size):
                grouped.append(current)
                current = []
            current_key = item_key
            current.append(item)

        if current:
            grouped.append(current)
        return grouped
