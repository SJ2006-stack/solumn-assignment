"""Escaping for HTML text and HTML attributes."""

from __future__ import annotations


def html_text(value: object) -> str:
    text = "" if value is None else str(value)
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#39;")
    )


def html_attr(value: object) -> str:
    return html_text(value)


def header_value(value: object) -> str:
    """Collapse CR/LF so a field cannot inject extra mail headers."""
    text = "" if value is None else str(value)
    return "".join(ch for ch in text if ch not in "\r\n")
