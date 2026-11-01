from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
from typing import Any

from app.db import get_cached_alphas, init_db
from app.services.audit import AuditLog
from app.services.hash_cache import HashCache
from app.services.llm_hub import LLMBudgetLedger, default_provider_catalog
from app.services.quota import QuotaGuard
from app.services.rules import load_rules
from app.services.runtime_security import RuntimeSecurity
from app.services.scheduler import Scheduler
from app.services.submission import AlphaDetail

BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATES = Jinja2Templates(directory=str(BASE_DIR / "app" / "templates"))

rules = load_rules()
quota_guard = QuotaGuard(rules)
hash_cache = HashCache()
scheduler = Scheduler(rules)
audit = AuditLog()
llm_budget = LLMBudgetLedger()
managed_child_processes: dict[str, Any] = {}


@asynccontextmanager
async def lifespan(_app: FastAPI):
    try:
        yield
    finally:
        scheduler.stop_all(within_seconds=10)
        RuntimeSecurity.stop_all(managed_child_processes, timeout=10)
        managed_child_processes.clear()


app = FastAPI(title="Alpha Engine", lifespan=lifespan)


def register_child_process(name: str, process: Any) -> None:
    if not name:
        raise ValueError("Managed child processes require a name")
    if name in managed_child_processes:
        raise ValueError(f"A managed child process named {name!r} is already registered")
    managed_child_processes[name] = process

init_db()


@app.get("/", response_class=HTMLResponse)
def home():
    template = BASE_DIR / "app" / "templates" / "index.html"
    return template.read_text(encoding="utf-8")


@app.get("/health")
def health():
    return {"status": "ok", "app": "alpha-engine"}


@app.get("/api/rules")
def get_rules():
    return rules


@app.get("/api/quota")
def get_quota():
    return {"remaining": quota_guard.remaining(), "reserve": quota_guard.reserve, "used_today": 0}


@app.get("/api/alphas")
def list_cached_alphas():
    return get_cached_alphas()


@app.get("/api/alphas/{alpha_id}")
def get_alpha_detail(alpha_id: str):
    cached = get_cached_alphas()
    for candidate in cached:
        if candidate.get("alpha_id") == alpha_id:
            return AlphaDetail.from_alpha(candidate).payload()
    raise HTTPException(status_code=404, detail="Alpha not found")


@app.get("/api/llm/providers")
def get_llm_providers():
    return default_provider_catalog().list_cards()


@app.get("/api/llm/budget")
def get_llm_budget():
    return llm_budget.summary()


@app.post("/api/simulations/validate")
def validate_simulation(payload: dict):
    config = payload.get("config", {})
    cached = hash_cache.check_and_store(config)
    if cached["hit"]:
        audit.log("hash_cache_hit", {"config": config, "saved": cached["saved"]})
        return {"sent": False, "cached": True, "result": cached["result"], "saved": cached["saved"]}

    if not quota_guard.can_send(headers={"X-Ratelimit-Remaining": str(quota_guard.remaining())}):
        audit.log("quota_blocked", {"config": config, "remaining": quota_guard.remaining()})
        raise HTTPException(status_code=429, detail="Quota guard blocked the simulation request.")

    audit.log("simulation_sent", {"config": config})
    return {"sent": True, "cached": False, "config": config}


@app.post("/api/tasks")
def create_task(payload: dict):
    task_name = payload.get("name", "new-task")
    source = payload.get("source", "LLM")
    task = scheduler.submit(task_name, source, payload.get("slots", 1))
    audit.log("task_started", {"task": task_name, "source": source, "slots": payload.get("slots", 1)})
    return task


@app.get("/api/tasks")
def list_tasks():
    return scheduler.list_tasks()


@app.get("/api/audit")
def list_audit():
    return audit.list_entries()
