#!/usr/bin/env python3
"""Local Super Board workbench server."""

from __future__ import annotations

import json
import mimetypes
import sys
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse


WEB_ROOT = Path(__file__).resolve().parent
ROOT = WEB_ROOT.parent
DIST_ROOT = WEB_ROOT / "dist"
PORT = 8766

sys.path.insert(0, str(ROOT / "scripts"))
from super_board_run import build_prompt_bundle, build_record, load_modes  # noqa: E402


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
        self.serve_static(parsed.path)

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/api/preview":
            payload = read_json(self)
            material = str(payload.get("material", "")).strip()
            mode_id = str(payload.get("mode_id", "deep_board_review"))
            if not material:
                json_response(self, {"error": "material is required"}, HTTPStatus.BAD_REQUEST)
                return
            modes = load_modes(ROOT)
            if mode_id not in modes:
                json_response(self, {"error": f"unknown mode: {mode_id}"}, HTTPStatus.BAD_REQUEST)
                return
            input_path = ROOT / "inline-input.md"
            record = build_record(input_path, material, modes[mode_id])
            prompt_bundle = build_prompt_bundle(input_path, material, modes[mode_id], record)
            json_response(
                self,
                {
                    "record": record,
                    "prompt_bundle": prompt_bundle,
                    "evidence_packets": record["evidence_packets"],
                    "assumptions": record["assumptions"],
                },
            )
            return
        if parsed.path == "/api/record":
            payload = read_json(self)
            decision_id = str(payload.get("decision_id", "")).strip()
            if not decision_id:
                json_response(self, {"error": "decision_id is required"}, HTTPStatus.BAD_REQUEST)
                return
            record_path = ROOT / "records" / f"{decision_id}.json"
            record_path.parent.mkdir(parents=True, exist_ok=True)
            record_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            json_response(self, {"ok": True, "path": str(record_path.relative_to(ROOT))})
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
