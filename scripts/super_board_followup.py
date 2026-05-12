#!/usr/bin/env python3
"""Generate follow-up review prompts from Super Board decision records."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VALID_CHECKPOINTS = {30, 60, 90}


def render_followup(record: dict[str, object], checkpoint: int) -> str:
    assumptions = record.get("assumptions", [])
    assumption_lines = "\n".join(
        f"- {item.get('assumption', item)}" if isinstance(item, dict) else f"- {item}" for item in assumptions
    )
    evidence = record.get("evidence_packets", [])
    evidence_lines = "\n".join(
        f"- {item.get('claim', item)}" if isinstance(item, dict) else f"- {item}" for item in evidence
    )
    return f"""# Super Board Follow-up Prompt

## Record

- 决策编号：{record.get("decision_id")}
- 标题：{record.get("title")}
- 审议模式：{record.get("mode_id")}
- 原始建议：{record.get("decision")}
- 当前检查点：{checkpoint} 天

## Key Assumptions

{assumption_lines or "- 未记录"}

## Evidence Packets

{evidence_lines or "- 未记录"}

## Review Instructions

使用 `templates/follow-up-review.md` 输出复盘审查。必须记录实际结果、假设命中情况、误判原因、下次调整和新的 Go / Pivot / No-Go 建议。不要补造不存在的结果；如果缺少结果证据，明确列出需要补充的事实。
"""


def run(args: argparse.Namespace) -> int:
    checkpoint = int(args.checkpoint)
    if checkpoint not in VALID_CHECKPOINTS:
        print("--checkpoint must be one of 30, 60, 90", file=sys.stderr)
        return 2

    record_path = Path(args.record).expanduser().resolve()
    if not record_path.is_file():
        print(f"record file not found: {record_path}", file=sys.stderr)
        return 2

    record = json.loads(record_path.read_text(encoding="utf-8"))
    content = render_followup(record, checkpoint)
    if args.output:
        output_path = Path(args.output).expanduser()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(content, encoding="utf-8")
    else:
        print(content)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate a Super Board follow-up review prompt.")
    parser.add_argument("--record", required=True, help="Decision record JSON path.")
    parser.add_argument("--checkpoint", required=True, choices=["30", "60", "90"], help="Follow-up checkpoint day.")
    parser.add_argument("--output", help="Path for the generated follow-up prompt.")
    return run(parser.parse_args(argv))


if __name__ == "__main__":
    sys.exit(main())
