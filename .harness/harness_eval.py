#!/usr/bin/env python3
"""Run ontology quality evaluation as a Harness eval."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    for command in [
        [sys.executable, "scripts/evaluate_ontology_quality.py"],
        [sys.executable, "-m", "unittest", "tests/test_visual_report_builder.py"],
        [sys.executable, "-m", "unittest", "tests/test_seat_view_selector.py"],
        [sys.executable, "-m", "unittest", "tests/test_persona_display_names.py"],
    ]:
        result = subprocess.run(command, cwd=ROOT, text=True, check=False)
        if result.returncode != 0:
            return result.returncode
    print("Harness eval passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
