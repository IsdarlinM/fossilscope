# Roadmap

## Current — 0.5.0 release candidate

Implemented in the 0.5 train:
- SRIC 0.5 integration.
- Passive-first re-observation prioritization with explicit current-exposure states.
- Separation of historical relevance, current exposure state and research priority.
- Bounded direct JSON import through the regular-file/symlink-safe loader.
- CLI/API surfaces and regression tests for re-observation prioritization.
- `doctor` compatibility updated for SRIC 0.5 and coordinated release-evidence gate v2.

## Next hardening
- Provider-specific CT/DNS/archive/repository/package adapters over the bounded collector runtime with quotas/terms metadata.
- Temporal graph virtualization for large histories and stronger source-independence calibration.
- Historical identity/OAuth/SDK evolution diffing and richer re-observation workflows.
- Cross-project correlation with Exposure DNA and TrustBoundary through shared Sentinel Cases.
- Larger temporal false-positive corpus, browser E2E and signed release attestations.

## 1.0
Stable temporal schemas, source adapter SDK, reproducible archaeology datasets and independently validated fossil scoring.
