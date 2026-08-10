# Test Evidence — FossilScope v0.5.16 Candidate

## Incident evidence — 2026-08-10

A real Windows FossilScope 0.5.14 run provided the decisive Web failure evidence. The native Dashboard, `/docs`, `/openapi.json` and `/workbench` assets returned HTTP 200, but `/api/v1/workbench/catalog` repeatedly returned HTTP 500. The traceback terminated in SRIC Web catalog generation with:

```text
TypeError: unsupported CLI parameter type in Web catalog: TyperArgument
```

That failure explains the apparently missing operation buttons/controls: the static page loaded, but the dynamic operation catalog never reached the browser.

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

This focused introspection is real execution evidence for the Typer compatibility decision only. It is not represented as a full repository/platform/browser PASS.

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
- detached Windows update verification also requires the complete CLI/Web feature contract before reporting `INSTALLED`.

## Hosted CI status

**THE COMPLETE FOSSILSCOPE 0.5.16 REPOSITORY GATES HAVE NOT EXECUTED IN HOSTED CI.**

FossilScope PR #24 exact-head workflow run `31441443770` created all eight configured Linux/Windows jobs for head `82b214e72c625ddc41fe989173915e1c65671cfe`. Every job reported `runner_id=0` and `steps=[]`. No checkout, Python setup, install, pytest, static analysis, installer smoke or release-gate command executed.

The associated SRIC Core 0.5.16 workflow showed the same condition across all configured jobs. A zero-step workflow is infrastructure evidence only. It is not a code-test failure and it is not PASS evidence.

The maintenance container also cannot resolve `github.com`, so it cannot independently materialize the complete FossilScope/SRIC repositories for a substitute full local run. Repository source and tests are being reviewed and modified through the authenticated GitHub connector; focused local package-level probes are distinguished explicitly from repository execution.

## Required exact-head execution before stable release promotion

```bash
python -m pytest -q tests/e2e/test_cli_all_commands_functional.py
python -m pytest -q tests/e2e/test_cli_web_parameter_matrix_v0516.py
python -m pytest -q tests/e2e/test_cli_exception_boundaries_v0516.py
python -m pytest -q tests/standalone/test_standalone_contract_v05.py
python -m pytest -q tests/e2e/test_security_workspace_v0514.py
python -m pytest -q tests/e2e/test_unified_web_theme_api_docs_v0515.py tests/security/test_web_catalog_compat_v0515.py
python -m sric.standalone_gate --root .
python scripts/release-gate.py
```

The full Definition of Done additionally requires successful clean Linux/Termux and transactional Windows install/repair, data-preserving update/rollback, dependency/secret/SAST/SBOM/build checks, responsive browser validation, browser-console error review and ecosystem integration against exact final commits.

## Release status

Implementation and merge readiness are separate from release evidence. Do not advance the official FossilScope update channel to 0.5.16 until the complete exact-head gates actually execute and pass. A merge commit, mergeability result or zero-step workflow must never be represented as test proof.
