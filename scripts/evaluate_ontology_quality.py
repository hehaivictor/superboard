#!/usr/bin/env python3
"""Evaluate Super Board ontology trace quality against local golden fixtures."""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import ontology_matcher


ROOT = Path(__file__).resolve().parents[1]
GOLDEN_CASES = [
    {
        "name": "pricing_strategy",
        "input": "tests/fixtures/ontology/pricing_strategy.md",
        "golden": "tests/golden/pricing_strategy.ontology_trace.json",
    }
]


@dataclass
class EvaluationIssue:
    case: str
    message: str


def load_expected(path: Path) -> set[tuple[str, str]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return {(str(item["persona_id"]), str(item["rule_id"])) for item in payload}


def hit_ids(trace: list[dict[str, Any]]) -> set[tuple[str, str]]:
    return {(str(hit["persona_id"]), str(hit["rule_id"])) for hit in trace}


def evaluate_case(case: dict[str, str]) -> tuple[list[EvaluationIssue], dict[str, Any]]:
    input_path = ROOT / case["input"]
    expected = load_expected(ROOT / case["golden"])
    trace = ontology_matcher.match_ontology_trace(ROOT, input_path.read_text(encoding="utf-8"))
    actual = hit_ids(trace)
    issues: list[EvaluationIssue] = []

    missing = sorted(expected - actual)
    if missing:
        issues.append(EvaluationIssue(case["name"], f"missing expected hits: {missing}"))

    specialist_hits = sorted(hit for hit in actual if hit[0] in {"sam-altman", "naval-ravikant", "elon-musk", "zhang-yiming"})
    if specialist_hits:
        issues.append(EvaluationIssue(case["name"], f"triggered specialists leaked into core hits: {specialist_hits}"))

    without_counter_tests = sorted(
        (str(hit.get("persona_id")), str(hit.get("rule_id")))
        for hit in trace
        if not str(hit.get("counter_test", "")).strip()
    )
    if without_counter_tests:
        issues.append(EvaluationIssue(case["name"], f"rule hits without counter tests: {without_counter_tests}"))

    summary = {
        "case": case["name"],
        "expected_hits": sorted(expected),
        "actual_hit_count": len(actual),
        "matched_expected_hits": sorted(expected & actual),
        "missing_expected_hits": missing,
    }
    return issues, summary


def main() -> int:
    all_issues: list[EvaluationIssue] = []
    summaries: list[dict[str, Any]] = []
    for case in GOLDEN_CASES:
        issues, summary = evaluate_case(case)
        all_issues.extend(issues)
        summaries.append(summary)

    report = {
        "status": "failed" if all_issues else "passed",
        "cases": summaries,
        "issues": [issue.__dict__ for issue in all_issues],
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if all_issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
