#!/usr/bin/env python3
"""Generate deterministic persona graph files from current ontology dossiers."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from ontology_loader import load_persona_ontologies
from persona_graph_loader import expected_persona_ids


ROOT = Path(__file__).resolve().parents[1]

COMMITTEE_COUNTERWEIGHTS = {
    "business-leaders": ["charlie-munger", "michael-porter"],
    "startup-mentors": ["charlie-munger", "michael-porter"],
    "investment-masters": ["peter-drucker", "marty-cagan"],
    "consulting-elite": ["warren-buffett", "marty-cagan"],
    "product-users": ["peter-drucker", "warren-buffett"],
    "organization-china": ["peter-drucker", "charlie-munger"],
    "philosophy-humanities": ["peter-drucker", "warren-buffett"],
    "archive": ["peter-drucker", "charlie-munger"],
}

HIGH_IMPACT_COUNTERWEIGHTS = {
    "peter-thiel": ["charlie-munger", "michael-porter"],
    "elon-musk": ["marty-cagan", "ren-zhengfei", "charlie-munger"],
    "mao-zedong": ["peter-drucker", "confucius", "charlie-munger"],
    "sun-tzu": ["michael-porter", "peter-drucker", "confucius"],
    "laozi": ["peter-drucker", "michael-porter", "warren-buffett"],
}


def ensure_items(values: list[str], fallback_prefix: str, minimum: int) -> list[str]:
    items = [str(value).strip() for value in values if str(value).strip()]
    while len(items) < minimum:
        items.append(f"{fallback_prefix}{len(items) + 1}")
    return items[: max(minimum, len(items))]


def source_quality(persona: dict[str, Any]) -> str:
    value = str(persona.get("source_quality", "medium"))
    return value if value in {"high", "medium", "low"} else "medium"


def make_sources(persona: dict[str, Any]) -> list[dict[str, Any]]:
    source_map = persona.get("source_map") if isinstance(persona.get("source_map"), list) else []
    display = str(persona.get("display_name") or persona.get("name") or persona.get("persona_id"))
    sources: list[dict[str, Any]] = []
    for index, source in enumerate(source_map[:3], start=1):
        if not isinstance(source, dict):
            continue
        sources.append(
            {
                "source_id": f"source_{index:03d}",
                "title": str(source.get("source") or f"{display}公开材料 {index}"),
                "source_type": str(source.get("type") or "local dossier"),
                "source_quality": source_quality(persona),
                "usage_boundary": "只能作为公开材料提炼依据，不得生成伪原话或私人记忆。",
            }
        )
    while len(sources) < 3:
        index = len(sources) + 1
        sources.append(
            {
                "source_id": f"source_{index:03d}",
                "title": f"{display}公开材料与本地本体档案 {index}",
                "source_type": "public_material_summary",
                "source_quality": source_quality(persona),
                "usage_boundary": "用于决策视角归纳，不代表本人实时观点或授权背书。",
            }
        )
    return sources


def make_claims(persona: dict[str, Any], concepts: list[str]) -> list[dict[str, Any]]:
    display = str(persona.get("display_name") or persona.get("name") or persona.get("persona_id"))
    claims = []
    for index, concept in enumerate(ensure_items(concepts, "证据约束判断 ", 5)[:5], start=1):
        claims.append(
            {
                "claim_id": f"claim_{index:03d}",
                "text": f"{display}视角下，{concept}必须被当前材料、来源证据和反证实验共同约束。",
                "claim_type": "decision_belief",
                "source_ids": [f"source_{((index - 1) % 3) + 1:03d}"],
                "confidence": source_quality(persona),
                "inference_boundary": "这是公开材料提炼的结构化推断，不是人物原话。",
            }
        )
    return claims


def make_models(persona: dict[str, Any], concepts: list[str]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    display = str(persona.get("display_name") or persona.get("name") or persona.get("persona_id"))
    concept_items = ensure_items(concepts, "决策模型 ", 5)
    mental_models = [
        {
            "model_id": f"model_{index:03d}",
            "name": concept,
            "description": f"把{concept}转化为可检查的商业判断，而不是停留在名人标签。",
            "claim_ids": [f"claim_{index:03d}"],
            "source_ids": [f"source_{((index - 1) % 3) + 1:03d}"],
            "fails_when": "当前材料无法提供用户、市场、组织或财务证据时必须降级。",
        }
        for index, concept in enumerate(concept_items[:3], start=1)
    ]
    heuristics = [
        {
            "heuristic_id": f"heuristic_{index:03d}",
            "name": f"{display}启发式 {index}",
            "description": f"遇到{concept_items[index + 2]}相关判断时，先问证据门槛、适用边界和反证信号。",
            "claim_ids": [f"claim_{index + 3:03d}"],
            "source_ids": [f"source_{((index + 2) % 3) + 1:03d}"],
        }
        for index in range(1, 3)
    ]
    return mental_models, heuristics


def make_boundaries(persona: dict[str, Any]) -> list[dict[str, Any]]:
    persona_id = str(persona.get("persona_id"))
    display = str(persona.get("display_name") or persona.get("name") or persona_id)
    committee = str(persona.get("committee", ""))
    common = [
        {
            "boundary_id": "boundary_001",
            "description": f"{display}本体只代表公开材料提炼的决策视角，不代表本人实时观点、参与或背书。",
            "severity": "hard",
        },
        {
            "boundary_id": "boundary_002",
            "description": "材料证据不足时，观点只能作为低置信提示，不能替代用户、客户、财务或组织证据。",
            "severity": "hard",
        },
        {
            "boundary_id": "boundary_003",
            "description": "不得生成伪原话、私人记忆或未经授权的现实身份判断。",
            "severity": "hard",
        },
    ]
    if committee == "philosophy-humanities" or persona_id in {"laozi", "confucius", "wang-yangming"}:
        common[1]["description"] = "古典或哲学视角用于现代价值、责任和长期性边界，不得替代现代商业证据。"
    return common


def make_counter_tests(persona: dict[str, Any]) -> list[dict[str, Any]]:
    counters = persona.get("counter_tests") if isinstance(persona.get("counter_tests"), list) else []
    values = ensure_items([str(item) for item in counters], "如果关键证据无法补齐，则下调该视角置信度。", 3)
    return [
        {
            "counter_test_id": f"counter_{index:03d}",
            "description": value if "反证" in value else f"反证实验：{value}",
            "source_ids": [f"source_{((index - 1) % 3) + 1:03d}"],
        }
        for index, value in enumerate(values[:3], start=1)
    ]


def make_decisions_and_episodes(persona: dict[str, Any], concepts: list[str]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    display = str(persona.get("display_name") or persona.get("name") or persona.get("persona_id"))
    case_map = persona.get("case_map") if isinstance(persona.get("case_map"), list) else []
    case_values = [
        f"{case.get('case')}：{case.get('lesson')}"
        for case in case_map
        if isinstance(case, dict) and case.get("case")
    ]
    case_values = ensure_items(case_values + concepts, "公开案例与决策场景 ", 3)
    decisions = [
        {
            "decision_id": f"decision_{index:03d}",
            "title": f"{display}公开决策样式 {index}",
            "description": value,
            "source_ids": [f"source_{((index - 1) % 3) + 1:03d}"],
            "lesson": "只抽象决策原则，不还原未证实细节。",
        }
        for index, value in enumerate(case_values[:3], start=1)
    ]
    episodes = [
        {
            "episode_id": f"episode_{index:03d}",
            "title": f"{display}适用场景 {index}",
            "description": f"当材料出现{case_values[index - 1]}时，可调用该人物视角进行约束审议。",
            "source_ids": [f"source_{((index - 1) % 3) + 1:03d}"],
        }
        for index in range(1, 4)
    ]
    return decisions, episodes


def make_decision_rules(persona: dict[str, Any]) -> list[dict[str, Any]]:
    rules = persona.get("decision_rules") if isinstance(persona.get("decision_rules"), list) else []
    graph_rules: list[dict[str, Any]] = []
    for index, rule in enumerate(rules[:5], start=1):
        if not isinstance(rule, dict):
            continue
        model_id = f"model_{index:03d}" if index <= 3 else f"heuristic_{index - 3:03d}"
        graph_rules.append(
            {
                "rule_id": str(rule.get("rule_id") or f"rule_{index:03d}"),
                "description": str(rule.get("description") or "本体决策规则"),
                "triggers": rule.get("triggers", []),
                "positive_signals": rule.get("positive_signals", []),
                "red_flags": rule.get("red_flags", []),
                "evidence_required": rule.get("evidence_required", []),
                "claim_id": f"claim_{index:03d}",
                "model_id": model_id,
                "source_ids": [f"source_{((index - 1) % 3) + 1:03d}"],
                "boundary_id": f"boundary_{((index - 1) % 3) + 1:03d}",
                "counter_test_id": f"counter_{((index - 1) % 3) + 1:03d}",
                "relation_ids": [f"relation_{index:03d}"],
                "confidence_boundary": rule.get("confidence_boundary", []),
            }
        )
    while len(graph_rules) < 5:
        index = len(graph_rules) + 1
        graph_rules.append(
            {
                "rule_id": f"{persona.get('persona_id')}_graph_rule_{index}",
                "description": "补充图谱规则，要求观点回到证据、边界和反证。",
                "triggers": ["证据", "反证"],
                "positive_signals": ["材料存在可验证证据"],
                "red_flags": ["只有名人标签"],
                "evidence_required": ["当前材料来源块"],
                "claim_id": f"claim_{index:03d}",
                "model_id": f"heuristic_{max(1, index - 3):03d}" if index > 3 else f"model_{index:03d}",
                "source_ids": [f"source_{((index - 1) % 3) + 1:03d}"],
                "boundary_id": f"boundary_{((index - 1) % 3) + 1:03d}",
                "counter_test_id": f"counter_{((index - 1) % 3) + 1:03d}",
                "relation_ids": [f"relation_{index:03d}"],
                "confidence_boundary": ["不代表本人实时观点或背书"],
            }
        )
    return graph_rules


def make_relations() -> list[dict[str, str]]:
    return [
        {"relation_id": "relation_001", "subject": "source_001", "predicate": "evidences", "object": "claim_001"},
        {"relation_id": "relation_002", "subject": "claim_001", "predicate": "supports", "object": "model_001"},
        {"relation_id": "relation_003", "subject": "model_001", "predicate": "generates", "object": "heuristic_001"},
        {"relation_id": "relation_004", "subject": "boundary_001", "predicate": "limits", "object": "action_001"},
        {"relation_id": "relation_005", "subject": "eval_001", "predicate": "tests", "object": "model_001"},
        {"relation_id": "relation_006", "subject": "counter_001", "predicate": "tests", "object": "claim_001"},
    ]


def make_graph(persona: dict[str, Any]) -> dict[str, Any]:
    persona_id = str(persona.get("persona_id"))
    display = str(persona.get("display_name") or persona.get("name") or persona_id)
    committee = str(persona.get("committee", "archive"))
    concepts = ensure_items([str(item) for item in persona.get("concepts", []) if str(item).strip()], "本体判断 ", 5)
    counterweights = HIGH_IMPACT_COUNTERWEIGHTS.get(persona_id) or COMMITTEE_COUNTERWEIGHTS.get(committee, ["peter-drucker", "charlie-munger"])
    sources = make_sources(persona)
    claims = make_claims(persona, concepts)
    mental_models, heuristics = make_models(persona, concepts)
    boundaries = make_boundaries(persona)
    counter_tests = make_counter_tests(persona)
    decisions, episodes = make_decisions_and_episodes(persona, concepts)
    rules = make_decision_rules(persona)
    return {
        "schema_version": "persona_graph/v1",
        "person": {
            "persona_id": persona_id,
            "display_name": display,
            "english_name": str(persona.get("english_name", "")),
            "committee": committee,
            "ontology_level": str(persona.get("ontology_level", "distilled_archive")),
            "source_quality": source_quality(persona),
        },
        "ontology_contract": {
            "purpose": "为 Super Board 提供公开材料提炼的决策本体视角。",
            "consent_level": "public_material_only",
            "allowed_actions": ["CritiquePlan", "FindMissingEvidence", "GenerateCounterTest", "CompareModels", "ExplainSelection", "CalibrateAfterOutcome"],
            "forbidden_actions": ["claim_to_be_real_person", "fabricate_private_memory", "invent_direct_quote", "override_current_evidence"],
            "high_stakes_boundary": "不能替代法律、医疗、财务、投资或安全等专业意见。",
            "public_figure_disclaimer": f"{display}本体是公开材料提炼的决策视角，不代表本人实时观点、参与、授权或背书。",
            "private_memory_policy": "不生成、推断或保存私人记忆。",
            "dangerous_when": ["当前材料缺少证据却要求高置信结论", "用户试图用名人效应替代事实审议"],
            "requires_counterweight_from": counterweights,
            "must_be_checked_by": counterweights[:2],
        },
        "sources": sources,
        "claims": claims,
        "mental_models": mental_models,
        "heuristics": heuristics,
        "historical_decisions": decisions,
        "episodes": episodes,
        "expression_patterns": [
            {
                "pattern_id": f"pattern_{index:03d}",
                "description": f"{display}视角摘要模式 {index}：用第三人称总结关注点。",
                "usage_boundary": "只能用于第三人称视角摘要，不得模仿本人发言或生成引号式原话。",
            }
            for index in range(1, 4)
        ],
        "boundaries": boundaries,
        "contradictions": [
            {
                "contradiction_id": "contradiction_001",
                "description": "人物框架可能强化单一视角，必须与其他委员会制衡。",
                "resolution": "优先当前材料证据和反证实验。",
            },
            {
                "contradiction_id": "contradiction_002",
                "description": "历史经验和当前业务场景可能不一致。",
                "resolution": "标注现代适用边界并降低置信度。",
            },
        ],
        "actions": [
            {"action_id": "action_001", "name": "ExplainSelection", "description": "解释本次为什么启用该席位。"},
            {"action_id": "action_002", "name": "GenerateCounterTest", "description": "生成可执行反证实验。"},
            {"action_id": "action_003", "name": "CompareModels", "description": "与制衡席位比较共识和分歧。"},
        ],
        "decision_rules": rules,
        "counter_tests": counter_tests,
        "relations": make_relations(),
        "representative_viewpoints": persona.get("representative_viewpoints", []),
        "evidence_graph": [
            {
                "evidence_id": f"evidence_{index:03d}",
                "source_id": f"source_{((index - 1) % 3) + 1:03d}",
                "claim_id": f"claim_{index:03d}",
                "strength": source_quality(persona),
                "limitation": "只证明该视角可用于审议，不证明结论必然正确。",
            }
            for index in range(1, 4)
        ],
        "model_comparisons": [
            {
                "comparison_id": "comparison_001",
                "with_persona_id": counterweights[0],
                "common_ground": "都要求把判断落到证据和执行约束。",
                "key_tension": "该人物视角可能强调突破，制衡席位强调风险、成本或长期责任。",
            }
        ],
        "action_audit": [
            {
                "audit_id": "audit-template-001",
                "action": "ExplainSelection",
                "evidence_refs": ["source_001"],
                "boundary_refs": ["boundary_001"],
                "counterweight_refs": counterweights[:1],
                "note": "运行时会生成具体审计条目。",
            }
        ],
        "eval_cases": [
            {
                "eval_id": f"eval_{index:03d}",
                "scenario": f"{display}视角评测场景 {index}",
                "tests": [f"是否能引用 claim_{index:03d}", f"是否能引用 boundary_{((index - 1) % 3) + 1:03d}"],
                "expected_behavior": "输出观点、证据、边界和反证，不生成伪原话。",
                "failure_signal": "只输出名人标签或无证据高置信判断。",
            }
            for index in range(1, 4)
        ],
        "ontology_updates": [
            {
                "update_id": "update_001",
                "status": "newly_added",
                "description": "persona graph v3 初始结构化版本。",
                "affected_objects": ["claim_001", "model_001", "boundary_001"],
            }
        ],
        "version_log": [
            {
                "version_id": "version_001",
                "version": 1,
                "change": "从 persona yaml 规则表升级为 persona graph。",
            }
        ],
    }


def main() -> int:
    personas = load_persona_ontologies(ROOT)
    graph_dir = ROOT / "ontology" / "persona_graphs"
    graph_dir.mkdir(parents=True, exist_ok=True)
    for persona_id in expected_persona_ids(ROOT):
        persona = personas.get(persona_id)
        if not persona:
            raise SystemExit(f"missing persona yaml: {persona_id}")
        graph = make_graph(persona)
        (graph_dir / f"{persona_id}.json").write_text(
            json.dumps(graph, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
