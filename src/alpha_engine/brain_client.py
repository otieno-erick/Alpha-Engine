from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Optional


@dataclass
class BrainEndpoint:
    name: str
    path: str
    method: str = "GET"
    source: str = "ace_lib.py" 
    verified_date: str = "2026-10-22"


@dataclass
class BrainEndpointCatalog:
    endpoints: Dict[str, BrainEndpoint] = field(
        default_factory=lambda: {
            "authentication": BrainEndpoint("authentication", "/authentication", "POST"),
            "list_alphas": BrainEndpoint("list_alphas", "/alphas", "GET"),
            "alpha_detail": BrainEndpoint("alpha_detail", "/alphas/{alpha_id}", "GET"),
            "check_submission": BrainEndpoint("check_submission", "/alphas/{alpha_id}/check", "GET"),
            "prod_correlation": BrainEndpoint("prod_correlation", "/alphas/{alpha_id}/correlations/prod", "GET"),
            "self_correlation": BrainEndpoint("self_correlation", "/alphas/{alpha_id}/correlations/self", "GET"),
            "simulations": BrainEndpoint("simulations", "/simulations", "POST"),
            "simulations_detail": BrainEndpoint("simulations_detail", "/simulations/{simulation_id}", "GET"),
            "simulation_progress": BrainEndpoint("simulation_progress", "/simulations/{simulation_id}", "GET"),
        }
    )

    def get(self, name: str) -> Optional[BrainEndpoint]:
        return self.endpoints.get(name)

    def list_names(self) -> Iterable[str]:
        return self.endpoints.keys()


DEFAULT_BRAIN_ENDPOINTS = BrainEndpointCatalog()

