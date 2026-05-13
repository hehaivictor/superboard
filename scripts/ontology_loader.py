#!/usr/bin/env python3
"""Load Super Board decision ontology files without third-party YAML dependencies."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


COMMITTEE_LABELS = {
    "business-leaders": "商业委员会",
    "startup-mentors": "创业委员会",
    "investment-masters": "投资委员会",
    "consulting-elite": "咨询委员会",
    "product-users": "产品委员会",
}


def load_json_or_yaml(path: Path) -> dict[str, Any]:
    """Load JSON or the small YAML subset used by this repository."""
    text = path.read_text(encoding="utf-8")
    stripped = text.strip()
    if not stripped:
        return {}
    if stripped.startswith("{"):
        payload = json.loads(stripped)
        return payload if isinstance(payload, dict) else {}
    if path.name == "default-board.yaml":
        return parse_board_yaml(text)
    raise ValueError(f"unsupported non-JSON ontology file: {path}")


def parse_board_yaml(text: str) -> dict[str, Any]:
    board: dict[str, Any] = {
        "board_id": "",
        "name": "",
        "committees": [],
        "core_board": {},
        "triggered_specialists": {},
        "distilled_archive": [],
    }
    current_committee: dict[str, Any] | None = None
    current_section = ""
    current_key = ""

    for raw_line in text.splitlines():
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue
        line = raw_line.rstrip()
        stripped = line.strip()
        indent = len(line) - len(line.lstrip(" "))
        if indent == 0 and ":" in stripped:
            key, value = stripped.split(":", 1)
            key = key.strip()
            value = value.strip()
            current_section = key
            current_key = ""
            if value:
                board[key] = value
            continue
        if current_section == "committees":
            if indent == 2 and stripped.startswith("- id: "):
                current_committee = {"id": stripped.split(":", 1)[1].strip(), "personas": []}
                board["committees"].append(current_committee)
                current_key = ""
                continue
            if current_committee is None:
                continue
            if indent == 4 and ":" in stripped:
                key, value = stripped.split(":", 1)
                key = key.strip()
                value = value.strip()
                current_key = key
                if value:
                    current_committee[key] = value
                elif key == "personas":
                    current_committee.setdefault("personas", [])
                continue
            if indent == 6 and stripped.startswith("- ") and current_key == "personas":
                current_committee.setdefault("personas", []).append(stripped[2:].strip())
                continue
        if current_section in {"triggered_specialists", "core_board"}:
            if indent == 2 and ":" in stripped:
                key, value = stripped.split(":", 1)
                key = key.strip()
                value = value.strip()
                current_key = key
                if value.startswith("[") and value.endswith("]"):
                    board[current_section][key] = [item.strip() for item in value[1:-1].split(",") if item.strip()]
                else:
                    board[current_section][key] = []
                continue
            if indent == 4 and stripped.startswith("- ") and current_key:
                board[current_section].setdefault(current_key, []).append(stripped[2:].strip())
                continue
        if current_section == "distilled_archive" and indent == 2 and stripped.startswith("- "):
            board["distilled_archive"].append(stripped[2:].strip())

    if not board["core_board"] and board["committees"]:
        board["core_board"] = {
            str(committee.get("id", "")): list(committee.get("personas", []))
            for committee in board["committees"]
            if committee.get("id")
        }
    return board


def load_persona_ontologies(root: Path) -> dict[str, dict[str, Any]]:
    personas: dict[str, dict[str, Any]] = {}
    for path in sorted((root / "ontology" / "personas").glob("*.yaml")):
        payload = load_json_or_yaml(path)
        persona_id = str(payload.get("persona_id") or path.stem)
        personas[persona_id] = payload
    return personas


def load_specialist_ontologies(root: Path) -> dict[str, dict[str, Any]]:
    specialists: dict[str, dict[str, Any]] = {}
    for path in sorted((root / "ontology" / "specialists").glob("*.yaml")):
        payload = load_json_or_yaml(path)
        persona_id = str(payload.get("persona_id") or path.stem)
        specialists[persona_id] = payload
    return specialists


def core_persona_ids(board: dict[str, Any]) -> list[str]:
    if board.get("core_board"):
        ids: list[str] = []
        for personas in board["core_board"].values():
            ids.extend(str(persona) for persona in personas)
        return ids
    ids = []
    for committee in board.get("committees", []):
        ids.extend(str(persona) for persona in committee.get("personas", []))
    return ids


def triggered_specialist_ids(board: dict[str, Any]) -> list[str]:
    ids: list[str] = []
    for personas in board.get("triggered_specialists", {}).values():
        ids.extend(str(persona) for persona in personas)
    return ids


def distilled_archive_ids(board: dict[str, Any]) -> list[str]:
    return [str(persona) for persona in board.get("distilled_archive", [])]
