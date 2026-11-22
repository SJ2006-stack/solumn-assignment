"""Walk catalog pages. Unfinished."""

from __future__ import annotations

from sync.cache import PageCache
from sync.client import Client
from sync.config import Quota


def collect(client: Client, cache: PageCache, quota: Quota) -> list[dict]:
    """Return every catalog item, in id order."""
    raise NotImplementedError("collect is unfinished")
