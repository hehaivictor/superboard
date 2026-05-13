#!/usr/bin/env python3
"""Audit exported Super Board memo markdown for structural repetition."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from board_memo_structure import audit_text


def main() -> int:
    parser = argparse.ArgumentParser(description="审计 Super Board 建议书是否存在重复章节或报告重启。")
    parser.add_argument("memo", help="要审计的 Markdown 建议书路径。")
    parser.add_argument("--json", action="store_true", help="以 JSON 输出审计结果。")
    args = parser.parse_args()

    path = Path(args.memo)
    markdown = path.read_text(encoding="utf-8")
    issues = audit_text(markdown)
    if args.json:
        print(json.dumps({"path": str(path), "issues": issues}, ensure_ascii=False, indent=2))
    elif issues:
        for issue in issues:
            print(f"[{issue['code']}] line {issue.get('line', '-')}: {issue['message']}")
    else:
        print("Board memo audit passed.")
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
