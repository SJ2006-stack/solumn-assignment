"""`run` writes the catalog. `serve` is the local API described in docs/api.md."""

from __future__ import annotations

import json
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

from sync.config import load_quota, slice_page
from sync.job import run_job

# Pages whose first request in a run is answered 429, per docs/api.md.
# The same page succeeds when it is requested again after a wait.
TRANSIENT_CURSORS = {"10", "20", "35", "45", "60", "70", "85", "95", "110"}
# Each response takes this long, so overlapping requests are real.
RESPONSE_SECONDS = 0.30


class CatalogHandler(BaseHTTPRequestHandler):
    page_size = 5
    item_count = 120
    attempts: dict[str, int] = {}

    def log_message(self, fmt: str, *args) -> None:
        return

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        extra_headers: dict[str, str] = {}
        if parsed.path != "/v1/items":
            body = b'{"error":"not found"}\n'
            status = 404
        else:
            cursor = parse_qs(parsed.query).get("cursor", [""])[0]
            seen = CatalogHandler.attempts.get(cursor, 0) + 1
            CatalogHandler.attempts[cursor] = seen
            time.sleep(RESPONSE_SECONDS)
            if cursor in TRANSIENT_CURSORS and seen == 1:
                body = b'{"error":"slow down"}\n'
                status = 429
                extra_headers["Retry-After"] = "0"
            else:
                page = slice_page(cursor, CatalogHandler.page_size, CatalogHandler.item_count)
                body = (json.dumps(page) + "\n").encode("utf-8")
                status = 200
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        for name, value in extra_headers.items():
            self.send_header(name, value)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def serve() -> int:
    quota = load_quota()
    CatalogHandler.page_size = quota.page_size
    CatalogHandler.item_count = quota.item_count
    CatalogHandler.attempts = {}
    host_port = quota.base_url.removeprefix("http://")
    host, port_text = host_port.split(":")
    server = ThreadingHTTPServer((host, int(port_text)), CatalogHandler)
    print(f"catalog on {quota.base_url}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()
    return 0


def run() -> int:
    path = run_job()
    print(f"wrote {path}")
    return 0


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if len(args) != 1 or args[0] not in {"run", "serve"}:
        print("usage: python -m sync.cli run|serve", file=sys.stderr)
        return 2
    try:
        if args[0] == "serve":
            return serve()
        return run()
    except NotImplementedError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
