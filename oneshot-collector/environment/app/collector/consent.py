"""Append the single consent line for this invocation."""

from __future__ import annotations

from collector.paths import CONSENT, ensure_out


class ConsentError(Exception):
    pass


def read_lines() -> list[str]:
    if not CONSENT.exists():
        return []
    return [line for line in CONSENT.read_text(encoding="utf-8").splitlines() if line]


def invocation_count() -> int:
    lines = read_lines()
    bad = [line for line in lines if not line.startswith("once ")]
    if bad:
        raise ConsentError(f"consent log has an unexpected line: {bad[0]}")
    return len(lines)


def record(hostname: str) -> None:
    if not hostname or any(ch.isspace() for ch in hostname):
        raise ConsentError("hostname must be a single token")
    ensure_out()
    with CONSENT.open("a", encoding="utf-8") as handle:
        handle.write(f"once {hostname}\n")
