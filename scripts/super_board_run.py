#!/usr/bin/env python3
"""Build Super Board prompt bundles and decision record skeletons."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MODE = "deep_board_review"

COMMITTEE_LABELS = {
    "business-leaders": "商业领袖组",
    "startup-mentors": "创业导师组",
    "investment-masters": "投资大师组",
    "consulting-elite": "咨询精英组",
    "product-users": "产品与用户组",
}

SECTION_LABELS = {
    "Evidence Packet": "证据包",
    "Assumption Ledger": "假设账本",
    "Decision Log Entry": "决策记录条目",
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
    if any(token in haystack for token in ["融资", "商业模式", "市场进入", "gtm", "business"]):
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


def build_record(input_path: Path, text: str, mode: dict[str, object]) -> dict[str, object]:
    created_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    title = extract_title(text, input_path)
    mode_id = str(mode["mode_id"])
    return {
        "decision_id": decision_id_for(title, mode_id, created_at),
        "created_at": created_at,
        "input_type": infer_input_type(text, input_path),
        "mode_id": mode_id,
        "title": title,
        "decision": "Pending",
        "assumptions": [
            {
                "assumption": "审议尚未由模型完成，此记录为运行器生成的待填充骨架。",
                "type": "process",
                "confidence": "low",
                "checkpoints": [30, 60, 90],
            }
        ],
        "evidence_packets": [
            {
                "claim": "输入材料已装配为超级董事会提示包。",
                "claim_type": "fact",
                "evidence_source": str(input_path),
                "confidence": "high",
                "counterevidence": "输入路径错误或文件内容为空。",
                "disproof_test": "重新读取输入文件并核对提示包。",
            }
        ],
        "follow_up_checkpoints": [
            {"day": 30, "question": "关键假设是否已有真实证据？"},
            {"day": 60, "question": "Go / Pivot / No-Go 条件是否被触发？"},
            {"day": 90, "question": "是否需要校准委员会判断？"},
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

## 执行说明

严格遵循 `protocols/board-review.md` 和 `templates/board-memo.md`。必须输出证据包、假设账本和决策记录条目。不得编造外部数据、人物原话或模型运行结果。

## 输入材料

```markdown
{text.strip()}
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
