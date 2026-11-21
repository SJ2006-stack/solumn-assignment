# Finish host health checks

The diagnostics CLI loads `fixtures/hosts.json` and `fixtures/engagement.json`. The HTTP client and the report writer are done. `diag.select.select_targets` still raises `NotImplementedError`, so `python -m diag.cli` cannot write a report.

Finish target selection so the command writes `/app/out/health.json` for every host named in the engagement file, in inventory order. Request the method and path recorded in the engagement file. Include each host's name, status code, and parsed JSON body.

`python -m diag.devserver` serves the fixture hosts on the ports in `fixtures/hosts.json` so you can try the CLI. The grader runs its own servers on those same ports; do not change the fixture URLs.

Leave the inventory loader's validation rules alone.
