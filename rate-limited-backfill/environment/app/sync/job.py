"""Run one backfill and write /app/out/items.json."""

from __future__ import annotations

import json
import os
from pathlib import Path

from sync.cache import PageCache
from sync.client import Client
from sync.config import ROOT, assert_complete, load_quota
from sync.pager import collect


def output_path() -> Path:
    override = os.environ.get("BACKFILL_OUT")
    if override:
        return Path(override)
    return ROOT / "out" / "items.json"


def run_job() -> Path:
    quota = load_quota()
    items = collect(Client(quota), PageCache(), quota)
    assert_complete(items, quota)
    path = output_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    document = {"schema": 1, "items": items}
    path.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
    return path
