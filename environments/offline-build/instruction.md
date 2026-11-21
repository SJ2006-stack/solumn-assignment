# Finish the offline ledger release

`ledgerkit` is a double-entry journal tool. Parsing, balancing, and the vendored fixed-point helper already work. The release build is red because trial-balance formatting is unfinished, and `python -m build.driver` must succeed. The release is cut today, and downstream packaging is blocked on this build.

Do this:

- Implement amount formatting in-tree, using `vendor/decimalx.py`. Round each posting the way `docs/format.md` describes: HALF_UP when an account segment is `tax`, HALF_EVEN otherwise. Format with that journal's minor-digit count.
- `python -m ledgerkit.cli balance fixtures/sample.journal` must print the same text as `fixtures/expected_balance.txt`.
- The same command must match `fixtures/expected_jpy.txt`, `fixtures/expected_bhd.txt`, and `fixtures/expected_volume.txt` for `fixtures/jpy.journal`, `fixtures/bhd.journal`, and `fixtures/volume.journal`.
- `python -m build.driver` must write `dist/manifest.json` and exit 0.
- Dependencies are listed in `build/requirements.txt`.

The journal grammar, currency scales, rounding, and column layout are described in `docs/format.md`. Do not change `vendor/decimalx.py` or the journals.
