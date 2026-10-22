from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path

from app.services.audit import AuditLog
from app.services.hash_cache import HashCache
from app.services.quota import QuotaGuard
from app.services.rules import load_rules
from app.services.scheduler import Scheduler

app = FastAPI(title="Alpha Engine")

BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATES = Jinja2Templates(directory=str(BASE_DIR / "app" / "templates"))

rules = load_rules()
quota_guard = QuotaGuard(rules)
hash_cache = HashCache()
scheduler = Scheduler(rules)
audit = AuditLog()


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

