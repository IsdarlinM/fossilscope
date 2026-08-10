# FossilScope

```text
FossilScope :: v0.5.15
Developer: IsdarlinM

Map historical attack surface and separate history from current exposure.
```

Attack Surface Archaeology + Temporal Security Graph for discovering historical capabilities without confusing historical evidence with current exposure.

> **AI proposes. Evidence proves. Humans control.**

## Standalone by design

FossilScope is independently installable and useful. Its package remains transition-compatible with **SRIC Core >=0.5.14,<0.6** so an existing 0.5.14 product can update safely; clean/repair 0.5.15 installs pin and verify **SRIC Core 0.5.15** for the canonical shared theme and catalog hardening. ReproSec, AuthTwin, TrustBoundary Mapper and Exposure DNA remain optional integrations.

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
- bounded compatibility bridge for the SRIC 0.5.14 unknown-parameter catalog failure so the reported `catalog HTTP 500` class does not collapse the Security Workspace during a product-first update;
- checkboxes/tri-state selectors for flags, combo/select controls for closed choices, numeric/path controls, repeated-value controls and protected sensitive fields;
- shared JSON-safe Web capability catalog generation with choice/bound/path metadata;
- structured redacted catalog failure handling instead of opaque user-visible serialization errors;
- bounded Web child termination/reaping and short-lived retired-job retention so active SSE/status readers do not race pruning;
- shared operational exception containment and Job Engine secret redaction;
- lazy shared-Web loading and actionable degraded `/workbench` behavior;
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

Clean/repair installation pins SRIC Core to GitHub-verified commit `95e093a0b8c2041037836cec235a73fd578d815c` (SRIC Core 0.5.15) and resolves that explicit first-party source in the same pip transaction as FossilScope. `SRIC_CORE_SOURCE=/path/to/sric-core` remains an explicit development/release-validation override only.

Installers are repair-capable while preserving workspaces, configuration and evidence. They validate host Python, bootstrap `pip`/`setuptools`/`wheel`, run `pip check`, import-probe `sric.web_console`, `sric.web_workbench`, `sric.web_security_workspace`, `sric.web_catalog`, `sric.web_runtime` and `sric.web_theme`, verify FossilScope `0.5.15` plus SRIC `>=0.5.15,<0.6`, and smoke-test version/doctor/capabilities plus root help aliases before reporting success. Windows repair is transactional: the prior isolated runtime is staged as `venv.rollback`, the replacement is verified, and the previous runtime is restored if installation validation fails.

Installer-internal smokes use `SENTINEL_BANNER=never`, so successful installation does not print the FossilScope banner repeatedly. Diagnostic output is captured and printed only when validation fails.

Termux prefers a writable `$PREFIX/bin` already present in `PATH`. Standard Linux falls back to `~/.local/bin`. Windows uses SRIC's registry-backed `sric.install_path` helper instead of `setx`.

### Product-first 0.5.14 -> 0.5.15 compatibility

The official source updater installs verified product archives with `--no-deps`. To avoid recreating the previous Windows update failure class, FossilScope 0.5.15 keeps its package dependency compatible with SRIC 0.5.14 while clean/repair installation pins SRIC 0.5.15. Two bounded bridges keep the upgraded product importable on an existing 0.5.14 shared runtime:

- the shared theme falls back locally only when `sric.web_theme` does not yet exist;
- the specific 0.5.14 Web-catalog `TypeError` path falls back to the legacy parameter serializer instead of returning catalog HTTP 500.

SRIC Core 0.5.15 contains the canonical implementations. The compatibility code does not replace an installed 0.5.15 module.

### Recover an existing Windows installation

When a broken runtime cannot import dependencies far enough to execute `fossilscope update`, run the external repair entrypoint from a current checkout:

```cmd
scripts\repair-windows.cmd
```

It rebuilds only `%USERPROFILE%\.fossilscope\venv` and preserves workspaces, configuration, evidence and reports.

Do not delete `~/.fossilscope/` to repair runtime problems; workspaces and evidence are intentionally preserved. Production update does not depend on blind `git pull`.

## CLI presentation and help contract

Interactive terminals display `FossilScope :: v0.5.15`, `Developer: IsdarlinM`, then the purpose statement. Use `fossilscope --no-color COMMAND`, `fossilscope COMMAND --no-color`, or `NO_COLOR=1` for plain output.

Supported help forms are:

```text
fossilscope --help
fossilscope -h
fossilscope help
fossilscope COMMAND --help
fossilscope COMMAND -h
fossilscope COMMAND help
```

Unexpected operational exceptions are redacted/contained by the shared SRIC boundary. `SENTINEL_DEBUG=1` is an explicit developer-only opt-in for raw local exception propagation.

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

The native temporal dashboard now uses the same Sentinel Forge product rail, blue/graphite surfaces, typography and spacing as Security Workspace. It remains the quick view for timeline, fossil candidates, lifecycle, search, job activity and evidence details.

### Security Workspace `/workbench`

The shared Workspace is generated from every public `fossilscope.cli_all` capability and parameter. Desktop uses a Sentinel Forge product rail, then Operations Library + Operation Workspace, with Recent Activity below. Configuration, approvals and execution evidence/output are distinct surfaces. Mobile collapses to guided Operations / Configure / Activity views.

`/api/v1/workbench/coverage` must report exact CLI/Web command and parameter parity. `/api/v1/runtime-compatibility` reports installed core version, required modules and incompatibility reasons. Shared Security Workspace CSS/JS are same-origin. No external fonts or CDN assets are required.

The 0.5.15 catalog path is hardened against the reported unknown Click/Typer parameter subtype failure. A single unsupported subtype is serialized conservatively rather than causing the entire catalog to fail with HTTP 500.

Users do not type command paths, option names, flags or free-form argv. Structured controls are deterministically serialized only as an internal transport detail to the fixed runner. Web execution uses `shell=False`, disabled stdin, CSRF protection, secret redaction, bounded/cancellable jobs, SSE output and mutation/destructive approval gates. Scope, terms acknowledgement, Policy and approval remain authoritative.

### API Reference `/docs`

The old green minimal API page was replaced with the same Sentinel Forge theme as the Dashboard and Workspace. It is a read-only OpenAPI explorer and renders:

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

The product updater remains zero-config and never falls back to blind `git pull`. FossilScope 0.5.15 is intentionally product-update compatible with an already-installed SRIC 0.5.14 runtime, while clean/repair installation resolves the signed SRIC 0.5.15 release. This avoids making the Web/API redesign depend on an unsafe in-process first-party dependency mutation.

## Validation gates

Repository coverage includes unit, integration, E2E CLI, fuzz/security, installer, Web/API and standalone contracts. The functional CLI gate executes all **45 public FossilScope commands** against deterministic offline fixtures and fails if the command tree changes without a matching smoke. Existing standalone coverage checks every supported command help form.

Required release commands include:

```bash
python -m pytest -q tests/e2e/test_cli_all_commands_functional.py
python -m pytest -q tests/standalone/test_standalone_contract_v05.py
python -m pytest -q tests/e2e/test_security_workspace_v0514.py
python -m pytest -q tests/e2e/test_unified_web_theme_api_docs_v0515.py tests/security/test_web_catalog_compat_v0515.py
python -m sric.standalone_gate --root .
python scripts/release-gate.py
```

The 0.5.15 Web/API regression specifically requires Dashboard and `/docs` to carry the Security Workspace theme tokens/fonts, validates rich OpenAPI contracts and checks both `/api/v1/console/catalog` and `/api/v1/workbench/catalog` return HTTP 200.

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
