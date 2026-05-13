#!/usr/bin/env python3
"""Lightweight Harness checks for Super Board ontology work."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REQUIRED_TASKS = [
    "ontology_schema_validation.yaml",
    "ontology_trace_golden.yaml",
    "board_memo_quality.yaml",
    "web_ontology_smoke.yaml",
    "record_followup_calibration.yaml",
]


def run(command: list[str]) -> int:
    result = subprocess.run(command, cwd=ROOT, text=True, check=False)
    return result.returncode


def main() -> int:
    missing = [name for name in REQUIRED_TASKS if not (ROOT / ".harness" / "tasks" / name).is_file()]
    if missing:
        print("missing harness tasks: " + ", ".join(missing), file=sys.stderr)
        return 1
    if not (ROOT / "PLANS.md").is_file():
        print("missing PLANS.md", file=sys.stderr)
        return 1
    if not (ROOT / ".harness" / "current_sprint.md").is_file():
        print("missing .harness/current_sprint.md", file=sys.stderr)
        return 1

    for command in [
        [sys.executable, "scripts/validate_skill.py"],
        [sys.executable, "scripts/validate_ontology.py"],
    ]:
        code = run(command)
        if code != 0:
            return code
    print("Harness check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
