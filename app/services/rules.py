from __future__ import annotations

from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parent.parent
RULES_DIR = ROOT / "rules"


def load_rules() -> dict:
    merged: dict[str, dict] = {}
    for path in sorted(RULES_DIR.glob("*.yaml")):
        rules = yaml.safe_load(path.read_text(encoding="utf-8")) or []
        for item in rules:
            if not isinstance(item, dict):
                continue
            if "id" not in item:
                continue
            merged[item["id"]] = {
                "id": item["id"],
                "value": item.get("value"),
                "source": item.get("source", "unknown"),
                "last_verified": item.get("last_verified", "unknown"),
            }
    return merged


def get_rule(rule_id: str, default=None):
    rules = load_rules()
    return rules.get(rule_id, default)

