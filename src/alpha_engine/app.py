from __future__ import annotations

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
