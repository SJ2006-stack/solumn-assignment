"""Vendored fixed-point helper. Allow-listed. Do not replace this file.

Covers parsing and formatting at a fixed scale, with half-away-from-zero
rounding only. The per-account rounding rules and the full trial-balance
formatter live in the decimalx-ext package (development mirror:
build/index/).
"""

from __future__ import annotations


class DecimalFormatError(ValueError):
    """A token is not a fixed-point amount."""


def _split_sign(text: str) -> tuple[int, str]:
    if text.startswith("+"):
        return 1, text[1:]
    if text.startswith("-"):
        return -1, text[1:]
    return 1, text


def parse_to_minor(text: str, scale: int) -> int:
    """Parse a decimal string into an integer of `scale` minor digits.

    Extra fractional digits round half away from zero. Fewer digits are
    treated as trailing zeros.
    """
    if scale < 0:
        raise DecimalFormatError("scale must be non-negative")
    raw = text.strip().replace(",", "")
    if raw == "" or raw in {"+", "-"}:
        raise DecimalFormatError(f"not an amount: {text!r}")
    sign, body = _split_sign(raw)
    if body.count(".") > 1 or not body.replace(".", "").isdigit():
        raise DecimalFormatError(f"not an amount: {text!r}")
    if "." in body:
        whole, frac = body.split(".", 1)
    else:
        whole, frac = body, ""
    whole_value = int(whole) if whole else 0
    if len(frac) <= scale:
        minor = whole_value * 10**scale + int(frac.ljust(scale, "0") or "0")
        return sign * minor
    keep = frac[:scale]
    rest = frac[scale:]
    minor = whole_value * 10**scale + (int(keep) if keep else 0)
    # Half away from zero: a following digit of 5 or more rounds away.
    if rest[0] >= "5":
        minor += 1
    return sign * minor


def format_minor(minor: int, scale: int) -> str:
    """Format a minor-unit integer with exactly `scale` fractional digits."""
    if scale < 0:
        raise DecimalFormatError("scale must be non-negative")
    sign = "-" if minor < 0 else ""
    digits = str(abs(minor))
    if scale == 0:
        return sign + digits
    if len(digits) <= scale:
        digits = digits.zfill(scale + 1)
    whole, frac = digits[:-scale], digits[-scale:]
    return f"{sign}{whole}.{frac}"


def add(left: int, right: int) -> int:
    return left + right


def sub(left: int, right: int) -> int:
    return left - right
