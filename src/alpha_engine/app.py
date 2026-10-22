<<<<<<< Updated upstream
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass
class RepairInstruction:
    failure: str
    action: str
    priority: int


class Diagnoser:
    def __init__(self):
        self.mapping = {
            "turnover_floor": RepairInstruction("turnover_floor", "increase turnover or reduce turnover floor risk", 1),
            "is_ladder": RepairInstruction("is_ladder", "adjust IS ladder and turnover assumptions", 2),
            "correlation": RepairInstruction("correlation", "change dataset, region, or delta structure", 3),
            "fitness": RepairInstruction("fitness", "rework operator settings and weights", 4),
        }

    def diagnose(self, checks: List[Dict[str, Any]]) -> Dict[str, Any]:
        for check in checks:
            if not check.get("passed", True):
                failure = check.get("name")
                instruction = self.mapping.get(failure, RepairInstruction(failure, "review configuration", 999))
                return {
                    "first_failure": failure,
                    "action": instruction.action,
                    "priority": instruction.priority,
                    "margin": check.get("margin", 0.0),
                }
        return {"first_failure": None, "action": "no repair required", "priority": 0, "margin": 0.0}


DEFAULT_DIAGNOSER = Diagnoser()
=======
﻿from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import JSONResponse
import yaml

from alpha_engine.brain_client import DEFAULT_BRAIN_ENDPOINTS
from alpha_engine.phase1 import DEFAULT_PHASE1_STATE
from alpha_engine.rules_registry import DEFAULT_RULES_REGISTRY
from alpha_engine.validator import DEFAULT_VALIDATOR
from alpha_engine.scorer import DEFAULT_SCORER

app = FastAPI(title="Alpha Engine", version="0.1.0")


def _load_rules() -> dict:
    rules_path = Path(__file__).resolve().parents[1] / "rules" / "engine_rules.yaml"
    with rules_path.open("r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}
    return data


@app.get("/")
def root() -> dict:
    return {"service": "alpha-engine", "status": "ready"}


@app.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "service": "alpha-engine",
        "rules_loaded": bool(_load_rules()),
    }


@app.get("/rules")
def read_rules() -> JSONResponse:
    return JSONResponse(content=_load_rules())


@app.get("/phase1/status")
def phase1_status() -> dict:
    return DEFAULT_PHASE1_STATE.status()


@app.get("/phase2/status")
def phase2_status() -> dict:
    return {
        "brain_endpoints": sorted(DEFAULT_BRAIN_ENDPOINTS.list_names()),
        "rules_registry": {
            "stale": DEFAULT_RULES_REGISTRY.has_stale_rules(),
            "conflicts": DEFAULT_RULES_REGISTRY.unresolved_conflicts(),
        },
        "validator": "ready",
        "scorer": "ready",
        "diagnoser": "ready",
    }


@app.get("/phase2/validate")
def phase2_validate(expression: str = "alpha_1 + beta_2") -> dict:
    result = DEFAULT_VALIDATOR.validate_expression(expression)
    return {"valid": result.valid, "errors": result.errors}


@app.get("/phase2/score")
def phase2_score() -> dict:
    result = DEFAULT_SCORER.score_alpha({"turnover": 0.30, "sharpe": 1.80, "correlation": 0.50, "fitness": 0.10})
    return {
        "checks": [check.__dict__ for check in result],
        "clean": DEFAULT_SCORER.clean_alpha({"turnover": 0.30, "sharpe": 1.80, "correlation": 0.50, "fitness": 0.10}),
    }
>>>>>>> Stashed changes
