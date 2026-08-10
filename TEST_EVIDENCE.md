# Test Evidence — FossilScope v0.5.12 Candidate

## Candidate review — 2026-08-10

FossilScope 0.5.12 aligns the product with the shared SRIC Core 0.5.12 operational runtime and closes the runtime-contract drift that could allow an older core to be treated as compatible outside the normal installer path.

Implemented candidate controls:

- package metadata, runtime bootstrap, `doctor`, Linux/Termux installer, Windows installer and lock snapshot all require SRIC `>=0.5.12,<0.6`;
- clean/repair installation pins the immutable GitHub-signature-verified SRIC main commit `4dd0ad417e55fc76fb67d582ec50234bffff2876`;
- required shared modules include `sric.web_console`, `sric.web_workbench`, `sric.web_catalog` and `sric.web_runtime`;
- supported stale SRIC releases advance through fixed signed snapshots one release at a time from 0.5.5 through 0.5.12;
- same-version corrupt 0.5.12 runtimes repair from the fixed 0.5.12 signed snapshot instead of depending on a moving update channel;
- installer-internal doctor/capability/help smokes remain banner-suppressed;
- the exhaustive standalone contract walks every public FossilScope CLI command, all root/subcommand help forms and exact ordered CLI/Web parameter parity;
- existing Web regressions cover Console/Workbench pages, CSS/JS assets, HTTP command/feature catalogs, coverage, runtime compatibility and native temporal API surfaces;
- shared SRIC 0.5.12 provides redacted operational exceptions, structured catalog 503 handling, bounded child reaping, SSE-safe retired jobs and persisted Job Engine secret redaction.

## Executed focused evidence relevant to this candidate

The shared SRIC 0.5.12 runtime changes used by FossilScope were exercised in a focused local harness. The first run exposed a real background-reaper return-code race (`3 passed, 1 failed`); the race was corrected and the harness was rerun successfully:

```text
4 passed in 0.19s
```

Those four checks covered catalog-503 redaction, terminal-job/SSE retention, final-wait background reaping and Job Engine persistence redaction.

This is evidence for the shared runtime paths only. It is **not** represented as a full FossilScope repository/platform/browser PASS.

## FossilScope exact-commit hosted CI status

**THE COMPLETE v0.5.12 FOSSILSCOPE TEST/RELEASE GATES HAVE NOT EXECUTED.**

GitHub Actions creates Linux/Windows installer and standalone jobs but does not allocate a runner. Jobs report `runner_id=0` and `steps=[]`. GitHub annotates the checks with:

```text
The job was not started because your account is locked due to a billing issue.
```

A zero-step workflow is infrastructure failure, not test evidence. No full pytest, static-analysis, clean-install, browser-E2E, supply-chain or release-gate PASS is claimed from those hosted runs.

The execution container available to this maintenance session also cannot resolve `github.com`, so it cannot materialize the complete repository checkout to substitute for the blocked hosted runners. Repository code, docs and test definitions were reviewed through the authenticated GitHub connector, but static review is not execution evidence.

## Required exact-commit evidence before declaring the release complete

```bash
python -m sric.standalone_gate --root fossilscope
python sric-core/scripts/release-standalone-ecosystem.py --root .
python fossilscope/scripts/release-gate.py
python sric-core/scripts/release-ecosystem.py --root .
```

The full Definition of Done still requires successful execution of:

- all unit, integration, E2E, security and fuzz tests;
- every public CLI command's `--help`, `-h` and trailing `help` forms plus exact CLI/Web parameter parity;
- Web Console and Workbench pages, assets, catalogs, coverage, form/button submission, cancellation, approval and SSE behavior;
- every documented GET/POST API route with valid and invalid inputs, including runtime-compatibility and degraded 503 behavior;
- clean Linux/Termux and Windows install, repair, PATH and banner-suppression checks;
- signed update/repair/rollback while preserving configuration, workspaces and evidence;
- dependency/secret/SAST/SBOM/build checks;
- responsive browser validation and console-error review;
- ecosystem integration against the exact final commits.

The 0.5.12 candidate may be integrated to `main` at the project owner's explicit request, but that integration must not be described as proof that the blocked release gates passed.
