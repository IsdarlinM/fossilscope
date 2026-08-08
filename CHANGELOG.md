# Changelog

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
