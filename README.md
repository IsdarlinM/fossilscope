# FossilScope

```text
FossilScope :: v0.5.14
Developer: IsdarlinM

Map historical attack surface and separate history from current exposure.
```

Attack Surface Archaeology + Temporal Security Graph for discovering historical capabilities without confusing historical evidence with current exposure.

> **AI proposes. Evidence proves. Humans control.**

## Standalone by design

FossilScope is independently installable and useful. It uses **SRIC Core >=0.5.14,<0.6** for evidence, provenance, workspaces, policy, scope, jobs and shared Web/runtime primitives. ReproSec, AuthTwin, TrustBoundary Mapper and Exposure DNA remain optional integrations.

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
- zero-config official product update flow with rollback and first-party runtime repair;
- exact SRIC distribution/module compatibility checks in `doctor` and `/api/v1/runtime-compatibility`;
- shared **Sentinel Forge Security Workspace** with a desktop product rail, operation library, dedicated operation workspace, separate evidence/output surface and full-width recent execution history;
- professional offline typography using Segoe UI Variable/Aptos/system UI with Cascadia Code/SFMono/Consolas for evidence output;
- restrained graphite/slate and teal interface palette shared across Sentinel Forge instead of the previous green three-column Workbench presentation;
- checkboxes/tri-state selectors for flags, combo/select controls for closed choices, numeric/path controls, repeated-value controls and protected sensitive fields;
- shared JSON-safe Web capability catalog generation with choice/bound/path metadata;
- structured redacted HTTP 503 behavior when capability-catalog construction itself fails;
- bounded Web child termination/reaping and short-lived retired-job retention so active SSE/status readers do not race pruning;
- shared operational exception containment and Job Engine secret redaction;
- lazy shared-Web loading and actionable degraded `/workbench` 503 behavior;
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

The installer pins SRIC Core to immutable GitHub-verified commit `3c5d1e0eff2584d069843a5234d9d8a0357718b9` and resolves that explicit first-party source in the same pip transaction as FossilScope. `SRIC_CORE_SOURCE=/path/to/sric-core` remains an explicit development/release-validation override only.

Installers are repair-capable while preserving workspaces, configuration and evidence. They validate host Python, bootstrap `pip`/`setuptools`/`wheel`, run `pip check`, import-probe `sric.web_console`, `sric.web_workbench`, `sric.web_security_workspace`, `sric.web_catalog` and `sric.web_runtime`, verify SRIC `>=0.5.14,<0.6`, and smoke-test doctor/capabilities plus `--help`, `-h` and `help` before reporting success. Windows repair is transactional: the prior isolated runtime is staged as `venv.rollback`, the replacement is verified, and the previous runtime is restored if installation validation fails.

Installer-internal smokes use `SENTINEL_BANNER=never`, so successful installation does not print the FossilScope banner repeatedly. Diagnostic output is captured and printed only when validation fails.

Termux prefers a writable `$PREFIX/bin` already present in `PATH`. Standard Linux falls back to `~/.local/bin`. Windows uses SRIC's registry-backed `sric.install_path` helper instead of `setx`.

### Recover an existing Windows installation

When a broken runtime cannot import dependencies far enough to execute `fossilscope update`, run the external repair entrypoint from a current checkout:

```cmd
scripts\repair-windows.cmd
```

It rebuilds only `%USERPROFILE%\.fossilscope\venv` and preserves workspaces, configuration, evidence and reports.

For a development checkout on Linux/Termux:

```bash
./scripts/install-linux.sh
fossilscope doctor --json
~/.fossilscope/venv/bin/python -m pip check
~/.fossilscope/venv/bin/python -c 'import sric.web_console, sric.web_workbench, sric.web_security_workspace, sric.web_catalog, sric.web_runtime; print("SRIC Web runtime OK")'
fossilscope web imr
```

Do not delete `~/.fossilscope/` to repair runtime problems; workspaces and evidence are intentionally preserved. Production update does not depend on blind `git pull`.

## CLI presentation and help contract

Interactive terminals display `FossilScope :: v0.5.14`, `Developer: IsdarlinM`, then the purpose statement. Use `fossilscope --no-color COMMAND`, `fossilscope COMMAND --no-color`, or `NO_COLOR=1` for plain output.

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

The native dashboard remains the temporal quick view for timeline, fossil candidates, lifecycle and evidence. `/workbench` is the primary **Sentinel Forge Security Workspace**, generated from every public `fossilscope.cli_all` capability and parameter. `/console` remains a compatibility alias that opens `/workbench`; it is not an argv-oriented user interface.

The Security Workspace is intentionally organized differently from the older three-column console. Desktop uses a Sentinel Forge product rail, then a two-column Operations Library + Operation Workspace. Recent Activity is a horizontal execution-history panel beneath the main workspace. Configuration, approvals and execution evidence/output are distinct surfaces. Mobile collapses to guided Operations / Configure / Activity views.

`/api/v1/workbench/coverage` must report exact CLI/Web command and parameter parity. `/api/v1/runtime-compatibility` reports installed core version, required modules and incompatibility reasons. Shared Security Workspace CSS/JS are same-origin and protected by restrictive CSP object/base/frame policies. No external fonts or CDN assets are required.

The capability catalog is normalized to JSON-safe primitives and includes choice, numeric-bound and path metadata so appropriate HTML controls can be rendered without duplicating CLI logic. A catalog-construction failure returns a bounded/redacted HTTP 503 instead of an opaque serialization HTTP 500.

Users do not type command paths, option names, flags or free-form argv. Structured controls are deterministically serialized only as an internal transport detail to the fixed runner. Web execution uses `shell=False`, disabled stdin, CSRF protection, secret redaction, bounded/cancellable jobs, SSE output and mutation/destructive approval gates. Scope, terms acknowledgement, Policy and approval remain authoritative.

Timed-out child processes use bounded terminate/kill/wait handling with a background reaper if required. Recently pruned terminal jobs are retained briefly for already-active status/SSE readers. Workspace names are not filesystem paths; traversal and workspace symlinks are rejected.

## Updates and SRIC repair

```bash
fossilscope update --check
fossilscope update
fossilscope update --force
```

For a functioning CLI, supported stale SRIC cores are advanced through immutable GitHub-signature-verified snapshots one release at a time from 0.5.5 through the 0.5.14 floor. The 0.5.14 transition introduces `sric.web_security_workspace` while retaining the existing fixed-runner and Workbench catalog/runtime compatibility layer. The product updater remains zero-config and never falls back to blind `git pull`.

The FossilScope 0.5.14 release channel uses a GitHub-verified product merge commit and retains the immediately preceding 0.5.13 release as rollback metadata.

## Validation gates

Repository coverage includes unit, integration, E2E CLI, fuzz/security, installer, Web/API and standalone contracts. The functional CLI gate executes all 45 public FossilScope commands against deterministic offline fixtures and fails if the command tree changes without a matching smoke. Existing standalone coverage checks every supported command help form. Security Workspace tests verify UI version 3, CLI/Web parity and fixed-runner safety metadata.

Required release commands include:

```bash
python -m pytest -q tests/e2e/test_cli_all_commands_functional.py
python -m pytest -q tests/e2e/test_security_workspace_v0514.py
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
