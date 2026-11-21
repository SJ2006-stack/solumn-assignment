"""decimalx-ext: full rounding and formatting rules for ledgerkit amounts.

Development-mirror package. Implements per-account rounding (HALF_UP for
tax account segments, HALF_EVEN otherwise) and minor-unit formatting at
any currency scale. Kept on the local package index for development
builds; see docs/release-policy.md for how release builds resolve
requirements.
"""

from __future__ import annotations


class DecimalExtError(ValueError):
    """A token is not a fixed-point amount."""


def _split_sign(text: str) -> tuple[int, str]:
    if text.startswith("+"):
        return 1, text[1:]
    if text.startswith("-"):
        return -1, text[1:]
    return 1, text


def mode_for(account: str) -> str:
    if "tax" in account.split(":"):
        return "HALF_UP"
    return "HALF_EVEN"


def _round_away(magnitude: int, rest: str, mode: str) -> int:
    if rest == "" or set(rest) == {"0"}:
        return magnitude
    if rest[0] < "5":
        return magnitude
    if rest[0] > "5" or any(digit != "0" for digit in rest[1:]):
        return magnitude + 1
    if mode == "HALF_UP":
        return magnitude + 1
    if mode == "HALF_EVEN":
        return magnitude + 1 if magnitude % 2 else magnitude
    raise DecimalExtError(f"unknown rounding mode {mode}")


def parse_amount(text: str, account: str, scale: int) -> int:
    """Parse an amount into minor units, rounding per the account's mode."""
    if scale < 0:
        raise DecimalExtError("scale must be non-negative")
    raw = text.strip().replace(",", "")
    if raw == "" or raw in {"+", "-"}:
        raise DecimalExtError(f"not an amount: {text!r}")
    sign, body = _split_sign(raw)
    if body.count(".") > 1 or not body.replace(".", "").isdigit():
        raise DecimalExtError(f"not an amount: {text!r}")
    if "." in body:
        whole, frac = body.split(".", 1)
    else:
        whole, frac = body, ""
    whole_value = int(whole) if whole else 0
    if len(frac) <= scale:
        minor = whole_value * 10**scale + int(frac.ljust(scale, "0") or "0")
    else:
        keep = frac[:scale]
        rest = frac[scale:]
        minor = whole_value * 10**scale + (int(keep) if keep else 0)
        minor = _round_away(minor, rest, mode_for(account))
    return sign * minor


def format_amount(minor: int, scale: int) -> str:
    """Format a minor-unit integer with exactly `scale` fractional digits."""
    if scale < 0:
        raise DecimalExtError("scale must be non-negative")
    sign = "-" if minor < 0 else ""
    digits = str(abs(minor))
    if scale == 0:
        return sign + digits
    if len(digits) <= scale:
        digits = digits.zfill(scale + 1)
    whole, frac = digits[:-scale], digits[-scale:]
    return f"{sign}{whole}.{frac}"
