#!/usr/bin/env python3
"""Evaluate persona graph quality against governance gates."""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import persona_graph_loader


ROOT = Path(__file__).resolve().parents[1]
GOLDEN_FILES = [
    "tests/golden/product_decision.persona_graph.json",
    "tests/golden/business_strategy.persona_graph.json",
    "tests/golden/misuse_guardrail.persona_graph.json",
    "tests/golden/philosophy_boundary.persona_graph.json",
]


@dataclass
class EvaluationIssue:
    persona_id: str
    message: str


def evaluate_graph(persona_id: str, graph: dict[str, Any]) -> list[EvaluationIssue]:
    issues: list[EvaluationIssue] = []
    contract = graph.get("ontology_contract", {}) if isinstance(graph.get("ontology_contract"), dict) else {}
    forbidden = set(str(item) for item in contract.get("forbidden_actions", []) if isinstance(contract.get("forbidden_actions"), list))
    if "invent_direct_quote" not in forbidden:
        issues.append(EvaluationIssue(persona_id, "missing direct quote guardrail"))
    if len(graph.get("model_comparisons", [])) < 1:
        issues.append(EvaluationIssue(persona_id, "missing model comparison"))
    if len(graph.get("historical_decisions", [])) < 3:
        issues.append(EvaluationIssue(persona_id, "insufficient historical decisions"))
    if len(graph.get("episodes", [])) < 3:
        issues.append(EvaluationIssue(persona_id, "insufficient episodes"))
    if str(graph.get("person", {}).get("committee")) == "philosophy-humanities":
        boundary_text = " ".join(str(item.get("description", "")) for item in graph.get("boundaries", []) if isinstance(item, dict))
        if "现代" not in boundary_text or "商业证据" not in boundary_text:
            issues.append(EvaluationIssue(persona_id, "philosophy persona missing modern business evidence boundary"))
    return issues


def evaluate_golden_files(root: Path) -> list[EvaluationIssue]:
    issues: list[EvaluationIssue] = []
    for relative in GOLDEN_FILES:
        path = root / relative
        if not path.is_file():
            issues.append(EvaluationIssue(relative, "golden case missing"))
            continue
        payload = json.loads(path.read_text(encoding="utf-8"))
        for field in ["case_id", "expected_personas", "expected_graph_fields", "must_not"]:
            if field not in payload:
                issues.append(EvaluationIssue(relative, f"golden case missing {field}"))
    return issues


def evaluate(root: Path = ROOT) -> tuple[list[EvaluationIssue], dict[str, Any]]:
    graphs = persona_graph_loader.load_persona_graphs(root)
    issues: list[EvaluationIssue] = []
    for persona_id, graph in graphs.items():
        issues.extend(evaluate_graph(persona_id, graph))
    issues.extend(evaluate_golden_files(root))
    summary = {
        "persona_count": len(graphs),
        "issue_count": len(issues),
        "golden_count": len(GOLDEN_FILES),
    }
    return issues, summary


def main() -> int:
    issues, summary = evaluate(ROOT)
    report = {
        "status": "failed" if issues else "passed",
        "summary": summary,
        "issues": [issue.__dict__ for issue in issues],
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
