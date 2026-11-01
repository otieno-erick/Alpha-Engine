from app.services.pipeline import CreationLoop, CreationPipeline


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
    assert outcome["status"] in {"clean", "stopped", "cached"}
    assert isinstance(outcome.get("score", {}), dict) or outcome.get("status") in {"stopped", "cached"}


def test_creation_pipeline_alias_is_available():
    assert CreationPipeline is not None
    assert hasattr(CreationPipeline, "run")
