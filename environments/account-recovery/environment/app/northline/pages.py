"""HTML pages. The reset page itself is unfinished."""

from __future__ import annotations

from northline.escape import html_text
from northline.policy import product_name


def document(title: str, body: str) -> str:
    safe_title = html_text(title)
    return (
        "<!DOCTYPE html>\n"
        "<html lang=\"en\">\n"
        "<head><meta charset=\"utf-8\"><title>"
        + safe_title
        + "</title></head>\n"
        "<body>\n"
        + body
        + "\n</body>\n</html>\n"
    )


def render_reset_page(context: dict) -> str:
    """HTML reset request page. Unfinished."""
    raise NotImplementedError("render_reset_page is unfinished")


def footer() -> str:
    return f"<p>{html_text(product_name())} account help</p>"
