"""Page cache. Unfinished: get and put still raise."""

from __future__ import annotations


class PageCache:
    """Remember pages by cursor so a rerun of the same cursor does not refetch."""

    def get(self, cursor: str) -> dict | None:
        raise NotImplementedError("PageCache.get is unfinished")

    def put(self, cursor: str, page: dict) -> None:
        raise NotImplementedError("PageCache.put is unfinished")
