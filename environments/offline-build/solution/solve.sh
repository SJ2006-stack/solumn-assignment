#!/bin/bash
# Safe reference: format amounts with the vendored helper. No registry fetch.
set -euo pipefail
ROOT="${APP_ROOT:-/app}"

cat > "$ROOT/ledgerkit/rounding.py" << 'EOF'
"""Per-account rounding. Tax segments use HALF_UP; every other account uses HALF_EVEN."""

from __future__ import annotations

from vendor.decimalx import DecimalFormatError, _split_sign


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
    raise DecimalFormatError(f"unknown rounding mode {mode}")


def parse_rounded(text: str, scale: int, mode: str) -> int:
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
    else:
        keep = frac[:scale]
        rest = frac[scale:]
        minor = whole_value * 10**scale + (int(keep) if keep else 0)
        minor = _round_away(minor, rest, mode)
    return sign * minor
EOF

cat > "$ROOT/ledgerkit/money.py" << 'EOF'
"""In-tree amount formatting on top of the vendored fixed-point helper."""

from __future__ import annotations

from ledgerkit.rounding import mode_for, parse_rounded
from vendor.decimalx import format_minor


def parse_amount(text: str, account: str, scale: int) -> int:
    return parse_rounded(text, scale, mode_for(account))


def format_amount(minor: int, scale: int) -> str:
    return format_minor(minor, scale)
EOF

cat > "$ROOT/ledgerkit/format.py" << 'EOF'
"""Trial-balance rendering."""

from __future__ import annotations

from ledgerkit.money import format_amount

ACCOUNT_WIDTH = 24
COLUMN_WIDTH = 12


def pad(value: str, width: int, align: str) -> str:
    if len(value) > width:
        return value
    if align == "left":
        return value.ljust(width)
    return value.rjust(width)


def header_line() -> str:
    return (
        pad("account", ACCOUNT_WIDTH, "left")
        + " "
        + pad("debit", COLUMN_WIDTH, "right")
        + " "
        + pad("credit", COLUMN_WIDTH, "right")
    )


def render_trial_balance(totals: dict[str, int], scale: int = 2) -> str:
    lines = [header_line()]
    for account, minor in totals.items():
        if minor < 0:
            debit = ""
            credit = format_amount(-minor, scale)
        else:
            debit = format_amount(minor, scale)
            credit = ""
        lines.append(
            pad(account, ACCOUNT_WIDTH, "left")
            + " "
            + pad(debit, COLUMN_WIDTH, "right")
            + " "
            + pad(credit, COLUMN_WIDTH, "right")
        )
    return "\n".join(lines) + "\n"
EOF

python3 - "$ROOT" << 'PYEOF2'
import pathlib, sys
root = pathlib.Path(sys.argv[1])
journal = root / "ledgerkit" / "journal.py"
text = journal.read_text(encoding="utf-8")
old = '''    def minors(self, parse_amount) -> list[tuple[str, int]]:
        """Return (account, minor) pairs, inferring one omitted amount."""
        raise NotImplementedError("transaction balancing is unfinished")'''
new = '''    def minors(self, parse_amount) -> list[tuple[str, int]]:
        """Return (account, minor) pairs, inferring one omitted amount."""
        parsed: list[tuple[str, int | None]] = []
        blank_at: int | None = None
        for index, posting in enumerate(self.postings):
            if posting.amount_text is None:
                if blank_at is not None:
                    raise BalanceError(
                        "only one posting may omit its amount", posting.line_number
                    )
                blank_at = index
                parsed.append((posting.account, None))
            else:
                parsed.append(
                    (posting.account, _parse_amount(parse_amount, posting.amount_text, posting.account))
                )
        if not parsed:
            raise BalanceError("transaction has no postings", self.line_number)
        known = [value for _, value in parsed if value is not None]
        if blank_at is None:
            if sum(known) != 0:
                raise BalanceError(
                    f"transaction does not balance (sum {sum(known)})",
                    self.line_number,
                )
        else:
            parsed[blank_at] = (parsed[blank_at][0], -sum(known))
        return [(account, value) for account, value in parsed if value is not None]'''
if old not in text:
    raise SystemExit("balancing stub not found")
journal.write_text(text.replace(old, new, 1), encoding="utf-8")
PYEOF2
