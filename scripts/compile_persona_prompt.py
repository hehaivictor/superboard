#!/usr/bin/env python3
"""Compile bounded prompt fragments from persona graph references."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import persona_graph_loader


def by_id(graph: dict[str, Any], collection: str, key: str, value: str) -> dict[str, Any]:
    for item in persona_graph_loader.graph_list(graph.get(collection)):
        if str(item.get(key, "")) == value:
            return item
    return {}


def compile_persona_fragment(graph: dict[str, Any], refs: dict[str, Any], max_chars: int = 2200) -> str:
    person = graph.get("person", {})
    contract = graph.get("ontology_contract", {})
    claim = by_id(graph, "claims", "claim_id", str(refs.get("claim_id", "")))
    model = by_id(graph, "mental_models", "model_id", str(refs.get("model_id", ""))) or by_id(
        graph, "heuristics", "heuristic_id", str(refs.get("model_id", ""))
    )
    boundary = by_id(graph, "boundaries", "boundary_id", str(refs.get("boundary_id", "")))
    counter = by_id(graph, "counter_tests", "counter_test_id", str(refs.get("counter_test_id", "")))
    source_lines = []
    for source_id in refs.get("source_ids", []) if isinstance(refs.get("source_ids"), list) else []:
        source = by_id(graph, "sources", "source_id", str(source_id))
        if source:
            source_lines.append(f"- {source_id}：{source.get('title')}（{source.get('source_quality')}）")
    fragment = f"""### {person.get('display_name')}本体片段

身份边界：{contract.get('public_figure_disclaimer', '仅代表公开材料提炼的决策视角，不代表本人参与或背书。')}
禁止动作：{', '.join(str(item) for item in contract.get('forbidden_actions', []))}

本次引用：
- claim_id：{refs.get('claim_id')} · {claim.get('text', '未记录')}
- model_id：{refs.get('model_id')} · {model.get('name', '未记录')}：{model.get('description', '')}
- boundary_id：{refs.get('boundary_id')} · {boundary.get('description', '未记录')}
- counter_test_id：{refs.get('counter_test_id')} · {counter.get('description', '未记录')}

来源：
{chr(10).join(source_lines) or '- 未记录来源'}

输出要求：用“{person.get('display_name')}视角下”表达，不使用第一人称，不生成伪原话，观点必须回到当前材料证据、适用边界和反证实验。
"""
    return fragment[:max_chars]
