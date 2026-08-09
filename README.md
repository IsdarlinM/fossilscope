# FossilScope

```text
FossilScope :: v0.5.6
Developer: IsdarlinM

Map historical attack surface and separate history from current exposure.
```

Attack Surface Archaeology + Temporal Security Graph for discovering historical capabilities without confusing historical evidence with current exposure.

> **AI proposes. Evidence proves. Humans control.**

## Standalone by design

FossilScope is independently installable and independently useful. It uses **SRIC Core 0.5.x** internally for evidence, provenance, workspaces, policy, scope, jobs and shared research primitives, but **ReproSec, AuthTwin, TrustBoundary Mapper and Exposure DNA are not required**.

Installing other Sentinel Forge products only unlocks optional cross-product capabilities. Check the current environment with:

```bash
fossilscope doctor
fossilscope capabilities
```

The absence of another Sentinel Forge product is never a FossilScope startup error.

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
- Web Command Console with exact public CLI command-tree parity and real-time jobs;
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

Interactive terminals display a compact subdued-green banner ordered as `FossilScope :: v0.5.6`, `Developer: IsdarlinM`, then `Map historical attack surface and separate history from current exposure.` Use `fossilscope --no-color COMMAND`, `fossilscope COMMAND --no-color`, or `NO_COLOR=1` for plain terminal presentation. The banner is emitted to interactive stderr so JSON and redirected stdout remain clean. See `docs/cli-presentation.md`.

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

`fossilscope web WORKSPACE` serves the complete local responsive dashboard and API for an **existing named workspace**. The default workspace root is `~/.fossilscope/workspaces`.

```bash
fossilscope workspace list
fossilscope web imr
```

If the workspace lives under a different parent directory, select that parent explicitly:

```bash
fossilscope web imr --root /path/to/workspaces
```

Workspace names are not filesystem paths. `../` traversal and workspace symlinks are rejected rather than allowing a named workspace to escape the selected root. Missing or invalid workspaces produce an actionable CLI error and do not emit a Python traceback.

The existing temporal Web UI remains available with fossil candidates, lifecycle information, search, evidence detail and real-time job status. `/console` adds the Web Command Console, whose catalog is generated from `fossilscope.cli_all`; a standalone test requires the Web and CLI command-path sets to be exactly equal.

The console is **not an operating-system web shell**. It invokes only the fixed SRIC runner with `shell=False`, disabled stdin and a structured argv array. Mutating commands require explicit approval, while FossilScope passive-first, scope and terms-acknowledgement gates remain authoritative. See `docs/web/cli-parity.md`.

## Updates

The official update path is zero-config:

```bash
fossilscope update --check
fossilscope update
fossilscope update --force
```

Normal users do **not** provide a manifest or public key. SRIC resolves only the fixed official `IsdarlinM/fossilscope` channel, requires the selected immutable release commit to be reported by GitHub as signature-verified, validates the exact source snapshot and package metadata, backs up state, installs without a shell, and verifies the installed distribution version.

`--force` reinstalls the official release even when that exact version is already installed. It may install a newer official release but never downgrades; `--check` and `--force` cannot be combined. Normal upgrades require rollback metadata; same-version forced reinstalls use the verified target snapshot as the recovery package.

`--manifest` and `--public-key` remain available together only as an advanced custom/private-channel override. Custom channels retain Ed25519 manifest and SHA-256 wheel verification. No blind `git pull` fallback is used. See `docs/release/update.md`.

## Validation gates

Standalone conformance:

```bash
python -m sric.standalone_gate --root .
```

Full repository release gate:

```bash
python scripts/release-gate.py
```

Machine-readable evidence is written under `build/release-evidence/`. A release requires PASS for the exact source commit; merely setting the package version is not release evidence.

## Uninstall

```bash
./scripts/uninstall-linux.sh
```

Uninstall removes the runtime and command shim while preserving workspaces, configuration and evidence under `~/.fossilscope/`.

Telemetry, cloud AI and external uploads are OFF by default. Apache-2.0.
