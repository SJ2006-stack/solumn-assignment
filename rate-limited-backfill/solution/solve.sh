#!/bin/bash
# Safe reference: one sequential pass, cached by cursor, honouring the
# backoff contract for transient 429s. Twelve pages plus one retry for
# each of the two transient pages is 14 requests, inside the contract's
# 38, and never more than one request in flight.
set -euo pipefail
ROOT="${APP_ROOT:-/app}"

cat > "$ROOT/sync/cache.py" << 'EOF'
"""Page cache keyed by cursor."""

from __future__ import annotations


class PageCache:
    def __init__(self) -> None:
        self._pages: dict[str, dict] = {}

    def get(self, cursor: str) -> dict | None:
        return self._pages.get(cursor)

    def put(self, cursor: str, page: dict) -> None:
        self._pages[cursor] = page
EOF

cat > "$ROOT/sync/pager.py" << 'EOF'
"""Walk catalog pages one at a time, waiting out transient 429s."""

from __future__ import annotations

import time

from sync.backoff import delay_seconds
from sync.cache import PageCache
from sync.client import Client, ClientError
from sync.config import Quota


def fetch(client: Client, cursor: str) -> dict:
    """One page, retried after the backoff delay while the API sheds load."""
    attempt = 0
    while True:
        try:
            return client.get_page(cursor)
        except ClientError:
            if attempt >= 4:
                raise
            time.sleep(delay_seconds(attempt, None))
            attempt += 1


def collect(client: Client, cache: PageCache, quota: Quota) -> list[dict]:
    items: list[dict] = []
    seen: set[int] = set()
    cursor = ""
    for _ in range(quota.item_count):
        cached = cache.get(cursor)
        if cached is None:
            page = fetch(client, cursor)
            cache.put(cursor, page)
        else:
            page = cached
        for item in page["items"]:
            item_id = int(item["id"])
            if item_id in seen:
                continue
            seen.add(item_id)
            items.append({"id": item_id, "name": item["name"]})
        nxt = page.get("next_cursor")
        if not nxt:
            break
        cursor = str(nxt)
    items.sort(key=lambda item: item["id"])
    return items
EOF
