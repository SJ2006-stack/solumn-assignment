#!/bin/bash
# Safe reference: one sequential pass, cached by cursor, inside the quota.
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
"""Walk catalog pages one at a time."""

from __future__ import annotations

from sync.cache import PageCache
from sync.client import Client
from sync.config import Quota


def collect(client: Client, cache: PageCache, quota: Quota) -> list[dict]:
    items: list[dict] = []
    seen: set[int] = set()
    cursor = ""
    # Six pages of five fit in the quota with room for a single repeat lookup.
    for _ in range(quota.item_count):
        cached = cache.get(cursor)
        if cached is None:
            page = client.get_page(cursor)
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
