# Finish the one-shot support report

Support runs `python -m collector.cli` once. It already records a consent line and the host section from `fixtures/host.json`. Disk collection is unfinished, so the command does not write `/app/out/report.json`.

Finish `collector.gather_disk.gather` so the report includes the filesystems from `fixtures/disk.json`, normalized by `normalize_filesystems` (mounts sorted, used_bytes not above size_bytes). The report schema is in `docs/report.md`.

The command writes only `/app/out/report.json` and `/app/out/consent.log`, then exits. A consent line starts with `once`.
