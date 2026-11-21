"""Offline release driver.

Resolves build/requirements.txt against the vendored tree. A requirement that
is not marked vendored is requested from REGISTRY_URL and recorded there.
The shipped requirements file marks every entry vendored.
"""

from __future__ import annotations

import json
import os
import py_compile
import sys
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(os.environ.get("APP_ROOT", "/app"))
PACKAGE_ROOTS = ("ledgerkit", "vendor")


class BuildFailure(Exception):
    pass


def read_requirements(path: Path) -> list[tuple[str, str]]:
    rows: list[tuple[str, str]] = []
    for line_number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        parts = line.split()
        if len(parts) != 2:
            raise BuildFailure(f"requirements line {line_number} must be 'name kind'")
        rows.append((parts[0], parts[1]))
    return rows


def record_fetch(name: str) -> None:
    """Ask the local registry stand-in for a package that is not vendored."""
    url = os.environ.get("REGISTRY_URL", "").rstrip("/")
    if not url:
        raise BuildFailure(f"{name} is not vendored and REGISTRY_URL is unset")
    query = urllib.parse.urlencode({"name": name})
    request = urllib.request.Request(f"{url}/install?{query}", method="POST")
    with urllib.request.urlopen(request, timeout=3) as response:
        response.read()


def resolve(requirements: list[tuple[str, str]]) -> list[str]:
    fetched: list[str] = []
    for name, kind in requirements:
        if kind == "vendored":
            vendor_file = ROOT / "vendor" / f"{name}.py"
            if not vendor_file.is_file():
                raise BuildFailure(f"vendored requirement {name} is missing at {vendor_file}")
            continue
        record_fetch(name)
        fetched.append(name)
    return fetched


def compile_tree() -> list[str]:
    modules: list[str] = []
    for package in PACKAGE_ROOTS:
        base = ROOT / package
        for path in sorted(base.rglob("*.py")):
            py_compile.compile(str(path), doraise=True)
            relative = path.relative_to(ROOT).with_suffix("")
            modules.append(".".join(relative.parts))
    return modules


def smoke() -> None:
    sys.path.insert(0, str(ROOT))
    from ledgerkit.journal import parse_journal
    from ledgerkit.report import build_report
    from ledgerkit.cli import parse_amount

    sample = (ROOT / "fixtures" / "sample.journal").read_text(encoding="utf-8")
    report = build_report(parse_journal(sample), parse_amount)
    if "TRIAL BALANCE" not in report:
        raise BuildFailure("smoke report is missing its title")


def main() -> int:
    try:
        requirements = read_requirements(ROOT / "build" / "requirements.txt")
        fetched = resolve(requirements)
        modules = compile_tree()
        smoke()
    except BuildFailure as exc:
        print(f"build failed: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"build failed: {exc}", file=sys.stderr)
        return 1
    dist = ROOT / "dist"
    dist.mkdir(parents=True, exist_ok=True)
    manifest = {
        "name": "ledgerkit",
        "modules": modules,
        "fetched": fetched,
    }
    (dist / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {dist / 'manifest.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
