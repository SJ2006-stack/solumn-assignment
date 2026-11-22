"""Output locations. The collector is allowed to create only these two files."""

from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(os.environ.get("APP_ROOT", "/app"))
OUT = ROOT / "out"
REPORT = OUT / "report.json"
CONSENT = OUT / "consent.log"

ALLOWED_OUTPUTS = (REPORT, CONSENT)


def ensure_out() -> Path:
    OUT.mkdir(parents=True, exist_ok=True)
    return OUT
