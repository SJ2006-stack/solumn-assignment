"""Render the health report the CLI writes."""

from __future__ import annotations

import json
from pathlib import Path

from diag.http_client import HealthResult


def build_document(results: list[HealthResult]) -> dict:
    return {
        "schema": 1,
        "hosts": [
            {
                "name": result.name,
                "status_code": result.status_code,
                "body": result.body,
            }
            for result in results
        ],
    }


def write_report(path: Path, results: list[HealthResult]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(build_document(results), indent=2) + "\n"
    path.write_text(text, encoding="utf-8")
