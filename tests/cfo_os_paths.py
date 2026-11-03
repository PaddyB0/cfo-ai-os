"""Paths the tests share. Imported by name, so the tests run inside a larger pytest tree too."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "template" / "CFO OS"
EXAMPLES = ROOT / "examples"

if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))
