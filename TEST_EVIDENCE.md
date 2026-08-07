# Test Evidence — FossilScope v0.3.1

## QA pass — 2026-08-07

Freshly executed in the current local runtime:

- Sentinel Forge cross-product high-risk regression matrix including FossilScope temporal artifact evolution: **7/7 matrix tests passed**;
- Python `compileall` over the reconstructed corrected modules: **PASS**;
- branch comparison against `main`: branch is ahead and **0 commits behind** at the time of this audit.

Current-source review and regression coverage include:

- historical/current lifecycle separation and false-resurrection controls;
- explicit empty evolution delta handling;
- stable artifact identity/type across temporal observations;
- timezone-aware reobservation timestamps and retry scheduling;
- passive-first planning with active HTTPS approval gates and zero execution in API tests;
- controlled 422 responses for invalid retry/evolution inputs;
- evolution/stale-reference endpoints actually registered in the vNext API;
- complete CLI entrypoint registration for evolution commands;
- recursive help-path coverage and controlled CLI input errors;
- `fossilscope web` serving the workspace-bound vNext API;
- public Python exports for evolution/reobservation primitives.

## Current release-gate status

**FULL CURRENT REPOSITORY GATE NOT EXECUTABLE IN THIS RUNTIME.**

The private repository cannot be materialized as a complete local checkout from the connector, and Ruff, mypy, `build` and `pip-audit` are unavailable from the runtime/index. No GitHub Actions, Codespaces or paid/hosted GitHub execution was used.

Before treating v0.3.1 as a fully validated release, run the exact commit from a local sibling checkout:

```bash
python -m pip install -e ../sric-core
python -m pip install -e '.[dev]'
python scripts/release-gate.py
```

## Previous validated baseline

The previous v0.3.0 state was recorded on 2026-07-22 with **21 pytest tests passed**, compileall/security scan/CLI help/synthetic smoke/build/isolated wheel smoke PASS. Those results are a historical baseline only.
