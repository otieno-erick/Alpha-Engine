import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.environ["ALPHA_ENGINE_DATA_DIR"] = str(ROOT / ".test-data")
