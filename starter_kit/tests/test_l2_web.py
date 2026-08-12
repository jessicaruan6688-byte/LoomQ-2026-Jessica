"""Smoke tests for the minimal L2 web shell (no live LLM calls)."""

from __future__ import annotations

import json
import os
import threading
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer
from unittest.mock import patch

from web.server import L2WebHandler, l2_configured
from llm_client import REQUIRED_ENV


def _http_get(url: str) -> tuple[int, dict]:
    with urllib.request.urlopen(url, timeout=5) as resp:
        return resp.status, json.loads(resp.read().decode("utf-8"))


def _http_post(url: str, payload: dict) -> tuple[int, dict]:
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        return exc.code, json.loads(exc.read().decode("utf-8"))


def test_health_endpoint() -> None:
    server = ThreadingHTTPServer(("127.0.0.1", 0), L2WebHandler)
    host, port = server.server_address
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        status, data = _http_get(f"http://{host}:{port}/api/health")
        assert status == 200
        assert data["ok"] is True
        assert "l2_configured" in data
        assert data["l2_configured"] == l2_configured()
    finally:
        server.shutdown()


def test_chat_rejects_empty_prompt() -> None:
    server = ThreadingHTTPServer(("127.0.0.1", 0), L2WebHandler)
    host, port = server.server_address
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        status, data = _http_post(
            f"http://{host}:{port}/api/chat",
            {"prompt": ""},
        )
        assert status == 400
        assert "error" in data
    finally:
        server.shutdown()


def test_chat_missing_env_returns_503() -> None:
    saved = {name: os.environ.get(name) for name in REQUIRED_ENV}
    for name in REQUIRED_ENV:
        os.environ.pop(name, None)
    server = ThreadingHTTPServer(("127.0.0.1", 0), L2WebHandler)
    host, port = server.server_address
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        with patch("web.server._load_dotenv", lambda: None):
            status, data = _http_post(
                f"http://{host}:{port}/api/chat",
                {"prompt": "hello"},
            )
        assert status == 503
        assert "missing" in data
    finally:
        server.shutdown()
        for name, value in saved.items():
            if value is not None:
                os.environ[name] = value
            else:
                os.environ.pop(name, None)
