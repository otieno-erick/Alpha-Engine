from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

RULES = [
    {
        "id": "quota.reserve",
        "value": 10,
        "source": "Alpha Engine policy; verified by app config",
        "last_verified": "2026-10-22",
    },
    {
        "id": "scheduler.max_concurrent",
        "value": 10,
        "source": "Phase 1 baseline; verified by app config",
        "last_verified": "2026-10-22",
    },
    {
        "id": "hash_cache.prune_days",
        "value": 90,
        "source": "Alpha Engine policy; verified by app config",
        "last_verified": "2026-10-22",
    },
]

for item in RULES:
    path = ROOT / "rules" / f"{item['id'].replace('.', '_')}.yaml"
    path.write_text(
        "- id: {id}\n  value: {value}\n  source: \"{source}\"\n  last_verified: \"{last_verified}\"\n".format(
            id=item["id"],
            value=item["value"],
            source=item["source"],
            last_verified=item["last_verified"],
        ),
        encoding="utf-8",
    )

