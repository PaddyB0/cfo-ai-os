"""Run cfo-os from a clone without installing it: python run.py <command> ..."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from cfo_os.cli import main  # noqa: E402

raise SystemExit(main())
