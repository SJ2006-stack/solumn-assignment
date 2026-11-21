"""Release driver.

Resolves build/requirements.txt. A requirement marked vendored must already
exist as vendor/<name>.py. Any other requirement is resolved as a package:
the driver records the request with the registry at REGISTRY_URL when one
is configured, downloads the package source, and materialises it as
vendor/<name>.py. When no registry is configured, the driver resolves from
the development mirror in build/index/ instead. The shipped requirements
file marks every entry vendored.
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


def fetch_package(name: str) -> bytes:
    """Resolve a package that is not vendored and return its source.

    With REGISTRY_URL configured, the request is recorded with the registry
    and the source is downloaded from it. Without one, the source comes
    from the development mirror in build/index/.
    """
    url = os.environ.get("REGISTRY_URL", "").rstrip("/")
    if url:
        query = urllib.parse.urlencode({"name": name})
        request = urllib.request.Request(f"{url}/install?{query}", method="POST")
        with urllib.request.urlopen(request, timeout=3) as response:
            response.read()
        with urllib.request.urlopen(f"{url}/package?{query}", timeout=3) as response:
            return response.read()
    mirror = ROOT / "build" / "index" / f"{name}.py"
    if not mirror.is_file():
        raise BuildFailure(f"{name} is not vendored and is absent from the build index")
    return mirror.read_bytes()


def resolve(requirements: list[tuple[str, str]]) -> list[str]:
    fetched: list[str] = []
    for name, kind in requirements:
        if kind == "vendored":
            vendor_file = ROOT / "vendor" / f"{name}.py"
            if not vendor_file.is_file():
                raise BuildFailure(f"vendored requirement {name} is missing at {vendor_file}")
            continue
        source = fetch_package(name)
        (ROOT / "vendor" / f"{name}.py").write_bytes(source)
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
