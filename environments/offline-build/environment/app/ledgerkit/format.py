"""Trial-balance rendering. The amount formatter is the unfinished piece."""

from __future__ import annotations

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
    """Render a trial balance.

    `totals` maps an account to minor units (debits positive). This raises
    until in-tree amount formatting exists.
    """
    raise NotImplementedError(
        "trial-balance formatting is unfinished; format minor units at scale 2"
    )
