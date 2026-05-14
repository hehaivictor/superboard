#!/usr/bin/env python3
"""Load and inspect Super Board persona graph files."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from ontology_loader import (
    core_persona_ids,
    distilled_archive_ids,
    load_json_or_yaml,
    triggered_specialist_ids,
)


ROOT = Path(__file__).resolve().parents[1]
GRAPH_DIR = Path("ontology/persona_graphs")


def expected_persona_ids(root: Path = ROOT) -> list[str]:
    board = load_json_or_yaml(root / "boards" / "default-board.yaml")
    ids = core_persona_ids(board) + triggered_specialist_ids(board) + distilled_archive_ids(board)
    return list(dict.fromkeys(ids))


def load_persona_graph(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def load_persona_graphs(root: Path = ROOT) -> dict[str, dict[str, Any]]:
    graphs: dict[str, dict[str, Any]] = {}
    graph_root = root / GRAPH_DIR
    if not graph_root.is_dir():
        return graphs
    for path in sorted(graph_root.glob("*.json")):
        graph = load_persona_graph(path)
        person = graph.get("person") if isinstance(graph.get("person"), dict) else {}
        persona_id = str(person.get("persona_id") or path.stem)
        graphs[persona_id] = graph
    return graphs


def graph_list(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, dict)]


def graph_object_ids(graph: dict[str, Any]) -> set[str]:
    ids: set[str] = set()
    person = graph.get("person")
    if isinstance(person, dict) and person.get("persona_id"):
        ids.add(str(person["persona_id"]))
    id_fields = [
        ("sources", "source_id"),
        ("claims", "claim_id"),
        ("mental_models", "model_id"),
        ("heuristics", "heuristic_id"),
        ("historical_decisions", "decision_id"),
        ("episodes", "episode_id"),
        ("expression_patterns", "pattern_id"),
        ("boundaries", "boundary_id"),
        ("contradictions", "contradiction_id"),
        ("actions", "action_id"),
        ("decision_rules", "rule_id"),
        ("counter_tests", "counter_test_id"),
        ("relations", "relation_id"),
        ("representative_viewpoints", "viewpoint_id"),
        ("evidence_graph", "evidence_id"),
        ("model_comparisons", "comparison_id"),
        ("action_audit", "audit_id"),
        ("eval_cases", "eval_id"),
        ("ontology_updates", "update_id"),
        ("version_log", "version_id"),
    ]
    for field, id_key in id_fields:
        for item in graph_list(graph.get(field)):
            value = item.get(id_key)
            if value:
                ids.add(str(value))
    return ids


def find_by_id(items: list[dict[str, Any]], key: str, value: str) -> dict[str, Any] | None:
    for item in items:
        if str(item.get(key, "")) == value:
            return item
    return None


def first_rule_reference(graph: dict[str, Any], preferred_rule_id: str | None = None) -> dict[str, Any]:
    rules = graph_list(graph.get("decision_rules"))
    if preferred_rule_id:
        matched = find_by_id(rules, "rule_id", preferred_rule_id)
        if matched:
            return matched
    return rules[0] if rules else {}


def persona_graph_refs(graph: dict[str, Any], rule_id: str | None = None) -> dict[str, Any]:
    rule = first_rule_reference(graph, rule_id)
    if not rule:
        return {}
    return {
        "persona_id": graph.get("person", {}).get("persona_id", ""),
        "display_name": graph.get("person", {}).get("display_name", ""),
        "claim_id": rule.get("claim_id", ""),
        "model_id": rule.get("model_id", ""),
        "source_ids": rule.get("source_ids", []),
        "boundary_id": rule.get("boundary_id", ""),
        "counter_test_id": rule.get("counter_test_id", ""),
        "relation_ids": rule.get("relation_ids", []),
    }


def main() -> int:
    graphs = load_persona_graphs(ROOT)
    print(json.dumps({"count": len(graphs), "persona_ids": sorted(graphs)}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
