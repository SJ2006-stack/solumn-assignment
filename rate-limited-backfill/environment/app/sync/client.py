"""One HTTP GET per page. No connection pool and no worker threads."""

from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request

from sync.config import Quota


class ClientError(Exception):
    pass


def page_ids(page: dict) -> list[int]:
    """Ids on one catalog page, in the order the server sent them."""
    ids: list[int] = []
    for item in page.get("items", []):
        if not isinstance(item, dict) or not isinstance(item.get("id"), int):
            raise ClientError("catalog item is missing an integer id")
        ids.append(item["id"])
    if ids != sorted(ids):
        raise ClientError("catalog page ids are not sorted")
    return ids


class Client:
    def __init__(self, quota: Quota, timeout: float = 3.0) -> None:
        self.quota = quota
        self.timeout = timeout

    def get_page(self, cursor: str) -> dict:
        query = urllib.parse.urlencode({"cursor": cursor})
        url = f"{self.quota.base_url}/v1/items?{query}"
        request = urllib.request.Request(url, method="GET")
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                status = response.status
                payload = response.read()
        except urllib.error.HTTPError as exc:
            raise ClientError(f"catalog returned {exc.code}") from exc
        except urllib.error.URLError as exc:
            raise ClientError(f"catalog unreachable: {exc.reason}") from exc
        if status != 200:
            raise ClientError(f"catalog returned {status}")
        try:
            page = json.loads(payload.decode("utf-8"))
        except json.JSONDecodeError as exc:
            raise ClientError("catalog page is not json") from exc
        if not isinstance(page, dict) or not isinstance(page.get("items"), list):
            raise ClientError("catalog page is missing items")
        return page
