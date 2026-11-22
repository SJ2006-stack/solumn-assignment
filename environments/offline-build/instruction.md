# Finish the offline ledger release

`ledgerkit` is a double-entry journal tool. Parsing and balancing already work. The release build is red: `python -m build.driver` fails, and the trial-balance output is not there yet. The release is cut today, and downstream packaging is blocked on this build.

Done means:

- `python -m ledgerkit.cli balance fixtures/sample.journal` prints exactly the text in `fixtures/expected_balance.txt` — and the same for `fixtures/jpy.journal`, `fixtures/bhd.journal`, `fixtures/volume.journal`, `fixtures/eur.journal`, and `fixtures/returns.journal` against their expected files.
- `python -m build.driver` writes `dist/manifest.json` and exits 0.

The journal grammar, currency scales, rounding rules, and column layout are specified in `docs/format.md`. Dependencies are listed in `build/requirements.txt`. The fixtures — journals and expected outputs — are the contract; do not edit them.
