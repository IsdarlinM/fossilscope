# Test Evidence — FossilScope v0.5.15 Candidate

Date: 2026-08-10

## Candidate scope

FossilScope 0.5.15 is the Web/API visual-consistency and catalog-reliability candidate built from the user-observed 0.5.14 runtime.

Implemented candidate controls include:

- one Sentinel Forge blue/graphite + teal visual contract across native Dashboard `/`, shared Security Workspace `/workbench`, legacy `/console` compatibility surface and API Reference `/docs`;
- offline professional Segoe UI Variable/Aptos/system typography and Cascadia Code/SFMono/Consolas evidence/code typography without external font/CDN dependencies;
- a read-only same-origin `/docs` OpenAPI renderer with search/tag filters, parameter metadata, request bodies, responses and component schemas; it contains no automatic request-execution control;
- expanded OpenAPI summaries, descriptions, query constraints and evidence/proof boundaries for temporal, intelligence, research-runtime, analysis, capabilities and runtime-compatibility endpoints;
- canonical SRIC Core 0.5.15 catalog hardening plus a bounded FossilScope compatibility bridge for the user-observed SRIC 0.5.14 `catalog HTTP 500` failure class during product-first update;
- clean/repair installation pinned to GitHub-verified SRIC Core 0.5.15 merge `95e093a0b8c2041037836cec235a73fd578d815c`;
- detached Windows update verification that builds the complete JSON-safe `fossilscope.cli_all` catalog before accepting the target product as installed;
- transactional Windows runtime repair and data-preserving uninstall semantics retained;
- mandatory deterministic functional smoke for all 45 public FossilScope commands;
- every root/subcommand `--help`, `-h` and trailing `help` form retained as a separate gate;
- dedicated E2E/security regressions for unified Web theme, OpenAPI completeness, read-only docs behavior and console/workbench catalog HTTP 200.

## Exact-head GitHub Actions attempt

PR candidate head:

```text
9b6842484ad8c62d3cbc8097bd728322dc5e74c5
```

GitHub Actions run:

```text
31437374502
```

The workflow created all eight configured jobs:

- installer-smoke (ubuntu-latest)
- installer-smoke (windows-latest)
- standalone ubuntu-latest Python 3.11 / 3.12 / 3.13
- standalone windows-latest Python 3.11 / 3.12 / 3.13

Every job completed with:

```text
runner_id = 0
runner_name = ""
steps = []
```

No checkout, Python setup, dependency installation, CLI command smoke, help smoke, Web/API test, security regression, installer test or release gate actually ran. GitHub records the jobs as failures because the external hosted runner/account infrastructure did not start the jobs. This is **not a FossilScope test failure and is not PASS evidence**.

The exact-head workflow therefore did **not** execute:

```bash
python -m pytest -q tests/e2e/test_cli_all_commands_functional.py
python -m pytest -q tests/standalone/test_standalone_contract_v05.py
python -m pytest -q tests/e2e/test_security_workspace_v0514.py
python -m pytest -q tests/e2e/test_unified_web_theme_api_docs_v0515.py tests/security/test_web_catalog_compat_v0515.py
python -m sric.standalone_gate --root .
python scripts/release-gate.py --quick
```

## Exact-head local execution attempt

The maintenance environment retried an exact branch checkout using:

```bash
git clone --depth 1 --branch web/unify-dashboard-api-docs-0.5.15 https://github.com/IsdarlinM/fossilscope.git /tmp/fossilscope-v0515
```

The checkout failed before any repository code was available:

```text
fatal: unable to access 'https://github.com/IsdarlinM/fossilscope.git/': Could not resolve host: github.com
```

The authenticated GitHub connector can inspect and modify repository content, but it is not a Python/Windows/Linux execution runner. Static/source review through that connector is not substituted for test execution.

## Shared SRIC 0.5.15 status

The exact first-party core used by this candidate is the GitHub-verified merge:

```text
95e093a0b8c2041037836cec235a73fd578d815c
```

Its PR workflow likewise created hosted jobs without allocating a runner (`runner_id=0`, zero executed steps). The shared theme/catalog changes are therefore integrated source, not a claimed full release PASS.

## Required evidence before declaring 0.5.15 complete/stable

The exact final FossilScope commit still must execute successfully on real runners/environment:

- all 45 public CLI functional command smokes;
- every root/subcommand help form;
- unit, integration, E2E, security and fuzz suites;
- Dashboard `/`, Security Workspace `/workbench`, `/console` alias and API Reference `/docs` HTTP/rendering checks;
- `/api/v1/console/catalog` and `/api/v1/workbench/catalog` HTTP 200 with non-empty catalogs;
- API OpenAPI schema completeness plus valid/invalid input behavior;
- responsive desktop/mobile browser checks and browser-console error review;
- clean Linux/Termux and Windows installation;
- Windows dependency-corruption repair and workspace/evidence preservation;
- detached Windows update, Web-catalog verification and rollback behavior;
- dependency/secret/SAST/SBOM/build/supply-chain checks;
- exact-commit SRIC/FossilScope integration.

A complete release run should include:

```bash
python -m pytest -q tests/e2e/test_cli_all_commands_functional.py
python -m pytest -q tests/standalone/test_standalone_contract_v05.py
python -m pytest -q tests/e2e/test_security_workspace_v0514.py
python -m pytest -q tests/e2e/test_unified_web_theme_api_docs_v0515.py tests/security/test_web_catalog_compat_v0515.py
python -m sric.standalone_gate --root .
python scripts/release-gate.py
```

The moving official update channel must not be interpreted as validated merely because source was merged. Advancing a stable update channel should follow successful exact-commit execution evidence.

---

## Historical evidence retained from the 0.5.12 stabilization cycle

The shared SRIC 0.5.12 runtime changes used by FossilScope were previously exercised in a focused local harness. The first run exposed a background-reaper return-code race (`3 passed, 1 failed`); after correction the focused harness reported:

```text
4 passed in 0.19s
```

Those checks covered catalog-503 redaction, terminal-job/SSE retention, final-wait background reaping and Job Engine persistence redaction. They remain historical evidence for those specific shared-runtime paths only and do not constitute 0.5.15 release evidence.
