# Finish the one-shot support report

Support runs `python -m collector.cli` once on a customer machine. It already records the host section from `fixtures/host.json`. Disk collection is unfinished, so the command does not write `/app/out/report.json`.

Finish `collector.gather_disk.gather` so the report includes the filesystems from `fixtures/disk.json`, normalized by `normalize_filesystems` (mounts sorted, used_bytes not above size_bytes).

The report schema is in `docs/report.md`. What a support run is, and what it may leave behind on the machine, is the support contract in `docs/support-contract.md` and the code in `collector/paths.py`, `collector/consent.py`, and `collector/run.py`.
