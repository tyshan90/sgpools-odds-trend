from __future__ import annotations

import argparse
import json
import mimetypes
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from .config import load_settings
from .store import OddsStore

STATIC_DIR = Path(__file__).resolve().parent / "static"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Local Singapore Pools odds trend dashboard")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--db", default=None, type=Path)
    parser.add_argument("--env-file", type=Path)
    args = parser.parse_args(argv)

    settings = load_settings(args.env_file, {"DATABASE_PATH": str(args.db) if args.db else None})
    server = make_server(args.host, args.port, OddsStore(settings.database_path))
    print(f"Dashboard running at http://{args.host}:{args.port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


def make_server(host: str, port: int, store: OddsStore) -> ThreadingHTTPServer:
    class DashboardHandler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            parsed = urlparse(self.path)
            if parsed.path == "/":
                self._serve_file(STATIC_DIR / "dashboard.html", "text/html; charset=utf-8")
                return
            if parsed.path == "/app.css":
                self._serve_file(STATIC_DIR / "dashboard.css", "text/css; charset=utf-8")
                return
            if parsed.path == "/app.js":
                self._serve_file(STATIC_DIR / "dashboard.js", "application/javascript; charset=utf-8")
                return
            if parsed.path == "/favicon.ico":
                self.send_response(HTTPStatus.NO_CONTENT)
                self.send_header("Cache-Control", "max-age=86400")
                self.end_headers()
                return
            if parsed.path == "/api/matches":
                params = parse_qs(parsed.query)
                market = _single(params, "market", "1X2")
                self._send_json({"matches": store.list_matches(market_name=market)})
                return
            if parsed.path == "/api/trend":
                params = parse_qs(parsed.query)
                event_id = _single(params, "event_id", "")
                market = _single(params, "market", "1X2")
                if not event_id:
                    self._send_json({"error": "event_id is required"}, status=HTTPStatus.BAD_REQUEST)
                    return
                self._send_json(store.trend_for_event(event_id, market_name=market))
                return
            self._send_json({"error": "not found"}, status=HTTPStatus.NOT_FOUND)

        def log_message(self, format: str, *args) -> None:
            return

        def _serve_file(self, path: Path, content_type: str | None = None) -> None:
            if not path.is_file():
                self._send_json({"error": "not found"}, status=HTTPStatus.NOT_FOUND)
                return
            body = path.read_bytes()
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", content_type or mimetypes.guess_type(path.name)[0] or "application/octet-stream")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

        def _send_json(self, payload: object, status: HTTPStatus = HTTPStatus.OK) -> None:
            body = json.dumps(payload, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

    return ThreadingHTTPServer((host, port), DashboardHandler)


def _single(params: dict[str, list[str]], name: str, default: str) -> str:
    values = params.get(name)
    if not values:
        return default
    return values[0]


if __name__ == "__main__":
    raise SystemExit(main())
