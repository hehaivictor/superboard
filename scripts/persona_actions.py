#!/usr/bin/env python3
"""Deterministic persona graph actions used by Super Board."""

from __future__ import annotations

from typing import Any


def first_item(items: Any) -> dict[str, Any]:
    if isinstance(items, list):
        for item in items:
            if isinstance(item, dict):
                return item
    return {}


def rule_for_graph(graph: dict[str, Any]) -> dict[str, Any]:
    return first_item(graph.get("decision_rules"))


def explain_selection(graph: dict[str, Any], matched_signals: list[str]) -> dict[str, Any]:
    person = graph.get("person", {})
    rule = rule_for_graph(graph)
    signals = "、".join(matched_signals) if matched_signals else "常驻审议维度"
    return {
        "action": "ExplainSelection",
        "persona_id": person.get("persona_id", ""),
        "display_name": person.get("display_name", ""),
        "body": f"因本次材料命中{signals}，该席位进入审议；其观点必须受来源、边界和反证约束。",
        "claim_id": rule.get("claim_id", ""),
        "model_id": rule.get("model_id", ""),
        "source_ids": rule.get("source_ids", []),
        "boundary_id": rule.get("boundary_id", ""),
        "counter_test_id": rule.get("counter_test_id", ""),
        "relation_ids": rule.get("relation_ids", []),
    }


def generate_counter_test(graph: dict[str, Any], decision_context: str) -> dict[str, Any]:
    person = graph.get("person", {})
    rule = rule_for_graph(graph)
    counter_tests = graph.get("counter_tests") or []
    counter = first_item(counter_tests)
    counter_body = counter.get("description") or rule.get("counter_test") or "用当前材料构造一个可执行反证实验。"
    return {
        "action": "GenerateCounterTest",
        "persona_id": person.get("persona_id", ""),
        "display_name": person.get("display_name", ""),
        "body": f"围绕“{decision_context}”设置反证：{counter_body}",
        "claim_id": rule.get("claim_id", ""),
        "model_id": rule.get("model_id", ""),
        "source_ids": rule.get("source_ids", []),
        "boundary_id": rule.get("boundary_id", ""),
        "counter_test_id": rule.get("counter_test_id") or counter.get("counter_test_id", ""),
        "relation_ids": rule.get("relation_ids", []),
    }
