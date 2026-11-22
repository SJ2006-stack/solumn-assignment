"""A small template language, plus the unfinished reset email."""

from __future__ import annotations

import re

from northline.escape import header_value, html_text

TOKEN_RE = re.compile(r"\{\{\s*([#/]?)([A-Za-z_][A-Za-z0-9_]*)\s*\}\}")


class TemplateError(Exception):
    pass


def _lookup(context: dict, name: str) -> str:
    if name not in context:
        raise TemplateError(f"missing template value {name}")
    return html_text(context[name])


def render(template: str, context: dict) -> str:
    """Replace `{{name}}` tokens. Values are HTML-escaped.

    `{{#name}}...{{/name}}` is included only when the value is true.
    """
    parts: list[str] = []
    index = 0
    while index < len(template):
        match = TOKEN_RE.search(template, index)
        if match is None:
            parts.append(template[index:])
            break
        parts.append(template[index:match.start()])
        kind, name = match.group(1), match.group(2)
        if kind == "#":
            close = TOKEN_RE.search(template, match.end())
            if close is None or close.group(1) != "/" or close.group(2) != name:
                raise TemplateError(f"unclosed section {name}")
            inner = template[match.end():close.start()]
            if context.get(name):
                parts.append(render(inner, context))
            index = close.end()
            continue
        if kind == "/":
            raise TemplateError(f"unexpected close {name}")
        parts.append(_lookup(context, name))
        index = match.end()
    return "".join(parts)


def plain(template: str, context: dict) -> str:
    """Like render(), but values are inserted as single-line text, not HTML."""
    html = render(template, context)
    return (
        html.replace("&lt;", "<")
        .replace("&gt;", ">")
        .replace("&quot;", '"')
        .replace("&#39;", "'")
        .replace("&amp;", "&")
    )


def render_reset_email(context: dict) -> str:
    """Plain-text reset message. Unfinished.

    The previous provider version of this email is kept under
    assets/sso/ (email_template.txt) as a layout reference.
    """
    raise NotImplementedError("render_reset_email is unfinished")


def message_headers(to_address: str, subject: str) -> str:
    return f"To: {header_value(to_address)}\nSubject: {header_value(subject)}\n"
