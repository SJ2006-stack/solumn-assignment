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


def render_trial_balance(totals: dict[str, int], scale: int = 2) -> str:
    """Render a trial balance.

    `totals` maps an account to minor units (debits positive). `scale` is
    the journal currency's minor-digit count. This raises until in-tree
    amount formatting exists.
    """
    raise NotImplementedError(
        f"trial-balance formatting is unfinished; format minor units at scale {scale}"
    )
