# FossilScope

```text
FossilScope :: v0.5.8
Developer: IsdarlinM

Map historical attack surface and separate history from current exposure.
```

Attack Surface Archaeology + Temporal Security Graph for discovering historical capabilities without confusing historical evidence with current exposure.

> **AI proposes. Evidence proves. Humans control.**

## Standalone by design

FossilScope is independently installable and independently useful. It uses **SRIC Core 0.5.x** internally for evidence, provenance, workspaces, policy, scope, jobs and shared research primitives, but **ReproSec, AuthTwin, TrustBoundary Mapper and Exposure DNA are not required**.

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
- organization-era-aware integration capabilities when compatible products are present;
- SRIC 0.5.x workspace, graph, jobs/SSE, lineage, notebook/search and confidence primitives;
- local API/Web UI, CLI, reports and offline demo;
- complete Web/API factory with vNext analysis and capability routes;
- validated named-workspace resolution for Web/extended CLI commands, with traversal/symlink escape rejection and actionable errors;
- zero-config official update flow with same-version `update --force`, rollback and first-party runtime repair;
- exact SRIC distribution/module compatibility checks in `doctor` and `/api/v1/runtime-compatibility`;
- **full Web Feature Workbench** with every public FossilScope CLI command and argument represented as structured responsive controls;
- lazy shared-Web loading so a stale/corrupt SRIC cannot crash every FossilScope CLI command at import time;
- actionable degraded `/workbench` 503 behavior when a shared UI module is unavailable;
- advanced Web Command Console with exact public CLI command-tree parity and real-time jobs;
- professional Rich/Typer terminal presentation with subdued green banner and `--no-color` support.

## Exposure lifecycle controls

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

The installers resolve the compatible SRIC Core package automatically. `SRIC_CORE_SOURCE=/path/to/sric-core` is an explicit development/release-validation override only; sibling repositories are never auto-detected.

The installers are repair-capable. Existing virtual environments are not blindly trusted: the pinned signed SRIC runtime and FossilScope are force-reinstalled, `pip check` must pass, both `sric.web_console` and `sric.web_workbench` must import, the SRIC version range is verified, and doctor/capability/help smokes run before installation is reported successful. Workspaces/configuration/evidence under `~/.fossilscope/` are preserved.

### Recovering a stale SRIC installation

If a previously installed FossilScope fails before command dispatch with a missing shared SRIC module, update the checkout and rerun the repair installer rather than deleting the workspace:

```bash
cd ~/fossilscope
git pull --ff-only
./scripts/install-linux.sh
fossilscope doctor --json
~/.fossilscope/venv/bin/python -m pip check
~/.fossilscope/venv/bin/python -c 'import sric.web_console, sric.web_workbench; print("SRIC Web runtime OK")'
fossilscope web imr
```

## CLI presentation

Interactive terminals display a compact subdued-green banner ordered as `FossilScope :: v0.5.8`, `Developer: IsdarlinM`, then `Map historical attack surface and separate history from current exposure.` Use `fossilscope --no-color COMMAND`, `fossilscope COMMAND --no-color`, or `NO_COLOR=1` for plain terminal presentation.

The help contract covers `fossilscope --help`, `fossilscope -h`, `fossilscope help`, `fossilscope COMMAND --help`, `fossilscope COMMAND -h` and `fossilscope COMMAND help`.

## Quickstart

```bash
fossilscope doctor --json
fossilscope capabilities
fossilscope init imr
fossilscope workspace list
fossilscope web imr
```

For the synthetic offline demo:

```bash
fossilscope demo --workspace demo
fossilscope timeline demo
fossilscope fossils demo
fossilscope web demo
```

Network collection is never hidden. `collect-url` requires HTTPS, explicit `--allow` scope and `--ack-terms`.

## Web and API

`fossilscope web WORKSPACE` serves the local dashboard and API for an **existing named workspace**. The default root is `~/.fossilscope/workspaces`.

The dashboard root is intentionally a quick temporal view and exposes visible navigation to:

- **All Features** → `/workbench`: every public `fossilscope.cli_all` command and every CLI argument/option as structured responsive controls;
- **Advanced Console** → `/console`: expert argv-oriented command execution.

The Workbench is derived from the installed CLI tree; `/api/v1/workbench/coverage` must report exact command/parameter parity. `/api/v1/runtime-compatibility` reports the installed core version, required modules and reasons when incompatible.

Shared Web modules are loaded lazily. If the Workbench is missing, the native temporal dashboard remains available and `/workbench` returns `RUNTIME_INCOMPATIBLE`/503 with repair guidance instead of raising `ModuleNotFoundError` during CLI startup.

Web command execution uses the fixed SRIC runner with `shell=False`, disabled stdin, CSRF protection, secret redaction, bounded/cancellable jobs and SSE output. FossilScope remains passive-first; scope, terms acknowledgement, Policy and approval gates remain authoritative.

Workspace names are not filesystem paths. `../` traversal and workspace symlinks are rejected. Missing or invalid workspaces produce actionable errors without Python tracebacks.

## Updates

```bash
fossilscope update --check
fossilscope update
fossilscope update --force
```

For a functioning CLI, the official update path checks SRIC before updating FossilScope. Supported stale cores are advanced through immutable GitHub-signature-verified 0.5.x transition snapshots to the compatible floor, while a compatible-version core missing required modules is force-reinstalled. Custom/private `--manifest` plus `--public-key` channels remain explicit and are not silently replaced with the official core channel.

A severely degraded installation that crashes before command dispatch must use the repair installer above first. The official path remains zero-config, may reinstall the same release or move forward, never downgrades, and never falls back to blind `git pull`.

## Validation gates

```bash
python -m sric.standalone_gate --root .
python scripts/release-gate.py
```

The 0.5.8 regression suite reproduces the exact reported stale-SRIC/missing-`sric.web_workbench` failure shape, validates the signed 0.5.5→0.5.6→0.5.7 transition chain and same-version repair, verifies degraded Web behavior, walks every public FossilScope command with all supported help forms, and compares every ordered CLI argument/option with the Workbench schema. Existing unit/integration/E2E/security suites continue to cover timeline, fossils, lifecycle, graph/clusters, passive adapters, bounded HTTPS collection, scope/terms gates, re-observation, workspace safety, import hardening and native Web/API routes. Active/destructive operations are gate-tested rather than executed merely for coverage.

Machine-readable evidence is written under `build/release-evidence/`. A release requires PASS for the exact source commit.

## Uninstall

```bash
./scripts/uninstall-linux.sh
```

Uninstall removes runtime and command shim while preserving workspaces, configuration and evidence under `~/.fossilscope/`.

Telemetry, cloud AI and external uploads are OFF by default. Apache-2.0.
