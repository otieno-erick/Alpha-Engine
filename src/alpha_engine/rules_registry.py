from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml


RULES_PATH = Path(__file__).resolve().parents[1] / "rules" / "phase2_rules.yaml"
 Stashed changes


@dataclass
class RuleRecord:
    key: str
    value: Any
    source: str
    last_verified: str
    tier: Optional[str] = None
    delay: Optional[str] = None
    region: Optional[str] = None
    universe: Optional[str] = None


class RulesRegistry:
    def __init__(self, rules_path: Optional[Path] = None):
        self.rules_path = rules_path or RULES_PATH
        self.rules = self._load_rules()

    def _load_rules(self) -> Dict[str, Any]:
        with self.rules_path.open("r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh) or {}
        return data

    def lookup(self, *, key: str, tier: str = "user", delay: str = "D0", region: str = "USA", universe: str = "TOP") -> Any:
        rules = self.rules.get("rules", {})
        candidates = rules.get(key, [])
        for item in candidates:
            if item.get("tier") == tier and item.get("delay") == delay and item.get("region") == region and item.get("universe") == universe:
                return item.get("value")
        for item in candidates:
            if item.get("tier") == tier and item.get("delay") == delay and item.get("region") == region and item.get("universe") in (None, "ALL"):
                return item.get("value")
        for item in candidates:
            if item.get("tier") == tier and item.get("delay") == delay and item.get("region") in (None, "ALL") and item.get("universe") == universe:
                return item.get("value")
        for item in candidates:
            if item.get("tier") == tier and item.get("delay") == delay:
                return item.get("value")
        raise KeyError(f"Rule not found for key={key}, tier={tier}, delay={delay}, region={region}, universe={universe}")

    def has_stale_rules(self, stale_after_days: int = 90) -> List[str]:
        stale = []
        cutoff = datetime.now() - timedelta(days=stale_after_days)
        for key, items in self.rules.get("rules", {}).items():
            for item in items:
                last_verified = item.get("last_verified")
                if not last_verified:
                    stale.append(key)
                    continue
                try:
                    if datetime.strptime(last_verified, "%Y-%m-%d") < cutoff:
                        stale.append(key)
                except ValueError:
                    stale.append(key)
        return stale

    def unresolved_conflicts(self) -> List[str]:
        conflicts = []
        for key, items in self.rules.get("rules", {}).items():
            seen = set()
            for item in items:
                if item.get("value") is None:
                    continue
                tag = (item.get("tier"), item.get("delay"), item.get("region"), item.get("universe"))
                if tag in seen:
                    conflicts.append(key)
                    break
                seen.add(tag)
        return conflicts


DEFAULT_RULES_REGISTRY = RulesRegistry()

