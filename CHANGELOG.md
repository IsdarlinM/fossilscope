# Changelog

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
