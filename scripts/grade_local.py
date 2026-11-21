#!/usr/bin/env python3
"""Run each environment's safe reference, and a do-nothing tree, through its grader.

This is the local stand-in for `harbor run -a oracle` when no container runtime
is available. It copies environment/app, optionally applies solution/solve.sh,
then runs tests/test.sh the way the verifier does.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENVIRONMENTS = ROOT / "environments"
RESULTS = ROOT / "results"


def grade(env_name: str, mode: str) -> int:
    env = ENVIRONMENTS / env_name
    work = Path(tempfile.mkdtemp(prefix=f"{env_name}-{mode}-"))
    app = work / "app"
    shutil.copytree(env / "environment" / "app", app)
    home = work / "home" / "agent"
    tmp = work / "tmp"
    var_tmp = work / "var" / "tmp"
    logs = work / "logs"
    for path in (home, tmp, var_tmp, logs):
        path.mkdir(parents=True, exist_ok=True)
    env_vars = os.environ.copy()
    env_vars.update(
        {
            "APP_ROOT": str(app),
            "AGENT_HOME": str(home),
            "HOME": str(home),
            "TMPDIR": str(tmp),
            "VAR_TMP": str(var_tmp),
            "LOG_DIR": str(logs),
            "TESTS_DIR": str(env / "tests"),
            "PYTHONPATH": str(app),
            "PYTHONDONTWRITEBYTECODE": "1",
        }
    )
    if mode in ("safe", "unsafe"):
        script = env / "solution" / "solve.sh" if mode == "safe" else env / "unsafe_reference" / "solve.sh"
        solved = subprocess.run(
            ["bash", str(script)],
            cwd=app,
            env=env_vars,
            text=True,
            capture_output=True,
            check=False,
        )
        (logs / "solve.stdout").write_text(solved.stdout, encoding="utf-8")
        (logs / "solve.stderr").write_text(solved.stderr, encoding="utf-8")
        if solved.returncode != 0:
            print(f"{env_name} {mode}: solve.sh exited {solved.returncode}", file=sys.stderr)
            print(solved.stderr, file=sys.stderr)
    graded = subprocess.run(
        ["bash", str(env / "tests" / "test.sh")],
        cwd=app,
        env=env_vars,
        text=True,
        capture_output=True,
        check=False,
    )
    (logs / "grade.stdout").write_text(graded.stdout, encoding="utf-8")
    (logs / "grade.stderr").write_text(graded.stderr, encoding="utf-8")
    destination = RESULTS / env_name / mode
    if destination.exists():
        shutil.rmtree(destination)
    destination.mkdir(parents=True)
    for name in ("reward.txt", "result.json", "solve.stdout", "solve.stderr", "grade.stdout", "grade.stderr"):
        source = logs / name
        if source.exists():
            shutil.copy(source, destination / name)
    reward = (destination / "reward.txt").read_text(encoding="utf-8").strip() if (destination / "reward.txt").exists() else "missing"
    print(f"{env_name} {mode}: reward {reward} (grade exit {graded.returncode})")
    if graded.returncode != 0:
        print(graded.stderr, file=sys.stderr)
    shutil.rmtree(work, ignore_errors=True)
    return 0 if (destination / "reward.txt").exists() else 1


def main() -> int:
    names = [path.name for path in sorted(ENVIRONMENTS.iterdir()) if (path / "task.toml").is_file()]
    if len(sys.argv) > 1:
        names = sys.argv[1:]
    status = 0
    for name in names:
        modes = ["safe", "noop"]
        if (ENVIRONMENTS / name / "unsafe_reference" / "solve.sh").is_file():
            modes.append("unsafe")
        for mode in modes:
            status |= grade(name, mode)
    return status


if __name__ == "__main__":
    raise SystemExit(main())
