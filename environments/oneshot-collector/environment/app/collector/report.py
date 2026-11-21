"""Assemble and check the support report."""

from __future__ import annotations

import json

from collector.paths import REPORT, ensure_out


class ReportError(Exception):
    pass


def build(host: dict, disk: dict) -> dict:
    filesystems = disk.get("filesystems")
    if not isinstance(filesystems, list) or not filesystems:
        raise ReportError("disk.filesystems is required")
    return {"schema": 1, "host": host, "disk": {"filesystems": filesystems}}


def validate(document: dict) -> None:
    if document.get("schema") != 1:
        raise ReportError("schema must be 1")
    host = document.get("host")
    disk = document.get("disk")
    if not isinstance(host, dict) or not isinstance(disk, dict):
        raise ReportError("host and disk are required")
    for key in ("hostname", "os", "cpu_count"):
        if key not in host:
            raise ReportError(f"host.{key} is required")
    rows = disk.get("filesystems")
    if not isinstance(rows, list) or not rows:
        raise ReportError("filesystems are required")
    mounts = [row.get("mount") for row in rows]
    if mounts != sorted(mounts):
        raise ReportError("filesystems must be sorted by mount")


def used_percent(used: int, size: int) -> str:
    """One decimal place, truncating toward zero. size is never zero."""
    if size < 1:
        raise ReportError("size_bytes must be positive")
    tenths = (used * 1000) // size
    whole, frac = divmod(tenths, 10)
    return f"{whole}.{frac}%"


def free_bytes(row: dict) -> int:
    """Bytes still available on one filesystem row."""
    return int(row["size_bytes"]) - int(row["used_bytes"])


def disk_totals(rows: list[dict]) -> dict[str, int]:
    return {
        "filesystems": len(rows),
        "size_bytes": sum(int(row["size_bytes"]) for row in rows),
        "used_bytes": sum(int(row["used_bytes"]) for row in rows),
    }


def render_text(document: dict) -> str:
    """A plain table for the operator. This is printed, not written to disk."""
    validate(document)
    host = document["host"]
    rows = document["disk"]["filesystems"]
    totals = disk_totals(rows)
    lines = [
        f"{host['hostname']} {host['os']} cpus={host['cpu_count']}",
        f"{'mount':<16} {'used':>12} {'size':>12} {'pct':>8}",
    ]
    for row in rows:
        lines.append(
            f"{row['mount']:<16} {row['used_bytes']:>12} {row['size_bytes']:>12} "
            f"{used_percent(row['used_bytes'], row['size_bytes']):>8}"
        )
    lines.append(
        f"{'total':<16} {totals['used_bytes']:>12} {totals['size_bytes']:>12} "
        f"{used_percent(totals['used_bytes'], totals['size_bytes']):>8}"
    )
    return "\n".join(lines) + "\n"


def render_sections(document: dict) -> str:
    """A second, line-oriented view of the same report. Printed, not stored."""
    validate(document)
    host = document["host"]
    rows = document["disk"]["filesystems"]
    totals = disk_totals(rows)
    lines = [
        "HOST",
        f"hostname {host['hostname']}",
        f"os {host['os']}",
        f"cpu_count {host['cpu_count']}",
        "DISK",
    ]
    for row in rows:
        free = free_bytes(row)
        note = " tight" if free * 5 <= int(row["size_bytes"]) else ""
        lines.append(
            f"mount {row['mount']} used {row['used_bytes']} free {free} size {row['size_bytes']}{note}"
        )
    lines.append(
        f"filesystems {totals['filesystems']} used {totals['used_bytes']} size {totals['size_bytes']}"
    )
    return "\n".join(lines) + "\n"


def write(document: dict) -> None:
    validate(document)
    ensure_out()
    REPORT.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
