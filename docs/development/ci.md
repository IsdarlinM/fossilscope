# Local release validation

FossilScope does not treat hosted CI availability as proof. The exact source commit must pass the local/reproducible release gate before a stable release is declared.

```bash
python -m pip install -e ../sric-core
python -m pip install -e '.[dev]'
python scripts/release-gate.py
```

The full local gate runs compilation, Ruff, strict mypy, all pytest suites, project security/evaluation scripts when present, dependency audit, SBOM generation when available, package build and isolated wheel installation.

## Mandatory CLI command gate

Every public FossilScope command must have a deterministic functional smoke in `tests/e2e/test_cli_all_commands_functional.py`. That test compares the real Typer command tree with the explicit smoke matrix. Adding or removing a public command without updating the functional tests fails the gate.

The existing standalone contract also checks every registered command with all supported help forms:

- `fossilscope COMMAND --help`
- `fossilscope COMMAND -h`
- `fossilscope COMMAND help`

Commands that would start a server or perform bounded network collection are exercised with deterministic fakes so the default test suite remains offline and cannot perform unauthorized active actions. Scope/Policy parsing and fail-closed behavior remain real.

## Windows corruption/repair gate

The Windows installer smoke deliberately removes `annotated-types` from an installed runtime, proves that the broken runtime cannot start, executes `scripts\repair-windows.cmd`, and then requires `version`, `doctor --json`, `capabilities`, workspace preservation and cleanup of the temporary rollback runtime. It then runs the data-preserving Windows uninstaller and verifies the runtime is removed while the workspace remains.

The gate writes machine-readable evidence and artifact SHA-256 hashes to `build/release-evidence/`. The `--quick` mode is for development only. A release requires a complete `PASS` report for the exact source commit.
