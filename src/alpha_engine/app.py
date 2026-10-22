from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from typing import Any, Dict

from alpha_engine.phase1 import DEFAULT_PHASE1_STATE
from alpha_engine.rules_registry import DEFAULT_RULES_REGISTRY

app = FastAPI(title="alpha-engine")


@app.get("/health")
def health() -> Dict[str, Any]:
    return {
        "status": "ok",
        "service": "alpha-engine",
        "rules_loaded": bool(DEFAULT_RULES_REGISTRY.rules),
    }


@app.get("/")
def root() -> Dict[str, Any]:
    return {"service": "alpha-engine", "status": "ready"}


@app.get("/phase1/status")
def phase1_status() -> Dict[str, Any]:
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
