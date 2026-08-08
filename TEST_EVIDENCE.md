# Test Evidence — FossilScope v0.5.0 Release Candidate

## Release-candidate review — 2026-08-08

The `agent/release-0.5.0` branch contains the FossilScope 0.5 changes under review:

- SRIC 0.5 compatibility;
- passive-first current-state re-observation planning;
- explicit separation of historical relevance, current exposure state and research priority;
- direct JSON import routed through the bounded regular-file/symlink-safe loader;
- 0.5 regression tests for import limits and passive planning;
- standardized release-evidence gate v2.

## Fresh execution status

**THE COMPLETE v0.5.0 RELEASE GATE HAS NOT BEEN EXECUTED SUCCESSFULLY FOR THIS BRANCH.**

The private repository cannot be mounted as a complete local checkout in this runtime. GitHub Actions currently ends in `startup_failure` before any test job starts; this is not considered test evidence.

## Required release evidence

Run from sibling 0.5 checkouts:

```bash
python sric-core/scripts/release-ecosystem.py --root .
```

The release train must produce a FossilScope exact-commit `release-gate.json` and the cross-product `ecosystem-release-gate.json`, both with `PASS`, before merge/tag.

Previous 0.3.x evidence remains a historical regression baseline only.
