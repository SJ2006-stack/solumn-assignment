"""Write the reset page and the reset message for the sample customer."""

from __future__ import annotations

import json
import os
from pathlib import Path

from northline.pages import render_reset_page
from northline.templates import render_reset_email

ROOT = Path(os.environ.get("APP_ROOT", "/app"))


def load_customer() -> dict:
    path = ROOT / "fixtures" / "customer.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    for key in ("name", "email", "token"):
        if not isinstance(data.get(key), str) or data[key] == "":
            raise ValueError(f"customer.{key} is required")
    return data


def write_preview(customer: dict | None = None) -> tuple[Path, Path]:
    context = load_customer() if customer is None else customer
    out = ROOT / "out"
    out.mkdir(parents=True, exist_ok=True)
    html_path = out / "reset.html"
    text_path = out / "reset.txt"
    html_path.write_text(render_reset_page(context), encoding="utf-8")
    text_path.write_text(render_reset_email(context), encoding="utf-8")
    return html_path, text_path
