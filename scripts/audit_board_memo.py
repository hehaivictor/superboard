#!/usr/bin/env python3
"""Audit exported Super Board memo markdown for structural repetition."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path


TERMINAL_SECTIONS = {"决策记录条目", "附录：各 Persona 关键意见摘要"}
RESTART_SECTIONS = {"输入类型与审议范围", "一句话结论", "核心判断", "证据包", "假设账本", "各委员会结论"}
ALIASES = {
    "人物附录：委员会审议角色画像": "附录：各 Persona 关键意见摘要",
    "最终董事会建议": "最终董事会建议",
    "董事会结论摘要": "一句话结论",
    "董事会核心判断": "核心判断",
}


def strip_heading_numbering(heading: str) -> str:
    text = heading.strip()
    text = re.sub(r"^\s*第[一二三四五六七八九十百千万零〇两]+[章节部分]?[、.．:：\s-]*", "", text)
    text = re.sub(r"^\s*[一二三四五六七八九十百千万零〇两]+[、.．:：\s-]+", "", text)
    text = re.sub(r"^\s*\d+[\.\)、:：\s-]+", "", text)
    text = re.sub(r"^[A-Z][\.\)、:：\s-]+", "", text)
    return text.strip()


def normalize_heading(heading: str) -> str:
    text = strip_heading_numbering(heading.strip().lstrip("#").strip())
    text = re.sub(r"\s+", " ", text)
    for alias, canonical in ALIASES.items():
        if text == alias or alias in text:
            return canonical
    return text


def heading_sequence(markdown: str) -> list[dict[str, object]]:
    headings: list[dict[str, object]] = []
    for line_number, line in enumerate(markdown.splitlines(), start=1):
        match = re.match(r"^##\s+(.+?)\s*$", line)
        if not match:
            continue
        raw = match.group(1).strip()
        headings.append({"line": line_number, "heading": raw, "canonical": normalize_heading(raw)})
    return headings


def audit_text(markdown: str) -> list[dict[str, object]]:
    issues: list[dict[str, object]] = []
    headings = heading_sequence(markdown)
    seen_terminal = False
    for item in headings:
        canonical = str(item["canonical"])
        if canonical in TERMINAL_SECTIONS:
            seen_terminal = True
            continue
        if seen_terminal and canonical in RESTART_SECTIONS:
            issues.append(
                {
                    "code": "duplicate_restart",
                    "line": item["line"],
                    "message": f"终章之后重新出现主报告章节：{item['heading']}",
                }
            )
            break

    counts = Counter(str(item["canonical"]) for item in headings)
    for canonical, count in sorted(counts.items()):
        if canonical in RESTART_SECTIONS and count > 1:
            lines = [item["line"] for item in headings if item["canonical"] == canonical]
            issues.append(
                {
                    "code": "duplicate_section",
                    "section": canonical,
                    "lines": lines,
                    "message": f"章节重复出现 {count} 次：{canonical}",
                }
            )
    return issues


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
