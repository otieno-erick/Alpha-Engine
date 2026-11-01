from app.services.evolution import EvolutionLab


class SeedAlpha:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


def test_seed_selection_and_mutation_generation():
    lab = EvolutionLab()
    seeds = [
        {"id": "A-1", "status": "ready", "expression": "rank(x)", "checks": [{"passed": True}]},
        {"id": "A-2", "status": "ready", "expression": "delta(x)", "checks": [{"passed": True}]},
        {"id": "A-3", "status": "pending", "expression": "short(x)", "checks": [{"passed": False}]},
    ]
    selected = lab.select_seeds(seeds, limit=2)
    assert [item["id"] for item in selected] == ["A-1", "A-2"]

    mutants = lab.generate_mutants(selected[0], mutation_types=["swap_field", "tweak_window"])
    assert len(mutants) == 2
    assert mutants[0]["mutation_type"] == "swap_field"


def test_evolution_filter_keeps_only_valid_mutants():
    lab = EvolutionLab()
    good = {"id": "M-1", "expression": "rank(x)", "checks": [{"passed": True}]}
    bad = {"id": "M-2", "expression": "rank(x)", "checks": [{"passed": False}]}
    approved = lab.approve_mutants([good, bad])
    assert [item["id"] for item in approved] == ["M-1"]


def test_evolution_run_builds_candidate_pool():
    lab = EvolutionLab()
    candidates = [
        {"id": "A-1", "status": "ready", "expression": "rank(x)", "checks": [{"passed": True}]},
        {"id": "A-2", "status": "ready", "expression": "delta(x)", "checks": [{"passed": True}]},
    ]
    results = lab.run(candidates, limit=2)
    assert len(results) >= 2
    assert all("mutation_type" in item for item in results)
