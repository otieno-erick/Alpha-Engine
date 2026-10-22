from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RULES_DIR = ROOT / "rules"

if not RULES_DIR.exists():
    RULES_DIR.mkdir(parents=True, exist_ok=True)

