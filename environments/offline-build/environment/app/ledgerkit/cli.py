"""Command line for ledgerkit."""

from __future__ import annotations

import sys
from pathlib import Path

from ledgerkit.journal import LedgerError, parse_journal, scale_of
from ledgerkit.report import build_report


def parse_amount(text: str) -> int:
    """Parse a USD amount once money.py exists. Imported lazily on purpose."""
    from ledgerkit.money import parse_amount as parse_minor

    return parse_minor(text, "", 2)


def balance_file(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    transactions = parse_journal(text)
    code = transactions[0].currency if transactions else "USD"
    scale = scale_of(code)

    def parse_with_account(amount: str, account: str) -> int:
        from ledgerkit.money import parse_amount as parse_minor

        return parse_minor(amount, account, scale)

    return build_report(transactions, parse_with_account, scale)


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if len(args) != 2 or args[0] != "balance":
        print("usage: python -m ledgerkit.cli balance JOURNAL", file=sys.stderr)
        return 2
    try:
        sys.stdout.write(balance_file(Path(args[1])))
    except LedgerError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    except NotImplementedError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
