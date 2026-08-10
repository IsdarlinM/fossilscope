# FossilScope

```text
FossilScope :: v0.5.13
Developer: IsdarlinM

Map historical attack surface and separate history from current exposure.
```

Attack Surface Archaeology + Temporal Security Graph for discovering historical capabilities without confusing historical evidence with current exposure.

> **AI proposes. Evidence proves. Humans control.**

## Standalone by design

FossilScope is independently installable and useful. It uses **SRIC Core >=0.5.13,<0.6** for evidence, provenance, workspaces, policy, scope, jobs and shared Web/runtime primitives. ReproSec, AuthTwin, TrustBoundary Mapper and Exposure DNA remain optional integrations.

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
- complete Web/API factory with vNext analysis and capability routes;
- validated named-workspace resolution with traversal/symlink escape rejection and actionable errors;
- zero-config official product update flow with same-version `update --force`, rollback and first-party runtime repair;
- exact SRIC distribution/module compatibility checks in `doctor` and `/api/v1/runtime-compatibility`;
- guided **Web Security Console** with every public FossilScope capability represented as operation cards and typed responsive controls;
- checkboxes/tri-state selectors for flags, combo/select controls for closed choices, numeric/path controls, repeated-value controls and protected sensitive fields;
- shared JSON-safe Web capability catalog generation with choice/bound/path metadata;
- structured redacted HTTP 503 behavior when capability-catalog construction itself fails;
- bounded Web child termination/reaping and short-lived retired-job retention so active SSE/status readers do not race pruning;
- shared operational exception containment and Job Engine secret redaction;
- lazy shared-Web loading and actionable degraded `/workbench` 503 behavior;
- fixed-runner execution with exact CLI-tree parity and real-time jobs while keeping free-form command/argv entry out of the user interface;
- professional Rich/Typer terminal presentation with subdued green banner and `--no-color` support.

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

The installer pins SRIC Core to immutable GitHub-verified commit `bd90fe668e4a2a23c00a39f7d63df1c092b63c12` and resolves that explicit first-party source in the same pip transaction as FossilScope. `SRIC_CORE_SOURCE=/path/to/sric-core` remains an explicit development/release-validation override only.

Installers are idempotent and repair-capable while preserving workspaces, configuration and evidence. They validate host Python and any existing venv, rebuild only a stale/broken isolated venv, bootstrap `pip`/`setuptools`/`wheel`, run `pip check`, import-probe `sric.web_console`, `sric.web_workbench`, `sric.web_catalog` and `sric.web_runtime`, verify SRIC `>=0.5.13,<0.6`, and smoke-test doctor/capabilities plus `--help`, `-h` and `help` before reporting success.

Installer-internal smokes use `SENTINEL_BANNER=never`, so successful installation does not print the FossilScope banner repeatedly. Diagnostic output is captured and printed only when validation fails. Normal installation does not use `--force-reinstall`; force reinstall is reserved for explicit repair/update operations.

Termux prefers a writable `$PREFIX/bin` already present in `PATH`. Standard Linux falls back to `~/.local/bin`. Windows uses SRIC's registry-backed `sric.install_path` helper instead of `setx`.

### Recover an existing installation

A normal product install/repair or verified `fossilscope update` is preferred. For a development checkout, after updating the checkout run:

```bash
./scripts/install-linux.sh
fossilscope doctor --json
~/.fossilscope/venv/bin/python -m pip check
~/.fossilscope/venv/bin/python -c 'import sric.web_console, sric.web_workbench, sric.web_catalog, sric.web_runtime; print("SRIC Web runtime OK")'
fossilscope web imr
```

Do not delete `~/.fossilscope/` to repair this class of runtime problem; workspaces and evidence are intentionally preserved. Production update does not depend on blind `git pull`.

## CLI presentation and help contract

Interactive terminals display `FossilScope :: v0.5.13`, `Developer: IsdarlinM`, then the purpose statement. Use `fossilscope --no-color COMMAND`, `fossilscope COMMAND --no-color`, or `NO_COLOR=1` for plain output.

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

The native dashboard remains the temporal quick view for timeline, fossil candidates, lifecycle and evidence. `/workbench` is the primary **Security Console**, generated from every public `fossilscope.cli_all` capability and parameter. `/console` is retained only as a compatibility alias that opens `/workbench`; it is not an argv-oriented user interface.

`/api/v1/workbench/coverage` must report exact CLI/Web command and parameter parity. `/api/v1/runtime-compatibility` reports installed core version, required modules and incompatibility reasons. Shared Security Console CSS/JS are same-origin and protected by restrictive CSP object/base/frame policies.

The capability catalog is normalized to JSON-safe primitives and includes choice, numeric-bound and path metadata so appropriate HTML controls can be rendered without duplicating CLI logic. A catalog-construction failure returns a bounded/redacted HTTP 503 instead of an opaque serialization HTTP 500.

Users do not type command paths, option names, flags or free-form argv. Structured controls are deterministically serialized only as an internal transport detail to the fixed runner. Web execution uses `shell=False`, disabled stdin, CSRF protection, secret redaction, bounded/cancellable jobs, SSE output and mutation/destructive approval gates. Scope, terms acknowledgement, Policy and approval remain authoritative.

Timed-out child processes use bounded terminate/kill/wait handling with a background reaper if required. Recently pruned terminal jobs are retained briefly for already-active status/SSE readers. Workspace names are not filesystem paths; traversal and workspace symlinks are rejected.

## Updates and SRIC repair

```bash
fossilscope update --check
fossilscope update
fossilscope update --force
```

For a functioning CLI, supported stale SRIC cores are advanced through immutable GitHub-signature-verified snapshots one release at a time from 0.5.5 through the 0.5.13 floor. This avoids unsafe rollback-metadata jumps. A same-version corrupt 0.5.13 runtime is repaired from the fixed verified 0.5.13 snapshot. The product updater remains zero-config and never falls back to blind `git pull`.

The FossilScope 0.5.13 official channel points to a GitHub-verified release commit and carries rollback metadata for the immediately preceding verified 0.5.12 snapshot. This keeps rollback metadata aligned with the actually installed prior version.

## Validation gates

Repository coverage includes unit, integration, E2E CLI, fuzz/security, installer, Web/API and standalone contracts. The 0.5.13 compatibility regressions walk every public CLI command, all supported help forms, exact ordered CLI/Web parameter parity, structured controls and absence of free-form argv UI. Existing Web tests cover the native dashboard, guided Workbench, legacy console alias, assets/catalogs/coverage and native API surfaces.

Required release commands include:

```bash
python -m sric.standalone_gate --root .
python scripts/release-gate.py
```

`TEST_EVIDENCE.md` is authoritative for what actually executed. GitHub-hosted runners are currently blocked by an account billing lock, so a zero-step workflow is not treated as PASS. The current execution environment also lacks GitHub network/DNS access, so no substitute clone-based local full-suite PASS is claimed.

## Uninstall

```bash
./scripts/uninstall-linux.sh
```

Uninstall removes runtime and command shim while preserving workspaces, configuration and evidence under `~/.fossilscope/`.

Telemetry, cloud AI and external uploads are OFF by default. Apache-2.0.
