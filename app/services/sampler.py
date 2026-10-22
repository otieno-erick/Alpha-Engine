from __future__ import annotations

from typing import Any


class SettingSampler:
    """Simple grid sampler for neutralization, decay, truncation, and other settings."""

    def generate_grid(
        self,
        base: dict[str, Any],
        *,
        neutralization: list[str] | None = None,
        decay: list[int] | None = None,
        truncation: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        neutralization = neutralization or ["RAM", "None"]
        decay = decay or [1, 2]
        truncation = truncation or ["none", "trim"]

        grid: list[dict[str, Any]] = []
        for neutral in neutralization:
            for decay_value in decay:
                for trunc in truncation:
                    item = dict(base)
                    item["neutralization"] = neutral
                    item["decay"] = decay_value
                    item["truncation"] = trunc
                    grid.append(item)
        return grid
