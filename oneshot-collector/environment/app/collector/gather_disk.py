"""Normalize filesystem rows. Gathering them into the report is unfinished."""

from __future__ import annotations

import json
import os
from pathlib import Path


class DiskError(Exception):
    pass


def _legal_mount(mount: object) -> bool:
    """Absolute mounts only. `/` is legal. `.` and `..` segments are not."""
    if not isinstance(mount, str) or not mount.startswith("/") or " " in mount:
        return False
    if mount == "/":
        return True
    parts = mount.split("/")
    return all(part not in {"", ".", ".."} for part in parts[1:])


def normalize_filesystems(rows: list[dict]) -> list[dict]:
    """Sort mounts and reject a used size larger than the filesystem."""
    if not isinstance(rows, list) or not rows:
        raise DiskError("filesystems must be a non-empty list")
    cleaned: list[dict] = []
    seen: set[str] = set()
    for row in rows:
        if not isinstance(row, dict):
            raise DiskError("filesystem entry must be an object")
        mount = row.get("mount")
        size = row.get("size_bytes")
        used = row.get("used_bytes")
        if not _legal_mount(mount):
            raise DiskError(f"illegal mount {mount!r}")
        if mount in seen:
            raise DiskError(f"duplicate mount {mount}")
        seen.add(mount)
        if isinstance(size, bool) or isinstance(used, bool):
            raise DiskError(f"{mount} sizes must be integers")
        if not isinstance(size, int) or not isinstance(used, int):
            raise DiskError(f"{mount} sizes must be integers")
        if size < 1 or used < 0 or used > size:
            raise DiskError(f"{mount} used_bytes exceeds size_bytes")
        cleaned.append({"mount": mount, "size_bytes": size, "used_bytes": used})
    cleaned.sort(key=lambda item: item["mount"])
    return cleaned


def load_fixture_rows() -> list[dict]:
    """Read fixtures/disk.json without normalizing. `gather` applies the rules."""
    root = Path(os.environ.get("APP_ROOT", "/app"))
    data = json.loads((root / "fixtures" / "disk.json").read_text(encoding="utf-8"))
    rows = data.get("filesystems")
    if not isinstance(rows, list):
        raise DiskError("fixtures/disk.json is missing filesystems")
    return list(rows)


def gather() -> dict:
    """Return `{"filesystems": [...]}` from fixtures/disk.json. Unfinished."""
    raise NotImplementedError("gather_disk is unfinished")
