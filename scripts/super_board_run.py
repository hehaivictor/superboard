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
                "claim": "输入材料已装配为 Super Board prompt bundle。",
                "claim_type": "fact",
                "evidence_source": str(input_path),
                "confidence": "high",
                "counterevidence": "输入路径错误或文件内容为空。",
                "disproof_test": "重新读取输入文件并核对 prompt bundle。",
            }
        ],
        "follow_up_checkpoints": [
            {"day": 30, "question": "关键假设是否已有真实证据？"},
            {"day": 60, "question": "Go / Pivot / No-Go 条件是否被触发？"},
            {"day": 90, "question": "是否需要校准委员会判断？"},
        ],
    }


def build_prompt_bundle(input_path: Path, text: str, mode: dict[str, object], record: dict[str, object]) -> str:
    required_sections = "\n".join(f"- {section}" for section in mode.get("required_sections", []))
    committees = "\n".join(f"- {committee}" for committee in mode.get("enabled_committees", []))
    return f"""# Super Board Prompt Bundle

## Decision Record

- 决策编号：{record["decision_id"]}
- 标题：{record["title"]}
- 输入类型：{record["input_type"]}
- 审议模式：{record["mode_id"]}

## Mode

- 名称：{mode.get("name")}
- 深度：{mode.get("depth")}
- 生成 persona 附录：{mode.get("include_persona_appendix")}

## Enabled Committees

{committees}

## Required Sections

{required_sections}

## Execution Instructions

严格遵循 `protocols/board-review.md` 和 `templates/board-memo.md`。必须输出 Evidence Packet、Assumption Ledger 和 Decision Log Entry。不得编造外部数据、人物原话或模型运行结果。

## Input Material

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
        print(f"dry-run prompt bundle generated for {record['decision_id']}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build a Super Board prompt bundle and decision record skeleton.")
    parser.add_argument("--input", required=True, help="Markdown input file to review.")
    parser.add_argument("--mode", default=DEFAULT_MODE, help=f"Review mode. Defaults to {DEFAULT_MODE}.")
    parser.add_argument("--output", help="Path for the generated prompt bundle Markdown.")
    parser.add_argument("--record", help="Path for the decision record JSON skeleton.")
    parser.add_argument("--dry-run", action="store_true", help="Do not call any model; only generate local artifacts.")
    return run(parser.parse_args(argv))


if __name__ == "__main__":
    sys.exit(main())
