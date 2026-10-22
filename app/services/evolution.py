from __future__ import annotations

from typing import Any


class EvolutionLab:
    """Minimal Evolution Lab baseline for Phase 5 testing.

    It supports seed selection, mutation generation, and a simple validator gate
    for candidate mutants before they are considered for evolution.
    """

    def __init__(self, validator: Any | None = None):
        self.validator = validator or self._default_validator

    def _default_validator(self, candidate: dict[str, Any]) -> bool:
        checks = candidate.get("checks", [])
        return isinstance(checks, list) and all(bool(item.get("passed", False)) for item in checks)

    def select_seeds(self, candidates: list[dict[str, Any]], *, limit: int = 3) -> list[dict[str, Any]]:
        selected = [candidate for candidate in candidates if candidate.get("status") == "ready"]
        return selected[:limit]

    def mutate(self, candidate: dict[str, Any], mutation_type: str) -> dict[str, Any]:
        mutated = dict(candidate)
        mutated["mutation_type"] = mutation_type
        mutated["expression"] = f"{candidate.get('expression', 'rank(x)')}::{mutation_type}"
        return mutated

    def generate_mutants(self, seed: dict[str, Any], *, mutation_types: list[str] | None = None) -> list[dict[str, Any]]:
        mutation_types = mutation_types or ["swap_field", "swap_dataset", "tweak_window"]
        return [self.mutate(seed, mutation_type) for mutation_type in mutation_types]

    def approve_mutants(self, mutants: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return [mutant for mutant in mutants if self.validator(mutant)]

    def run(self, candidates: list[dict[str, Any]], *, limit: int = 3) -> list[dict[str, Any]]:
        seeds = self.select_seeds(candidates, limit=limit)
        mutants: list[dict[str, Any]] = []
        for seed in seeds:
            mutants.extend(self.generate_mutants(seed))
        return self.approve_mutants(mutants)
