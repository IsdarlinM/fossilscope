# FossilScope

```text
FossilScope :: v0.5.11
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
- JSON-safe shared Web command catalog generation, preventing non-primitive Typer metadata from surfacing as an opaque HTTP 500;
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

The normal installer pins SRIC Core to an immutable GitHub commit and resolves that explicit first-party source **in the same pip transaction as FossilScope**. This is important because `sric-core` is intentionally not discovered from PyPI; a separate product-only reinstall would make pip search the public index and can produce `ResolutionImpossible` even after SRIC was already bootstrapped. `SRIC_CORE_SOURCE=/path/to/sric-core` remains an explicit development/release-validation override only.

The installers are idempotent and repair-capable while preserving workspaces/configuration/evidence. They validate the host Python and any existing venv; an obsolete, incomplete or broken runtime rebuilds **only** `~/.fossilscope/venv`. They bootstrap `pip`, `setuptools` and `wheel`, resolve the constrained product + explicit SRIC source, run `pip check`, import `sric.web_console`, `sric.web_workbench` and `sric.web_catalog`, verify SRIC `>=0.5.11,<0.6`, and run doctor/capability plus `--help`, `-h` and `help` smokes before reporting success.

Installer-internal CLI smokes use `SENTINEL_BANNER=never`; their output is written to a temporary validation log and is shown only when a check fails. A successful install therefore no longer prints the FossilScope banner repeatedly. Normal installation also does not use `--force-reinstall`; that behavior remains reserved for explicit repair/update force operations.

On Termux a writable `$PREFIX/bin` already present in `PATH` is preferred so the command is immediately available. Standard Linux falls back to `~/.local/bin` and persists the canonical profile entry only when needed. Windows uses SRIC's registry-backed `sric.install_path` helper instead of `setx`, preserving the existing user PATH value type and broadcasting the environment change; any Python 3 interpreter satisfying `>=3.11` is accepted.

### Recovering an existing installation

```bash
cd ~/fossilscope
git pull --ff-only
./scripts/install-linux.sh
fossilscope doctor --json
~/.fossilscope/venv/bin/python -m pip check
~/.fossilscope/venv/bin/python -c 'import sric.web_console, sric.web_workbench, sric.web_catalog; print("SRIC Web runtime OK")'
fossilscope web imr
```

Do not delete `~/.fossilscope/` to repair this class of runtime problem; workspaces and evidence are intentionally preserved.

## CLI presentation

Interactive terminals display a compact subdued-green banner ordered as `FossilScope :: v0.5.11`, `Developer: IsdarlinM`, then `Map historical attack surface and separate history from current exposure.` Use `fossilscope --no-color COMMAND`, `fossilscope COMMAND --no-color`, or `NO_COLOR=1` for plain terminal presentation.

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

The native CSP permits same-origin shared Web CSS/JS while retaining `object-src 'none'`, `base-uri 'none'` and `frame-ancestors 'none'`. The command catalog is normalized to JSON-safe primitives before FastAPI serialization, so `Path`, enum/container defaults and unusual Typer metadata do not produce the previous `catalog HTTP 500` failure.

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

The 0.5.11 installer regressions cover atomic first-party resolution, immutable SRIC 0.5.11 pin/lock, venv-only repair, Termux `$PREFIX/bin`, safe Windows PATH handling, quiet banner-free installation smokes and dependency/import/help checks. Web regressions verify `/console` plus its CSS/JS assets, a non-empty HTTP-200 command catalog, `/workbench`, its feature catalog and exact CLI/Web coverage.

Machine-readable evidence is written under `build/release-evidence/`. A release requires PASS for the exact source commit.

## Uninstall

```bash
./scripts/uninstall-linux.sh
```

Uninstall removes runtime and command shim while preserving workspaces, configuration and evidence under `~/.fossilscope/`.

Telemetry, cloud AI and external uploads are OFF by default. Apache-2.0.
