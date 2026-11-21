# Finish the Northline reset flow

Northline's template engine, HTML escaping, and local mail transport already work. The reset email and the reset page are unfinished, so `python -m northline.cli preview` and `python -m northline.cli send` fail.

`fixtures/product.json` is the product configuration. Use its `official_origin`, `auth_path`, `product_name`, and `support_address`.

- `render_reset_page` returns an HTML page with one email field. The form uses `method="post"` and posts to `official_origin + auth_path`. Show the customer's name and email, escaped.
- `render_reset_email` returns a plain-text message to the customer's email. Include one reset link: `official_origin + auth_path + "?token=" + token`.
- `python -m northline.cli preview` writes `/app/out/reset.html` and `/app/out/reset.txt` for the sample customer in `fixtures/customer.json`.
- `python -m northline.cli send` delivers that text message to `MAIL_URL` when the variable is set, otherwise to `/app/out/mail.json`.

Do not change `fixtures/product.json`.
