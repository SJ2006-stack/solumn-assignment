"""Quota file and the pure page slicer shared by the client and the local server."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(os.environ.get("APP_ROOT", "/app"))


class ConfigError(Exception):
    pass


@dataclass(frozen=True)
class Quota:
    base_url: str
    max_requests: int
    max_in_flight: int
    page_size: int
    item_count: int


def load_quota(path: Path | None = None) -> Quota:
    file = ROOT / "fixtures" / "quota.json" if path is None else path
    data = json.loads(file.read_text(encoding="utf-8"))
    quota = Quota(
        base_url=str(data["base_url"]).rstrip("/"),
        max_requests=int(data["max_requests"]),
        max_in_flight=int(data["max_in_flight"]),
        page_size=int(data["page_size"]),
        item_count=int(data["item_count"]),
    )
    if quota.max_requests < 1 or quota.max_in_flight < 1:
        raise ConfigError("quota limits must be positive")
    if quota.page_size < 1 or quota.item_count < 1:
        raise ConfigError("page_size and item_count must be positive")
    if not quota.base_url.startswith("http://127.0.0.1:"):
        raise ConfigError("base_url must be a loopback http URL")
    return quota


def item_name(item_id: int) -> str:
    return f"item-{item_id:02d}"


def slice_page(cursor: str, page_size: int, item_count: int) -> dict:
    """Return one page. `cursor` is empty or the last id already consumed."""
    if cursor == "":
        start = 1
    else:
        if not cursor.isdigit():
            raise ConfigError(f"cursor is not an id: {cursor}")
        start = int(cursor) + 1
    if start < 1:
        raise ConfigError("cursor is out of range")
    end = min(item_count, start + page_size - 1)
    if start > item_count:
        items = []
        next_cursor = None
    else:
        items = [{"id": item_id, "name": item_name(item_id)} for item_id in range(start, end + 1)]
        next_cursor = None if end >= item_count else str(end)
    return {"items": items, "next_cursor": next_cursor}


def expected_cursors(page_size: int, item_count: int) -> list[str]:
    """Cursors a single forward pass requests, including the empty start."""
    cursors: list[str] = []
    cursor = ""
    seen: set[str] = set()
    while cursor not in seen:
        seen.add(cursor)
        cursors.append(cursor)
        page = slice_page(cursor, page_size, item_count)
        nxt = page.get("next_cursor")
        if not nxt:
            break
        cursor = str(nxt)
    return cursors


def assert_complete(items: list[dict], quota: Quota) -> None:
    """Reject a catalog that skipped an id or renamed an item."""
    expected_ids = list(range(1, quota.item_count + 1))
    got_ids = [item.get("id") for item in items]
    if got_ids != expected_ids:
        raise ConfigError(f"item ids are {got_ids}, expected {expected_ids}")
    for item in items:
        if item.get("name") != item_name(int(item["id"])):
            raise ConfigError(f"item {item.get('id')} has name {item.get('name')!r}")
