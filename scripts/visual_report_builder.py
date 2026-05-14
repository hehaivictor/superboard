#!/usr/bin/env python3
"""Build visual Super Board report payloads from existing review artifacts."""

from __future__ import annotations

import html
import json
import re
import sys
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import board_memo_structure


SCHEMA_VERSION = "1.0"

MODE_LABELS = {
    "quick_triage": "快速审议",
    "deep_board_review": "深度董事会审议",
    "red_team": "红队反证审查",
    "pre_mortem": "事前验尸",
    "investment_committee": "投资委员会",
    "product_discovery": "产品发现审议",
    "go_to_market_review": "市场进入审议",
    "synthetic_user_panel": "用户模拟委员会",
}

DECISION_LABELS = {
    "Pending": "待判断",
    "Go": "推进",
    "Pivot": "调整",
    "No-Go": "不推进",
}

COMMITTEE_LABELS = {
    "business-leaders": "商业与长期价值委员会",
    "startup-mentors": "创业与非共识机会委员会",
    "investment-masters": "投资与风险委员会",
    "consulting-elite": "战略与竞争委员会",
    "product-users": "产品与用户委员会",
    "organization-china": "组织与中国商业实践委员会",
    "philosophy-humanities": "哲学与人文委员会",
    "synthetic-users": "用户模拟组",
}

TYPE_LABELS = {
    "fact": "事实",
    "inference": "推断",
    "assumption": "假设",
    "process": "流程",
    "high": "高",
    "medium": "中",
    "low": "低",
}

TONE_BY_COMMITTEE = {
    "business-leaders": "amber",
    "startup-mentors": "violet",
    "investment-masters": "emerald",
    "consulting-elite": "cyan",
    "product-users": "rose",
    "organization-china": "blue",
    "philosophy-humanities": "violet",
    "synthetic-users": "blue",
}


def compact_text(value: Any, limit: int = 180) -> str:
    text = re.sub(r"\s+", " ", str(value or "")).strip()
    if len(text) <= limit:
        return text
    return text[: max(0, limit - 1)].rstrip() + "…"


def as_dict_list(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, dict)]


def as_string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value if str(item).strip()]


def display_mode(mode_id: Any) -> str:
    text = str(mode_id or "")
    return MODE_LABELS.get(text, text)


def display_decision(decision: Any) -> str:
    text = str(decision or "")
    return DECISION_LABELS.get(text, text)


def display_committee(committee: Any) -> str:
    text = str(committee or "")
    return COMMITTEE_LABELS.get(text, text)


def display_value(value: Any) -> str:
    text = str(value or "")
    return TYPE_LABELS.get(text, text)


def material_pack(record: dict[str, Any]) -> dict[str, Any]:
    value = record.get("material_pack", {})
    return value if isinstance(value, dict) else {}


def make_card(
    card_id: str,
    title: str,
    body: str,
    tone: str,
    source_fields: list[str],
    value: str = "",
    meta: str = "",
    badges: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "card_id": card_id,
        "title": title,
        "body": compact_text(body, 260),
        "tone": tone,
        "value": value,
        "meta": meta,
        "badges": badges or [],
        "source_fields": source_fields,
    }


def section_text(board_memo: str, canonical: str) -> str:
    for _heading, normalized, block in board_memo_structure.split_markdown_blocks(board_memo):
        if normalized == canonical:
            lines = block.splitlines()
            if lines and lines[0].lstrip().startswith("#"):
                lines = lines[1:]
            return "\n".join(lines).strip()
    return ""


def find_labeled_line(text: str, labels: list[str]) -> str:
    for line in text.splitlines():
        stripped = line.strip().lstrip("-").strip()
        for label in labels:
            match = re.match(rf"^{re.escape(label)}\s*[：:]\s*(.+)$", stripped)
            if match:
                return match.group(1).strip()
    return ""


def first_nonempty_line(text: str) -> str:
    for line in text.splitlines():
        stripped = line.strip().lstrip("-").strip()
        if stripped and not stripped.startswith("```"):
            return stripped
    return ""


def build_hero(record: dict[str, Any]) -> dict[str, Any]:
    pack = material_pack(record)
    files = as_dict_list(pack.get("files"))
    source_blocks = as_dict_list(pack.get("source_blocks"))
    decision = str(record.get("decision", "Pending"))
    generation = record.get("generation", {})
    generated_by_model = isinstance(generation, dict) and generation.get("source") == "model"
    return {
        "title": str(record.get("title", "")),
        "decision_id": str(record.get("decision_id", "")),
        "mode_id": str(record.get("mode_id", "")),
        "mode_label": display_mode(record.get("mode_id")),
        "decision": decision,
        "decision_label": display_decision(decision),
        "confidence_label": "模型生成" if generated_by_model else "本地草案",
        "source_block_count": len(source_blocks),
        "material_file_count": len(files),
    }


def build_decision_cards(record: dict[str, Any], board_memo: str) -> list[dict[str, Any]]:
    conclusion = section_text(board_memo, "一页结论")
    go_pivot = section_text(board_memo, "Go / No-Go / Pivot 建议")
    risk_section = section_text(board_memo, "最大机会、最大风险与反证路径")
    roadmap = section_text(board_memo, "30 / 60 / 90 天行动计划")

    opportunity = find_labeled_line(risk_section, ["最大机会"]) or "从材料中识别可验证的产品、商业或执行增量。"
    risk = find_labeled_line(risk_section, ["最大风险"]) or "证据链不足时，建议可能退化为泛化判断。"
    counter = find_labeled_line(risk_section, ["反证路径", "反证实验"]) or "优先验证最强反例，确认需求、成本和替代方案。"
    next_action = first_nonempty_line(roadmap) or "按 30 / 60 / 90 天检查点推进复盘。"

    return [
        make_card(
            "decision-current",
            "当前董事会建议",
            find_labeled_line(conclusion, ["当前建议"]) or first_nonempty_line(conclusion) or "等待完整审议输出。",
            "slate",
            ["record.decision", "board_memo.一页结论"],
            value=display_decision(record.get("decision", "Pending")),
            meta=str(record.get("decision_id", "")),
        ),
        make_card(
            "decision-go-pivot",
            "推进 / 调整 / 不推进条件",
            first_nonempty_line(go_pivot) or "用推进、调整、不推进三类条件约束最终判断。",
            "blue",
            ["board_memo.Go / No-Go / Pivot 建议"],
            value="条件判断",
        ),
        make_card(
            "decision-opportunity",
            "最大机会",
            opportunity,
            "emerald",
            ["board_memo.最大机会、最大风险与反证路径"],
            value="机会",
        ),
        make_card(
            "decision-risk",
            "最大风险",
            risk,
            "rose",
            ["board_memo.最大机会、最大风险与反证路径"],
            value="风险",
        ),
        make_card(
            "decision-counter-test",
            "反证路径",
            counter,
            "amber",
            ["board_memo.最大机会、最大风险与反证路径", "ontology_rule_hits.counter_test"],
            value="反证",
        ),
        make_card(
            "decision-next-action",
            "下一步动作",
            next_action,
            "violet",
            ["board_memo.30 / 60 / 90 天行动计划", "record.follow_up_checkpoints"],
            value="复盘",
        ),
    ]


def build_committee_cards(record: dict[str, Any]) -> list[dict[str, Any]]:
    matrix = as_dict_list(record.get("committee_rule_matrix"))
    rule_hits = as_dict_list(record.get("ontology_rule_hits"))
    selected_seats = as_dict_list(record.get("selected_seats"))
    committees = list(dict.fromkeys([str(seat.get("committee", "")) for seat in selected_seats if seat.get("committee")]))
    for group in matrix:
        committee = str(group.get("committee", ""))
        if committee and committee not in committees:
            committees.append(committee)
    hits_by_committee = {str(group.get("committee", "")): as_dict_list(group.get("rule_hits")) for group in matrix}
    cards: list[dict[str, Any]] = []
    for committee in committees:
        hits = hits_by_committee.get(committee, [])
        first_hit = hits[0] if hits else {}
        missing = []
        for hit in rule_hits:
            if str(hit.get("committee", "")) == committee:
                missing.extend(as_string_list(hit.get("missing_evidence")))
        missing_text = "、".join(dict.fromkeys(missing[:3])) or "未记录额外证据缺口"
        selected_names = "、".join(
            str(seat.get("display_name", ""))
            for seat in selected_seats
            if str(seat.get("committee", "")) == committee and str(seat.get("display_name", "")).strip()
        )
        body = (
            f"本次代表：{selected_names or '未记录'}。"
            f"命中 {len(hits)} 条本体规则；首要规则 "
            f"{first_hit.get('rule_id', '未记录')}。"
            f"优先补齐：{missing_text}。"
        )
        cards.append(
            make_card(
                f"committee-{committee or len(cards) + 1}",
                display_committee(committee),
                body,
                TONE_BY_COMMITTEE.get(committee, "slate"),
                ["committee_rule_matrix", "ontology_rule_hits.missing_evidence"],
                value=f"{len(hits)} 条规则",
                badges=[display_committee(committee)],
            )
        )
    return cards


def build_seat_view_cards(record: dict[str, Any]) -> list[dict[str, Any]]:
    cards: list[dict[str, Any]] = []
    for index, seat in enumerate(as_dict_list(record.get("selected_seats")), start=1):
        committee = str(seat.get("committee", ""))
        name = str(seat.get("display_name") or seat.get("persona_id") or f"席位 {index}")
        body = (
            f"入选原因：{seat.get('selection_reason', '未记录')}。"
            f"证据门槛：{seat.get('evidence_basis', '未记录')}。"
            f"反证信号：{seat.get('counter_signal', '未记录')}。"
        )
        cards.append(
            make_card(
                f"seat-{index:02d}",
                name,
                body,
                TONE_BY_COMMITTEE.get(committee, "slate"),
                ["selected_seats", "seat_viewpoints", "seat_selection_trace"],
                value=display_committee(committee),
                meta=str(seat.get("ontology_level", "")),
                badges=[display_committee(committee)],
            )
        )
    return cards


def build_ontology_cards(record: dict[str, Any], limit: int = 8) -> list[dict[str, Any]]:
    cards: list[dict[str, Any]] = []
    for index, hit in enumerate(as_dict_list(record.get("ontology_rule_hits"))[:limit], start=1):
        triggers = "、".join(as_string_list(hit.get("triggered_by"))[:4]) or "未记录触发词"
        missing = "、".join(as_string_list(hit.get("missing_evidence"))[:3]) or "未记录证据缺口"
        counter = str(hit.get("counter_test") or "未记录反证实验")
        body = f"触发词：{triggers}。证据缺口：{missing}。反证实验：{counter}"
        title = str(hit.get("persona_name") or hit.get("persona_id") or f"本体规则 {index}")
        cards.append(
            make_card(
                f"ontology-{index:02d}",
                title,
                body,
                TONE_BY_COMMITTEE.get(str(hit.get("committee", "")), "blue"),
                ["ontology_rule_hits.triggered_by", "ontology_rule_hits.missing_evidence", "ontology_rule_hits.counter_test"],
                value=str(hit.get("rule_id", "")),
                meta=display_committee(hit.get("committee")),
            )
        )
    return cards


def build_persona_graph_cards(record: dict[str, Any], limit: int = 8) -> list[dict[str, Any]]:
    cards: list[dict[str, Any]] = []
    for index, ref in enumerate(as_dict_list(record.get("persona_graph_refs"))[:limit], start=1):
        source_ids = "、".join(as_string_list(ref.get("source_ids"))) or "未记录"
        body = (
            f"主张：{ref.get('claim_id', '未记录')}；模型：{ref.get('model_id', '未记录')}；"
            f"边界：{ref.get('boundary_id', '未记录')}；反证：{ref.get('counter_test_id', '未记录')}；"
            f"来源：{source_ids}。"
        )
        cards.append(
            make_card(
                f"persona-graph-{index:02d}",
                str(ref.get("display_name") or ref.get("persona_id") or f"人物本体 {index}"),
                body,
                "violet",
                ["persona_graph_refs"],
                value=str(ref.get("persona_id", "")),
                badges=["图谱引用"],
            )
        )
    return cards


def build_model_comparison_cards(record: dict[str, Any], limit: int = 8) -> list[dict[str, Any]]:
    cards: list[dict[str, Any]] = []
    for index, item in enumerate(as_dict_list(record.get("model_comparisons"))[:limit], start=1):
        body = (
            f"制衡对象：{item.get('with_persona_id', '未记录')}。"
            f"共识：{item.get('common_ground', '未记录')}。"
            f"张力：{item.get('key_tension', '未记录')}。"
        )
        cards.append(
            make_card(
                f"model-comparison-{index:02d}",
                str(item.get("display_name") or item.get("persona_id") or f"模型制衡 {index}"),
                body,
                "amber",
                ["model_comparisons"],
                value="制衡关系",
            )
        )
    return cards


def build_action_audit_cards(record: dict[str, Any], limit: int = 8) -> list[dict[str, Any]]:
    cards: list[dict[str, Any]] = []
    for index, item in enumerate(as_dict_list(record.get("action_audit"))[:limit], start=1):
        body = (
            f"动作：{item.get('action', '未记录')}。"
            f"输入：{item.get('input_summary', '未记录')}。"
            f"输出：{item.get('output_summary', '未记录')}。"
        )
        cards.append(
            make_card(
                f"action-audit-{index:02d}",
                str(item.get("persona_id") or f"动作审计 {index}"),
                body,
                "slate",
                ["action_audit"],
                value=str(item.get("audit_id", "")),
            )
        )
    return cards


def build_evidence_cards(record: dict[str, Any], limit: int = 6) -> list[dict[str, Any]]:
    cards: list[dict[str, Any]] = []
    for index, evidence in enumerate(as_dict_list(record.get("evidence_packets"))[:limit], start=1):
        confidence = display_value(evidence.get("confidence", ""))
        source = f"{evidence.get('source_file', '')} / {evidence.get('source_block_id', '')}".strip(" /")
        body = (
            f"{display_value(evidence.get('claim_type', ''))}判断。"
            f"来源：{source or evidence.get('evidence_source', '未记录')}。"
            f"反证方式：{evidence.get('disproof_test', '未记录')}。"
        )
        cards.append(
            make_card(
                f"evidence-{index:02d}",
                str(evidence.get("claim") or f"依据 {index}"),
                body,
                "cyan",
                ["evidence_packets"],
                value=f"置信度：{confidence}",
                meta=source,
            )
        )
    return cards


def build_assumption_cards(record: dict[str, Any], limit: int = 6) -> list[dict[str, Any]]:
    cards: list[dict[str, Any]] = []
    for index, assumption in enumerate(as_dict_list(record.get("assumptions"))[:limit], start=1):
        checkpoints = " / ".join(str(item) for item in as_string_list(assumption.get("checkpoints"))) or "未记录"
        cards.append(
            make_card(
                f"assumption-{index:02d}",
                str(assumption.get("assumption") or f"待验证假设 {index}"),
                f"类型：{display_value(assumption.get('type', ''))}。检查点：{checkpoints}。",
                "amber",
                ["assumptions"],
                value=display_value(assumption.get("confidence", "")),
                meta=str(assumption.get("source_block_id", "")),
            )
        )
    return cards


def build_insight_cards(record: dict[str, Any]) -> list[dict[str, Any]]:
    pack = material_pack(record)
    rule_hits = as_dict_list(record.get("ontology_rule_hits"))
    matrix = as_dict_list(record.get("committee_rule_matrix"))
    evidence_packets = as_dict_list(record.get("evidence_packets"))
    assumptions = as_dict_list(record.get("assumptions"))
    source_blocks = as_dict_list(pack.get("source_blocks"))

    missing: list[str] = []
    counters: list[str] = []
    for hit in rule_hits:
        missing.extend(as_string_list(hit.get("missing_evidence")))
        if hit.get("counter_test"):
            counters.append(str(hit["counter_test"]))

    unique_missing = list(dict.fromkeys(missing))
    unique_counters = list(dict.fromkeys(counters))

    return [
        make_card(
            "insight-evidence-gap",
            "证据缺口优先级",
            "当前本体规则集中要求补齐：" + ("、".join(unique_missing[:4]) if unique_missing else "直接用户证据、成本证据和反证样本。"),
            "blue",
            ["ontology_rule_hits.missing_evidence"],
            value=f"{len(unique_missing)} 类缺口",
        ),
        make_card(
            "insight-counter-test",
            "最短反证路径",
            unique_counters[0] if unique_counters else "先用最小样本验证最强反例，再决定是否扩大审议投入。",
            "rose",
            ["ontology_rule_hits.counter_test"],
            value="反证优先",
        ),
        make_card(
            "insight-committee-balance",
            "委员会覆盖度",
            f"当前记录覆盖 {len(matrix)} 个委员会、{len(rule_hits)} 条本体规则，适合用作结构化审议输入，但仍要由证据包约束结论。",
            "violet",
            ["committee_rule_matrix", "ontology_rule_hits"],
            value=f"{len(matrix)} 个委员会",
        ),
        make_card(
            "insight-traceability",
            "来源可追踪性",
            f"材料包包含 {len(source_blocks)} 个可引用来源块，已沉淀 {len(evidence_packets)} 条证据和 {len(assumptions)} 条待验证假设。",
            "emerald",
            ["material_pack.source_blocks", "evidence_packets", "assumptions"],
            value=f"{len(source_blocks)} 个来源块",
        ),
    ]


def build_roadmap(record: dict[str, Any]) -> list[dict[str, Any]]:
    roadmap: list[dict[str, Any]] = []
    for checkpoint in as_dict_list(record.get("follow_up_checkpoints")):
        day = int(checkpoint.get("day", 0) or 0)
        roadmap.append(
            {
                "day": day,
                "title": f"{day} 天复盘",
                "body": str(checkpoint.get("question", "")),
                "evidence": "来源：record.follow_up_checkpoints",
            }
        )
    return roadmap


def build_appendix_sections(record: dict[str, Any], board_memo: str) -> list[dict[str, Any]]:
    return [
        {
            "title": "结构化建议书正文摘要",
            "body": compact_text(board_memo, 900),
            "source_fields": ["board_memo"],
        },
        {
            "title": "决策记录摘要",
            "body": compact_text(json.dumps({key: record.get(key) for key in ["decision_id", "title", "mode_id", "decision"]}, ensure_ascii=False), 360),
            "source_fields": ["record"],
        },
        {
            "title": "证据链摘要",
            "body": compact_text(json.dumps(record.get("evidence_packets", []), ensure_ascii=False), 700),
            "source_fields": ["evidence_packets"],
        },
    ]


def build_visual_report(record: dict[str, Any], board_memo: str) -> dict[str, Any]:
    """Build a visual report without inventing new facts beyond existing artifacts."""
    return {
        "schema_version": SCHEMA_VERSION,
        "hero": build_hero(record),
        "seat_view_cards": build_seat_view_cards(record),
        "decision_cards": build_decision_cards(record, board_memo),
        "committee_cards": build_committee_cards(record),
        "persona_graph_cards": build_persona_graph_cards(record),
        "model_comparison_cards": build_model_comparison_cards(record),
        "action_audit_cards": build_action_audit_cards(record),
        "ontology_cards": build_ontology_cards(record),
        "evidence_cards": build_evidence_cards(record),
        "assumption_cards": build_assumption_cards(record),
        "insight_cards": build_insight_cards(record),
        "roadmap": build_roadmap(record),
        "appendix_sections": build_appendix_sections(record, board_memo),
    }


def render_card_markdown(card: dict[str, Any]) -> str:
    badges = "、".join(str(item) for item in card.get("badges", []) if str(item).strip())
    lines = [
        f"### {card.get('title', '')}",
        "",
        f"- 色彩：{card.get('tone', '')}",
        f"- 指标：{card.get('value', '')}",
        f"- 说明：{card.get('body', '')}",
        f"- 来源字段：{', '.join(str(item) for item in card.get('source_fields', []))}",
    ]
    if card.get("meta"):
        lines.append(f"- 元信息：{card.get('meta')}")
    if badges:
        lines.append(f"- 标签：{badges}")
    return "\n".join(lines).strip()


def render_visual_report_markdown(report: dict[str, Any]) -> str:
    hero = report.get("hero", {}) if isinstance(report.get("hero"), dict) else {}

    def render_group(title: str, cards: Any) -> list[str]:
        values = as_dict_list(cards)
        if not values:
            return [f"## {title}", "", "- 暂无内容", ""]
        return [f"## {title}", "", *[render_card_markdown(card) + "\n" for card in values]]

    roadmap_lines = ["## 30 / 60 / 90 天路线图", ""]
    for item in as_dict_list(report.get("roadmap")):
        roadmap_lines.extend(
            [
                f"### {item.get('title', '')}",
                "",
                f"- 检查问题：{item.get('body', '')}",
                f"- 来源：{item.get('evidence', '')}",
                "",
            ]
        )

    appendix_lines = ["## 附录", ""]
    for item in as_dict_list(report.get("appendix_sections")):
        appendix_lines.extend(
            [
                f"### {item.get('title', '')}",
                "",
                str(item.get("body", "")),
                "",
            ]
        )

    return "\n".join(
        [
            f"# 视觉版董事会建议书：{hero.get('title', '')}",
            "",
            f"- 决策编号：{hero.get('decision_id', '')}",
            f"- 审议模式：{hero.get('mode_label', '')}",
            f"- 当前建议：{hero.get('decision_label', '')}",
            f"- 证据口径：{hero.get('material_file_count', 0)} 个材料文件，{hero.get('source_block_count', 0)} 个可引用来源块",
            "",
            *render_group("本次参与席位", report.get("seat_view_cards")),
            *render_group("人物本体图谱", report.get("persona_graph_cards")),
            *render_group("模型制衡关系", report.get("model_comparison_cards")),
            *render_group("动作审计", report.get("action_audit_cards")),
            *render_group("决策摘要卡片", report.get("decision_cards")),
            *render_group("委员会卡片", report.get("committee_cards")),
            *render_group("AI 洞察", report.get("insight_cards")),
            *render_group("本体规则卡片", report.get("ontology_cards")),
            *render_group("证据卡片", report.get("evidence_cards")),
            *render_group("假设卡片", report.get("assumption_cards")),
            *roadmap_lines,
            *appendix_lines,
        ]
    ).strip() + "\n"


def render_visual_report_html(report: dict[str, Any]) -> str:
    markdown = render_visual_report_markdown(report)
    escaped = html.escape(markdown)
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <title>视觉版董事会建议书</title>
  <style>
    body {{ margin: 0; background: #f8fafc; color: #0f172a; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }}
    main {{ max-width: 1120px; margin: 32px auto; background: white; border: 1px solid #e2e8f0; border-radius: 16px; padding: 32px; }}
    pre {{ white-space: pre-wrap; line-height: 1.7; font-size: 14px; }}
  </style>
</head>
<body>
  <main><pre>{escaped}</pre></main>
</body>
</html>
"""


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="从 Super Board 决策记录生成视觉版报告。")
    parser.add_argument("--record", required=True, help="决策记录 JSON 路径。")
    parser.add_argument("--output", required=True, help="视觉版 Markdown 输出路径。")
    args = parser.parse_args()

    record_path = Path(args.record).expanduser().resolve()
    record = json.loads(record_path.read_text(encoding="utf-8"))
    board_memo = str(record.get("board_memo", ""))
    report = build_visual_report(record, board_memo)
    Path(args.output).expanduser().write_text(render_visual_report_markdown(report), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
