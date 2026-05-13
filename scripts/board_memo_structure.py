#!/usr/bin/env python3
"""Shared structure rules for Super Board memo markdown."""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass


BOARD_MEMO_REQUIRED_SECTION_GROUPS = [
    ("# 《董事会建议书》", ["# 《董事会建议书》", "《董事会建议书》", "董事会建议书"]),
    ("一页结论", ["一页结论", "一句话结论", "董事会结论摘要", "最终董事会建议"]),
    ("输入材料与审议范围", ["输入材料与审议范围", "输入类型与审议范围", "输入材料结构化拆解"]),
    ("Go / No-Go / Pivot 建议", ["Go / No-Go / Pivot 建议", "推进 / 调整 / 不推进条件", "最终董事会建议"]),
    ("核心判断依据", ["核心判断依据", "核心判断", "董事会核心判断"]),
    ("五个委员会意见", ["五个委员会意见", "各委员会结论"]),
    ("跨委员会共识与关键分歧", ["跨委员会共识与关键分歧", "跨委员会共识", "关键分歧", "综合信号"]),
    ("最大机会、最大风险与反证路径", ["最大机会、最大风险与反证路径", "最大机会", "最大风险", "重大风险与缓释措施", "反证与失败路径", "需要补充验证的问题", "关键反证问题", "反证实验设计"]),
    ("30 / 60 / 90 天行动计划", ["30 / 60 / 90 天行动计划", "建议行动清单", "董事会建议行动计划", "90 天行动方案", "30 / 60 / 90 天行动方案", "30 / 60 / 90 天路线图"]),
    ("附录 A：证据包", ["附录 A：证据包", "证据包", "证据强度评级", "判断依据", "依据"]),
    ("附录 B：待验证假设", ["附录 B：待验证假设", "待验证假设", "假设账本", "核心假设表"]),
    ("附录 C：Persona 关键意见摘要", ["附录 C：Persona 关键意见摘要", "附录：各 Persona 关键意见摘要", "人物附录：委员会审议角色画像", "Persona 关键意见摘要"]),
    ("附录 D：决策记录", ["附录 D：决策记录", "决策记录条目", "决策记录"]),
]

BOARD_MEMO_CANONICAL_SECTIONS = [section for section, _aliases in BOARD_MEMO_REQUIRED_SECTION_GROUPS]
BOARD_MEMO_RESTART_SECTIONS = {"输入材料与审议范围", "一页结论", "核心判断依据", "附录 A：证据包", "附录 B：待验证假设", "五个委员会意见"}
BOARD_MEMO_TERMINAL_SECTIONS = {"附录 D：决策记录", "附录 C：Persona 关键意见摘要"}


@dataclass(frozen=True)
class MemoHeading:
    line: int
    level: int
    heading: str
    canonical: str


def strip_heading_numbering(heading: str) -> str:
    text = heading.strip()
    text = re.sub(r"^\s*第[一二三四五六七八九十百千万零〇两]+[章节部分]?[、.．:：\s-]*", "", text)
    text = re.sub(r"^\s*附录\s*[A-Z一二三四五六七八九十百千万零〇两\d]*[、.．:：\s-]*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"^\s*[一二三四五六七八九十百千万零〇两]+[、.．:：\s-]+", "", text)
    text = re.sub(r"^\s*\d+[\.\)、:：\s-]+", "", text)
    text = re.sub(r"^[A-Z][\.\)、:：\s-]+", "", text)
    return text.strip()


def normalize_heading(heading: str) -> str:
    text = heading.strip().lstrip("#").strip()
    text = strip_heading_numbering(text)
    text = re.sub(r"\s+", " ", text)
    for canonical, aliases in BOARD_MEMO_REQUIRED_SECTION_GROUPS:
        for alias in aliases:
            normalized_alias = strip_heading_numbering(alias.strip().lstrip("#").strip())
            if text == normalized_alias or normalized_alias in text:
                return canonical
    return text


def heading_sequence(markdown: str) -> list[MemoHeading]:
    headings: list[MemoHeading] = []
    in_fence = False
    for line_number, line in enumerate(markdown.splitlines(), start=1):
        stripped = line.strip()
        if stripped.startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        match = re.match(r"^(#{1,6})\s+(.+?)\s*$", line)
        if not match:
            continue
        raw_heading = match.group(2).strip()
        headings.append(
            MemoHeading(
                line=line_number,
                level=len(match.group(1)),
                heading=raw_heading,
                canonical=normalize_heading(raw_heading),
            )
        )
    return headings


def present_sections(markdown: str) -> set[str]:
    return {heading.canonical for heading in heading_sequence(markdown)}


def missing_markers(markdown: str) -> list[str]:
    present = present_sections(markdown)
    return [canonical for canonical in BOARD_MEMO_CANONICAL_SECTIONS if canonical not in present]


def has_duplicate_restart(markdown: str) -> bool:
    seen_terminal = False
    for heading in heading_sequence(markdown):
        if heading.canonical in BOARD_MEMO_TERMINAL_SECTIONS:
            seen_terminal = True
            continue
        if seen_terminal and heading.canonical in BOARD_MEMO_RESTART_SECTIONS:
            return True
    return False


def audit_text(markdown: str) -> list[dict[str, object]]:
    issues: list[dict[str, object]] = []
    headings = heading_sequence(markdown)
    seen_terminal = False
    for heading in headings:
        if heading.canonical in BOARD_MEMO_TERMINAL_SECTIONS:
            seen_terminal = True
            continue
        if seen_terminal and heading.canonical in BOARD_MEMO_RESTART_SECTIONS:
            issues.append(
                {
                    "code": "duplicate_restart",
                    "line": heading.line,
                    "message": f"终章之后重新出现主报告章节：{heading.heading}",
                }
            )
            break

    counts = Counter(heading.canonical for heading in headings)
    for canonical, count in sorted(counts.items()):
        if canonical in BOARD_MEMO_RESTART_SECTIONS and count > 1:
            lines = [heading.line for heading in headings if heading.canonical == canonical]
            issues.append(
                {
                    "code": "duplicate_section",
                    "section": canonical,
                    "lines": lines,
                    "message": f"章节重复出现 {count} 次：{canonical}",
                }
            )
    return issues


def split_markdown_blocks(text: str) -> list[tuple[str | None, str | None, str]]:
    in_fence = False
    matches: list[tuple[int, int, str]] = []
    for line in re.finditer(r"^.*$", text, flags=re.MULTILINE):
        stripped = line.group(0).strip()
        if stripped.startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        match = re.match(r"^(#{1,6})\s+(.+?)\s*$", line.group(0))
        if match:
            matches.append((line.start(), line.end(), match.group(2).strip()))

    if not matches:
        return [(None, None, text.strip())] if text.strip() else []

    blocks: list[tuple[str | None, str | None, str]] = []
    intro = text[: matches[0][0]].strip()
    if intro:
        blocks.append((None, None, intro))
    for index, (start, _line_end, heading) in enumerate(matches):
        end = matches[index + 1][0] if index + 1 < len(matches) else len(text)
        blocks.append((heading, normalize_heading(heading), text[start:end].strip()))
    return blocks


def merge_model_parts(parts: list[str]) -> str:
    merged_blocks: list[str] = []
    seen_sections: set[str] = set()
    for part_index, part in enumerate(parts):
        for _heading, canonical, block in split_markdown_blocks(part):
            if not block:
                continue
            if canonical is None:
                if part_index == 0:
                    merged_blocks.append(block)
                continue
            if canonical in seen_sections:
                continue
            merged_blocks.append(block)
            seen_sections.add(canonical)
    return "\n\n".join(merged_blocks).strip()
