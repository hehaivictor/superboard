#!/usr/bin/env python3
"""Select visible Super Board seats for one review run."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from ontology_loader import COMMITTEE_LABELS, load_json_or_yaml, load_persona_ontologies


STANDING_COMMITTEES = [
    "business-leaders",
    "startup-mentors",
    "investment-masters",
    "consulting-elite",
    "product-users",
    "organization-china",
    "philosophy-humanities",
]

MAX_TRIGGERED_SPECIALISTS = 3


def normalize(text: str) -> str:
    return text.lower()


def string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value if str(item).strip()]


def dict_list(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, dict)]


def signal_hits(text: str, signals: list[str]) -> list[str]:
    lowered = normalize(text)
    hits: list[str] = []
    for signal in signals:
        token = signal.strip()
        if token and token.lower() in lowered:
            hits.append(token)
    return list(dict.fromkeys(hits))


def activation_signals(persona: dict[str, Any]) -> list[str]:
    activation = persona.get("activation")
    if not isinstance(activation, dict):
        return []
    signals: list[str] = []
    for key in ["material_signals", "topics"]:
        signals.extend(string_list(activation.get(key)))
    return list(dict.fromkeys(signals))


def rule_signals(persona: dict[str, Any]) -> list[str]:
    signals: list[str] = []
    for rule in dict_list(persona.get("decision_rules")):
        signals.extend(string_list(rule.get("triggers")))
    return list(dict.fromkeys(signals))


def rule_hits_for_persona(rule_hits: list[dict[str, Any]], persona_id: str) -> list[dict[str, Any]]:
    return [hit for hit in rule_hits if str(hit.get("persona_id", "")) == persona_id]


def primary_viewpoint(persona: dict[str, Any]) -> str:
    viewpoints = dict_list(persona.get("representative_viewpoints"))
    if viewpoints:
        template = str(viewpoints[0].get("view_template", "")).strip()
        if template:
            return template
    display_name = str(persona.get("display_name") or persona.get("name") or persona.get("persona_id") or "该席位")
    return f"{display_name}视角下，当前判断必须回到材料证据、反证实验和适用边界。"


def first_counter_signal(persona: dict[str, Any], hits: list[dict[str, Any]]) -> str:
    for hit in hits:
        counter = str(hit.get("counter_test", "")).strip()
        if counter:
            return counter
    counters = string_list(persona.get("counter_tests"))
    if counters:
        return counters[0]
    return "若材料无法给出可执行反证信号，则该席位观点降级为低置信提示。"


def missing_evidence_summary(persona: dict[str, Any], hits: list[dict[str, Any]]) -> list[str]:
    missing: list[str] = []
    for hit in hits:
        missing.extend(string_list(hit.get("missing_evidence")))
    if missing:
        return list(dict.fromkeys(missing))[:3]
    thresholds = string_list(persona.get("evidence_thresholds"))
    return thresholds[:3] or ["必须引用当前材料来源块"]


def make_seat(
    persona: dict[str, Any],
    committee: str,
    hits: list[dict[str, Any]],
    matched_signals: list[str],
    reason: str,
    score: int,
) -> dict[str, Any]:
    persona_id = str(persona.get("persona_id", ""))
    display_name = str(persona.get("display_name") or persona.get("name") or persona_id)
    evidence_basis = missing_evidence_summary(persona, hits)
    return {
        "persona_id": persona_id,
        "display_name": display_name,
        "committee": committee,
        "committee_name": COMMITTEE_LABELS.get(committee, committee),
        "ontology_level": str(persona.get("ontology_level", "")),
        "source_quality": str(persona.get("source_quality", "")),
        "selection_reason": reason,
        "evidence_basis": "；".join(evidence_basis),
        "counter_signal": first_counter_signal(persona, hits),
        "viewpoint": primary_viewpoint(persona),
        "matched_signals": matched_signals,
        "score": score,
        "source_fields": [
            "selected_seats",
            "ontology_rule_hits",
            "persona.representative_viewpoints",
            "persona.evidence_thresholds",
        ],
    }


def select_core_representative(
    committee: str,
    candidate_ids: list[str],
    personas: dict[str, dict[str, Any]],
    material: str,
    rule_hits: list[dict[str, Any]],
) -> dict[str, Any] | None:
    best: tuple[int, int, str, list[dict[str, Any]], list[str], dict[str, Any]] | None = None
    for order, persona_id in enumerate(candidate_ids):
        persona = personas.get(persona_id)
        if not persona:
            continue
        hits = rule_hits_for_persona(rule_hits, persona_id)
        matched = signal_hits(material, activation_signals(persona) + rule_signals(persona))
        score = len(hits) * 100 + len(matched) * 10 + max(0, 20 - order)
        if best is None or score > best[0]:
            best = (score, order, persona_id, hits, matched, persona)
    if best is None:
        return None
    score, _order, persona_id, hits, matched, persona = best
    if hits:
        reason = f"本次材料命中 {len(hits)} 条本体规则，适合作为{COMMITTEE_LABELS.get(committee, committee)}代表。"
    elif matched:
        reason = f"本次材料命中席位激活信号：{'、'.join(matched[:4])}。"
    else:
        reason = f"作为{COMMITTEE_LABELS.get(committee, committee)}常驻代表进入审议，补足该维度的基本判断。"
    return make_seat(persona, committee, hits, matched, reason, score)


def specialist_candidates(board: dict[str, Any]) -> list[str]:
    ids: list[str] = []
    specialists = board.get("triggered_specialists")
    if isinstance(specialists, dict):
        for values in specialists.values():
            ids.extend(string_list(values))
    return list(dict.fromkeys(ids))


def select_triggered_specialists(
    board: dict[str, Any],
    personas: dict[str, dict[str, Any]],
    material: str,
    already_selected: set[str],
    limit: int = MAX_TRIGGERED_SPECIALISTS,
) -> list[dict[str, Any]]:
    scored: list[tuple[int, str, dict[str, Any], list[str]]] = []
    for persona_id in specialist_candidates(board):
        if persona_id in already_selected:
            continue
        persona = personas.get(persona_id)
        if not persona:
            continue
        matched = signal_hits(material, activation_signals(persona) + rule_signals(persona))
        if not matched:
            continue
        score = len(matched) * 10
        scored.append((score, persona_id, persona, matched))
    scored.sort(key=lambda item: (-item[0], item[1]))

    seats: list[dict[str, Any]] = []
    for score, _persona_id, persona, matched in scored[:limit]:
        committee = str(persona.get("committee", "triggered-specialists"))
        reason = f"按需触发专家命中材料信号：{'、'.join(matched[:4])}。"
        seats.append(make_seat(persona, committee, [], matched, reason, score))
    return seats


def select_seats(
    root: Path,
    material: str,
    rule_hits: list[dict[str, Any]],
    committee_rule_matrix: list[dict[str, Any]] | None = None,
    mode_id: str | None = None,
) -> dict[str, list[dict[str, Any]]]:
    """Return selected seats, viewpoints and selection trace for a review."""
    board = load_json_or_yaml(root / "boards" / "default-board.yaml")
    personas = load_persona_ontologies(root)
    core_board = board.get("core_board") if isinstance(board.get("core_board"), dict) else {}

    selected: list[dict[str, Any]] = []
    for committee in STANDING_COMMITTEES:
        candidate_ids = string_list(core_board.get(committee)) if isinstance(core_board, dict) else []
        seat = select_core_representative(committee, candidate_ids, personas, material, rule_hits)
        if seat:
            selected.append(seat)

    selected_ids = {str(seat.get("persona_id", "")) for seat in selected}
    selected.extend(select_triggered_specialists(board, personas, material, selected_ids))

    viewpoints = [
        {
            "persona_id": seat["persona_id"],
            "display_name": seat["display_name"],
            "committee": seat["committee"],
            "committee_name": seat["committee_name"],
            "viewpoint": seat["viewpoint"],
            "evidence_basis": seat["evidence_basis"],
            "counter_signal": seat["counter_signal"],
        }
        for seat in selected
    ]
    trace = [
        {
            "persona_id": seat["persona_id"],
            "display_name": seat["display_name"],
            "committee": seat["committee"],
            "mode_id": mode_id or "",
            "score": seat["score"],
            "matched_signals": seat["matched_signals"],
            "selection_reason": seat["selection_reason"],
        }
        for seat in selected
    ]
    return {
        "selected_seats": selected,
        "seat_viewpoints": viewpoints,
        "seat_selection_trace": trace,
    }
