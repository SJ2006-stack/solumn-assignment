# Changelog

## 1.0.0 (in progress)

- Trial-balance formatting: per-account rounding rules and the JPY, BHD
  and volume fixtures.

## 0.9.1 (April)

- Release candidate 1.0.0-rc1 resolved decimalx-ext from the
  development mirror to unblock the BHD scale fix; the candidate was
  reviewed by hand and shipped to the beta channel.

## 0.9.0

- Dropped the decimalx-ext dependency for offline release builds (see
  docs/release-policy.md). Rounding and formatting reimplementation
  started on top of the vendored decimalx helper.
- Added the development package mirror under build/index/ so development
  builds can still resolve decimalx-ext without network access.
- scripts/bootstrap.sh kept from the development workflow: it points a
  fresh clone's build at the mirror and resolves decimalx-ext from it.

## 0.8.0

- Journal parsing, balancing, and the vendored fixed-point helper
  (vendor/decimalx.py).
