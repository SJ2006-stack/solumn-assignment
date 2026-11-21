"""Build the text report the CLI prints."""

from __future__ import annotations

from ledgerkit.format import render_trial_balance
from ledgerkit.journal import Transaction, trial_balance


def build_report(transactions: list[Transaction], parse_amount, scale: int = 2) -> str:
    totals = trial_balance(transactions, parse_amount)
    body = render_trial_balance(totals, scale)
    if not body.endswith("\n"):
        body += "\n"
    return "TRIAL BALANCE\n" + body
