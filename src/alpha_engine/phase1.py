from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict

from alpha_engine.auth import AuthService, DEFAULT_AUTH_SERVICE
from alpha_engine.hash_cache import HashCache, DEFAULT_HASH_CACHE
from alpha_engine.quota import QuotaLedger, DEFAULT_QUOTA_LEDGER
from alpha_engine.scheduler import Task, TaskScheduler, DEFAULT_TASK_SCHEDULER
from alpha_engine.sync import SyncService, DEFAULT_SYNC_SERVICE


@dataclass
class Phase1State:
    auth_service: AuthService = DEFAULT_AUTH_SERVICE
    sync_service: SyncService = DEFAULT_SYNC_SERVICE
    hash_cache: HashCache = DEFAULT_HASH_CACHE
    scheduler: TaskScheduler = DEFAULT_TASK_SCHEDULER
    quota: QuotaLedger = DEFAULT_QUOTA_LEDGER

    def status(self) -> Dict[str, Any]:
        return {
            "auth": {"authenticated": self.auth_service.session.authenticated, "username": self.auth_service.session.username},
            "sync": {"region": self.sync_service.region, "field_count": self.sync_service.field_count},
            "hash_cache_size": len(self.hash_cache.entries),
            "scheduler": self.scheduler.summary(),
            "quota": self.quota.summary(),
        }


DEFAULT_PHASE1_STATE = Phase1State()
