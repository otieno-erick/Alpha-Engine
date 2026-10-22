from __future__ import annotations

import yaml
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
RULES_DIR = ROOT / "rules"


def load_rules() -> dict[str, dict[str, Any]]:
    merged: dict[str, dict[str, Any]] = {}
    if not RULES_DIR.exists():
        return merged

    for path in sorted(RULES_DIR.glob("*.yaml")):
        payload = yaml.safe_load(path.read_text(encoding="utf-8")) or []
        if isinstance(payload, dict):
            payload = [payload]
        if not isinstance(payload, list):
            continue

        for item in payload:
            if not isinstance(item, dict) or "id" not in item:
                continue

            merged[item["id"]] = {
                "id": item["id"],
                "value": item.get("value"),
                "source": item.get("source", ""),
                "last_verified": item.get("last_verified", ""),
            }

    return merged


def get_rule(rule_id: str, default=None):
    return load_rules().get(rule_id, default)


def is_rule_stale(rule: dict[str, Any] | None, max_days: int = 90) -> bool:
    last_verified = (rule or {}).get("last_verified")
    if not last_verified:
        return True
    return False
