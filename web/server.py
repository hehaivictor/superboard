#!/usr/bin/env python3
"""Local Super Board workbench server."""

from __future__ import annotations

import json
import mimetypes
import os
import re
import sys
import hashlib
import threading
import urllib.error
import urllib.request
import uuid
from datetime import datetime, timezone
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse


WEB_ROOT = Path(__file__).resolve().parent
ROOT = WEB_ROOT.parent
DIST_ROOT = WEB_ROOT / "dist"
PORT = 8766
MODEL_CONFIG_PATH = ROOT / ".super-board-model.json"
GENERATION_JOBS: dict[str, dict[str, object]] = {}
GENERATION_JOBS_LOCK = threading.Lock()
DEFAULT_MODEL_TIMEOUT = 240
DEFAULT_MODEL_MAX_TOKENS = 16000
DEFAULT_MODEL_CONTINUATIONS = 3

BOARD_MEMO_REQUIRED_SECTION_GROUPS = [
    ("# 《董事会建议书》", ["# 《董事会建议书》"]),
    ("输入类型与审议范围", ["输入类型与审议范围", "输入材料结构化拆解"]),
    ("一句话结论", ["一句话结论", "董事会结论摘要", "最终董事会建议"]),
    ("Go / No-Go / Pivot 建议", ["Go / No-Go / Pivot 建议", "推进 / 调整 / 不推进条件", "最终董事会建议"]),
    ("核心判断", ["核心判断", "董事会核心判断"]),
    ("证据包", ["证据包"]),
    ("假设账本", ["假设账本"]),
    ("各委员会结论", ["各委员会结论"]),
    ("跨委员会共识", ["跨委员会共识", "综合信号"]),
    ("关键分歧", ["关键分歧"]),
    ("最大机会", ["最大机会"]),
    ("最大风险", ["最大风险", "重大风险与缓释措施"]),
    ("建议行动清单", ["建议行动清单", "90 天行动方案"]),
    ("需要补充验证的问题", ["需要补充验证的问题", "关键反证问题", "反证实验设计"]),
    ("附录：各 Persona 关键意见摘要", ["附录：各 Persona 关键意见摘要", "人物附录：委员会审议角色画像"]),
    ("决策记录条目", ["决策记录条目"]),
]

BOARD_MEMO_CANONICAL_SECTIONS = [section for section, _aliases in BOARD_MEMO_REQUIRED_SECTION_GROUPS]
BOARD_MEMO_RESTART_SECTIONS = {"输入类型与审议范围", "一句话结论", "核心判断", "证据包", "假设账本", "各委员会结论"}
BOARD_MEMO_TERMINAL_SECTIONS = {"决策记录条目", "附录：各 Persona 关键意见摘要"}

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

sys.path.insert(0, str(ROOT / "scripts"))
from super_board_run import build_board_memo, build_material_pack_from_text, build_prompt_bundle, build_record, load_modes  # noqa: E402


def template_version() -> str:
    template_path = ROOT / "templates" / "board-memo.md"
    return str(int(template_path.stat().st_mtime)) if template_path.is_file() else "unknown"


def json_response(handler: BaseHTTPRequestHandler, payload: object, status: HTTPStatus = HTTPStatus.OK) -> None:
    body = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


def read_json(handler: BaseHTTPRequestHandler) -> dict[str, object]:
    length = int(handler.headers.get("Content-Length", "0"))
    body = handler.rfile.read(length).decode("utf-8")
    return json.loads(body or "{}")


def stable_id(prefix: str, value: str) -> str:
    digest = hashlib.sha1(value.encode("utf-8")).hexdigest()[:10]
    return f"{prefix}-{digest}"


def load_local_model_config() -> dict[str, object]:
    if not MODEL_CONFIG_PATH.is_file():
        return {}
    try:
        payload = json.loads(MODEL_CONFIG_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def model_config() -> dict[str, object]:
    local = load_local_model_config()
    base_url = str(
        os.environ.get("SUPER_BOARD_LLM_BASE_URL")
        or local.get("base_url")
        or os.environ.get("OPENAI_BASE_URL")
        or "https://api.openai.com/v1"
    ).rstrip("/")
    model = str(
        os.environ.get("SUPER_BOARD_LLM_MODEL")
        or local.get("model")
        or os.environ.get("OPENAI_MODEL")
        or "gpt-4.1"
    )
    api_key = str(os.environ.get("SUPER_BOARD_LLM_API_KEY") or local.get("api_key") or os.environ.get("OPENAI_API_KEY") or "")
    timeout = int(os.environ.get("SUPER_BOARD_LLM_TIMEOUT") or local.get("timeout") or DEFAULT_MODEL_TIMEOUT)
    max_tokens = int(os.environ.get("SUPER_BOARD_LLM_MAX_TOKENS") or local.get("max_tokens") or DEFAULT_MODEL_MAX_TOKENS)
    continuations = int(
        os.environ.get("SUPER_BOARD_LLM_CONTINUATIONS")
        or local.get("continuations")
        or DEFAULT_MODEL_CONTINUATIONS
    )
    temperature = float(os.environ.get("SUPER_BOARD_LLM_TEMPERATURE") or local.get("temperature") or 0.2)
    missing = []
    if not api_key:
        missing.append("SUPER_BOARD_LLM_API_KEY 或 OPENAI_API_KEY")
    if not model:
        missing.append("SUPER_BOARD_LLM_MODEL 或 OPENAI_MODEL")
    return {
        "configured": len(missing) == 0,
        "base_url": base_url,
        "model": model,
        "api_key": api_key,
        "timeout": timeout,
        "max_tokens": max_tokens,
        "continuations": continuations,
        "temperature": temperature,
        "missing": missing,
        "config_file": str(MODEL_CONFIG_PATH.relative_to(ROOT)),
    }


def public_model_config() -> dict[str, object]:
    config = model_config()
    return {
        "configured": config["configured"],
        "base_url": config["base_url"],
        "model": config["model"],
        "missing": config["missing"],
        "config_file": config["config_file"],
        "timeout": config["timeout"],
        "max_tokens": config["max_tokens"],
        "continuations": config["continuations"],
    }


def chat_completions_url(base_url: str) -> str:
    return base_url if base_url.endswith("/chat/completions") else f"{base_url}/chat/completions"


def normalize_model_error(status_code: int, detail: str) -> str:
    request_id = ""
    if status_code == 504 or "Gateway Time-out" in detail or "Gateway Timeout" in detail:
        return "模型网关生成超时。已连接到模型服务，但上游网关在建议书生成完成前断开，请稍后重试或减少材料长度。"
    try:
        payload = json.loads(detail)
        error = payload.get("error")
        if isinstance(error, dict):
            message = str(error.get("message") or "")
            request_id = str(error.get("request_id") or "")
        else:
            message = str(payload.get("message") or "")
    except json.JSONDecodeError:
        message = detail

    if "额度不足" in message or "余额" in message or "insufficient" in message.lower() or "quota" in message.lower():
        suffix = f" request_id: {request_id}" if request_id else ""
        return f"模型账户额度不足，请充值或更换可用 API Key 后重试。{suffix}"
    return f"模型接口返回 {status_code}：{message or detail}"


def strip_heading_numbering(heading: str) -> str:
    text = heading.strip()
    text = re.sub(r"^\s*第[一二三四五六七八九十百千万零〇两]+[章节部分]?[、.．:：\s-]*", "", text)
    text = re.sub(r"^\s*[一二三四五六七八九十百千万零〇两]+[、.．:：\s-]+", "", text)
    text = re.sub(r"^\s*\d+[\.\)、:：\s-]+", "", text)
    text = re.sub(r"^[A-Z][\.\)、:：\s-]+", "", text)
    return text.strip()


def normalize_board_memo_heading(heading: str) -> str:
    text = heading.strip().lstrip("#").strip()
    text = strip_heading_numbering(text)
    text = re.sub(r"\s+", " ", text)
    for canonical, aliases in BOARD_MEMO_REQUIRED_SECTION_GROUPS:
        if canonical.startswith("# "):
            continue
        for alias in aliases:
            if text == alias or alias in text:
                return canonical
    return text


def board_memo_heading_sequence(board_memo: str) -> list[tuple[int, str, str]]:
    headings: list[tuple[int, str, str]] = []
    for line_number, line in enumerate(board_memo.splitlines(), start=1):
        match = re.match(r"^##\s+(.+?)\s*$", line)
        if not match:
            continue
        raw_heading = match.group(1).strip()
        headings.append((line_number, raw_heading, normalize_board_memo_heading(raw_heading)))
    return headings


def board_memo_present_sections(board_memo: str) -> set[str]:
    present = {canonical for _line_number, _raw, canonical in board_memo_heading_sequence(board_memo)}
    if "# 《董事会建议书》" in board_memo:
        present.add("# 《董事会建议书》")
    return present


def board_memo_missing_markers(board_memo: str) -> list[str]:
    present = board_memo_present_sections(board_memo)
    return [canonical for canonical in BOARD_MEMO_CANONICAL_SECTIONS if canonical not in present]


def board_memo_has_duplicate_restart(board_memo: str) -> bool:
    seen_terminal = False
    for _line_number, _raw, canonical in board_memo_heading_sequence(board_memo):
        if canonical in BOARD_MEMO_TERMINAL_SECTIONS:
            seen_terminal = True
            continue
        if seen_terminal and canonical in BOARD_MEMO_RESTART_SECTIONS:
            return True
    return False


def board_memo_is_complete(board_memo: str) -> bool:
    if not board_memo.strip():
        return False
    return not board_memo_missing_markers(board_memo) and not board_memo_has_duplicate_restart(board_memo)


def split_markdown_h2_blocks(text: str) -> list[tuple[str | None, str | None, str]]:
    matches = list(re.finditer(r"^##\s+(.+?)\s*$", text, flags=re.MULTILINE))
    if not matches:
        return [(None, None, text.strip())] if text.strip() else []
    blocks: list[tuple[str | None, str | None, str]] = []
    intro = text[: matches[0].start()].strip()
    if intro:
        blocks.append((None, None, intro))
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        heading = match.group(1).strip()
        blocks.append((heading, normalize_board_memo_heading(heading), text[match.start() : end].strip()))
    return blocks


def merge_model_parts(parts: list[str]) -> str:
    merged_blocks: list[str] = []
    seen_sections: set[str] = set()
    for part_index, part in enumerate(parts):
        for _heading, canonical, block in split_markdown_h2_blocks(part):
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


def continuation_prompt(missing_markers: list[str], finish_reason: str) -> str:
    missing = "\n".join(f"- {marker}" for marker in missing_markers) or "- 未检测到缺失章节，但上一段达到长度上限。"
    return (
        "上一段《董事会建议书》输出未完整结束。"
        f"finish_reason={finish_reason or 'unknown'}。\n\n"
        "只输出缺失章节，不要从头重写报告，不要重复已经存在的章节。"
        "禁止再次输出“输入类型与审议范围”“一句话结论”“核心判断”等已存在章节，除非它们列在缺失章节中。"
        "从当前最后一个章节之后继续，保持中文、证据约束和 Mermaid 代码块格式。\n\n"
        f"当前仍缺少的关键章节：\n{missing}"
    )


def read_streaming_chat_completion(response: object) -> tuple[str, str]:
    chunks: list[str] = []
    finish_reason = ""
    while True:
        raw_line = response.readline()
        if not raw_line:
            break
        line = raw_line.decode("utf-8", errors="replace").strip()
        if not line or line.startswith(":"):
            continue
        if not line.startswith("data:"):
            continue
        data = line[5:].strip()
        if data == "[DONE]":
            break
        try:
            payload = json.loads(data)
        except json.JSONDecodeError:
            continue
        choices = payload.get("choices", [])
        if not choices or not isinstance(choices[0], dict):
            continue
        choice = choices[0]
        if choice.get("finish_reason"):
            finish_reason = str(choice["finish_reason"])
        delta = choice.get("delta", {})
        if isinstance(delta, dict) and delta.get("content"):
            chunks.append(str(delta["content"]))
            continue
        message = choice.get("message", {})
        if isinstance(message, dict) and message.get("content"):
            chunks.append(str(message["content"]))
    return "".join(chunks).strip(), finish_reason


def call_streaming_chat_completion(messages: list[dict[str, str]], config: dict[str, object]) -> tuple[str, str]:
    body = json.dumps(
        {
            "model": config["model"],
            "messages": messages,
            "temperature": config["temperature"],
            "max_tokens": config["max_tokens"],
            "stream": True,
        },
        ensure_ascii=False,
    ).encode("utf-8")
    request = urllib.request.Request(
        chat_completions_url(str(config["base_url"])),
        data=body,
        headers={
            "Authorization": f"Bearer {config['api_key']}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=int(config["timeout"])) as response:
            return read_streaming_chat_completion(response)
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:1000]
        api_key = str(config.get("api_key", ""))
        if api_key:
            detail = detail.replace(api_key, "[redacted]")
        raise RuntimeError(normalize_model_error(exc.code, detail)) from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"模型接口不可达：{exc.reason}") from exc


def call_model(prompt_bundle: str, config: dict[str, object]) -> str:
    messages = [
        {
            "role": "system",
            "content": (
                "你是 Super Board 的董事会审议生成器。"
                "必须根据用户提供的提示包输出中文《董事会建议书》。"
                "不得编造外部事实；无法由来源块支持的内容必须标注为推断或假设。"
                "必须包含证据包、假设账本、反证实验、推进/调整/不推进条件和决策记录条目。"
            ),
        },
        {"role": "user", "content": prompt_bundle},
    ]
    parts: list[str] = []
    finish_reasons: list[str] = []
    max_continuations = max(0, int(config.get("continuations", DEFAULT_MODEL_CONTINUATIONS)))

    for attempt in range(max_continuations + 1):
        text, finish_reason = call_streaming_chat_completion(messages, config)
        if text:
            parts.append(text)
        finish_reasons.append(finish_reason or "")
        board_memo = merge_model_parts(parts)
        missing_markers = board_memo_missing_markers(board_memo)

        if board_memo and finish_reason != "length" and not missing_markers and not board_memo_has_duplicate_restart(board_memo):
            return board_memo

        if attempt >= max_continuations:
            if not board_memo:
                raise RuntimeError("模型响应中没有可用正文。")
            missing_text = "、".join(missing_markers) if missing_markers else "无"
            duplicate_text = "；检测到报告重复重启" if board_memo_has_duplicate_restart(board_memo) else ""
            raise RuntimeError(
                "模型输出疑似截断或未按董事会模板补齐，已停止展示半截报告。"
                f"finish_reason 序列：{', '.join(reason or 'unknown' for reason in finish_reasons)}；"
                f"缺失章节：{missing_text}{duplicate_text}；"
                f"已生成字符数：{len(board_memo)}。"
                "请提高 SUPER_BOARD_LLM_MAX_TOKENS / continuations，或缩短输入材料后重试。"
            )

        context_tail = text or board_memo[-12000:]
        messages.append({"role": "assistant", "content": context_tail[-12000:]})
        messages.append({"role": "user", "content": continuation_prompt(missing_markers, finish_reason)})

    raise RuntimeError("模型生成未能完成。")


def call_model_non_streaming(prompt_bundle: str, config: dict[str, object]) -> str:
    body = json.dumps(
        {
            "model": config["model"],
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "你是 Super Board 的董事会审议生成器。"
                        "必须根据用户提供的提示包输出中文《董事会建议书》。"
                        "不得编造外部事实；无法由来源块支持的内容必须标注为推断或假设。"
                        "必须包含证据包、假设账本、反证实验、推进/调整/不推进条件和决策记录条目。"
                    ),
                },
                {"role": "user", "content": prompt_bundle},
            ],
            "temperature": config["temperature"],
            "max_tokens": config["max_tokens"],
        },
        ensure_ascii=False,
    ).encode("utf-8")
    request = urllib.request.Request(
        chat_completions_url(str(config["base_url"])),
        data=body,
        headers={
            "Authorization": f"Bearer {config['api_key']}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=int(config["timeout"])) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:1000]
        api_key = str(config.get("api_key", ""))
        if api_key:
            detail = detail.replace(api_key, "[redacted]")
        raise RuntimeError(normalize_model_error(exc.code, detail)) from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"模型接口不可达：{exc.reason}") from exc

    choices = payload.get("choices", [])
    if choices and isinstance(choices[0], dict):
        message = choices[0].get("message", {})
        if isinstance(message, dict) and message.get("content"):
            return str(message["content"]).strip()
    if payload.get("output_text"):
        return str(payload["output_text"]).strip()
    raise RuntimeError("模型响应中没有可用正文。")


def build_preview_payload(material: str, mode_id: str, material_pack: object) -> dict[str, object]:
    modes = load_modes(ROOT)
    if mode_id not in modes:
        raise ValueError(f"unknown mode: {mode_id}")
    input_path = ROOT / "inline-input.md"
    record = build_record(
        input_path,
        material,
        modes[mode_id],
        material_pack if isinstance(material_pack, dict) else None,
    )
    prompt_bundle = build_prompt_bundle(input_path, material, modes[mode_id], record)
    board_memo = build_board_memo(input_path, material, modes[mode_id], record)
    record["board_memo"] = board_memo
    return {
        "record": record,
        "board_memo": board_memo,
        "prompt_bundle": prompt_bundle,
        "evidence_packets": record["evidence_packets"],
        "assumptions": record["assumptions"],
        "material_pack": record["material_pack"],
        "review_run": record["review_run"],
        "action_items": record["action_items"],
        "calibration_events": record["calibration_events"],
        "generated_by": "local_draft",
    }


def attach_model_memo(payload: dict[str, object], board_memo: str, config: dict[str, object]) -> dict[str, object]:
    record = payload["record"]
    assert isinstance(record, dict)
    generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    prompt_bundle = str(payload.get("prompt_bundle", ""))
    record["board_memo"] = board_memo
    record["generation"] = {
        "source": "model",
        "model": config["model"],
        "base_url": config["base_url"],
        "generated_at": generated_at,
        "prompt_hash": hashlib.sha256(prompt_bundle.encode("utf-8")).hexdigest()[:16],
        "output_chars": len(board_memo),
        "missing_required_sections": board_memo_missing_markers(board_memo),
        "max_tokens": config.get("max_tokens"),
        "continuations": config.get("continuations"),
    }
    payload["board_memo"] = board_memo
    payload["generated_by"] = "model"
    payload["generation"] = record["generation"]
    return payload


def update_generation_job(job_id: str, values: dict[str, object]) -> None:
    with GENERATION_JOBS_LOCK:
        job = GENERATION_JOBS.setdefault(job_id, {})
        job.update(values)


def read_generation_job(job_id: str) -> dict[str, object] | None:
    with GENERATION_JOBS_LOCK:
        job = GENERATION_JOBS.get(job_id)
        return dict(job) if job else None


def start_generation_job(material: str, mode_id: str, material_pack: object, config: dict[str, object]) -> str:
    job_id = f"gen-{uuid.uuid4().hex[:12]}"
    update_generation_job(
        job_id,
        {
            "job_id": job_id,
            "status": "running",
            "created_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
            "model": config["model"],
        },
    )

    def run_job() -> None:
        try:
            response_payload = build_preview_payload(material, mode_id, material_pack)
            prompt_bundle = str(response_payload["prompt_bundle"])
            update_generation_job(job_id, {"status": "calling_model", "prompt_hash": hashlib.sha256(prompt_bundle.encode("utf-8")).hexdigest()[:16]})
            board_memo = call_model(prompt_bundle, config)
            result = attach_model_memo(response_payload, board_memo, config)
            update_generation_job(
                job_id,
                {
                    "status": "succeeded",
                    "finished_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
                    "result": result,
                },
            )
        except Exception as exc:
            update_generation_job(
                job_id,
                {
                    "status": "failed",
                    "finished_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
                    "error": str(exc),
                },
            )

    threading.Thread(target=run_job, daemon=True).start()
    return job_id


def build_material_pack_from_files(files: list[dict[str, object]]) -> dict[str, object]:
    combined_text = "\n\n".join(str(item.get("content", "")) for item in files)
    pack_id = stable_id("pack", combined_text[:500] or datetime.now(timezone.utc).isoformat())
    source_blocks: list[dict[str, object]] = []
    file_entries: list[dict[str, object]] = []
    warnings: list[str] = []

    for file_index, item in enumerate(files, start=1):
        name = str(item.get("name", f"material-{file_index}.txt"))
        content = str(item.get("content", ""))
        file_id = stable_id("file", f"{name}|{file_index}")
        if not content.strip():
            warnings.append(f"{name} 内容为空或未能读取。")
        file_entries.append(
            {
                "file_id": file_id,
                "name": name,
                "size": int(item.get("size", len(content.encode("utf-8"))) or 0),
                "type": str(item.get("type", Path(name).suffix.lstrip(".") or "text")),
                "status": "read" if content.strip() else "empty",
            }
        )
        base_pack = build_material_pack_from_text(Path(name), content)
        for block_index, block in enumerate(base_pack["source_blocks"], start=1):
            source_blocks.append(
                {
                    "block_id": f"src-{len(source_blocks) + 1:03d}",
                    "file_id": file_id,
                    "source_file": name,
                    "text": block["text"],
                    "local_index": block_index,
                }
            )

    title = "多文件审议材料包"
    for item in files:
        content = str(item.get("content", ""))
        for line in content.splitlines():
            stripped = line.strip()
            if stripped.startswith("#"):
                title = stripped.lstrip("#").strip() or title
                break
        if title != "多文件审议材料包":
            break

    return {
        "pack_id": pack_id,
        "title": title,
        "files": file_entries,
        "source_blocks": source_blocks,
        "warnings": warnings,
    }


def record_path_for(decision_id: str) -> Path:
    return ROOT / "records" / f"{decision_id}.json"


def list_records() -> list[dict[str, object]]:
    records = []
    for path in sorted((ROOT / "records").glob("*.json"), key=lambda item: item.stat().st_mtime, reverse=True):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        records.append(
            {
                "decision_id": payload.get("decision_id", path.stem),
                "title": payload.get("title", path.stem),
                "mode_id": payload.get("mode_id", ""),
                "decision": payload.get("decision", ""),
                "created_at": payload.get("created_at", ""),
            }
        )
    return records


def render_record_markdown(record: dict[str, object]) -> str:
    evidence = record.get("evidence_packets", [])
    assumptions = record.get("assumptions", [])
    actions = record.get("action_items", [])
    return "\n".join(
        [
            f"# 决策记录：{record.get('title', '')}",
            "",
            f"- 决策编号：{record.get('decision_id', '')}",
            f"- 审议模式：{MODE_LABELS.get(str(record.get('mode_id', '')), record.get('mode_id', ''))}",
            f"- 当前建议：{DECISION_LABELS.get(str(record.get('decision', '')), record.get('decision', ''))}",
            "",
            "## 证据包",
            "```json",
            json.dumps(evidence, ensure_ascii=False, indent=2),
            "```",
            "",
            "## 假设账本",
            "```json",
            json.dumps(assumptions, ensure_ascii=False, indent=2),
            "```",
            "",
            "## 行动项",
            "```json",
            json.dumps(actions, ensure_ascii=False, indent=2),
            "```",
            "",
        ]
    )


def render_record_html(record: dict[str, object]) -> str:
    markdown = render_record_markdown(record)
    escaped = (
        markdown.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <title>{record.get('title', 'Super Board')}</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; margin: 40px; color: #0f172a; }}
    pre {{ white-space: pre-wrap; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 16px; }}
  </style>
</head>
<body><pre>{escaped}</pre></body>
</html>
"""


class Handler(BaseHTTPRequestHandler):
    def log_message(self, format: str, *args: object) -> None:
        return

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/api/config":
            modes = list(load_modes(ROOT).values())
            json_response(
                self,
                {
                    "board_id": "default",
                    "modes": modes,
                    "template_version": template_version(),
                    "llm": public_model_config(),
                },
            )
            return
        if parsed.path == "/api/records":
            json_response(self, {"records": list_records()})
            return
        if parsed.path.startswith("/api/records/"):
            parts = parsed.path.strip("/").split("/")
            if len(parts) >= 3:
                decision_id = parts[2]
                record_path = record_path_for(decision_id)
                if not record_path.is_file():
                    json_response(self, {"error": "record not found"}, HTTPStatus.NOT_FOUND)
                    return
                record = json.loads(record_path.read_text(encoding="utf-8"))
                if len(parts) == 3:
                    json_response(self, record)
                    return
                if len(parts) == 4 and parts[3] == "export":
                    fmt = dict(item.split("=", 1) for item in parsed.query.split("&") if "=" in item).get("format", "markdown")
                    if fmt == "json":
                        json_response(self, record)
                        return
                    if fmt == "html":
                        body = render_record_html(record).encode("utf-8")
                        self.send_response(HTTPStatus.OK)
                        self.send_header("Content-Type", "text/html; charset=utf-8")
                        self.send_header("Content-Length", str(len(body)))
                        self.end_headers()
                        self.wfile.write(body)
                        return
                    body = render_record_markdown(record).encode("utf-8")
                    self.send_response(HTTPStatus.OK)
                    self.send_header("Content-Type", "text/markdown; charset=utf-8")
                    self.send_header("Content-Length", str(len(body)))
                    self.end_headers()
                    self.wfile.write(body)
                    return
        if parsed.path.startswith("/api/jobs/"):
            parts = parsed.path.strip("/").split("/")
            if len(parts) == 3:
                job = read_generation_job(parts[2])
                if not job:
                    json_response(self, {"error": "job not found"}, HTTPStatus.NOT_FOUND)
                    return
                json_response(self, job)
                return
        self.serve_static(parsed.path)

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/api/materials/preview":
            payload = read_json(self)
            raw_files = payload.get("files", [])
            if not isinstance(raw_files, list):
                json_response(self, {"error": "files must be an array"}, HTTPStatus.BAD_REQUEST)
                return
            pack = build_material_pack_from_files([item for item in raw_files if isinstance(item, dict)])
            json_response(self, {"material_pack": pack})
            return
        if parsed.path == "/api/preview":
            payload = read_json(self)
            material = str(payload.get("material", "")).strip()
            mode_id = str(payload.get("mode_id", "deep_board_review"))
            material_pack = payload.get("material_pack")
            if not material:
                json_response(self, {"error": "material is required"}, HTTPStatus.BAD_REQUEST)
                return
            try:
                json_response(self, build_preview_payload(material, mode_id, material_pack))
            except ValueError as exc:
                json_response(self, {"error": str(exc)}, HTTPStatus.BAD_REQUEST)
                return
            return
        if parsed.path == "/api/generate":
            payload = read_json(self)
            material = str(payload.get("material", "")).strip()
            mode_id = str(payload.get("mode_id", "deep_board_review"))
            material_pack = payload.get("material_pack")
            if not material:
                json_response(self, {"error": "material is required"}, HTTPStatus.BAD_REQUEST)
                return
            config = model_config()
            if not config["configured"]:
                json_response(
                    self,
                    {
                        "error": "模型未配置",
                        "missing": config["missing"],
                        "hint": "设置环境变量 SUPER_BOARD_LLM_API_KEY / SUPER_BOARD_LLM_MODEL / SUPER_BOARD_LLM_BASE_URL，或创建本地 .super-board-model.json。",
                        "config_file": config["config_file"],
                    },
                    HTTPStatus.BAD_REQUEST,
                )
                return
            try:
                modes = load_modes(ROOT)
                if mode_id not in modes:
                    json_response(self, {"error": f"unknown mode: {mode_id}"}, HTTPStatus.BAD_REQUEST)
                    return
                job_id = start_generation_job(material, mode_id, material_pack, config)
                json_response(
                    self,
                    {
                        "job_id": job_id,
                        "status": "running",
                        "model": config["model"],
                    },
                    HTTPStatus.ACCEPTED,
                )
            except ValueError as exc:
                json_response(self, {"error": str(exc)}, HTTPStatus.BAD_REQUEST)
            except RuntimeError as exc:
                json_response(self, {"error": str(exc)}, HTTPStatus.BAD_GATEWAY)
            return
        if parsed.path == "/api/record":
            payload = read_json(self)
            decision_id = str(payload.get("decision_id", "")).strip()
            if not decision_id:
                json_response(self, {"error": "decision_id is required"}, HTTPStatus.BAD_REQUEST)
                return
            record_path = record_path_for(decision_id)
            record_path.parent.mkdir(parents=True, exist_ok=True)
            record_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            json_response(self, {"ok": True, "path": str(record_path.relative_to(ROOT))})
            return
        if parsed.path == "/api/calibration":
            payload = read_json(self)
            decision_id = str(payload.get("decision_id", "")).strip()
            if not decision_id:
                json_response(self, {"error": "decision_id is required"}, HTTPStatus.BAD_REQUEST)
                return
            event_id = stable_id("cal", json.dumps(payload, ensure_ascii=False) + datetime.now(timezone.utc).isoformat())
            event = {
                "event_id": event_id,
                "decision_id": decision_id,
                "created_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
                "mode_id": payload.get("mode_id", ""),
                "signal": payload.get("signal", "manual_note"),
                "note": payload.get("note", ""),
            }
            path = ROOT / "calibration" / "events.jsonl"
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(event, ensure_ascii=False) + "\n")
            json_response(self, {"ok": True, "event": event})
            return
        json_response(self, {"error": "not found"}, HTTPStatus.NOT_FOUND)

    def serve_static(self, path: str) -> None:
        requested = "index.html" if path in {"", "/"} else path.lstrip("/")
        target = (DIST_ROOT / requested).resolve()
        if not str(target).startswith(str(DIST_ROOT.resolve())) or not target.is_file():
            target = DIST_ROOT / "index.html"
        if not target.is_file():
            body = b"Run `npm run build` in web/ before starting server.py.\n"
            self.send_response(HTTPStatus.NOT_FOUND)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        content = target.read_bytes()
        content_type = mimetypes.guess_type(target.name)[0] or "application/octet-stream"
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)


def main() -> None:
    server = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    print(f"Super Board workbench: http://127.0.0.1:{PORT}")
    server.serve_forever()


if __name__ == "__main__":
    main()
