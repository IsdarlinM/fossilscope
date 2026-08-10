# Local release validation

FossilScope does not treat hosted CI availability as proof. The exact source commit must pass the local/reproducible release gate before a stable release is declared.

```bash
python -m pip install -e ../sric-core
python -m pip install -e '.[dev]'
python scripts/release-gate.py
```

The full local gate runs compilation, Ruff, strict mypy, all pytest suites, project security/evaluation scripts when present, dependency audit, SBOM generation when available, package build and isolated wheel installation.

## Mandatory CLI command gate

Every public FossilScope command must have a deterministic functional smoke in `tests/e2e/test_cli_all_commands_functional.py`. That test compares the real Typer command tree with the explicit smoke matrix. Adding or removing a public command without updating the functional tests fails the gate. The current contract covers all 45 public commands.

The standalone contract checks every registered command with all supported help forms:

- `fossilscope COMMAND --help`
- `fossilscope COMMAND -h`
- `fossilscope COMMAND help`

Root `--help`, `-h` and `help` aliases are also smoke-tested. Commands that would start a server or perform bounded network collection are exercised with deterministic fakes so the default test suite remains offline and cannot perform unauthorized active actions. Scope/Policy parsing and fail-closed behavior remain real.

## Mandatory CLI/Web parameter gate

FossilScope 0.5.16 adds a second exhaustive gate that is deliberately different from the functional command smoke:

```bash
python -m pytest -q tests/e2e/test_cli_web_parameter_matrix_v0516.py
```

It walks the actual Typer command tree and, for every public command and every raw parameter:

- requires exact CLI catalog / Web feature catalog command parity;
- requires exact ordered parameter parity;
- records the concrete parameter class;
- distinguishes real `TyperArgument` from `TyperOption` using semantic parameter metadata;
- requires positional arguments to remain positional (`opts=[]`, no Web option token);
- requires options to retain a concrete option token beginning with `-`;
- requires every parameter to map to a supported structured Web control;
- synthesizes deterministic parser-only values for choices, paths, numeric bounds, datetimes, booleans and text and runs Click/Typer conversion without invoking active callbacks;
- invokes every command with an unknown option and requires a controlled parser failure with no traceback;
- invokes every command with required inputs omitted and requires a controlled parser failure with no traceback;
- submits every executable command through `WebConsoleManager` with its real approval classification while replacing the execution thread with a deterministic no-side-effect test double;
- verifies context-only operations are rejected as context-only rather than accidentally executed.

This gate exists because a command can work through CLI happy-path tests while still disappearing from the Web UI due to bad parameter metadata.

## Mandatory Web/API gate

The Web/API regressions require:

```bash
python -m pytest -q \
  tests/e2e/test_security_workspace_v0514.py \
  tests/e2e/test_unified_web_theme_api_docs_v0515.py \
  tests/security/test_web_catalog_compat_v0515.py
```

They require:

- Dashboard `/`, Security Workspace `/workbench` and API Reference `/docs` to use the Sentinel Forge blue/graphite visual contract and professional offline font stacks;
- the Dashboard/API Reference not to regress to the previous green tokens;
- no external font/CDN dependency in the primary product surfaces;
- `/docs` to remain a read-only OpenAPI renderer with no automatic request execution;
- OpenAPI to contain summaries, descriptions, response descriptions and request bodies for documented product/analysis endpoints;
- component schemas to be present;
- `/api/v1/console/catalog`, `/api/v1/workbench/catalog` and `/api/v1/workbench/coverage` to return healthy contracts when runtime integrity is valid;
- Security Workspace execution metadata to keep `user_supplied_argv=false`;
- the real reported `TyperArgument` failure class to be covered for SRIC 0.5.14 and the positional-semantics issue to be covered for SRIC 0.5.15;
- current SRIC 0.5.16 to use its canonical implementation rather than the FossilScope compatibility bridge;
- Run, Cancel, Refresh and Reload interface controls to remain reachable through the page/script contract.

SRIC Core 0.5.16 additionally gates unexpected catalog/coverage/submission/history/status/cancellation failures as bounded redacted HTTP 503 responses and unexpected SSE runtime failures as controlled terminal events.

## Windows corruption/repair gate

The Windows installer smoke deliberately removes `annotated-types` from an installed runtime, proves that the broken runtime cannot start, executes `scripts\repair-windows.cmd`, and then requires `version`, `doctor --json`, `capabilities`, workspace preservation and cleanup of the temporary rollback runtime. It also requires the complete `fossilscope.cli_all` Web feature contract to build after repair. It then runs the data-preserving Windows uninstaller and verifies the runtime is removed while the workspace remains.

The detached Windows product updater verifies the installed FossilScope metadata, imports SRIC Web guardrails, builds the complete JSON-safe CLI catalog and Web feature catalog, requires feature-contract completeness and runs `pip check` before writing an `INSTALLED` result. An update that installs the package but leaves the Web capability catalog unusable is considered failed and follows rollback behavior.

## Exact first-party runtime

CI and clean/repair installers pin SRIC Core to signed merge `b1436b4690d3560fdc84878fce5bda8f6a418b91` (0.5.16), declared in `requirements/first-party.txt` and `.github/workflows/ci.yml`. Development may use `SRIC_CORE_SOURCE` only as an explicit local validation override.

The gate writes machine-readable evidence and artifact SHA-256 hashes to `build/release-evidence/`. The `--quick` mode is for development only. A release requires a complete `PASS` report for the exact source commit. A GitHub Actions job with `runner_id=0` / no executed steps is neither PASS nor a code-test failure.
