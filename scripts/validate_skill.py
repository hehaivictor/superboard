#!/usr/bin/env python3
"""Validate the Super Board skill layout without third-party dependencies."""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path


REQUIRED_FILES = [
    "SKILL.md",
    "boards/default-board.yaml",
    "sources/awesome-persona-skills.yaml",
    "sources/license-audit.md",
    "adapters/persona-skill-adapter.md",
    "adapters/board-persona-contract.md",
    "protocols/board-review.md",
    "templates/board-memo.md",
    "templates/committee-summary.md",
    "templates/decision-log-entry.md",
    "templates/follow-up-review.md",
    "templates/user-panel-summary.md",
    "templates/persona-dossier.md",
    "docs/source-policy.md",
    "schemas/board_mode.schema.json",
    "schemas/decision_record.schema.json",
    "schemas/evidence_packet.schema.json",
    "schemas/material_pack.schema.json",
    "schemas/review_run.schema.json",
    "schemas/calibration_event.schema.json",
    "schemas/action_item.schema.json",
]

REQUIRED_PERSONA_FIELDS = [
    "identity",
    "upstream_sources",
    "license_status",
    "distillation_method",
    "source_basis",
    "source_map",
    "signature_cases",
    "core_models",
    "decision_rules",
    "default_questions",
    "deep_diagnostic_questions",
    "red_flags",
    "positive_signals",
    "failure_modes",
    "evidence_requirements",
    "debate_moves",
    "disagreement_style",
    "committee_role",
    "board_usage_notes",
    "output_constraints",
    "anti_hallucination_rules",
]

REQUIRED_BOARD_MEMO_SECTIONS = [
    "输入材料结构化拆解",
    "价值链 / 工作流图",
    "核心假设表",
    "证据强度评级",
    "证据包",
    "假设账本",
    "委员会质询记录摘要",
    "董事会审议信号图",
    "反证与失败路径",
    "决策条件",
    "30 / 60 / 90 天行动方案",
    "30 / 60 / 90 天路线图",
    "决策记录条目",
    "不建议做什么",
]

REQUIRED_MODE_IDS = [
    "quick_triage",
    "deep_board_review",
    "red_team",
    "pre_mortem",
    "investment_committee",
    "product_discovery",
    "go_to_market_review",
    "synthetic_user_panel",
]

REQUIRED_MODE_FIELDS = [
    "mode_id",
    "name",
    "description",
    "recommended_for",
    "enabled_committees",
    "required_sections",
    "depth",
    "include_persona_appendix",
]

REQUIRED_SCHEMA_FILES = [
    "schemas/board_mode.schema.json",
    "schemas/decision_record.schema.json",
    "schemas/evidence_packet.schema.json",
    "schemas/material_pack.schema.json",
    "schemas/review_run.schema.json",
    "schemas/calibration_event.schema.json",
    "schemas/action_item.schema.json",
]

REQUIRED_MERMAID_BLOCKS = 3

REQUIRED_NUWA_RESEARCH_FILES = [
    "references/research/01-writings.md",
    "references/research/02-conversations.md",
    "references/research/03-expression-dna.md",
    "references/research/04-external-views.md",
    "references/research/05-decisions.md",
    "references/research/06-timeline.md",
    "references/sources/source-index.md",
    "SKILL.md",
]

DEEP_OUTPUTS = [
    "examples/output-deep-product-board-memo.md",
    "examples/output-deep-business-board-memo.md",
    "examples/output-deep-project-board-memo.md",
]

EXPECTED_COMMITTEE_COUNT = 5
EXPECTED_PERSONA_COUNT = 25
REPLACED_PERSONA_IDS = [
    "mckinsey-strategy-partner",
    "bcg-growth-partner",
    "bain-operating-partner",
]


@dataclass(frozen=True)
class ValidationIssue:
    path: str
    message: str


def parse_board_personas(board_path: Path) -> tuple[list[str], list[str]]:
    """Parse the restricted YAML shape used by boards/default-board.yaml."""
    committees: list[str] = []
    personas: list[str] = []

    for line in board_path.read_text(encoding="utf-8").splitlines():
        if line.startswith("  - id: "):
            committees.append(line.split(":", 1)[1].strip())
        elif line.startswith("      - "):
            persona_id = line.strip()[2:].strip()
            if persona_id:
                personas.append(persona_id)

    return committees, personas


def parse_custom_personas(source_catalog_path: Path) -> list[str]:
    custom_personas: list[str] = []
    in_custom = False

    for line in source_catalog_path.read_text(encoding="utf-8").splitlines():
        if line.startswith("custom_personas:"):
            in_custom = True
            continue
        if not in_custom:
            continue
        if line.startswith("  - "):
            persona_id = line.strip()[2:].strip()
            if persona_id:
                custom_personas.append(persona_id)
        elif line and not line.startswith(" "):
            break

    return custom_personas


def parse_simple_yaml_fields(path: Path) -> dict[str, str]:
    """Parse top-level scalar and list field names from the restricted mode YAML files."""
    fields: dict[str, str] = {}

    for line in path.read_text(encoding="utf-8").splitlines():
        if not line or line.startswith(" ") or line.startswith("-") or line.startswith("#"):
            continue
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        fields[key.strip()] = value.strip()

    return fields


def has_nonempty_heading(markdown: str, heading: str) -> bool:
    pattern = re.compile(
        rf"^## {re.escape(heading)}\s*$([\s\S]*?)(?=^## |\Z)",
        re.MULTILINE,
    )
    match = pattern.search(markdown)
    if not match:
        return False
    content = match.group(1).strip()
    return bool(content)


def validate(root: Path) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []

    for relative in REQUIRED_FILES:
        if not (root / relative).is_file():
            issues.append(ValidationIssue(relative, "required file is missing"))

    for relative in REQUIRED_SCHEMA_FILES:
        schema_path = root / relative
        if not schema_path.is_file():
            continue
        schema_text = schema_path.read_text(encoding="utf-8")
        for marker in ['"$schema"', '"type"', '"required"']:
            if marker not in schema_text:
                issues.append(ValidationIssue(relative, f"schema missing marker: {marker}"))

    mode_dir = root / "boards" / "modes"
    seen_mode_ids: list[str] = []
    if not mode_dir.is_dir():
        issues.append(ValidationIssue("boards/modes", "mode directory is missing"))
    else:
        for mode_id in REQUIRED_MODE_IDS:
            mode_path = mode_dir / f"{mode_id}.yaml"
            if not mode_path.is_file():
                issues.append(ValidationIssue(f"boards/modes/{mode_id}.yaml", "required mode file is missing"))
                continue
            fields = parse_simple_yaml_fields(mode_path)
            for field in REQUIRED_MODE_FIELDS:
                if field not in fields:
                    issues.append(ValidationIssue(str(mode_path.relative_to(root)), f"missing mode field: {field}"))
            parsed_mode_id = fields.get("mode_id")
            if parsed_mode_id:
                seen_mode_ids.append(parsed_mode_id)
                if parsed_mode_id != mode_id:
                    issues.append(
                        ValidationIssue(
                            str(mode_path.relative_to(root)),
                            f"mode_id must match filename: expected {mode_id}, found {parsed_mode_id}",
                        )
                    )
        duplicates = sorted({mode_id for mode_id in seen_mode_ids if seen_mode_ids.count(mode_id) > 1})
        for duplicate in duplicates:
            issues.append(ValidationIssue("boards/modes", f"duplicate mode id: {duplicate}"))

    board_template = root / "templates/board-memo.md"
    if board_template.is_file():
        template_text = board_template.read_text(encoding="utf-8")
        for section in REQUIRED_BOARD_MEMO_SECTIONS:
            if f"## {section}" not in template_text:
                issues.append(ValidationIssue("templates/board-memo.md", f"missing board memo section: {section}"))
        if template_text.count("```mermaid") < REQUIRED_MERMAID_BLOCKS:
            issues.append(
                ValidationIssue(
                    "templates/board-memo.md",
                    f"expected at least {REQUIRED_MERMAID_BLOCKS} mermaid blocks",
                )
            )

    source_catalog = root / "sources/awesome-persona-skills.yaml"
    custom_persona_ids: list[str] = []
    if source_catalog.is_file():
        source_text = source_catalog.read_text(encoding="utf-8")
        for marker in ["direct_upstreams:", "method_upstreams:", "custom_personas:", "license_status: MIT"]:
            if marker not in source_text:
                issues.append(ValidationIssue("sources/awesome-persona-skills.yaml", f"missing source marker: {marker}"))
        custom_persona_ids = parse_custom_personas(source_catalog)

    for persona_id in custom_persona_ids:
        artifact_root = root / "nuwa_distillations" / persona_id
        for relative in REQUIRED_NUWA_RESEARCH_FILES:
            if not (artifact_root / relative).is_file():
                issues.append(
                    ValidationIssue(
                        str((Path("nuwa_distillations") / persona_id / relative).as_posix()),
                        "required full Nuwa artifact file is missing",
                    )
                )

    for relative in DEEP_OUTPUTS:
        output_path = root / relative
        if not output_path.is_file():
            issues.append(ValidationIssue(relative, "deep output example is missing"))
            continue
        output_text = output_path.read_text(encoding="utf-8")
        for section in REQUIRED_BOARD_MEMO_SECTIONS:
            if f"## {section}" not in output_text:
                issues.append(ValidationIssue(relative, f"missing deep output section: {section}"))
        for marker in ["反证", "失败路径", "决策条件", "30 / 60 / 90"]:
            if marker not in output_text:
                issues.append(ValidationIssue(relative, f"missing deep output marker: {marker}"))
        if output_text.count("```mermaid") < REQUIRED_MERMAID_BLOCKS:
            issues.append(
                ValidationIssue(
                    relative,
                    f"expected at least {REQUIRED_MERMAID_BLOCKS} mermaid blocks",
                )
            )

    board_path = root / "boards/default-board.yaml"
    if not board_path.is_file():
        return issues

    committees, persona_ids = parse_board_personas(board_path)

    if len(committees) != EXPECTED_COMMITTEE_COUNT:
        issues.append(
            ValidationIssue(
                "boards/default-board.yaml",
                f"expected {EXPECTED_COMMITTEE_COUNT} committees, found {len(committees)}",
            )
        )

    unique_persona_ids = sorted(set(persona_ids))
    if len(unique_persona_ids) != EXPECTED_PERSONA_COUNT:
        issues.append(
            ValidationIssue(
                "boards/default-board.yaml",
                f"expected {EXPECTED_PERSONA_COUNT} unique personas, found {len(unique_persona_ids)}",
            )
        )

    duplicates = sorted({persona_id for persona_id in persona_ids if persona_ids.count(persona_id) > 1})
    for persona_id in duplicates:
        issues.append(ValidationIssue("boards/default-board.yaml", f"duplicate persona id: {persona_id}"))

    for replaced in REPLACED_PERSONA_IDS:
        if replaced in persona_ids:
            issues.append(ValidationIssue("boards/default-board.yaml", f"replaced functional persona still referenced: {replaced}"))
        if (root / "personas" / f"{replaced}.md").exists():
            issues.append(ValidationIssue(f"personas/{replaced}.md", "replaced functional persona file should not exist"))

    for persona_id in unique_persona_ids:
        persona_path = root / "personas" / f"{persona_id}.md"
        relative = f"personas/{persona_id}.md"
        if not persona_path.is_file():
            issues.append(ValidationIssue(relative, "persona referenced by board does not exist"))
            continue

        markdown = persona_path.read_text(encoding="utf-8")
        for field in REQUIRED_PERSONA_FIELDS:
            if not has_nonempty_heading(markdown, field):
                issues.append(ValidationIssue(relative, f"missing or empty field: {field}"))
        if "license_status" in markdown and "## license_status" in markdown:
            if "MIT" not in markdown and "original dossier" not in markdown:
                issues.append(ValidationIssue(relative, "license_status must mention MIT or original dossier"))
        if persona_id in custom_persona_ids:
            if f"nuwa_distillations/{persona_id}/" not in markdown:
                issues.append(ValidationIssue(relative, "custom persona must reference its full Nuwa artifact"))
            if "nuwa-method-full artifact -> super-board compressed dossier" not in markdown:
                issues.append(ValidationIssue(relative, "custom persona must be marked as full Nuwa artifact compression"))

    searchable_files = [
        root / "sources/awesome-persona-skills.yaml",
        root / "sources/license-audit.md",
        *[root / relative for relative in DEEP_OUTPUTS],
    ]
    for path in searchable_files:
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        for replaced in REPLACED_PERSONA_IDS:
            if replaced in text:
                issues.append(ValidationIssue(str(path.relative_to(root)), f"replaced functional persona still mentioned: {replaced}"))

    return issues


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate Super Board skill files.")
    parser.add_argument(
        "root",
        nargs="?",
        default=Path(__file__).resolve().parents[1],
        type=Path,
        help="Skill root directory. Defaults to the parent of scripts/.",
    )
    args = parser.parse_args(argv)

    issues = validate(args.root.resolve())
    if issues:
        print("Super Board skill validation failed:")
        for issue in issues:
            print(f"- {issue.path}: {issue.message}")
        return 1

    print("Super Board skill validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
