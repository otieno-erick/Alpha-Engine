from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import JSONResponse
import yaml

from alpha_engine.phase1 import DEFAULT_PHASE1_STATE

app = FastAPI(title="Alpha Engine", version="0.1.0")


def _load_rules() -> dict:
    rules_path = Path(__file__).resolve().parents[2] / "rules" / "engine_rules.yaml"
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
