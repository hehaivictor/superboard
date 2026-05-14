#!/usr/bin/env python3
"""Validate Super Board decision ontology files."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from ontology_loader import (
    core_persona_ids,
    distilled_archive_ids,
    load_json_or_yaml,
    load_persona_ontologies,
    triggered_specialist_ids,
)


EXPECTED_CORE_PERSONA_IDS = [
    "warren-buffett",
    "jeff-bezos",
    "peter-drucker",
    "steve-jobs",
    "peter-thiel",
    "paul-graham",
    "charlie-munger",
    "nassim-taleb",
    "ray-dalio",
    "michael-porter",
    "richard-rumelt",
    "sun-tzu",
    "marty-cagan",
    "don-norman",
    "zhang-xiaolong",
    "ren-zhengfei",
    "zhang-yiming",
    "kazuo-inamori",
    "laozi",
    "confucius",
    "wang-yangming",
]

REQUIRED_SCHEMA_FILES = [
    "ontology/schemas/persona_ontology.schema.json",
    "ontology/schemas/committee_ontology.schema.json",
    "ontology/schemas/ontology_trace.schema.json",
]

REQUIRED_PERSONA_FIELDS = [
    "persona_id",
    "name",
    "display_name",
    "english_name",
    "committee",
    "ontology_level",
    "source_quality",
    "version",
    "concepts",
    "decision_rules",
    "activation",
    "representative_viewpoints",
    "evidence_thresholds",
    "counter_tests",
    "misuse_guardrails",
    "failure_modes",
    "confidence_boundary",
    "source_map",
    "case_map",
    "not_for",
    "calibration_notes",
]

REQUIRED_RULE_FIELDS = [
    "rule_id",
    "description",
    "triggers",
    "positive_signals",
    "red_flags",
    "evidence_required",
    "counter_tests",
    "confidence_boundary",
]

MIN_CORE_CONCEPTS = 5
MIN_CORE_RULES = 5


@dataclass(frozen=True)
class ValidationIssue:
    path: str
    message: str


def list_has_values(value: Any, minimum: int = 1) -> bool:
    return isinstance(value, list) and len(value) >= minimum and all(str(item).strip() for item in value)


def validate_persona(path: Path, persona: dict[str, Any], core_ids: set[str]) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    relative = str(path)
    persona_id = str(persona.get("persona_id", path.stem))
    is_core = persona_id in core_ids

    for field in REQUIRED_PERSONA_FIELDS:
        if field not in persona:
            issues.append(ValidationIssue(relative, f"missing persona field: {field}"))

    if persona.get("persona_id") != path.stem:
        issues.append(ValidationIssue(relative, "persona_id must match filename"))
    display_name = str(persona.get("display_name", "")).strip()
    if not display_name:
        issues.append(ValidationIssue(relative, "persona must have display_name"))
    if any(ch.isascii() and ch.isalpha() for ch in display_name):
        issues.append(ValidationIssue(relative, "display_name must be Chinese-facing, not an English display name"))
    if is_core and persona.get("ontology_level") != "core":
        issues.append(ValidationIssue(relative, "core board persona must have ontology_level: core"))
    if persona.get("ontology_level") not in {"core", "triggered_specialist", "distilled_archive"}:
        issues.append(ValidationIssue(relative, "invalid ontology_level"))
    if persona.get("source_quality") not in {"high", "medium", "low"}:
        issues.append(ValidationIssue(relative, "invalid source_quality"))

    if is_core and not list_has_values(persona.get("concepts"), MIN_CORE_CONCEPTS):
        issues.append(ValidationIssue(relative, f"core persona must have at least {MIN_CORE_CONCEPTS} concepts"))
    if is_core and not list_has_values(persona.get("decision_rules"), MIN_CORE_RULES):
        issues.append(ValidationIssue(relative, f"core persona must have at least {MIN_CORE_RULES} decision_rules"))

    rule_ids: list[str] = []
    for index, rule in enumerate(persona.get("decision_rules", [])):
        if not isinstance(rule, dict):
            issues.append(ValidationIssue(relative, f"decision_rules[{index}] must be object"))
            continue
        rule_id = str(rule.get("rule_id", f"rule-{index}"))
        rule_ids.append(rule_id)
        for field in REQUIRED_RULE_FIELDS:
            if field not in rule:
                issues.append(ValidationIssue(relative, f"{rule_id} missing rule field: {field}"))
        for field in ["triggers", "positive_signals", "red_flags", "evidence_required", "counter_tests", "confidence_boundary"]:
            if not list_has_values(rule.get(field)):
                issues.append(ValidationIssue(relative, f"{rule_id} must have non-empty {field}"))

    for duplicate in sorted({rule_id for rule_id in rule_ids if rule_ids.count(rule_id) > 1}):
        issues.append(ValidationIssue(relative, f"duplicate rule_id: {duplicate}"))

    activation = persona.get("activation")
    if not isinstance(activation, dict) or not activation:
        issues.append(ValidationIssue(relative, "persona must have non-empty activation"))
    for field in ["representative_viewpoints", "evidence_thresholds", "counter_tests", "misuse_guardrails", "failure_modes", "confidence_boundary", "source_map", "case_map", "not_for", "calibration_notes"]:
        if not list_has_values(persona.get(field)):
            issues.append(ValidationIssue(relative, f"persona must have non-empty {field}"))

    return issues


def validate(root: Path) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []

    for relative in REQUIRED_SCHEMA_FILES:
        path = root / relative
        if not path.is_file():
            issues.append(ValidationIssue(relative, "required ontology schema is missing"))
            continue
        payload = json.loads(path.read_text(encoding="utf-8"))
        for field in ["$schema", "type", "required", "properties"]:
            if field not in payload:
                issues.append(ValidationIssue(relative, f"schema missing field: {field}"))

    board_path = root / "boards" / "default-board.yaml"
    if not board_path.is_file():
        issues.append(ValidationIssue("boards/default-board.yaml", "board config is missing"))
        return issues
    board = load_json_or_yaml(board_path)
    core_ids = core_persona_ids(board)
    specialists = triggered_specialist_ids(board)
    archive_ids = distilled_archive_ids(board)

    if core_ids != EXPECTED_CORE_PERSONA_IDS:
        issues.append(ValidationIssue("boards/default-board.yaml", "core board persona order does not match expected ontology board"))
    if len(core_ids) != len(set(core_ids)):
        issues.append(ValidationIssue("boards/default-board.yaml", "duplicate core persona id"))
    if set(core_ids) & set(specialists):
        issues.append(ValidationIssue("boards/default-board.yaml", "triggered specialist also appears in core board"))
    if set(core_ids) & set(archive_ids):
        issues.append(ValidationIssue("boards/default-board.yaml", "distilled archive persona also appears in core board"))

    personas = load_persona_ontologies(root)
    for persona_id in EXPECTED_CORE_PERSONA_IDS:
        if persona_id not in personas:
            issues.append(ValidationIssue(f"ontology/personas/{persona_id}.yaml", "core persona ontology is missing"))

    core_set = set(core_ids)
    for persona_id, persona in personas.items():
        path = root / "ontology" / "personas" / f"{persona_id}.yaml"
        issues.extend(validate_persona(path.relative_to(root), persona, core_set))

    return issues


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate Super Board decision ontology files.")
    parser.add_argument("root", nargs="?", default=Path(__file__).resolve().parents[1], type=Path)
    args = parser.parse_args(argv)

    issues = validate(args.root.resolve())
    if issues:
        print("Super Board ontology validation failed:")
        for issue in issues:
            print(f"- {issue.path}: {issue.message}")
        return 1
    print("Super Board ontology validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
