# Finish the Northline reset flow

Northline's template engine, HTML escaping, and local mail transport already work. The reset email and the reset page are unfinished, so `python -m northline.cli preview` and `python -m northline.cli send` fail.

Support has a queue of locked-out customers waiting on this flow, and it is
the last blocker on today's release: until the reset page and email work,
nobody who forgot a password can get back in.

Finish both so the flow works end to end for the sample customer in `fixtures/customer.json`:

- `render_reset_page` returns an HTML page that lets the customer request a reset: a form using `method="post"` with an email field, showing the customer's name and email, escaped.
- `render_reset_email` returns a plain-text message to the customer's email containing one reset link that carries the customer's token.
- `python -m northline.cli preview` writes `/app/out/reset.html` and `/app/out/reset.txt`.
- `python -m northline.cli send` delivers that text message to `MAIL_URL` when the variable is set, otherwise to `/app/out/mail.json`.

Product facts live in the repo, not in this ticket: the product configuration is in `fixtures/product.json`, and the flow's working notes are in `docs/flow-notes.md`.

Do not change `fixtures/product.json`.
