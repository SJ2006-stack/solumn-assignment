"""Read the host fixture. This section is already finished."""

from __future__ import annotations

import json
import os
from pathlib import Path

ROOT = Path(os.environ.get("APP_ROOT", "/app"))


class HostError(Exception):
    pass


def gather() -> dict:
    path = ROOT / "fixtures" / "host.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    hostname = data.get("hostname")
    system = data.get("os")
    cpu_count = data.get("cpu_count")
    if not isinstance(hostname, str) or not hostname or any(ch.isspace() for ch in hostname):
        raise HostError("hostname must be a single token")
    if system != "linux":
        raise HostError("os must be linux")
    if not isinstance(cpu_count, int) or isinstance(cpu_count, bool) or cpu_count < 1:
        raise HostError("cpu_count must be a positive integer")
    return {"hostname": hostname, "os": system, "cpu_count": cpu_count}
