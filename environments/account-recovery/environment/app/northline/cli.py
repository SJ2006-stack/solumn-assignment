"""Preview and send the Northline reset flow."""

from __future__ import annotations

import sys

from northline.mailer import MailError, deliver
from northline.preview import load_customer, write_preview
from northline.templates import message_headers


def preview() -> int:
    html_path, text_path = write_preview()
    print(f"wrote {html_path}")
    print(f"wrote {text_path}")
    return 0


def send() -> int:
    customer = load_customer()
    _html_path, text_path = write_preview(customer)
    body = text_path.read_text(encoding="utf-8")
    subject = "Reset your Northline password"
    deliver({"to": customer["email"], "subject": subject, "body": body})
    sys.stdout.write(message_headers(customer["email"], subject))
    return 0


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if len(args) != 1 or args[0] not in {"preview", "send"}:
        print("usage: python -m northline.cli preview|send", file=sys.stderr)
        return 2
    try:
        if args[0] == "preview":
            return preview()
        return send()
    except NotImplementedError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    except (MailError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
