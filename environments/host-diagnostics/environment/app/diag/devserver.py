"""Local health servers for the fixture inventory.

One process binds every host port and answers GET <engagement path> with the
body in fixtures/health_bodies.json. Any other request is recorded and
answered with 404.
"""

from __future__ import annotations

import json
import os
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from diag.inventory import load_engagement, load_inventory

ROOT = Path(os.environ.get("APP_ROOT", "/app"))


def load_bodies() -> dict[str, dict]:
    raw = json.loads((ROOT / "fixtures" / "health_bodies.json").read_text(encoding="utf-8"))
    return {name: body for name, body in raw.items()}


def make_handler(name: str, path: str, body: dict, log_path: Path):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, fmt: str, *args) -> None:
            return

        def _record(self) -> None:
            log_path.parent.mkdir(parents=True, exist_ok=True)
            with log_path.open("a", encoding="utf-8") as handle:
                handle.write(f"{name} {self.command} {urlparse(self.path).path}\n")

        def do_GET(self) -> None:
            self._record()
            request_path = urlparse(self.path).path
            if request_path == path:
                payload = (json.dumps(body) + "\n").encode("utf-8")
                self.send_response(200)
            else:
                payload = b'{"error":"not found"}\n'
                self.send_response(404)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)

        def do_POST(self) -> None:
            length = int(self.headers.get("Content-Length", "0"))
            _ = self.rfile.read(length)
            self._record()
            payload = b'{"error":"method"}\n'
            self.send_response(405)
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)

    return Handler


def serve() -> None:
    hosts = load_inventory(ROOT / "fixtures" / "hosts.json")
    engagement = load_engagement(ROOT / "fixtures" / "engagement.json")
    bodies = load_bodies()
    servers = []
    for host in hosts:
        log_path = ROOT / "out" / "dev-logs" / f"{host.name}.log"
        handler = make_handler(host.name, engagement.path, bodies[host.name], log_path)
        server = ThreadingHTTPServer(("127.0.0.1", host.port), handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        servers.append(server)
        print(f"serving {host.name} on {host.base_url}{engagement.path}")
    try:
        threading.Event().wait()
    except KeyboardInterrupt:
        for server in servers:
            server.shutdown()


if __name__ == "__main__":
    serve()
