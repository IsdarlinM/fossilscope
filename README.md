# FossilScope

```text
FossilScope :: v0.5.7
Developer: IsdarlinM

Map historical attack surface and separate history from current exposure.
```

Attack Surface Archaeology + Temporal Security Graph for discovering historical capabilities without confusing historical evidence with current exposure.

> **AI proposes. Evidence proves. Humans control.**

## Standalone by design

FossilScope is independently installable and independently useful. It uses **SRIC Core 0.5.x** internally for evidence, provenance, workspaces, policy, scope, jobs and shared research primitives, but **ReproSec, AuthTwin, TrustBoundary Mapper and Exposure DNA are not required**.

```bash
fossilscope doctor
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
- zero-config official update flow with safe same-version `update --force` reinstall support;
- **full Web Feature Workbench** with every public FossilScope CLI command and argument represented as structured responsive controls;
- advanced Web Command Console with exact public CLI command-tree parity and real-time jobs;
- professional Rich/Typer terminal presentation with subdued green banner and `--no-color` support.

## Exposure lifecycle controls

FossilScope distinguishes `HISTORICAL_ONLY`, `CURRENT_DNS`, `CURRENT_TLS`, `CURRENT_HTTP`, `CURRENT_AUTHENTICATED`, `REDIRECTED`, `PARKED`, `SINKHOLED`, `TRANSFERRED`, `RETIRED` and `UNKNOWN_CURRENT_STATE`.

Historical evidence never proves present reachability. DNS alone does not prove an application is active. Wildcard DNS, shared infrastructure, default virtual hosts, parking, sinkholes, ownership transfers and retirement records reduce or disqualify resurrection candidates. A historical asset with direct current application evidence may become a `HYPOTHESIS`; it never becomes `VALIDATED` without deterministic evidence and human-controlled validation.

## Standalone install

Linux:

```bash
./scripts/install-linux.sh
fossilscope doctor
fossilscope capabilities
```

Windows:

```cmd
scripts\install-windows.cmd
fossilscope doctor
fossilscope capabilities
```

The installers resolve the compatible SRIC Core package automatically. `SRIC_CORE_SOURCE=/path/to/sric-core` is an explicit development/release-validation override only; sibling repositories are never auto-detected.

## CLI presentation

Interactive terminals display a compact subdued-green banner ordered as `FossilScope :: v0.5.7`, `Developer: IsdarlinM`, then `Map historical attack surface and separate history from current exposure.` Use `fossilscope --no-color COMMAND`, `fossilscope COMMAND --no-color`, or `NO_COLOR=1` for plain terminal presentation.

## Quickstart

```bash
fossilscope doctor
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

The dashboard root is intentionally a quick temporal view, but it now exposes visible navigation to:

- **All Features** → `/workbench`: every public `fossilscope.cli_all` command and every CLI argument/option as structured responsive controls;
- **Advanced Console** → `/console`: expert argv-oriented command execution.

This directly avoids the previous situation where the root dashboard displayed only Temporal Security Graph, Fossil Candidates and Lifecycle while the rest of the product was hidden from normal Web navigation.

The Workbench is derived from the installed CLI tree; `/api/v1/workbench/coverage` must report exact command/parameter parity. It uses the fixed SRIC runner with `shell=False`, disabled stdin, CSRF protection, secret redaction, bounded/cancellable jobs and SSE output. FossilScope remains passive-first; scope, terms acknowledgement, Policy and approval gates remain authoritative.

Workspace names are not filesystem paths. `../` traversal and workspace symlinks are rejected. Missing or invalid workspaces produce actionable errors without Python tracebacks.

## Updates

```bash
fossilscope update --check
fossilscope update
fossilscope update --force
```

The official path is zero-config. Normal users provide no manifest or public key. `--force` can reinstall the same official version or move forward, never downgrade. Custom `--manifest` + `--public-key` remains an advanced signed-channel override.

## Validation gates

```bash
python -m sric.standalone_gate --root .
python scripts/release-gate.py
```

The 0.5.7 interface suite walks every public FossilScope command with `--help`, verifies every option and required argument, compares the complete ordered CLI parameter tree with the Workbench catalog, verifies the dashboard links to all features, and smoke-tests the native timeline/candidates/lifecycle/graph/clusters/jobs/notebook APIs. Destructive or active operations are gate-tested rather than executed merely for coverage.

Machine-readable evidence is written under `build/release-evidence/`. A release requires PASS for the exact source commit.

## Uninstall

```bash
./scripts/uninstall-linux.sh
```

Uninstall removes runtime and command shim while preserving workspaces, configuration and evidence under `~/.fossilscope/`.

Telemetry, cloud AI and external uploads are OFF by default. Apache-2.0.
