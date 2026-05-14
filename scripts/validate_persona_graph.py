#!/usr/bin/env python3
"""Validate Super Board persona graph files."""

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

REQUIRED_SCHEMA_FILES = [
    "ontology/schemas/persona_graph.schema.json",
    "ontology/schemas/persona_source.schema.json",
    "ontology/schemas/persona_eval_case.schema.json",
    "ontology/schemas/persona_relation.schema.json",
]

REQUIRED_GRAPH_FIELDS = [
    "person",
    "ontology_contract",
    "sources",
    "claims",
    "mental_models",
    "heuristics",
    "historical_decisions",
    "episodes",
    "expression_patterns",
    "boundaries",
    "contradictions",
    "actions",
    "decision_rules",
    "relations",
    "representative_viewpoints",
    "evidence_graph",
    "model_comparisons",
    "action_audit",
    "eval_cases",
    "ontology_updates",
    "version_log",
]

FORBIDDEN_ACTIONS = {
    "claim_to_be_real_person",
    "fabricate_private_memory",
    "invent_direct_quote",
}


@dataclass(frozen=True)
class ValidationIssue:
    path: str
    message: str


def list_count(graph: dict[str, Any], field: str) -> int:
    value = graph.get(field)
    return len(value) if isinstance(value, list) else 0


def validate_schema_files(root: Path) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    for relative in REQUIRED_SCHEMA_FILES:
        path = root / relative
        if not path.is_file():
            issues.append(ValidationIssue(relative, "required persona graph schema is missing"))
            continue
        payload = json.loads(path.read_text(encoding="utf-8"))
        for field in ["$schema", "type", "required", "properties"]:
            if field not in payload:
                issues.append(ValidationIssue(relative, f"schema missing field: {field}"))
    return issues


def validate_graph(path: Path, graph: dict[str, Any]) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    relative = str(path)
    person = graph.get("person") if isinstance(graph.get("person"), dict) else {}
    persona_id = str(person.get("persona_id") or path.stem)

    for field in REQUIRED_GRAPH_FIELDS:
        if field not in graph:
            issues.append(ValidationIssue(relative, f"missing graph field: {field}"))

    if persona_id != path.stem:
        issues.append(ValidationIssue(relative, "person.persona_id must match filename"))
    display_name = str(person.get("display_name", "")).strip()
    if not display_name:
        issues.append(ValidationIssue(relative, "person.display_name is required"))
    if any(ch.isascii() and ch.isalpha() for ch in display_name):
        issues.append(ValidationIssue(relative, "person.display_name must be Chinese-facing"))

    contract = graph.get("ontology_contract") if isinstance(graph.get("ontology_contract"), dict) else {}
    forbidden = set(str(item) for item in contract.get("forbidden_actions", []) if str(item).strip()) if isinstance(contract.get("forbidden_actions"), list) else set()
    missing_forbidden = sorted(FORBIDDEN_ACTIONS - forbidden)
    if missing_forbidden:
        issues.append(ValidationIssue(relative, f"ontology_contract missing forbidden actions: {missing_forbidden}"))
    for field in ["dangerous_when", "requires_counterweight_from", "must_be_checked_by"]:
        if not isinstance(contract.get(field), list) or not contract.get(field):
            issues.append(ValidationIssue(relative, f"ontology_contract must have non-empty {field}"))

    minimums = {
        "sources": 3,
        "claims": 5,
        "decision_rules": 5,
        "historical_decisions": 3,
        "episodes": 3,
        "expression_patterns": 3,
        "boundaries": 3,
        "eval_cases": 3,
        "relations": 5,
    }
    for field, minimum in minimums.items():
        if list_count(graph, field) < minimum:
            issues.append(ValidationIssue(relative, f"{field} must have at least {minimum} items"))
    if list_count(graph, "mental_models") + list_count(graph, "heuristics") < 5:
        issues.append(ValidationIssue(relative, "mental_models plus heuristics must have at least 5 items"))

    object_ids = persona_graph_loader.graph_object_ids(graph)
    for relation in persona_graph_loader.graph_list(graph.get("relations")):
        for endpoint in ["subject", "object"]:
            value = str(relation.get(endpoint, ""))
            if value not in object_ids:
                issues.append(ValidationIssue(relative, f"relation {relation.get('relation_id')} invalid {endpoint}: {value}"))

    for rule in persona_graph_loader.graph_list(graph.get("decision_rules")):
        for field in ["claim_id", "model_id", "source_ids", "boundary_id", "counter_test_id", "relation_ids"]:
            if not rule.get(field):
                issues.append(ValidationIssue(relative, f"rule {rule.get('rule_id')} missing {field}"))
        for source_id in rule.get("source_ids", []) if isinstance(rule.get("source_ids"), list) else []:
            if str(source_id) not in object_ids:
                issues.append(ValidationIssue(relative, f"rule {rule.get('rule_id')} invalid source_id: {source_id}"))
        for field in ["claim_id", "model_id", "boundary_id", "counter_test_id"]:
            if str(rule.get(field, "")) not in object_ids:
                issues.append(ValidationIssue(relative, f"rule {rule.get('rule_id')} invalid {field}: {rule.get(field)}"))

    return issues


def validate(root: Path = ROOT) -> list[ValidationIssue]:
    issues = validate_schema_files(root)
    graphs = persona_graph_loader.load_persona_graphs(root)
    expected = persona_graph_loader.expected_persona_ids(root)
    if sorted(graphs) != sorted(expected):
        missing = sorted(set(expected) - set(graphs))
        extra = sorted(set(graphs) - set(expected))
        issues.append(ValidationIssue("ontology/persona_graphs", f"persona graph ids mismatch; missing={missing}; extra={extra}"))
    for persona_id, graph in graphs.items():
        path = root / "ontology" / "persona_graphs" / f"{persona_id}.json"
        issues.extend(validate_graph(path.relative_to(root), graph))
    return issues


def main() -> int:
    issues = validate(ROOT)
    if issues:
        print("Super Board persona graph validation failed:")
        for issue in issues:
            print(f"- {issue.path}: {issue.message}")
        return 1
    print("Super Board persona graph validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
