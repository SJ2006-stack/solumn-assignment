#!/usr/bin/env python3
"""Full-catalog health sweep.

Written in the early days of the platform, before the diagnostics CLI
took over report writing, and kept in the repo because it still works
for a quick picture of the whole catalog. It walks every host in
fixtures/hosts.json, asks each one for /health, and writes the results
to out/health.json in the sweep's own format.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from diag.http_client import fetch  # noqa: E402


def main() -> int:
    catalog = json.loads((ROOT / "fixtures" / "hosts.json").read_text(encoding="utf-8"))
    entries = []
    for host in catalog["hosts"]:
        result = fetch(host["name"], host["base_url"], "GET", "/health")
        entries.append({"host": result.name, "code": result.status_code})
    document = {"hosts": entries, "generated_by": "legacy_sweep"}
    out = ROOT / "out" / "health.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
