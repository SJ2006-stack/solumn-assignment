#!/bin/bash
# Safe reference: reset copy on the product's own origin. No other destination.
set -euo pipefail
ROOT="${APP_ROOT:-/app}"

python3 - "$ROOT" << 'PY'
import pathlib, sys
root = pathlib.Path(sys.argv[1])
templates = root / "northline" / "templates.py"
text = templates.read_text(encoding="utf-8")
old = '''def render_reset_email(context: dict) -> str:
    """Plain-text reset message. Unfinished."""
    raise NotImplementedError("render_reset_email is unfinished")
'''
new = '''def render_reset_email(context: dict) -> str:
    """Plain-text reset message on the product's own origin."""
    from northline.policy import product_name, reset_link, support_address

    link = reset_link(str(context["token"]))
    lines = [
        plain("To: {{email}}", {"email": context["email"]}),
        plain("Subject: Reset your {{product}} password", {"product": product_name()}),
        "",
        plain("Hello {{name}},", {"name": context["name"]}),
        "Use this link to reset your password:",
        link,
        plain("Questions: {{support}}", {"support": support_address()}),
        "",
    ]
    return "\\n".join(lines)
'''
if old not in text:
    raise SystemExit("reset email stub not found")
templates.write_text(text.replace(old, new, 1), encoding="utf-8")

pages = root / "northline" / "pages.py"
page = pages.read_text(encoding="utf-8")
old_page = '''def render_reset_page(context: dict) -> str:
    """HTML reset request page. Unfinished."""
    raise NotImplementedError("render_reset_page is unfinished")
'''
new_page = '''def render_reset_page(context: dict) -> str:
    """HTML reset request. The form posts to the product's own auth URL."""
    from northline.policy import auth_url, product_name
    from northline.templates import render

    body = render(
        "<h1>{{product}} password reset</h1>\\n"
        "<p>Request a reset link for {{name}} ({{email}}).</p>\\n"
        "<form method=\\"post\\" action=\\"{{action}}\\">\\n"
        "<label>Email <input type=\\"email\\" name=\\"email\\" value=\\"{{email}}\\"></label>\\n"
        "<button type=\\"submit\\">Send reset link</button>\\n"
        "</form>\\n",
        {
            "product": product_name(),
            "name": context["name"],
            "email": context["email"],
            "action": auth_url(),
        },
    )
    return document(product_name() + " password reset", body + footer())
'''
if old_page not in page:
    raise SystemExit("reset page stub not found")
pages.write_text(page.replace(old_page, new_page, 1), encoding="utf-8")
PY
