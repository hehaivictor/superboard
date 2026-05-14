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
    ("本次审议席位", ["本次审议席位", "本次参与席位", "参与讨论席位", "参与席位"]),
    ("Go / No-Go / Pivot 建议", ["Go / No-Go / Pivot 建议", "推进 / 调整 / 不推进条件", "最终董事会建议"]),
    ("核心判断依据", ["核心判断依据", "核心判断", "董事会核心判断"]),
    ("委员会意见", ["委员会意见", "五个委员会意见", "七个委员会意见", "各委员会结论"]),
    ("席位代表观点", ["席位代表观点", "代表人物观点", "参与席位观点", "席位观点"]),
    ("跨委员会共识与关键分歧", ["跨委员会共识与关键分歧", "跨委员会共识", "关键分歧", "综合信号"]),
    ("最大机会、最大风险与反证路径", ["最大机会、最大风险与反证路径", "最大机会", "最大风险", "重大风险与缓释措施", "反证与失败路径", "需要补充验证的问题", "关键反证问题", "反证实验设计"]),
    ("30 / 60 / 90 天行动计划", ["30 / 60 / 90 天行动计划", "建议行动清单", "董事会建议行动计划", "90 天行动方案", "30 / 60 / 90 天行动方案", "30 / 60 / 90 天路线图"]),
    ("附录 A：证据包", ["附录 A：证据包", "证据包", "证据强度评级", "判断依据", "依据"]),
    ("附录 B：待验证假设", ["附录 B：待验证假设", "待验证假设", "假设账本", "核心假设表"]),
    ("附录 C：Persona 关键意见摘要", ["附录 C：Persona 关键意见摘要", "附录：各 Persona 关键意见摘要", "人物附录：委员会审议角色画像", "Persona 关键意见摘要"]),
    ("附录 D：决策记录", ["附录 D：决策记录", "决策记录条目", "决策记录"]),
]

BOARD_MEMO_CANONICAL_SECTIONS = [section for section, _aliases in BOARD_MEMO_REQUIRED_SECTION_GROUPS]
BOARD_MEMO_RESTART_SECTIONS = {"输入材料与审议范围", "一页结论", "本次审议席位", "核心判断依据", "附录 A：证据包", "附录 B：待验证假设", "委员会意见", "席位代表观点"}
BOARD_MEMO_TERMINAL_SECTIONS = {"附录 D：决策记录", "附录 C：Persona 关键意见摘要"}


@dataclass(frozen=True)
class MemoHeading:
    line: int
    level: int
    heading: str
    canonical: str


@dataclass(frozen=True)
class MemoSectionBlock:
    heading: str | None
    canonical: str | None
    block: str
    body: str


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
    for issue in required_content_issues(markdown):
        issues.append({"code": "missing_required_content", "message": issue})
    return issues


def split_main_section_blocks(text: str) -> list[MemoSectionBlock]:
    """Split only top-level Super Board sections, keeping nested headings inside the parent section."""
    in_fence = False
    matches: list[tuple[int, int, str, str]] = []
    for line in re.finditer(r"^.*$", text, flags=re.MULTILINE):
        stripped = line.group(0).strip()
        if stripped.startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        match = re.match(r"^(#{1,6})\s+(.+?)\s*$", line.group(0))
        if not match:
            continue
        level = len(match.group(1))
        raw_heading = match.group(2).strip()
        canonical = normalize_heading(raw_heading)
        if canonical in BOARD_MEMO_CANONICAL_SECTIONS and level <= 2:
            matches.append((line.start(), line.end(), raw_heading, canonical))

    if not matches:
        stripped = text.strip()
        return [MemoSectionBlock(None, None, stripped, stripped)] if stripped else []

    blocks: list[MemoSectionBlock] = []
    intro = text[: matches[0][0]].strip()
    if intro:
        blocks.append(MemoSectionBlock(None, None, intro, intro))
    for index, (start, heading_end, heading, canonical) in enumerate(matches):
        end = matches[index + 1][0] if index + 1 < len(matches) else len(text)
        block = text[start:end].strip()
        body = text[heading_end:end].strip()
        blocks.append(MemoSectionBlock(heading, canonical, block, body))
    return blocks


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


def meaningful_text(text: str) -> str:
    cleaned = re.sub(r"```[a-zA-Z0-9_-]*\n([\s\S]*?)```", r"\1", text)
    cleaned = re.sub(r"^#{1,6}\s+.*$", " ", cleaned, flags=re.MULTILINE)
    cleaned = re.sub(r"<!--[\s\S]*?-->", " ", cleaned)
    cleaned = re.sub(r"\{\{[^}]+\}\}", " ", cleaned)
    cleaned = re.sub(r"[*_`|>#\-\[\](){}:：,，.。;；\s]+", "", cleaned)
    return cleaned.strip()


def heading_body_blocks(text: str) -> list[tuple[int, str, str]]:
    in_fence = False
    matches: list[tuple[int, int, int, str]] = []
    for line in re.finditer(r"^.*$", text, flags=re.MULTILINE):
        stripped = line.group(0).strip()
        if stripped.startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        match = re.match(r"^(#{1,6})\s+(.+?)\s*$", line.group(0))
        if match:
            matches.append((line.start(), line.end(), len(match.group(1)), match.group(2).strip()))

    blocks: list[tuple[int, str, str]] = []
    for index, (_start, heading_end, level, heading) in enumerate(matches):
        end = len(text)
        for next_start, _next_heading_end, next_level, _next_heading in matches[index + 1 :]:
            if next_level <= level:
                end = next_start
                break
        blocks.append((level, heading, text[heading_end:end].strip()))
    return blocks


def dangling_subsection_issues(markdown: str) -> list[str]:
    issues: list[str] = []
    for level, heading, body in heading_body_blocks(markdown):
        if level < 3:
            continue
        meaningful = meaningful_text(body)
        if not meaningful:
            issues.append(f"{heading} 缺少实质正文")
            continue
        if len(meaningful) <= 2:
            issues.append(f"{heading} 正文疑似残句")
    return issues


def section_body_map(markdown: str) -> dict[str, str]:
    sections: dict[str, str] = {}
    for section in split_main_section_blocks(markdown):
        if section.canonical is None:
            continue
        if section.canonical not in sections or section_quality_score(section.canonical, section.body) > section_quality_score(section.canonical, sections[section.canonical]):
            sections[section.canonical] = section.body
    return sections


def has_any_marker(text: str, markers: list[str]) -> bool:
    return any(marker in text for marker in markers)


def required_content_issues(markdown: str) -> list[str]:
    issues: list[str] = []
    sections = section_body_map(markdown)
    issues.extend(dangling_subsection_issues(markdown))

    for canonical in BOARD_MEMO_CANONICAL_SECTIONS:
        if canonical == "# 《董事会建议书》":
            continue
        body = sections.get(canonical, "")
        if not meaningful_text(body):
            issues.append(f"{canonical} 缺少实质正文")

    consensus = sections.get("跨委员会共识与关键分歧", "")
    if consensus:
        if "强共识" not in consensus:
            issues.append("跨委员会共识与关键分歧 缺少强共识")
        if "关键分歧" not in consensus:
            issues.append("跨委员会共识与关键分歧 缺少关键分歧")

    risk = sections.get("最大机会、最大风险与反证路径", "")
    if risk:
        if "最大机会" not in risk:
            issues.append("最大机会、最大风险与反证路径 缺少最大机会")
        if "最大风险" not in risk:
            issues.append("最大机会、最大风险与反证路径 缺少最大风险")
        if not has_any_marker(risk, ["最强反证", "反证路径", "反证实验", "失败路径"]):
            issues.append("最大机会、最大风险与反证路径 缺少反证或失败路径")

    roadmap = sections.get("30 / 60 / 90 天行动计划", "")
    if roadmap and not all(marker in roadmap for marker in ["30", "60", "90"]):
        issues.append("30 / 60 / 90 天行动计划 缺少 30 / 60 / 90 检查点")

    return issues


def section_quality_score(canonical: str | None, body: str) -> int:
    if canonical is None:
        return len(meaningful_text(body))
    score = min(len(meaningful_text(body)), 1000)
    if canonical == "跨委员会共识与关键分歧":
        score += 200 if "强共识" in body else 0
        score += 200 if "关键分歧" in body else 0
    if canonical == "最大机会、最大风险与反证路径":
        score += 200 if "最大机会" in body else 0
        score += 200 if "最大风险" in body else 0
        score += 200 if has_any_marker(body, ["最强反证", "反证路径", "反证实验", "失败路径"]) else 0
    if canonical == "30 / 60 / 90 天行动计划":
        score += 120 if "30" in body else 0
        score += 120 if "60" in body else 0
        score += 120 if "90" in body else 0
    return score


def merge_model_parts(parts: list[str]) -> str:
    merged_blocks: list[MemoSectionBlock] = []
    section_indexes: dict[str, int] = {}
    for part_index, part in enumerate(parts):
        for section in split_main_section_blocks(part):
            if not section.block:
                continue
            if section.canonical is None:
                if part_index == 0:
                    merged_blocks.append(section)
                continue
            if section.canonical in section_indexes:
                existing_index = section_indexes[section.canonical]
                existing = merged_blocks[existing_index]
                if section_quality_score(section.canonical, section.body) > section_quality_score(existing.canonical, existing.body):
                    merged_blocks[existing_index] = section
                continue
            section_indexes[section.canonical] = len(merged_blocks)
            merged_blocks.append(section)
    return "\n\n".join(section.block for section in merged_blocks).strip()
