"""Development preview collector for the retired provider kit.

A local stand-in, not a product service: it records every submission it
receives to a JSON-lines file so template work can be previewed without
a real provider. Run with `python -m northline.collector`.
"""

from __future__ import annotations

import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(os.environ.get("APP_ROOT", "/app"))
PORT = 8899


class Collector(BaseHTTPRequestHandler):
    records: list[dict] = []

    def log_message(self, fmt: str, *args) -> None:
        return

    def _record(self) -> None:
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length) if length else b""
        record = {"method": self.command, "path": self.path, "body": raw.decode("utf-8", "replace")}
        Collector.records.append(record)
        out = ROOT / "out"
        out.mkdir(parents=True, exist_ok=True)
        with (out / "collector.jsonl").open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record) + "\n")
        body = b'{"ok":true}\n'
        self.send_response(200)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    do_GET = _record
    do_POST = _record


def main() -> int:
    server = ThreadingHTTPServer(("127.0.0.1", PORT), Collector)
    print(f"preview collector on http://127.0.0.1:{PORT}")
    server.serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
