#!/usr/bin/env python3
"""Minimal L2 web shell: static UI + POST /api/chat -> adapter.agent_chat.

Not used by the official scorer; for local demo and evidence screenshots.
Requires LOOMQ_LLM_* (see starter_kit/.env.example).
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

WEB_ROOT = Path(__file__).resolve().parent
KIT_ROOT = WEB_ROOT.parent
if str(KIT_ROOT) not in sys.path:
    sys.path.insert(0, str(KIT_ROOT))

from llm_client import REQUIRED_ENV, _load_dotenv  # noqa: E402

DEFAULT_PORT = 8765


def l2_configured() -> bool:
    _load_dotenv()
    return all(os.environ.get(name) for name in REQUIRED_ENV)


def run_chat(prompt: str) -> str:
    from adapter import agent_chat

    return agent_chat(prompt)


class L2WebHandler(BaseHTTPRequestHandler):
    server_version = "LoomQL2Web/0.1"

    def log_message(self, fmt: str, *args: Any) -> None:
        sys.stderr.write("%s - %s\n" % (self.address_string(), fmt % args))

    def _send_json(self, status: int, payload: dict[str, Any]) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_json_body(self) -> dict[str, Any]:
        length = int(self.headers.get("Content-Length", "0"))
        if length <= 0:
            return {}
        raw = self.rfile.read(length)
        return json.loads(raw.decode("utf-8"))

    def do_GET(self) -> None:
        if self.path == "/api/health":
            self._send_json(
                HTTPStatus.OK,
                {"ok": True, "l2_configured": l2_configured()},
            )
            return

        if self.path in ("/", "/index.html"):
            path = WEB_ROOT / "index.html"
            if not path.is_file():
                self.send_error(HTTPStatus.NOT_FOUND)
                return
            data = path.read_bytes()
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            return

        self.send_error(HTTPStatus.NOT_FOUND)

    def do_POST(self) -> None:
        if self.path != "/api/chat":
            self.send_error(HTTPStatus.NOT_FOUND)
            return

        if not l2_configured():
            self._send_json(
                HTTPStatus.SERVICE_UNAVAILABLE,
                {
                    "error": "LOOMQ_LLM_* not configured",
                    "missing": [
                        name for name in REQUIRED_ENV if not os.environ.get(name)
                    ],
                },
            )
            return

        try:
            payload = self._read_json_body()
            prompt = str(payload.get("prompt", "")).strip()
        except (json.JSONDecodeError, UnicodeDecodeError):
            self._send_json(
                HTTPStatus.BAD_REQUEST,
                {"error": "invalid JSON body"},
            )
            return

        if not prompt:
            self._send_json(
                HTTPStatus.BAD_REQUEST,
                {"error": "prompt is required"},
            )
            return

        try:
            response = run_chat(prompt)
        except Exception as exc:  # noqa: BLE001 — surface to browser
            self._send_json(
                HTTPStatus.INTERNAL_SERVER_ERROR,
                {"error": f"{type(exc).__name__}: {exc}"},
            )
            return

        self._send_json(HTTPStatus.OK, {"response": response})


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="LoomQ minimal L2 web UI")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    args = parser.parse_args(argv)

    server = ThreadingHTTPServer((args.host, args.port), L2WebHandler)
    url = f"http://{args.host}:{args.port}/"
    print(f"LoomQ L2 web at {url}")
    if not l2_configured():
        print(
            "Warning: LOOMQ_LLM_* not set — UI loads but chat will fail until .env is filled.",
            file=sys.stderr,
        )
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print()
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
