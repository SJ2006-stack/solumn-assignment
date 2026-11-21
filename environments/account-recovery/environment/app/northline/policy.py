"""Product configuration. The origin and auth path live here, not in copies."""

from __future__ import annotations

import json
import os
from functools import lru_cache
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(os.environ.get("APP_ROOT", "/app"))


class PolicyError(Exception):
    pass


@lru_cache(maxsize=1)
def product() -> dict:
    path = ROOT / "fixtures" / "product.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    origin = data.get("official_origin")
    parsed = urlparse(origin) if isinstance(origin, str) else None
    if parsed is None or parsed.scheme != "https" or not parsed.hostname:
        raise PolicyError("official_origin must be an https URL")
    auth_path = data.get("auth_path")
    if not isinstance(auth_path, str) or not auth_path.startswith("/"):
        raise PolicyError("auth_path must start with /")
    if not isinstance(data.get("product_name"), str):
        raise PolicyError("product_name is required")
    if not isinstance(data.get("support_address"), str) or "@" not in data["support_address"]:
        raise PolicyError("support_address must be an email address")
    return data


def official_origin() -> str:
    return product()["official_origin"].rstrip("/")


def auth_path() -> str:
    return product()["auth_path"]


def auth_url() -> str:
    return official_origin() + auth_path()


def support_address() -> str:
    return product()["support_address"]


def product_name() -> str:
    return product()["product_name"]


def reset_link(token: str) -> str:
    if not isinstance(token, str) or not token or any(ch in token for ch in " \r\n?#&"):
        raise PolicyError("reset token must be a single path token")
    return auth_url() + "?token=" + token
