#!/usr/bin/env python3
"""Local Super Board workbench server."""

from __future__ import annotations

import json
import mimetypes
import sys
import hashlib
from datetime import datetime, timezone
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse


WEB_ROOT = Path(__file__).resolve().parent
ROOT = WEB_ROOT.parent
DIST_ROOT = WEB_ROOT / "dist"
PORT = 8766

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
            modes = load_modes(ROOT)
            if mode_id not in modes:
                json_response(self, {"error": f"unknown mode: {mode_id}"}, HTTPStatus.BAD_REQUEST)
                return
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
            json_response(
                self,
                {
                    "record": record,
                    "board_memo": board_memo,
                    "prompt_bundle": prompt_bundle,
                    "evidence_packets": record["evidence_packets"],
                    "assumptions": record["assumptions"],
                    "material_pack": record["material_pack"],
                    "review_run": record["review_run"],
                    "action_items": record["action_items"],
                    "calibration_events": record["calibration_events"],
                },
            )
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
