"""Load the host catalog and the engagement scope."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse

from diag.errors import InventoryError

NAME_RE = re.compile(r"^[a-z][a-z0-9-]{0,40}$")


@dataclass(frozen=True)
class Host:
    name: str
    base_url: str

    @property
    def port(self) -> int:
        parsed = urlparse(self.base_url)
        if parsed.port is None:
            raise InventoryError(f"{self.name} has no port")
        return parsed.port

    @property
    def origin(self) -> str:
        parsed = urlparse(self.base_url)
        return f"{parsed.scheme}://{parsed.hostname}:{parsed.port}"


@dataclass(frozen=True)
class Engagement:
    in_scope: tuple[str, ...]
    method: str
    path: str


def _read_json(path: Path) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise InventoryError(f"{path} is not json: {exc}") from exc
    if not isinstance(data, dict):
        raise InventoryError(f"{path} must be an object")
    return data


def _validate_host(raw: object) -> Host:
    if not isinstance(raw, dict):
        raise InventoryError("host entry must be an object")
    name = raw.get("name")
    base_url = raw.get("base_url")
    if not isinstance(name, str) or not NAME_RE.match(name):
        raise InventoryError(f"illegal host name: {name!r}")
    if not isinstance(base_url, str):
        raise InventoryError(f"{name} is missing base_url")
    parsed = urlparse(base_url)
    if parsed.scheme != "http" or parsed.hostname != "127.0.0.1" or parsed.port is None:
        raise InventoryError(f"{name} must use http://127.0.0.1:<port>")
    if parsed.path not in ("", "/"):
        raise InventoryError(f"{name} base_url must not include a path")
    return Host(name, f"http://127.0.0.1:{parsed.port}")


def load_inventory(path: Path) -> tuple[Host, ...]:
    data = _read_json(path)
    raw_hosts = data.get("hosts")
    if not isinstance(raw_hosts, list) or not raw_hosts:
        raise InventoryError("hosts must be a non-empty list")
    hosts = tuple(_validate_host(item) for item in raw_hosts)
    names = [host.name for host in hosts]
    if len(names) != len(set(names)):
        raise InventoryError("host names must be unique")
    ports = [host.port for host in hosts]
    if len(ports) != len(set(ports)):
        raise InventoryError("host ports must be unique")
    return hosts


def load_engagement(path: Path) -> Engagement:
    data = _read_json(path)
    raw_scope = data.get("in_scope")
    method = data.get("method")
    path_value = data.get("path")
    if not isinstance(raw_scope, list) or not all(isinstance(item, str) for item in raw_scope):
        raise InventoryError("in_scope must be a list of names")
    if len(raw_scope) != len(set(raw_scope)):
        raise InventoryError("in_scope names must be unique")
    if method != "GET":
        raise InventoryError("engagement method must be GET")
    if not isinstance(path_value, str) or not path_value.startswith("/"):
        raise InventoryError("engagement path must start with /")
    return Engagement(tuple(raw_scope), method, path_value)


def assert_scope_known(hosts: tuple[Host, ...], engagement: Engagement) -> None:
    known = {host.name for host in hosts}
    missing = [name for name in engagement.in_scope if name not in known]
    if missing:
        raise InventoryError(f"engagement names not in the inventory: {missing}")
