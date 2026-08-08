# Test Evidence — FossilScope v0.5.3

## Focused regression review — 2026-08-08

FossilScope 0.5.3 addresses the observed `fossilscope web imr` failure in which a missing or invalid named workspace reached `FossilEngine` and surfaced `FileNotFoundError: workspace.json not found` as a Python traceback.

Implemented regression controls:

- named workspaces are resolved below the selected workspace root before Web/API construction;
- `Workspace.open()` validates and migrates an existing workspace before use;
- missing workspaces return an actionable CLI error, list available valid workspaces when possible, and do not auto-create data;
- path-like names, traversal (`../`) and workspace symlinks are rejected to prevent escape from the selected `--root`;
- `fossilscope web` now constructs the complete `api_all` application, including vNext analysis and capability routes;
- the stale `cli_all` API-factory monkey patch was removed;
- E2E regression tests cover valid Web startup wiring, missing workspaces, traversal, symlink escape, and complete API route registration.

## Executed focused evidence

A focused local workspace-resolution test executed successfully for the new resolution policy:

```text
focused_workspace_resolution=PASS
```

The exercised cases were:

- direct workspace `imr` below the selected root resolves successfully;
- `../outside` and `..` are rejected as invalid workspace names;
- a missing workspace is classified as missing rather than producing a raw filesystem traceback;
- a workspace symlink is rejected when symlink creation is supported by the platform.

The shared CLI presentation logic was also previously exercised locally for the 0.5.2 release train, including canonical banner ordering and global `--no-color` normalization. The 0.5.3 branding regression now derives the expected banner version from the installed package version instead of hard-coding 0.5.2.

## GitHub Actions status

**THE COMPLETE v0.5.3 TEST/RELEASE GATES HAVE NOT EXECUTED SUCCESSFULLY.**

GitHub Actions currently creates workflow jobs but does not provision a runner. Representative jobs report `runner_id=0`, an empty runner name, and `steps=[]`. Therefore no checkout, pytest, installer smoke, static analysis, build, audit, or wheel validation from those runs is counted as execution evidence.

This is classified as CI infrastructure/provisioning failure, not a test PASS and not a code-test failure.

## Required complete release evidence

When runners are available, execute the exact-commit gates:

```bash
python -m sric.standalone_gate --root fossilscope
python sric-core/scripts/release-standalone-ecosystem.py --root .
python fossilscope/scripts/release-gate.py
python sric-core/scripts/release-ecosystem.py --root .
```

The full Definition of Done still requires those gates, clean install/update checks, CLI/help checks, Web/browser checks, security tests, supply-chain checks, and evidence tied to the exact source commit. Focused PASS evidence above validates the targeted regression only; it is not a substitute for the complete release gate.
