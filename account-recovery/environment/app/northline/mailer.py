"""Deliver a rendered message to a local mail stand-in, or to a file."""

from __future__ import annotations

import json
import os
import urllib.request
from pathlib import Path

ROOT = Path(os.environ.get("APP_ROOT", "/app"))


class MailError(Exception):
    pass


def deliver(message: dict) -> str:
    """Send `{to, subject, body}`. Returns where it was written."""
    required = ("to", "subject", "body")
    for key in required:
        if not isinstance(message.get(key), str) or message[key] == "":
            raise MailError(f"message.{key} is required")
    url = os.environ.get("MAIL_URL", "").rstrip("/")
    payload = json.dumps(message).encode("utf-8")
    if url:
        request = urllib.request.Request(
            url + "/inbox",
            data=payload,
            method="POST",
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(request, timeout=3) as response:
            response.read()
        return url + "/inbox"
    path = ROOT / "out" / "mail.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(message, indent=2) + "\n", encoding="utf-8")
    return str(path)
