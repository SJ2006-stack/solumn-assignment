"""HTTP client used by the health check. One request, no redirects."""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from dataclasses import dataclass

from diag.errors import RequestError


@dataclass(frozen=True)
class HealthResult:
    name: str
    status_code: int
    body: dict


def fetch(name: str, base_url: str, method: str, path: str, timeout: float = 2.0) -> HealthResult:
    if method != "GET":
        raise RequestError(f"{name}: only GET is implemented")
    url = base_url.rstrip("/") + path
    request = urllib.request.Request(url, method="GET")
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            status = response.status
            payload = response.read()
    except urllib.error.HTTPError as exc:
        status = exc.code
        payload = exc.read()
    except urllib.error.URLError as exc:
        raise RequestError(f"{name}: {exc.reason}") from exc
    try:
        body = json.loads(payload.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RequestError(f"{name}: health body is not json") from exc
    if not isinstance(body, dict):
        raise RequestError(f"{name}: health body must be an object")
    return HealthResult(name, status, body)
