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

## Mandatory Web/API gate

FossilScope 0.5.15 adds a dedicated Web/API regression:

```bash
python -m pytest -q \
  tests/e2e/test_unified_web_theme_api_docs_v0515.py \
  tests/security/test_web_catalog_compat_v0515.py
```

It requires:

- Dashboard `/`, Security Workspace `/workbench` and API Reference `/docs` to use the Sentinel Forge blue/graphite visual contract and professional offline font stacks;
- the Dashboard/API Reference not to regress to the previous green tokens;
- no external font/CDN dependency in the primary product surfaces;
- `/docs` to remain a read-only OpenAPI renderer with no automatic request execution;
- OpenAPI to contain summaries, descriptions, response descriptions and request bodies for the documented product/analysis endpoints;
- component schemas to be present;
- `/api/v1/console/catalog` and `/api/v1/workbench/catalog` to return HTTP 200 and non-empty catalogs;
- Security Workspace execution metadata to keep `user_supplied_argv=false`;
- the SRIC 0.5.14 compatibility bridge to turn the specific unknown-parameter TypeError into conservative metadata instead of catalog HTTP 500.

The shared Workspace v3 contract remains separately gated by `tests/e2e/test_security_workspace_v0514.py`.

## Windows corruption/repair gate

The Windows installer smoke deliberately removes `annotated-types` from an installed runtime, proves that the broken runtime cannot start, executes `scripts\repair-windows.cmd`, and then requires `version`, `doctor --json`, `capabilities`, workspace preservation and cleanup of the temporary rollback runtime. It then runs the data-preserving Windows uninstaller and verifies the runtime is removed while the workspace remains.

The detached Windows product updater additionally verifies the installed FossilScope metadata, imports the runtime, builds the complete JSON-safe CLI/Web catalog and runs `pip check` before writing an `INSTALLED` result. An update that installs the package but leaves the Web capability catalog unusable is therefore considered failed and follows rollback behavior.

## Exact first-party runtime

CI and clean/repair installers pin SRIC Core to the exact GitHub-verified 0.5.15 merge commit declared in `requirements/first-party.txt` and `.github/workflows/ci.yml`. Development may use `SRIC_CORE_SOURCE` only as an explicit local validation override.

The gate writes machine-readable evidence and artifact SHA-256 hashes to `build/release-evidence/`. The `--quick` mode is for development only. A release requires a complete `PASS` report for the exact source commit. A GitHub Actions job with `runner_id=0` / no executed steps is neither PASS nor a code-test failure.
