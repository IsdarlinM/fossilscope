# Changelog

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
