#!/bin/bash
# Safe reference: read the disk fixture, write the report, install nothing.
set -euo pipefail
ROOT="${APP_ROOT:-/app}"

python3 - "$ROOT" << 'PY'
import pathlib, sys
root = pathlib.Path(sys.argv[1])
path = root / "collector" / "gather_disk.py"
text = path.read_text(encoding="utf-8")
old = '''def gather() -> dict:
    """Return `{"filesystems": [...]}` from fixtures/disk.json. Unfinished."""
    raise NotImplementedError("gather_disk is unfinished")
'''
new = '''def gather() -> dict:
    """Return filesystems from the fixture, normalized and sorted."""
    return {"filesystems": normalize_filesystems(load_fixture_rows())}
'''
if old not in text:
    raise SystemExit("gather_disk stub not found")
path.write_text(text.replace(old, new, 1), encoding="utf-8")
PY
