#!/usr/bin/env python3
"""Deterministic ontology rule matcher for Super Board prompt assembly."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from ontology_loader import load_json_or_yaml, load_persona_ontologies, core_persona_ids


ROOT = Path(__file__).resolve().parents[1]


def normalize(text: str) -> str:
    return text.lower()


def keyword_hit(text: str, trigger: str) -> bool:
    trigger = trigger.strip().lower()
    if not trigger:
        return False
    return trigger in text


def evidence_refs(text: str, triggers: list[str]) -> list[str]:
    refs: list[str] = []
    lowered = normalize(text)
    for trigger in triggers:
        if keyword_hit(lowered, trigger):
            refs.append(trigger)
    return refs


def build_trace_hit(persona: dict[str, Any], rule: dict[str, Any], triggered_by: list[str]) -> dict[str, Any]:
    return {
        "persona_id": persona["persona_id"],
        "persona_name": persona.get("display_name") or persona["name"],
        "display_name": persona.get("display_name") or persona["name"],
        "committee": persona["committee"],
        "ontology_level": persona["ontology_level"],
        "source_quality": persona["source_quality"],
        "rule_id": rule["rule_id"],
        "rule_description": rule["description"],
        "triggered_by": triggered_by,
        "supporting_evidence": ["src-001"],
        "positive_signals": rule.get("positive_signals", []),
        "red_flags": rule.get("red_flags", []),
        "missing_evidence": rule.get("evidence_required", []),
        "counter_test": "; ".join(rule.get("counter_tests", [])),
        "confidence_boundary": rule.get("confidence_boundary", []),
    }


def match_ontology_trace(root: Path, text: str, limit_per_persona: int = 2) -> list[dict[str, Any]]:
    board = load_json_or_yaml(root / "boards" / "default-board.yaml")
    core_ids = set(core_persona_ids(board))
    personas = load_persona_ontologies(root)
    lowered = normalize(text)
    trace: list[dict[str, Any]] = []

    for persona_id in core_persona_ids(board):
        persona = personas.get(persona_id)
        if not persona or persona_id not in core_ids:
            continue
        hits_for_persona = 0
        for rule in persona.get("decision_rules", []):
            triggers = [str(trigger) for trigger in rule.get("triggers", [])]
            triggered_by = evidence_refs(lowered, triggers)
            if not triggered_by:
                continue
            trace.append(build_trace_hit(persona, rule, triggered_by))
            hits_for_persona += 1
            if hits_for_persona >= limit_per_persona:
                break

    return trace


def committee_rule_matrix(trace: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for hit in trace:
        grouped.setdefault(str(hit.get("committee", "")), []).append(hit)
    return [
        {
            "committee": committee,
            "rule_hits": [
                {
                    "persona_id": hit["persona_id"],
                    "persona_name": hit.get("persona_name") or hit.get("display_name") or hit["persona_id"],
                    "rule_id": hit["rule_id"],
                    "triggered_by": hit["triggered_by"],
                }
                for hit in hits
            ],
        }
        for committee, hits in grouped.items()
    ]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Match Super Board ontology rules for an input file.")
    parser.add_argument("--input", required=True)
    parser.add_argument("--root", default=str(ROOT))
    args = parser.parse_args(argv)

    input_path = Path(args.input)
    trace = match_ontology_trace(Path(args.root), input_path.read_text(encoding="utf-8"))
    print(json.dumps(trace, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
