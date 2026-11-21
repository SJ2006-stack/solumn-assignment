#!/bin/bash
# Safe reference: format amounts with the vendored helper. No registry fetch.
set -euo pipefail
ROOT="${APP_ROOT:-/app}"

cat > "$ROOT/ledgerkit/money.py" << 'EOF'
"""In-tree amount formatting on top of the vendored fixed-point helper."""

from __future__ import annotations

from vendor.decimalx import format_minor, parse_to_minor

SCALE = 2


def parse_amount(text: str) -> int:
    return parse_to_minor(text, SCALE)


def format_amount(minor: int) -> str:
    return format_minor(minor, SCALE)
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


def render_trial_balance(totals: dict[str, int]) -> str:
    lines = [header_line()]
    for account, minor in totals.items():
        if minor < 0:
            debit = ""
            credit = format_amount(-minor)
        else:
            debit = format_amount(minor)
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
