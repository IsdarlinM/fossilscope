# Changelog

## 0.5.13 - 2026-08-10
- Fixed the Windows self-update failure where `fossilscope update --force` attempted to replace the running `Scripts\fossilscope.exe`, causing `WinError 32`, a partial pip uninstall, and a secondary rollback failure on loaded native modules.
- Official Windows updates now stage and verify the target first, hand installation to a detached helper, wait for the active FossilScope process to exit, verify the repaired runtime, and retain deterministic rollback/result logs.
- Hardened Windows installation/repair so an existing runtime is moved to `venv.rollback` before a fresh canonical venv is created. Failed installation or validation restores the previous runtime when available without deleting workspaces, configuration, evidence, or reports.
- Added `scripts\repair-windows.cmd` for explicit recovery when a corrupted runtime cannot import FossilScope far enough to execute `fossilscope update`.
- Added an exact regression for the reported missing `annotated_types` failure: Windows CI deliberately removes `annotated-types`, requires the CLI to fail, repairs the runtime, and verifies `version`, `doctor --json`, `capabilities`, workspace preservation, rollback cleanup and the data-preserving Windows uninstaller.
- Added a mandatory deterministic functional smoke for all 45 current public CLI commands. The test compares the real Typer command tree against the smoke matrix, so a new public command cannot be introduced without functional coverage; all existing `--help`, `-h`, and trailing `help` coverage remains required.
- Replaced private-token/same-branch SRIC CI coupling with an exact public SRIC Core stabilization commit and corrected `doctor` to report the canonical `>=0.5.13,<0.6` compatibility range.
- Integrated the audited Web/API stabilization: controlled invalid-input responses, same-origin offline OpenAPI docs, `--version`, and data-preserving Windows uninstall behavior.
- Hosted CI availability is not represented as proof; release status requires executed exact-head evidence.

## 0.5.12 - 2026-08-10
- Updated FossilScope to the signed SRIC Core 0.5.12 main revision and raised the runtime floor to `>=0.5.12,<0.6` across package metadata, bootstrap, `doctor` and installers.
- Added the shared SRIC 0.5.12 operational exception boundary, structured redacted catalog 503 behavior, bounded process reaping, SSE-safe terminal-job retention and Job Engine secret redaction without duplicating shared runtime logic in FossilScope.
- Linux/Termux and Windows installers now import-probe `sric.web_runtime` in addition to Console/Workbench/catalog modules and keep internal validation banners suppressed.
- Updated runtime compatibility regressions so SRIC 0.5.11 is treated as stale for the 0.5.12 train while same-version missing-module repair remains explicit.
- Preserved passive-first collection, scope/terms acknowledgement, deterministic evidence states and the existing Web/CLI parity contract.

## 0.5.11 - 2026-08-09
- Fixed the unstyled `/console`/`/workbench` rendering by allowing same-origin shared stylesheets in the native FossilScope CSP while retaining restrictive object/base/frame policies.
- Adopted SRIC Core 0.5.11 JSON-safe command catalog generation so non-primitive Typer metadata cannot surface as the reported `catalog HTTP 500` failure.
- Pinned and locked the exact signed SRIC Core 0.5.11 merge used by clean and repair installation.
- Kept normal Linux/Termux/Windows installs idempotent and free of `--force-reinstall`; installer-internal doctor/capability/help smokes now suppress repeated banners and print their captured diagnostics only on failure.
- Added regressions for Console CSS/JS, HTTP-200 command catalog, Workbench catalog/coverage and the complete installer contract.

## 0.5.10 - 2026-08-09
- Hardened repair installation so an obsolete, incomplete or broken Python environment rebuilds only `~/.fossilscope/venv`; workspaces, configuration and evidence are never removed.
- Termux now prefers a writable `$PREFIX/bin` already present in `PATH`, making the `fossilscope` command immediately reachable after install.
- Windows installer PATH updates now use SRIC Core's registry-backed `sric.install_path` helper instead of `setx`, preventing PATH truncation/rewrite risks and broadcasting environment changes safely.
- Preserved the 0.5.9 atomic FossilScope + explicit first-party SRIC resolver fix and updated the immutable SRIC pin/runtime lock to SRIC Core 0.5.10.
- Expanded installer regression coverage for venv-only repair, Termux path selection, safe Windows PATH handling, Python discovery, dependency integrity and CLI help smokes.

## 0.5.9 - 2026-08-09
- Fixed `ResolutionImpossible` during clean/repair installation when `fossilscope` depended on the first-party `sric-core` package that is intentionally distributed from an immutable GitHub snapshot rather than PyPI.
- Linux/Termux and Windows now resolve FossilScope plus the explicit SRIC source in one pip transaction, so `--force-reinstall` never launches a product-only resolver pass that has no first-party candidate.
- Updated the immutable first-party SRIC pin and runtime lock to SRIC Core 0.5.9.
- Fixed Linux PATH persistence so `.profile` does not inject literal quote characters into PATH.
- Fixed Windows Python discovery to accept any installed Python 3 runtime that satisfies `>=3.11`, instead of requiring `py -3.11` specifically.
- Installers now bootstrap pip/setuptools/wheel, run `pip check`, verify shared Web modules, and smoke-test `--help`, `-h`, and `help` before reporting success.
- Added standalone regressions for the exact resolver topology, first-party pin, PATH quoting and Windows Python selection.

## 0.5.8 - 2026-08-09
- Fixed the reported `ModuleNotFoundError: No module named 'sric.web_workbench'` failure caused by a newer FossilScope being installed beside an older SRIC runtime.
- Shared Web modules are now loaded lazily; stale/corrupt SRIC no longer makes every FossilScope command fail at import time, and an unavailable Workbench returns an actionable 503 compatibility response.
- `doctor` and `/api/v1/runtime-compatibility` now verify the exact SRIC version range and required Web Console/Workbench modules rather than accepting any `0.5.*` runtime.
- Official update repair can bridge signed SRIC 0.5.5→0.5.6→0.5.7 snapshots before updating FossilScope, and same-version corrupt cores are force-reinstalled through the verified official channel.
- Linux/Termux and Windows installers now force-reinstall the pinned signed SRIC/FossilScope packages, run `pip check`, import-probe shared Web modules, verify the core version range, and execute doctor/capability/help smokes without deleting user workspaces.
- Added regression coverage reproducing the exact Termux failure shape, signed transition chain, same-version repair, degraded Workbench behavior, every public CLI help form and exact ordered CLI/Web parameter parity.
- New installs pin signed SRIC Core 0.5.8.

## 0.5.7 - 2026-08-09
- Added the full Web Feature Workbench at `/workbench`, generated from `fossilscope.cli_all`, with structured responsive controls for every public CLI command and argument.
- Fixed the native dashboard discoverability gap shown on mobile: the root page now exposes visible Dashboard / All Features / Advanced Console navigation and a full-feature callout.
- Preserved passive-first semantics, named-workspace safety, scope/terms acknowledgement and active-action policy/approval gates.
- Updated SRIC Core floor, runtime lock and exact first-party pin to the signed SRIC 0.5.6 Workbench release.
- Added exhaustive CLI help/argument-to-Web parity tests and native temporal API smoke coverage.

## 0.5.6 - 2026-08-08
- Made the official FossilScope updater zero-config: `fossilscope update`, `fossilscope update --check`, and `fossilscope update --force` no longer require user-supplied manifest/key configuration.
- Delegated official update trust and immutable GitHub signed-commit validation to SRIC Core 0.5.5 while preserving same-version force reinstall and downgrade rejection.
- Kept `--manifest` plus `--public-key` as an explicit advanced custom/private-channel override.
- Updated the SRIC Core runtime floor, lock, and exact first-party pin to the signed SRIC 0.5.5 release commit without changing workspace resolution or passive-first analysis behavior.
- Added standalone regression coverage proving `fossilscope update --force` selects the official channel with no manifest/key.

## 0.5.5 - 2026-08-08
- Added the SRIC Web Command Console at `/console`, exposing the complete installed `fossilscope.cli_all` command tree without an operating-system shell.
- Added exact Web-catalog-to-CLI-tree regression coverage so future public CLI commands cannot silently disappear from the Web console.
- Preserved the 0.5.3+ named-workspace validation and complete Web/API factory behavior while adding the shared console.
- Preserved passive-first defaults, explicit scope/terms acknowledgement and active HTTPS safety gates.
- Added fixed-runner `shell=False` execution, explicit mutation approval, secret redaction, cancellable jobs and real-time SSE output through SRIC Core 0.5.4.

## 0.5.4 - 2026-08-08
- Added `fossilscope update --force` for explicit same-version reinstall of a trusted signed release using pip `--force-reinstall`.
- Preserved Ed25519 manifest verification, SHA-256 wheel verification, state backup and rollback behavior.
- `--force` may install the same or a newer signed release, never an older release; SemVer prerelease precedence is enforced by SRIC Core.
- `--check` and `--force` are mutually exclusive.
- Updated the SRIC Core runtime floor, lock and exact first-party source pin to 0.5.3.
- Added standalone regression coverage for the public `--force` CLI contract while preserving the 0.5.3 Web workspace-resolution fixes.

## 0.5.3 - 2026-08-08
- Fixed `fossilscope web WORKSPACE` raising an uncaught `FileNotFoundError` when the named workspace does not exist under the selected root.
- Added centralized named-workspace validation for extended CLI commands with actionable missing-workspace errors and no Python traceback.
- Rejects path-like workspace names, `../` traversal and workspace symlinks that could escape the selected `--root`.
- Fixed the Web command to construct the complete `api_all` application, including vNext analysis routes and `/api/v1/capabilities`, instead of the older base API factory.
- Removed stale API-factory monkey patching from `cli_all` that did not affect the `cli_more.web` command.
- Added E2E regression coverage for successful Web startup wiring, missing workspaces, traversal, symlink escape and complete API routes.
- Updated README/CLI documentation and runtime/package version to 0.5.3.

## 0.5.2 - 2026-08-08
- Added a subdued green interactive CLI banner ordered as `FossilScope :: v0.5.2`, `Developer: IsdarlinM`, then the product description.
- Added colorized Typer/Rich command help plus global `--no-color` and `NO_COLOR` support.
- Kept banner output on interactive stderr so JSON, graph output and automation stdout remain clean.
- Added CLI branding regression tests and documentation.
- Updated the SRIC Core runtime floor, lock and first-party source pin to 0.5.2.
- Corrected the passive-planning property test to match the production `active HTTPS` limitation text.

## 0.5.1 - 2026-08-08
- Fixed clean installation when `sric-core` is not published on PyPI.
- Added `requirements/first-party.txt` pinned to the exact SRIC Core 0.5.1 GitHub commit.
- Windows and Linux installers now bootstrap first-party dependencies before resolving the product and third-party runtime dependencies.
- Preserved `SRIC_CORE_SOURCE` as an explicit development override and kept normal users independent of adjacent repository checkouts.
- Updated the runtime lock to SRIC Core 0.5.1 and added standalone regression coverage for the installer dependency contract.

## 0.5.0 - 2026-08-08
- Added passive-first re-observation planning that prioritizes uncertain current state, current references, authorization relevance, source conflicts and temporal staleness without treating priority as severity.
- Added explicit current-exposure planning states and deterministic deduplicated re-observation request IDs.
- Hardened `import_json()` to use the existing bounded regular-file loader, closing the path/symlink/size-check bypass in the direct JSON import path.
- Preserved active HTTPS re-observation as a separate approval-gated workflow; the planner emits passive requests only.
- Updated SRIC compatibility to the Sentinel Forge 0.5 release train.
- Added standalone capability discovery with no mandatory sibling-product dependencies.
- Reworked Linux/Windows installers to resolve SRIC 0.5 automatically instead of silently consuming adjacent repositories or older core versions.
- Added standalone CLI/API/Web tests, recursive parser/help contracts, clean-install smokes and data-preserving Linux uninstall behavior.
- Added regression tests for bounded import enforcement and passive re-observation prioritization.

## 0.3.1 - 2026-08-06
- Added explicit current lifecycle states for DNS, TLS, HTTP, authenticated access, redirects, parking, sinkholes, transfers, retirement and unknown current state.
- Added source-group deduplication so mirrors and derived providers do not count as independent confirmation.
- Added controls for wildcard DNS, shared infrastructure and default virtual hosts.
- Historical evidence plus current DNS/TLS alone no longer produces a resurrection candidate; a current application response is required.
- Parking, sinkhole, transfer and retirement evidence disqualify automatic resurrection hypotheses.
- Added tests for historical-only assets, DNS-only evidence, wildcard DNS, direct HTTP candidates, transfers and duplicate upstream sources.
- Replaced hosted GitHub Actions/Dependabot automation with a local reproducible release gate.

## 0.3.0 - 2026-07-22
- Added bounded passive HTTPS collector runtime with explicit scope, DNS revalidation/pinning, no redirects, rate limits, cache and provenance.
- Added time-travel graph views, separate historical/current confidence, resurrection detection and mobile/API archaeology.
- Preserved passive-by-default behavior and strict separation of historical evidence from current exposure.
- Upgraded to shared SRIC 0.4 workspace namespaces and graph/jobs/lineage primitives.

## 0.2.0 - 2026-07-21
- Added SRIC-backed time-travel temporal graph, fossil lifecycle, confidence decay, acquisition lineage and explainable clustering.
- Added historical OpenAPI diff and passive local adapters.
