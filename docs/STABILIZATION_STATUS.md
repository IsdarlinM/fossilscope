# FossilScope 0.5.13 stabilization status

Date: 2026-08-10

FossilScope 0.5.13 is under Sentinel Forge P0/P1 stabilization and must not be described as a fully gated stable release until the exact release commit passes the coordinated release gate.

This stabilization branch adds a data-preserving Windows uninstaller, converts audited invalid-input HTTP 500 paths to controlled 404/422 responses, replaces CDN-dependent Swagger with same-origin offline OpenAPI documentation, removes CI private-token/branch coupling and adds regressions. Historical evidence still never proves current exposure.

The official update channel remains unchanged until hosted CI can execute, dependency advisory review is complete, and signed release/SBOM/provenance evidence is available.
