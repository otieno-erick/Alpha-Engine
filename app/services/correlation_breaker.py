from __future__ import annotations

from typing import Any


class CorrelationBreaker:
    """Minimal structured correlation repair generator."""

    def __init__(self):
        self.allowed_variants = [
            "RAM neutralization",
            "trade_when trigger",
            "Fast D1 delta",
            "dataset change",
            "region change",
        ]

    def generate_variants(self, alpha: dict[str, Any], *, reason: str = "correlation") -> list[dict[str, Any]]:
        base = dict(alpha)
        base["reason"] = reason
        variants: list[dict[str, Any]] = []
        for variant_type in self.allowed_variants:
            candidate = dict(base)
            candidate["variant_type"] = variant_type
            candidate["settings"] = dict(base.get("settings", {}))
            if variant_type == "RAM neutralization":
                candidate["settings"]["neutralization"] = "RAM"
            elif variant_type == "trade_when trigger":
                candidate["settings"]["trade_when"] = "signal > 0"
            elif variant_type == "Fast D1 delta":
                candidate["settings"]["delay"] = "D1"
            elif variant_type == "dataset change":
                candidate["settings"]["dataset"] = f"{base.get('dataset', 'USA_EQ')}-alt"
            elif variant_type == "region change":
                candidate["settings"]["region"] = "ASI"
            variants.append(candidate)
        return variants
