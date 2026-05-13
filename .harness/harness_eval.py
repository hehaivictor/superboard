#!/usr/bin/env python3
"""Run ontology quality evaluation as a Harness eval."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    result = subprocess.run([sys.executable, "scripts/evaluate_ontology_quality.py"], cwd=ROOT, text=True, check=False)
    if result.returncode != 0:
        return result.returncode
    print("Harness eval passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
