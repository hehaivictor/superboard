#!/usr/bin/env python3
"""Build Super Board prompt bundles and decision record skeletons."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import ontology_matcher


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MODE = "deep_board_review"

COMMITTEE_LABELS = {
    "business-leaders": "商业委员会",
    "startup-mentors": "创业委员会",
    "investment-masters": "投资委员会",
    "consulting-elite": "咨询委员会",
    "product-users": "产品委员会",
    "synthetic-users": "用户模拟组",
}

SECTION_LABELS = {
    "证据包": "证据包",
    "假设账本": "假设账本",
    "决策记录条目": "决策记录条目",
}

DEPTH_LABELS = {
    "quick": "快速",
    "focused": "聚焦",
    "deep": "深度",
}

INPUT_TYPE_LABELS = {
    "product_requirement": "产品需求",
    "project_plan": "项目计划",
    "business_plan": "商业计划",
    "unknown": "未识别",
}

STATUS_LABELS = {
    "ready": "就绪",
    "pending_model": "等待模型",
    "not_started": "未开始",
    "in_progress": "进行中",
    "validated": "已验证",
    "failed": "失败",
}

DECISION_LABELS = {
    "Pending": "待判断",
    "Go": "推进",
    "Pivot": "调整",
    "No-Go": "不推进",
}

REVIEW_STAGES = [
    ("material_breakdown", "材料拆解", "已生成材料包和来源块。"),
    ("independent_review", "独立审阅", "等待模型按委员会契约独立审阅。"),
    ("committee_deliberation", "委员会合议", "等待模型归并共识、分歧和少数派警告。"),
    ("cross_committee_synthesis", "跨委员会综合", "等待模型综合冲突和证据强度。"),
    ("evidence_packet", "证据包", "已生成本地证据包骨架。"),
    ("decision_record", "决策记录", "已生成可复盘的决策记录骨架。"),
]


def parse_mode(path: Path) -> dict[str, object]:
    mode: dict[str, object] = {}
    current_list: str | None = None

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.rstrip()
        if not line or line.startswith("#"):
            continue
        if not line.startswith(" ") and ":" in line:
            key, value = line.split(":", 1)
            key = key.strip()
            value = value.strip()
            if value:
                if value in {"true", "false"}:
                    mode[key] = value == "true"
                else:
                    mode[key] = value
                current_list = None
            else:
                mode[key] = []
                current_list = key
            continue
        if current_list and line.strip().startswith("- "):
            cast_list = mode.setdefault(current_list, [])
            assert isinstance(cast_list, list)
            cast_list.append(line.strip()[2:].strip())

    return mode


def load_modes(root: Path = ROOT) -> dict[str, dict[str, object]]:
    modes: dict[str, dict[str, object]] = {}
    for path in sorted((root / "boards" / "modes").glob("*.yaml")):
        mode = parse_mode(path)
        mode_id = str(mode.get("mode_id", path.stem))
        modes[mode_id] = mode
    return modes


def infer_input_type(text: str, path: Path) -> str:
    haystack = f"{path.name}\n{text}".lower()
    if any(token in haystack for token in ["融资", "商业模式", "市场进入", "定价", "获客成本", "客户支付", "gtm", "business"]):
        return "business_plan"
    if any(token in haystack for token in ["里程碑", "项目计划", "迁移", "资源安排", "project"]):
        return "project_plan"
    if any(token in haystack for token in ["prd", "产品需求", "用户故事", "mvp", "product"]):
        return "product_requirement"
    return "unknown"


def extract_title(text: str, path: Path) -> str:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            return stripped.lstrip("#").strip() or path.stem
    return path.stem.replace("-", " ")


def decision_id_for(title: str, mode_id: str, created_at: str) -> str:
    digest = hashlib.sha1(f"{title}|{mode_id}|{created_at}".encode("utf-8")).hexdigest()[:10]
    return f"SB-{digest}"


def stable_id(prefix: str, value: str, length: int = 10) -> str:
    digest = hashlib.sha1(value.encode("utf-8")).hexdigest()[:length]
    return f"{prefix}-{digest}"


def chunk_text(text: str, size: int = 1200) -> list[str]:
    paragraphs = [paragraph.strip() for paragraph in text.split("\n\n") if paragraph.strip()]
    chunks: list[str] = []
    current = ""
    for paragraph in paragraphs or [text.strip()]:
        if current and len(current) + len(paragraph) + 2 > size:
            chunks.append(current)
            current = paragraph
        else:
            current = f"{current}\n\n{paragraph}".strip() if current else paragraph
    if current:
        chunks.append(current)
    return chunks


def build_material_pack_from_text(input_path: Path, text: str) -> dict[str, Any]:
    title = extract_title(text, input_path)
    file_id = stable_id("file", str(input_path))
    source_blocks = [
        {
            "block_id": f"src-{index + 1:03d}",
            "file_id": file_id,
            "source_file": input_path.name,
            "text": chunk,
        }
        for index, chunk in enumerate(chunk_text(text))
    ]
    return {
        "pack_id": stable_id("pack", f"{input_path}|{text[:200]}"),
        "title": title,
        "files": [
            {
                "file_id": file_id,
                "name": input_path.name,
                "size": len(text.encode("utf-8")),
                "type": input_path.suffix.lstrip(".") or "markdown",
                "status": "read",
            }
        ],
        "source_blocks": source_blocks,
        "warnings": [],
    }


def normalize_material_pack(input_path: Path, text: str, material_pack: dict[str, Any] | None = None) -> dict[str, Any]:
    if material_pack and material_pack.get("source_blocks"):
        return material_pack
    return build_material_pack_from_text(input_path, text)


def build_review_run(mode_id: str) -> dict[str, object]:
    return {
        "run_id": stable_id("run", f"{mode_id}|{datetime.now(timezone.utc).isoformat()}"),
        "mode_id": mode_id,
        "stages": [
            {
                "stage_id": stage_id,
                "name": name,
                "status": "ready" if stage_id in {"material_breakdown", "evidence_packet", "decision_record"} else "pending_model",
                "summary": summary,
            }
            for stage_id, name, summary in REVIEW_STAGES
        ],
    }


def compact_ontology_rule_hits(trace: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "persona_id": hit.get("persona_id", ""),
            "persona_name": hit.get("persona_name", ""),
            "committee": hit.get("committee", ""),
            "rule_id": hit.get("rule_id", ""),
            "triggered_by": hit.get("triggered_by", []),
            "missing_evidence": hit.get("missing_evidence", []),
            "counter_test": hit.get("counter_test", ""),
            "confidence_boundary": hit.get("confidence_boundary", []),
        }
        for hit in trace
    ]


def first_source_block(material_pack: dict[str, Any]) -> dict[str, Any]:
    blocks = material_pack.get("source_blocks") or []
    if blocks and isinstance(blocks[0], dict):
        return blocks[0]
    return {"block_id": "src-000", "source_file": "inline-input.md", "text": ""}


def build_record(
    input_path: Path,
    text: str,
    mode: dict[str, object],
    material_pack: dict[str, Any] | None = None,
) -> dict[str, object]:
    created_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    normalized_pack = normalize_material_pack(input_path, text, material_pack)
    title = str(normalized_pack.get("title") or extract_title(text, input_path))
    mode_id = str(mode["mode_id"])
    source = first_source_block(normalized_pack)
    source_text = str(source.get("text", "")).strip()
    source_excerpt = source_text[:220] + ("..." if len(source_text) > 220 else "")
    review_run = build_review_run(mode_id)
    decision_id = decision_id_for(title, mode_id, created_at)
    ontology_trace = ontology_matcher.match_ontology_trace(ROOT, text)
    ontology_rule_hits = compact_ontology_rule_hits(ontology_trace)
    committee_rule_matrix = ontology_matcher.committee_rule_matrix(ontology_trace)
    return {
        "decision_id": decision_id,
        "created_at": created_at,
        "input_type": infer_input_type(text, input_path),
        "mode_id": mode_id,
        "title": title,
        "decision": "Pending",
        "material_pack": normalized_pack,
        "review_run": review_run,
        "ontology_trace": ontology_trace,
        "ontology_rule_hits": ontology_rule_hits,
        "committee_rule_matrix": committee_rule_matrix,
        "triggered_specialists": [],
        "assumptions": [
            {
                "assumption": "审议尚未由模型完成，此记录为运行器生成的待填充骨架。",
                "type": "process",
                "confidence": "low",
                "checkpoints": [30, 60, 90],
                "source_block_id": source.get("block_id", "src-000"),
            }
        ],
        "evidence_packets": [
            {
                "claim": "输入材料已装配为超级董事会提示包。",
                "claim_type": "fact",
                "evidence_source": str(input_path),
                "source_file": source.get("source_file", input_path.name),
                "source_block_id": source.get("block_id", "src-000"),
                "source_excerpt": source_excerpt,
                "confidence": "high",
                "counterevidence": "输入路径错误或文件内容为空。",
                "disproof_test": "重新读取输入文件并核对提示包。",
            }
        ],
        "action_items": [
            {
                "action_id": "act-001",
                "description": "补充真实材料证据后运行完整董事会审议。",
                "owner": "",
                "due": "",
                "status": "not_started",
            }
        ],
        "follow_up_checkpoints": [
            {"day": 30, "question": "关键假设是否已有真实证据？"},
            {"day": 60, "question": "推进 / 调整 / 不推进条件是否被触发？"},
            {"day": 90, "question": "是否需要校准委员会判断？"},
        ],
        "calibration_events": [
            {
                "event_id": stable_id("cal", decision_id),
                "decision_id": decision_id,
                "created_at": created_at,
                "mode_id": mode_id,
                "signal": "pending_followup",
                "note": "等待 30 / 60 / 90 天复盘后记录命中情况。",
            }
        ],
    }


def build_prompt_bundle(input_path: Path, text: str, mode: dict[str, object], record: dict[str, object]) -> str:
    required_sections = "\n".join(
        f"- {SECTION_LABELS.get(str(section), str(section))}" for section in mode.get("required_sections", [])
    )
    committees = "\n".join(
        f"- {COMMITTEE_LABELS.get(str(committee), str(committee))}" for committee in mode.get("enabled_committees", [])
    )
    input_type = str(record["input_type"])
    depth = str(mode.get("depth"))
    include_appendix = "是" if mode.get("include_persona_appendix") else "否"
    mode_name = str(mode.get("name", record["mode_id"]))
    material_pack = record.get("material_pack", {})
    source_blocks = []
    files = []
    if isinstance(material_pack, dict):
        source_blocks = material_pack.get("source_blocks", [])
        files = material_pack.get("files", [])
    source_block_lines = "\n".join(
        f"- {block.get('block_id')} · {block.get('source_file')}：{str(block.get('text', '')).strip()[:140]}"
        for block in source_blocks
        if isinstance(block, dict)
    )
    stage_lines = "\n".join(
        f"- {stage.get('name')}：{STATUS_LABELS.get(str(stage.get('status')), str(stage.get('status')))}"
        for stage in record.get("review_run", {}).get("stages", [])  # type: ignore[union-attr]
        if isinstance(stage, dict)
    )
    rule_hits = record.get("ontology_rule_hits", [])
    rule_hit_lines = "\n".join(
        "- {committee} / {persona} / {rule}：触发词 {triggers}；反证 {counter}".format(
            committee=hit.get("committee", ""),
            persona=hit.get("persona_id", ""),
            rule=hit.get("rule_id", ""),
            triggers=", ".join(str(item) for item in hit.get("triggered_by", [])),
            counter=hit.get("counter_test", ""),
        )
        for hit in rule_hits
        if isinstance(hit, dict)
    )
    return f"""# 超级董事会提示包

## 决策记录

- 决策编号：{record["decision_id"]}
- 标题：{record["title"]}
- 输入类型：{INPUT_TYPE_LABELS.get(input_type, input_type)}
- 审议模式：{mode_name}

## 审议模式

- 名称：{mode.get("name")}
- 深度：{DEPTH_LABELS.get(depth, depth)}
- 生成人物附录：{include_appendix}

## 启用委员会

{committees}

## 必选章节

{required_sections}

## 材料包

- 材料包编号：{material_pack.get("pack_id") if isinstance(material_pack, dict) else ""}
- 材料标题：{material_pack.get("title") if isinstance(material_pack, dict) else ""}
- 文件数量：{len(files)}
- 来源块数量：{len(source_blocks)}
- 口径说明：来源块是材料文件拆分后的可引用文本片段，不代表不同文件；报告中必须写成“X 个材料文件，共拆分为 Y 个可引用来源块”。

## 来源块

{source_block_lines or "- 暂无来源块"}

## 审议流程

{stage_lines}

## 本体触发摘要

{rule_hit_lines or "- 暂无本体规则命中；请在模型审议时明确说明证据缺口。"}

## 执行说明

严格遵循 `protocols/board-review.md` 和 `templates/board-memo.md`。只输出一套董事会建议书目录，不要先生成自定义目录再追加模板目录。正文只引用证据编号，来源摘录集中放在附录 A；待验证假设集中放在附录 B；Persona 摘要集中放在附录 C；决策记录集中放在附录 D。每条核心判断必须引用来源块；没有来源块时必须标注为推断或假设。不得编造外部数据、人物原话或模型运行结果。同一事实不要在三个以上章节重复展开。解释输入材料时必须区分“材料文件”和“来源块”：来源块是同一材料文件拆分后的文本片段，不代表不同文件。

## 输入材料

```markdown
{text.strip()}
```
"""


def source_block_summary(record: dict[str, object], limit: int = 5) -> str:
    material_pack = record.get("material_pack", {})
    blocks = material_pack.get("source_blocks", []) if isinstance(material_pack, dict) else []
    lines = []
    for block in blocks[:limit]:
        if not isinstance(block, dict):
            continue
        excerpt = str(block.get("text", "")).strip().replace("\n", " ")
        if len(excerpt) > 180:
            excerpt = excerpt[:180] + "..."
        lines.append(f"- {block.get('block_id')} · {block.get('source_file')}：{excerpt}")
    return "\n".join(lines) or "- 暂无来源块"


def build_board_memo(input_path: Path, text: str, mode: dict[str, object], record: dict[str, object]) -> str:
    """Generate a local board memo draft without calling an external model."""
    mode_id = str(record.get("mode_id", ""))
    input_type = str(record.get("input_type", "unknown"))
    source = first_source_block(record.get("material_pack", {}) if isinstance(record.get("material_pack"), dict) else {})
    source_block_id = str(source.get("block_id", "src-000"))
    title = str(record.get("title", extract_title(text, input_path)))
    decision = str(record.get("decision", "Pending"))
    committees = "\n".join(
        f"- {COMMITTEE_LABELS.get(str(committee), str(committee))}" for committee in mode.get("enabled_committees", [])
    )
    required_sections = "\n".join(
        f"- {SECTION_LABELS.get(str(section), str(section))}" for section in mode.get("required_sections", [])
    )
    evidence = record.get("evidence_packets", [])
    assumptions = record.get("assumptions", [])
    checkpoints = record.get("follow_up_checkpoints", [])
    actions = record.get("action_items", [])
    rule_hits = record.get("ontology_rule_hits", [])
    committee_rule_matrix = record.get("committee_rule_matrix", [])
    material_pack = record.get("material_pack", {}) if isinstance(record.get("material_pack"), dict) else {}
    file_count = len(material_pack.get("files", [])) if isinstance(material_pack, dict) else 0
    source_block_count = len(material_pack.get("source_blocks", [])) if isinstance(material_pack, dict) else 0

    return f"""# 《董事会建议书》：{title}

## 1. 一页结论

- 生成方式：本地结构化建议书草案，未调用外部模型。
- 决策编号：{record.get("decision_id", "")}
- 审议模式：{mode.get("name", mode_id)}
- 输入类型：{INPUT_TYPE_LABELS.get(input_type, input_type)}
- 当前建议：{DECISION_LABELS.get(decision, decision)}
- 一句话结论：当前材料可进入董事会审议，但还不足以直接给出最终裁决。

## 2. 输入材料与审议范围

本次审议基于 {file_count} 个材料文件，共拆分为 {source_block_count} 个可引用来源块。来源块是同一文件的文本片段，不代表不同文件。

### 来源块摘要

{source_block_summary(record)}

### 启用委员会

{committees or "- 暂无启用委员会"}

### 本模式要求输出

{required_sections or "- 暂无必选章节"}

## 3. Go / No-Go / Pivot 建议

- 推进：关键假设获得直接证据支持，且风险已有负责人和验证节奏。
- 调整：目标仍成立，但范围、用户、定价、交付路径或证据链需要调整。
- 不推进：核心用户需求、商业价值或执行约束无法通过反证实验。

## 4. 核心判断依据

1. 输入材料已被拆解为来源块，首个可引用来源为 `{source_block_id}`。
2. 所有后续判断都应绑定来源块，避免把推断写成事实。
3. 本体规则命中用于约束董事会审议角度，不替代模型董事会审议。

### 本体触发摘要

```json
{json.dumps(rule_hits, ensure_ascii=False, indent=2)}
```

### 委员会规则矩阵

```json
{json.dumps(committee_rule_matrix, ensure_ascii=False, indent=2)}
```

## 5. 五个委员会意见

{committees or "- 暂无启用委员会"}

## 6. 跨委员会共识与关键分歧

- 共识：需要补齐证据强度、关键假设和反证实验。
- 分歧：等待模型按委员会角色形成具体意见。

## 7. 最大机会、最大风险与反证路径

- 最大机会：材料中可能存在可验证的产品或商业增量。
- 最大风险：核心判断缺少直接证据时，建议会退化为泛化建议。
- 反证路径：要求反方审查只寻找最强反例：用户是否真的需要、成本是否被低估、替代方案是否更便宜。

## 8. 30 / 60 / 90 天行动计划

```json
{json.dumps(checkpoints, ensure_ascii=False, indent=2)}
```

## 附录 A：证据包

```json
{json.dumps(evidence, ensure_ascii=False, indent=2)}
```

## 附录 B：待验证假设

```json
{json.dumps(assumptions, ensure_ascii=False, indent=2)}
```

## 附录 C：Persona 关键意见摘要

- 本地草案不模拟 Persona 观点，等待模型生成。

## 附录 D：决策记录

```json
{json.dumps({**record, "action_items": actions}, ensure_ascii=False, indent=2)}
```
"""


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def run(args: argparse.Namespace) -> int:
    input_path = Path(args.input).expanduser().resolve()
    if not input_path.is_file():
        print(f"input file not found: {input_path}", file=sys.stderr)
        return 2

    modes = load_modes(ROOT)
    if args.mode not in modes:
        print(f"unknown mode: {args.mode}", file=sys.stderr)
        print("available modes: " + ", ".join(sorted(modes)), file=sys.stderr)
        return 2

    text = input_path.read_text(encoding="utf-8")
    record = build_record(input_path, text, modes[args.mode])
    bundle = build_prompt_bundle(input_path, text, modes[args.mode], record)

    if args.output:
        write_text(Path(args.output).expanduser(), bundle)
    else:
        print(bundle)

    if args.record:
        write_json(Path(args.record).expanduser(), record)

    if args.dry_run:
        print(f"已生成本地提示包：{record['decision_id']}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="生成超级董事会本地提示包和决策记录骨架。")
    parser.add_argument("--input", required=True, help="待审议的 Markdown 输入文件。")
    parser.add_argument("--mode", default=DEFAULT_MODE, help=f"审议模式，默认 {DEFAULT_MODE}。")
    parser.add_argument("--output", help="生成的提示包 Markdown 路径。")
    parser.add_argument("--record", help="生成的决策记录 JSON 路径。")
    parser.add_argument("--dry-run", action="store_true", help="不调用模型，只生成本地产物。")
    return run(parser.parse_args(argv))


if __name__ == "__main__":
    sys.exit(main())
