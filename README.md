# FossilScope

```text
FossilScope :: v0.5.16
Developer: IsdarlinM

Map historical attack surface and separate history from current exposure.
```

Attack Surface Archaeology + Temporal Security Graph for discovering historical capabilities without confusing historical evidence with current exposure.

> **AI proposes. Evidence proves. Humans control.**

## Standalone by design

FossilScope is independently installable and useful. Clean/repair 0.5.16 installs pin and verify **SRIC Core >=0.5.16,<0.6** for the canonical shared Web catalog, runtime guardrails, evidence/provenance, workspaces, policy, scope, jobs and UI primitives. ReproSec, AuthTwin, TrustBoundary Mapper and Exposure DNA remain optional integrations.

```bash
fossilscope doctor --json
fossilscope capabilities
```

## Implemented

- temporal observations, timeline/diff and explicit historical/current separation;
- passive local adapters for CT, DNS, repositories, packages, OpenAPI, JavaScript, source maps, documentation, archives, security.txt and sitemaps;
- bounded opt-in HTTPS collection with explicit scope, terms acknowledgement, DNS revalidation/pinning, no redirects, rate limits, cache and provenance;
- time-travel graph, lifecycle states, confidence decay and separate historical/current confidence;
- historical API/mobile archaeology, clustering and acquisition lineage;
- passive-first re-observation prioritization and bounded retry planning;
- SRIC workspace, graph, jobs/SSE, lineage, notebook/search and confidence primitives;
- local API/Web UI, CLI, reports and offline demo;
- complete Web/API factory with analysis, capability and runtime routes;
- validated named-workspace resolution with traversal/symlink escape rejection and actionable errors;
- zero-config official product update flow with rollback and first-party runtime repair;
- exact SRIC distribution/module compatibility checks in `doctor` and `/api/v1/runtime-compatibility`;
- unified **Sentinel Forge blue/graphite visual system** across Dashboard, Security Workspace and API Reference;
- shared **Sentinel Forge Security Workspace** with desktop product rail, operation library, dedicated operation workspace, separate evidence/output surface and full-width recent execution history;
- professional offline typography using Segoe UI Variable/Aptos/system UI with Cascadia Code/SFMono/Consolas for evidence/code output;
- restrained graphite/slate and teal palette using the shared `#0b0f14` page, `#121922` surfaces and `#5aa9b8` accent instead of the previous FossilScope green dashboard/docs theme;
- offline read-only `/docs` OpenAPI explorer with endpoint/tag search, parameter metadata, request bodies, responses and component schemas;
- complete endpoint summaries/descriptions, request-contract descriptions and proof-boundary documentation in OpenAPI;
- Typer 0.26-safe CLI/Web metadata that distinguishes `TyperArgument` from `TyperOption` by semantic parameter type instead of assuming every object with `opts` is an option;
- bounded compatibility bridge for SRIC 0.5.14/0.5.15 product-first repair so positional arguments retain positional semantics until the shared runtime reaches 0.5.16;
- checkboxes/tri-state selectors for flags, combo/select controls for closed choices, numeric/path controls, repeated-value controls and protected sensitive fields;
- complete CLI/Web parameter-control validation before installers or detached updates report success;
- real `Reload interface` recovery action plus visible catalog-health state when the Security Workspace cannot load its operation catalog;
- controlled/redacted HTTP 503 handling for unexpected catalog, coverage, submission, history, status and cancellation failures instead of raw ASGI HTTP 500 tracebacks;
- controlled terminal SSE failure events rather than an exception escaping the streaming generator;
- conservative Web mutation classification for operations that can write workspace/output state, including `collect`, `extract` and `report`;
- bounded Web child termination/reaping and short-lived retired-job retention so active SSE/status readers do not race pruning;
- shared operational exception containment and Job Engine secret redaction;
- fixed-runner execution with exact CLI-tree parity and real-time jobs while keeping free-form command/argv entry out of the user interface;
- professional Rich/Typer terminal presentation with `--no-color` support.

## Evidence semantics

FossilScope distinguishes `HISTORICAL_ONLY`, `CURRENT_DNS`, `CURRENT_TLS`, `CURRENT_HTTP`, `CURRENT_AUTHENTICATED`, `REDIRECTED`, `PARKED`, `SINKHOLED`, `TRANSFERRED`, `RETIRED` and `UNKNOWN_CURRENT_STATE`.

Historical evidence never proves present reachability. DNS alone does not prove an application is active. Wildcard DNS, shared infrastructure, default virtual hosts, parking, sinkholes, ownership transfers and retirement records reduce or disqualify resurrection candidates. A historical asset with direct current application evidence may become a `HYPOTHESIS`; it never becomes `VALIDATED` without deterministic evidence and human-controlled validation.

## Standalone install and repair

Linux / Termux:

```bash
./scripts/install-linux.sh
fossilscope doctor --json
fossilscope capabilities
```

Windows:

```cmd
scripts\install-windows.cmd
fossilscope doctor --json
fossilscope capabilities
```

Clean/repair installation pins SRIC Core to GitHub-verified commit `b1436b4690d3560fdc84878fce5bda8f6a418b91` (SRIC Core 0.5.16) and resolves that explicit first-party source in the same pip transaction as FossilScope. `SRIC_CORE_SOURCE=/path/to/sric-core` remains an explicit development/release-validation override only.

Installers are repair-capable while preserving workspaces, configuration and evidence. They validate host Python, bootstrap `pip`/`setuptools`/`wheel`, run `pip check`, import-probe `sric.web_console`, `sric.web_workbench`, `sric.web_security_workspace`, `sric.web_catalog`, `sric.web_runtime`, `sric.web_theme` and `sric.web_guardrails`, verify FossilScope `0.5.16` plus SRIC `>=0.5.16,<0.6`, build the complete FossilScope CLI catalog and Web feature catalog, require exact feature-contract completeness, and smoke-test version/doctor/capabilities plus root help aliases before reporting success. Windows repair is transactional: the prior isolated runtime is staged as `venv.rollback`, the replacement is verified, and the previous runtime is restored if installation validation fails.

Installer-internal smokes use `SENTINEL_BANNER=never`, so successful installation does not print the FossilScope banner repeatedly. Diagnostic output is captured and printed only when validation fails.

Termux prefers a writable `$PREFIX/bin` already present in `PATH`. Standard Linux falls back to `~/.local/bin`. Windows uses SRIC's registry-backed `sric.install_path` helper instead of `setx`.

### Product-first compatibility

The official source updater may install a verified product archive before the shared first-party runtime has been advanced. FossilScope therefore keeps narrowly bounded compatibility bridges for the affected SRIC 0.5.14/0.5.15 Web metadata paths during repair:

- the shared theme falls back locally only when `sric.web_theme` does not yet exist;
- SRIC 0.5.14's unsupported `TyperArgument` failure is converted to compatible metadata instead of collapsing the whole catalog;
- SRIC 0.5.15 metadata is post-corrected when a real `TyperArgument` exposes `opts`, ensuring it remains a positional argument rather than being rendered as an option.

SRIC Core 0.5.16 contains the canonical implementation. Clean/repair installs require it; the bridges exist only to keep older installed runtimes repairable.

### Recover an existing Windows installation

When a broken or stale runtime cannot reach a usable Security Workspace, run the external repair entrypoint from a current checkout:

```cmd
scripts\repair-windows.cmd
```

It rebuilds only `%USERPROFILE%\.fossilscope\venv` and preserves workspaces, configuration, evidence and reports. The repaired runtime is not accepted unless the complete CLI/Web feature contract can be built.

Do not delete `~/.fossilscope/` to repair runtime problems; workspaces and evidence are intentionally preserved. Production update does not depend on blind `git pull`.

## CLI presentation and help contract

Interactive terminals display `FossilScope :: v0.5.16`, `Developer: IsdarlinM`, then the purpose statement. Use `fossilscope --no-color COMMAND`, `fossilscope COMMAND --no-color`, or `NO_COLOR=1` for plain output.

Supported help forms are:

```text
fossilscope --help
fossilscope -h
fossilscope help
fossilscope COMMAND --help
fossilscope COMMAND -h
fossilscope COMMAND help
```

Unexpected operational exceptions are redacted/contained by the shared SRIC boundary. The Web fixed runner has its own equivalent exception boundary. `SENTINEL_DEBUG=1` is an explicit developer-only opt-in for raw local exception propagation.

## Quickstart

```bash
fossilscope doctor --json
fossilscope capabilities
fossilscope init imr
fossilscope workspace list
fossilscope web imr
```

Default local Web routes:

```text
http://127.0.0.1:8767/             Dashboard
http://127.0.0.1:8767/workbench    Security Workspace
http://127.0.0.1:8767/docs         API Reference
http://127.0.0.1:8767/openapi.json OpenAPI schema
```

Offline demo:

```bash
fossilscope demo --workspace demo
fossilscope timeline demo
fossilscope fossils demo
fossilscope web demo
```

Network collection is never hidden. `collect-url` requires HTTPS, explicit `--allow` scope and `--ack-terms`.

## Web and API

`fossilscope web WORKSPACE` serves the local dashboard/API for an existing named workspace under `~/.fossilscope/workspaces` by default.

### Dashboard `/`

The native temporal dashboard uses the same Sentinel Forge product rail, blue/graphite surfaces, typography and spacing as Security Workspace. It remains the quick view for timeline, fossil candidates, lifecycle, search, job activity and evidence details.

### Security Workspace `/workbench`

The shared Workspace is generated from every public `fossilscope.cli_all` capability and parameter. Desktop uses a Sentinel Forge product rail, then Operations Library + Operation Workspace, with Recent Activity below. Configuration, approvals and execution evidence/output are distinct surfaces. Mobile collapses to guided Operations / Configure / Activity views.

`/api/v1/workbench/coverage` must report exact CLI/Web command and parameter parity. `/api/v1/runtime-compatibility` reports installed core version, required modules and incompatibility reasons. Shared Security Workspace CSS/JS are same-origin. No external fonts or CDN assets are required.

The 0.5.16 catalog path explicitly understands modern Typer `param_type_name`, so `TyperArgument` remains positional even though current Typer also exposes `opts` on it. Every generated parameter must map to one of the supported Web controls before a release/install gate can pass.

If catalog/runtime loading fails unexpectedly, the API returns a bounded/redacted 503 rather than an opaque 500 traceback. The UI surfaces the failure in the evidence/output area and exposes **Reload interface** plus a catalog-health indicator instead of silently showing an empty operations library.

Users do not type command paths, option names, flags or free-form argv. Structured controls are deterministically serialized only as an internal transport detail to the fixed runner. Web execution uses `shell=False`, disabled stdin, CSRF protection, secret redaction, bounded/cancellable jobs, SSE output and mutation/destructive approval gates. Scope, terms acknowledgement, Policy and approval remain authoritative.

### API Reference `/docs`

The API Reference uses the same Sentinel Forge theme as the Dashboard and Workspace. It is a read-only OpenAPI explorer and renders:

- searchable/filterable endpoint catalog and tags;
- method/path, summary and full description;
- parameters with location, type, required/default/example metadata;
- request-body content types and schemas;
- response status descriptions;
- OpenAPI component/data-model schemas.

It deliberately provides no automatic request-execution control. Loading `/docs` only fetches same-origin `/openapi.json`.

Complete API documentation: [`docs/api/README.md`](docs/api/README.md). Analysis-specific contracts: [`docs/api/analysis-vnext.md`](docs/api/analysis-vnext.md).

## Updates and SRIC repair

```bash
fossilscope update --check
fossilscope update
fossilscope update --force
```

The product updater remains zero-config and never falls back to blind `git pull`. Detached Windows update verification now checks not only package import and `pip check`, but also the complete FossilScope CLI catalog, Web feature catalog and feature contract. A product that installs but leaves the Security Workspace incomplete is rejected and the existing rollback path is used.

## Validation gates

Repository coverage includes unit, integration, E2E CLI, fuzz/security, installer, Web/API and standalone contracts. The functional CLI gate executes all **45 public FossilScope commands** against deterministic offline fixtures and fails if the command tree changes without a matching smoke. Existing standalone coverage checks every supported command help form.

The 0.5.16 parameter/interface gate additionally:

- walks every raw command parameter;
- validates `TyperArgument`/`TyperOption` semantics;
- synthesizes parser-only values for every argument/option without executing active callbacks;
- requires every parameter to map to a supported Web control;
- verifies unknown options and missing required values fail cleanly without tracebacks;
- submits every executable command through the fixed Web transport with the correct approval contract while replacing the execution thread with a deterministic no-side-effect test double;
- requires `/workbench`, catalog and coverage to load successfully and exposes Run, Cancel, Refresh and Reload interface controls.

Required release commands include:

```bash
python -m pytest -q tests/e2e/test_cli_all_commands_functional.py
python -m pytest -q tests/e2e/test_cli_web_parameter_matrix_v0516.py
python -m pytest -q tests/standalone/test_standalone_contract_v05.py
python -m pytest -q tests/e2e/test_security_workspace_v0514.py
python -m pytest -q tests/e2e/test_unified_web_theme_api_docs_v0515.py tests/security/test_web_catalog_compat_v0515.py
python -m sric.standalone_gate --root .
python scripts/release-gate.py
```

`TEST_EVIDENCE.md` is authoritative for what actually executed. A hosted job that never starts its steps is not treated as PASS.

## Uninstall

Linux / Termux:

```bash
./scripts/uninstall-linux.sh
```

Windows:

```cmd
scripts\uninstall-windows.cmd
```

Uninstall removes runtime and command shim while preserving workspaces, configuration and evidence under `~/.fossilscope/` / `%USERPROFILE%\.fossilscope`.

Telemetry, cloud AI and external uploads are OFF by default. Apache-2.0.
