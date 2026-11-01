from app.services.correlation_breaker import CorrelationBreaker
from app.services.sampler import SettingSampler
from app.services.template_lab import TemplateLab


def test_template_lab_expands_and_counts_preview():
    lab = TemplateLab()
    lab.add_template("momentum", "{field}_{window}_{group}")
    expanded = lab.expand("momentum", ["value", "mkt"], [5, 21], ["all"])
    assert len(expanded) == 4
    assert expanded[0]["expression"] == "value_5_all"
    assert lab.preview_count("momentum", ["value"], [5], ["all", "top"]) == 2


def test_correlation_breaker_generates_structured_variants():
    breaker = CorrelationBreaker()
    variants = breaker.generate_variants({"id": "A-7", "dataset": "USA_EQ", "settings": {"region": "USA"}})
    assert len(variants) == 5
    assert {item["variant_type"] for item in variants} == {
        "RAM neutralization",
        "trade_when trigger",
        "Fast D1 delta",
        "dataset change",
        "region change",
    }
    assert variants[0]["settings"]["neutralization"] == "RAM"


def test_sampler_builds_setting_grid_for_defaults():
    sampler = SettingSampler()
    grid = sampler.generate_grid({"region": "USA"}, neutralization=["RAM", "None"], decay=[1, 2], truncation=["none", "trim"])
    assert len(grid) == 8
    assert grid[0]["neutralization"] == "RAM"
    assert grid[0]["decay"] == 1
    assert grid[0]["truncation"] == "none"
