# Test Evidence — FossilScope v0.5.16 Candidate

## Incident evidence — 2026-08-10

Two real Windows FossilScope 0.5.14 runs now provide release-blocking evidence.

### Security Workspace catalog failure

The native Dashboard, `/docs`, `/openapi.json` and `/workbench` assets returned HTTP 200, but `/api/v1/workbench/catalog` repeatedly returned HTTP 500. The traceback terminated in SRIC Web catalog generation with:

```text
TypeError: unsupported CLI parameter type in Web catalog: TyperArgument
```

That failure explains the apparently missing operation buttons/controls: the static page loaded, but the dynamic operation catalog never reached the browser.

### Windows `update --force` opened multiple CLI windows

A second real 0.5.14 execution used:

```text
fossilscope update --force
```

The visible process reported a same-version official release (`current_version=0.5.14`, `available_version=0.5.14`, `same_version=true`) and staged the Windows post-exit handoff, but incorrectly emitted `forced=false`. During the handoff, multiple CLI/console windows appeared.

Source inspection identified the concrete process topology behind that behavior:

- the first helper process was launched with detached/no-window flags;
- the helper subsequently executed `python -m pip` and verification subprocesses without `CREATE_NO_WINDOW`;
- the helper received a verified source ZIP, so pip could start additional source-build/backend processes after detachment;
- the status payload copied the check result's default `forced=false` instead of overriding it from the actual `--force` request.

The 0.5.16 candidate changes this contract. Verified source snapshots are converted to metadata-verified target/rollback `.whl` files while the original visible process is still running. The post-exit helper refuses source archives, accepts only prebuilt wheels, launches direct child processes with `CREATE_NO_WINDOW`, and the helper launcher uses `CREATE_NO_WINDOW | CREATE_NEW_PROCESS_GROUP` without `DETACHED_PROCESS`. A same-version force request must report `forced=true` and `action=FORCED_REINSTALL`. The final `update-result.json` also preserves that force/action evidence from the staged update lock.

This user-provided Windows behavior is real incident evidence. The 0.5.16 fix still requires actual Windows execution before the incident can be marked VALIDATED as resolved.

## Focused executed evidence

A focused local Typer 0.26.3 introspection was executed in the maintenance runtime. It established a second compatibility detail that static review alone had not proven:

```text
TyperArgument:
  isinstance(click.Argument)  -> False
  isinstance(click.Parameter) -> False
  param_type_name             -> "argument"
  opts                        -> ["target"]

TyperOption:
  param_type_name             -> "option"
  opts                        -> option tokens such as "--flag"
```

This proves that two older assumptions are unsafe:

1. relying only on Click subclass identity rejects modern `TyperArgument` objects;
2. treating every parameter with an `opts` attribute as an option misclassifies real positional Typer arguments.

SRIC Core 0.5.16 therefore uses semantic `param_type_name` first. The exact signed shared-core merge used by this candidate is:

```text
b1436b4690d3560fdc84878fce5bda8f6a418b91
```

The merge is GitHub signature-verified.

Focused local updater probes also verified the intended same-version status semantics (`same_version=true`, `forced=true`, `staged=true`, `action=FORCED_REINSTALL`), rejection of mismatched wheel Version metadata, and the no-window flag contract (`CREATE_NO_WINDOW` present, `DETACHED_PROCESS` absent). These are focused logic checks, not real Windows process-topology proof.

## Candidate controls implemented

FossilScope 0.5.16 currently contains the following release gates and runtime controls:

- exact 45-command functional smoke against deterministic offline fixtures;
- root and per-command `--help`, `-h` and trailing `help` contracts;
- an exhaustive raw-parameter matrix that checks concrete Typer parameter class, positional/option semantics, type conversion and exact Web control mapping;
- deterministic parser-only values for every command/argument so parameter parsing is exercised without triggering active callbacks;
- controlled unknown-option and missing-required-input failures for every public command;
- a Web fixed-transport gate that submits every executable operation through `WebConsoleManager` while replacing execution threads with deterministic no-side-effect test doubles;
- context-only commands must remain non-executable;
- approval-required commands must reject execution without approval before their successful transport path is tested;
- product callback guardrails wrap every registered command after the complete Typer tree is assembled;
- expected file/value/schema failures produce controlled exit code 2 responses;
- unexpected callback failures are secret-redacted and converted to controlled exit code 1 responses;
- explicit validation handling exists for plugin inspection, bounded `collect-url`, time-travel, mobile archaeology, lifecycle assessment and reobservation plan/retry inputs;
- healthy `/workbench`, console catalog, workbench catalog and workbench coverage contracts must return successfully;
- every Web parameter must map to a supported typed control;
- browser recovery exposes `Reload interface`, visible catalog health and Promise/script failure handling;
- unexpected shared Web catalog/coverage/submission/history/status/cancellation failures become bounded redacted HTTP 503 responses;
- unexpected shared Web SSE runtime failures become controlled terminal failed events;
- Web operations that can write workspace/output state, including `collect`, `extract` and `report`, are conservatively `MUTATING_REVERSIBLE` and approval-gated;
- Windows/Linux installers refuse success unless FossilScope 0.5.16 + SRIC >=0.5.16,<0.6 pass `pip check`, required module imports and complete CLI/Web catalog parity;
- Windows update staging builds and verifies target/rollback wheels before the active executable exits;
- the post-exit helper rejects source archives and uses hidden child-process flags;
- same-version `--force` metadata must preserve `forced=true` and `action=FORCED_REINSTALL` in both staging and final-result evidence;
- detached Windows update verification requires the complete CLI/Web feature contract before reporting `INSTALLED`.

## Real Windows handoff validation

Because the production channel is intentionally still held at 0.5.14, an installed 0.5.16 candidate must not use normal `fossilscope update --force` to test this fix: production update semantics correctly refuse a downgrade to the older channel.

The candidate therefore includes a developer-only local process-topology smoke:

```cmd
scripts\test-windows-update-handoff.cmd
```

Its Python driver (`scripts/windows-update-handoff-smoke.py`) substitutes only official-channel discovery/download with the current local checkout. It performs no network request and does not modify the production channel. The real Windows staging code builds the wheel, launches the real hidden post-exit helper and reinstalls the candidate into the isolated FossilScope venv.

The smoke is successful only when the operator observes **one visible CMD window**, no additional console windows appear, and the script prints:

```text
Windows handoff smoke PASS: one visible CLI, hidden helper result INSTALLED, forced action preserved, no stale lock.
```

It also requires `update-result.json` to contain `status=INSTALLED`, `installed=true`, `forced=true`, `action=FORCED_REINSTALL`, and requires the temporary update lock to be removed. `tests/standalone/test_windows_update_smoke_script_v0516.py` statically gates the smoke harness itself. This does not replace official signature/channel verification or the complete release gate.

## Hosted CI status

**THE COMPLETE FOSSILSCOPE 0.5.16 REPOSITORY GATES HAVE NOT EXECUTED IN HOSTED CI.**

FossilScope PR #24 workflows repeatedly created all eight configured Linux/Windows jobs but every job returned no executable steps (`steps=[]` or `steps=null`) and no usable job logs. No checkout, Python setup, install, pytest, static analysis, installer smoke or release-gate command executed. Any run created before the final candidate head is historical infrastructure evidence only.

The associated SRIC Core 0.5.16 workflow showed the same zero-runner condition. A zero-step workflow is infrastructure evidence only. It is not a code-test failure and it is not PASS evidence.

The maintenance container also cannot resolve `github.com`, so it cannot independently materialize the complete FossilScope/SRIC repositories for a substitute full local run. Repository source and tests are being reviewed and modified through the authenticated GitHub connector; focused local package-level probes are distinguished explicitly from repository execution.

## Required exact-head execution before stable release promotion

```bash
python -m pytest -q tests/e2e/test_cli_all_commands_functional.py
python -m pytest -q tests/e2e/test_cli_web_parameter_matrix_v0516.py
python -m pytest -q tests/e2e/test_cli_exception_boundaries_v0516.py
python -m pytest -q tests/standalone/test_standalone_contract_v05.py
python -m pytest -q tests/standalone/test_windows_update_handoff_v0513.py tests/standalone/test_windows_update_smoke_script_v0516.py
python -m pytest -q tests/e2e/test_security_workspace_v0514.py
python -m pytest -q tests/e2e/test_unified_web_theme_api_docs_v0515.py tests/security/test_web_catalog_compat_v0515.py
python -m sric.standalone_gate --root .
python scripts/release-gate.py
```

The full Definition of Done additionally requires successful clean Linux/Termux and transactional Windows install/repair, data-preserving update/rollback, dependency/secret/SAST/SBOM/build checks, responsive browser validation, browser-console error review and ecosystem integration against exact final commits. The Windows updater regression specifically requires the real one-console local smoke above before the candidate can be promoted.

## Release status

Implementation and merge readiness are separate from release evidence. Do not advance the official FossilScope update channel to 0.5.16 until the complete exact-head gates actually execute and pass. A merge commit, mergeability result or zero-step workflow must never be represented as test proof.
