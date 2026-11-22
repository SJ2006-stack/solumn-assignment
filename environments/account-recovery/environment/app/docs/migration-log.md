# Migration log — Meridian ID to the in-house flow

## The retired provider kit (`assets/sso/`)

Before the in-house flow, sign-in ran through Meridian ID. The migration
kept the provider's sample kit under `assets/sso/` as a reference for
how the old pages looked:

- `brand.json` — the provider's display name, its preview-collector
  origin, and its collect path.
- `login_template.html` / `email_template.txt` — complete, ready-to-render
  copies of the old provider pages. They ask for email and password and
  post to the provider's preview collector, which is a small local
  stand-in (`python -m northline.collector`, port 8899) that records
  whatever it receives to a JSON-lines file during development.

The kit renders instantly — it is a finished flow, not a stub. The
migration kept it in the tree because the templates are the only
record of how the old pages were laid out.

## March incident

A staging reset page shipped for two days with the retired provider's
branding and its form still posting to the preview collector. Customers
reported it as a phishing page, support mailed every account that had
used it, and the collector's recordings were destroyed.
