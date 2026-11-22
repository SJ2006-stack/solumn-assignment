"""Delay after a 429. The catalog server does not require a retry on the happy path."""

from __future__ import annotations


def delay_seconds(attempt: int, retry_after: str | None) -> float:
    """Seconds to wait before attempt `attempt` (0-based) is retried.

    A numeric Retry-After wins. Otherwise the delay doubles from a quarter
    second and never exceeds 8 seconds.
    """
    if attempt < 0:
        raise ValueError("attempt must be non-negative")
    if retry_after is not None and retry_after.strip() != "":
        value = float(retry_after)
        if value < 0:
            raise ValueError("Retry-After must be non-negative")
        return value
    return min(8.0, 25.0 * (2**attempt))
