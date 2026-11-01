from __future__ import annotations

from typing import Any

from app.services.pipeline import (  # noqa: F401
    CreationLoop,
    CreationPipeline,
    FieldProfiler,
    LineageStore,
    OverfittingGuard,
    RepairPromptBuilder,
)


def test_creation_loop_selects_datasets_and_generates_hypotheses():
    loop = CreationLoop()
    datasets = [
        {"name": "USA_EQ", "region": "USA", "category": "value", "fields": ["value", "momentum", "trend"]},
        {"name": "GLB_EQ", "region": "GLOBAL", "category": "value", "fields": ["volume", "trend"]},
    ]

    selected = loop.select_datasets(datasets, filters={"region": "USA"})
    assert len(selected) == 1
    assert selected[0]["name"] == "USA_EQ"

    hypotheses = loop.generate_hypotheses(selected[0])
    assert len(hypotheses) == 2
    assert hypotheses[0]["prompt_version"] == "v1"
    assert "field_cards" in hypotheses[0]


def test_creation_loop_generates_expressions_and_runs_pipeline():
    loop = CreationLoop()
    dataset = {"name": "USA_EQ", "region": "USA", "fields": ["value", "momentum", "trend"]}
    hypotheses = loop.generate_hypotheses(dataset)
    expressions = loop.generate_expressions(hypotheses[0])

    assert len(expressions) == 2
    assert expressions[0].startswith("rank(")

    outcome = loop.run(expressions[0], {"dataset": "USA_EQ", "expression": expressions[0]})
    assert outcome["status"] in {"clean", "stopped", "cached", "guarded"}
    assert outcome.get("score") is None or isinstance(outcome["score"], dict)


def test_creation_loop_repair_prompts_and_lineage_are_recorded():
    loop = CreationLoop()
    prompt = loop.generate_repair_prompt("is_ladder", margin=-0.05, instruction="IS Ladder")
    assert "is_ladder" in prompt
    assert "-0.05" in prompt
    assert "IS Ladder" in prompt

    store = LineageStore()
    lineage = store.record("A-900", parent=None, settings={"dataset": "USA_EQ"}, result={"status": "stopped"}, failure_reason="is_ladder", prompt_version="v3")
    assert lineage["alpha_id"] == "A-900"
    assert lineage["prompt_version"] == "v3"


def test_creation_pipeline_alias_is_available():
    assert CreationPipeline is not None
    assert hasattr(CreationPipeline, "run")


def test_field_profiler_and_overfitting_guard_are_available():
    profiler = FieldProfiler()
    cards = profiler.profile(["value", "momentum", "trend"])
    assert len(cards) == 3
    guard = OverfittingGuard()
    assert guard.check("rank(value) + lag(momentum, 3) + zscore(volume)", settings={"test_period": 12, "universe": "TOP3000"})["allowed"] is True
