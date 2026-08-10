# FossilScope

```text
FossilScope :: v0.5.12
Developer: IsdarlinM

Map historical attack surface and separate history from current exposure.
```

Attack Surface Archaeology + Temporal Security Graph for discovering historical capabilities without confusing historical evidence with current exposure.

> **AI proposes. Evidence proves. Humans control.**

## Standalone by design

FossilScope is independently installable and useful. It uses **SRIC Core >=0.5.12,<0.6** for evidence, provenance, workspaces, policy, scope, jobs and shared Web/runtime primitives. ReproSec, AuthTwin, TrustBoundary Mapper and Exposure DNA remain optional integrations.

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
- **full Web Feature Workbench** with every public FossilScope CLI command and argument represented as structured responsive controls;
- shared JSON-safe Web command catalog generation;
- structured redacted HTTP 503 behavior when command-catalog construction itself fails;
- bounded Web Console child termination/reaping and short-lived retired-job retention so active SSE/status readers do not race pruning;
- shared operational exception containment and Job Engine secret redaction;
- lazy shared-Web loading and actionable degraded `/workbench` 503 behavior;
- advanced Web Command Console with fixed-runner execution, exact CLI-tree parity and real-time jobs;
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

The installer pins SRIC Core to the immutable GitHub commit `4dd0ad417e55fc76fb67d582ec50234bffff2876` and resolves that explicit first-party source in the same pip transaction as FossilScope. `SRIC_CORE_SOURCE=/path/to/sric-core` remains an explicit development/release-validation override only.

Installers are idempotent and repair-capable while preserving workspaces, configuration and evidence. They validate host Python and any existing venv, rebuild only a stale/broken isolated venv, bootstrap `pip`/`setuptools`/`wheel`, run `pip check`, import-probe `sric.web_console`, `sric.web_workbench`, `sric.web_catalog` and `sric.web_runtime`, verify SRIC `>=0.5.12,<0.6`, and smoke-test doctor/capabilities plus `--help`, `-h` and `help` before reporting success.

Installer-internal smokes use `SENTINEL_BANNER=never`, so successful installation does not print the FossilScope banner repeatedly. Diagnostic output is captured and printed only when validation fails. Normal installation does not use `--force-reinstall`; force reinstall is reserved for explicit repair/update operations.

Termux prefers a writable `$PREFIX/bin` already present in `PATH`. Standard Linux falls back to `~/.local/bin`. Windows uses SRIC's registry-backed `sric.install_path` helper instead of `setx`.

### Recover an existing installation

```bash
cd ~/fossilscope
git pull --ff-only
./scripts/install-linux.sh
fossilscope doctor --json
~/.fossilscope/venv/bin/python -m pip check
~/.fossilscope/venv/bin/python -c 'import sric.web_console, sric.web_workbench, sric.web_catalog, sric.web_runtime; print("SRIC Web runtime OK")'
fossilscope web imr
```

Do not delete `~/.fossilscope/` to repair this class of runtime problem; workspaces and evidence are intentionally preserved.

## CLI presentation and help contract

Interactive terminals display `FossilScope :: v0.5.12`, `Developer: IsdarlinM`, then the purpose statement. Use `fossilscope --no-color COMMAND`, `fossilscope COMMAND --no-color`, or `NO_COLOR=1` for plain output.

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

The dashboard exposes:

- **All Features** → `/workbench`, generated from every public `fossilscope.cli_all` command and parameter;
- **Advanced Console** → `/console`, expert argv-oriented command execution through the fixed Python runner.

`/api/v1/workbench/coverage` must report exact CLI/Web command and parameter parity. `/api/v1/runtime-compatibility` reports installed core version, required modules and incompatibility reasons. Shared Console/Workbench CSS/JS are same-origin and protected by restrictive CSP object/base/frame policies.

The command catalog is normalized to JSON-safe primitives. A catalog-construction failure returns a bounded/redacted HTTP 503 instead of an opaque serialization HTTP 500. Web execution uses `shell=False`, disabled stdin, CSRF protection, secret redaction, bounded/cancellable jobs, SSE output and mutation/destructive approval gates. Scope, terms acknowledgement, Policy and approval remain authoritative.

Timed-out child processes use bounded terminate/kill/wait handling with a background reaper if required. Recently pruned terminal jobs are retained briefly for already-active status/SSE readers. Workspace names are not filesystem paths; traversal and workspace symlinks are rejected.

## Updates and SRIC repair

```bash
fossilscope update --check
fossilscope update
fossilscope update --force
```

For a functioning CLI, supported stale SRIC cores are advanced through immutable GitHub-signature-verified snapshots one release at a time from 0.5.5 through the 0.5.12 floor. This avoids unsafe rollback-metadata jumps. A same-version corrupt 0.5.12 runtime is repaired from the fixed signed 0.5.12 snapshot. The product updater remains zero-config and never falls back to blind `git pull`.

The SRIC official update channel may remain on the previous fully gated release until 0.5.12's exact-commit release gates execute; FossilScope's pinned first-party dependency is independent of that channel.

## Validation gates

Repository coverage includes unit, integration, E2E CLI, fuzz/security, installer, Web/API and standalone contracts. The 0.5.12 compatibility regression walks every public CLI command, all supported help forms and exact ordered CLI/Web parameter parity. Existing Web tests cover Console/Workbench pages/assets/catalogs/coverage and native API surfaces.

Required release commands include:

```bash
python -m sric.standalone_gate --root .
python scripts/release-gate.py
```

`TEST_EVIDENCE.md` is authoritative for what actually executed. GitHub-hosted runners are currently blocked by an account billing lock, so a zero-step workflow is not treated as PASS. The shared SRIC 0.5.12 focused runtime harness passed its four targeted regressions after identifying and fixing a background-reaper return-code race; this does not substitute for FossilScope's full exact-commit gates.

## Uninstall

```bash
./scripts/uninstall-linux.sh
```

Uninstall removes runtime and command shim while preserving workspaces, configuration and evidence under `~/.fossilscope/`.

Telemetry, cloud AI and external uploads are OFF by default. Apache-2.0.
