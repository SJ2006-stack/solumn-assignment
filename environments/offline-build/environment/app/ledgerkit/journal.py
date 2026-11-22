"""Parse and balance a double-entry journal."""

from __future__ import annotations

import inspect
import re
from dataclasses import dataclass, field


class LedgerError(Exception):
    """Base class for journal errors. Carries the source line when known."""

    def __init__(self, message: str, line_number: int | None = None) -> None:
        self.line_number = line_number
        if line_number is None:
            super().__init__(message)
        else:
            super().__init__(f"line {line_number}: {message}")


class ParseError(LedgerError):
    """The journal text is not in the documented grammar."""


class BalanceError(LedgerError):
    """A transaction does not balance, or an amount cannot be inferred."""


class AccountNameError(LedgerError):
    """An account name fails the documented pattern."""

ACCOUNT_RE = re.compile(r"^[a-z][a-z0-9_]*(?::[a-z][a-z0-9_]*)*$")
HEADER_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})\s+(\S.*)$")
AMOUNT_RE = re.compile(r"^[+-]?\d+(?:\.\d+)?$")
CURRENCY_RE = re.compile(r"^currency\s+([A-Z]{3})$")
CURRENCY_SCALE = {"USD": 2, "EUR": 2, "JPY": 0, "BHD": 3}


@dataclass
class Posting:
    account: str
    amount_text: str | None
    line_number: int


@dataclass
class Transaction:
    date: str
    description: str
    postings: list[Posting] = field(default_factory=list)
    line_number: int = 1
    currency: str = "USD"

    def minors(self, parse_amount) -> list[tuple[str, int]]:
        """Return (account, minor) pairs, inferring one omitted amount."""
        raise NotImplementedError("transaction balancing is unfinished")


def scale_of(code: str) -> int:
    try:
        return CURRENCY_SCALE[code]
    except KeyError as exc:
        raise ParseError(f"unknown currency {code}") from exc


def _parse_amount(parse_amount, text: str, account: str) -> int:
    try:
        parameters = inspect.signature(parse_amount).parameters
    except (TypeError, ValueError):
        parameters = {}
    if len(parameters) >= 2:
        return parse_amount(text, account)
    return parse_amount(text)


def validate_account(name: str, line_number: int) -> str:
    if not ACCOUNT_RE.match(name):
        raise AccountNameError(f"illegal account name {name!r}", line_number)
    return name


def _split_posting(text: str, line_number: int) -> tuple[str, str | None]:
    """A posting is an account, then an optional amount separated by 2+ spaces."""
    if "  " not in text:
        return validate_account(text.strip(), line_number), None
    account, amount = text.rsplit("  ", 1)
    account = account.strip()
    amount = amount.strip()
    validate_account(account, line_number)
    if not AMOUNT_RE.match(amount):
        raise ParseError(f"not an amount: {amount!r}", line_number)
    return account, amount


def parse_journal(text: str) -> list[Transaction]:
    """Parse journal text. Comments start with ';' and are ignored."""
    transactions: list[Transaction] = []
    current: Transaction | None = None
    currency = "USD"
    for line_number, raw in enumerate(text.splitlines(), start=1):
        stripped_comment = raw.split(";", 1)[0].rstrip()
        if not stripped_comment.strip():
            continue
        if stripped_comment.startswith((" ", "\t")):
            if current is None:
                raise ParseError("posting before a transaction header", line_number)
            account, amount = _split_posting(stripped_comment.strip(), line_number)
            current.postings.append(Posting(account, amount, line_number))
            continue
        if current is not None:
            transactions.append(current)
        currency_match = CURRENCY_RE.match(stripped_comment.strip())
        if currency_match:
            currency = currency_match.group(1)
            scale_of(currency)
            current = None
            continue
        match = HEADER_RE.match(stripped_comment.strip())
        if match is None:
            raise ParseError(
                "header must be YYYY-MM-DD followed by a description", line_number
            )
        current = Transaction(
            date=match.group(1),
            description=match.group(2).strip(),
            line_number=line_number,
            currency=currency,
        )
    if current is not None:
        transactions.append(current)
    return transactions


def trial_balance(transactions: list[Transaction], parse_amount) -> dict[str, int]:
    """Sum minor units by account. Debits are positive, credits negative."""
    totals: dict[str, int] = {}
    for transaction in transactions:
        for account, minor in transaction.minors(parse_amount):
            totals[account] = totals.get(account, 0) + minor
    if sum(totals.values()) != 0:
        raise BalanceError("journal trial balance is not zero")
    return dict(sorted(totals.items()))
