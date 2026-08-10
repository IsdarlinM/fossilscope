# FossilScope Web UI

FossilScope is local-first. `fossilscope web WORKSPACE` opens the selected workspace on loopback (`127.0.0.1:8767` by default); non-loopback binding is denied until authenticated TLS mode exists.

## Unified Sentinel Forge theme

FossilScope 0.5.15 uses one visual language across all primary Web surfaces:

- page: graphite `#0b0f14`;
- rail: `#0e141b`;
- surfaces: `#121922`, `#161f29`, `#0f151d`;
- borders: `#283544` / `#202b38`;
- accent: restrained teal `#5aa9b8` / `#70bdca`;
- primary typography: Segoe UI Variable Text / Segoe UI Variable / Aptos / system fallbacks;
- evidence/code typography: Cascadia Code / SFMono / Consolas / Liberation Mono fallbacks.

No Google Fonts, external font files, Swagger CDN or other visual CDN is required. This preserves offline demos and restrictive Content Security Policy behavior.

SRIC Core 0.5.15 owns the canonical shared theme tokens. FossilScope contains a bounded 0.5.14 compatibility bridge only so an already-installed product can update safely before its shared runtime is repaired. Clean 0.5.15 installs use the SRIC-owned theme.

## Routes

### `/` — Temporal Dashboard

The native FossilScope dashboard is the quick temporal-research view. It contains:

- Sentinel Forge product rail and navigation;
- explicit historical/current evidence guardrail;
- search over visible temporal records;
- Temporal Security Graph observations;
- Fossil Candidates with explainable prioritization scores;
- lifecycle state;
- evidence/explainability detail drawer;
- real-time job activity through same-origin SSE.

The dashboard does not claim a candidate is vulnerable merely because it is historical, unusual or highly ranked.

### `/workbench` — Security Workspace

The shared Sentinel Forge Security Workspace is generated from the installed `fossilscope.cli_all` command tree. Users select capabilities and enter structured values rather than typing an arbitrary command line.

The fixed runner preserves:

- `shell=False`;
- no browser-controlled executable;
- no user-supplied free-form argv surface;
- CSRF protection;
- output/secret redaction;
- bounded/cancellable jobs;
- mutation/destructive approval gates;
- Scope/Policy/rate/approval authority for active product operations.

FossilScope 0.5.15 also bridges the SRIC 0.5.14 unknown-parameter catalog failure class so one unfamiliar Click/Typer-compatible parameter subtype no longer collapses the complete catalog into HTTP 500. SRIC 0.5.15 contains the canonical shared fix.

### `/docs` — API Reference

The API Reference is an offline, read-only OpenAPI explorer using the same theme and typography as Dashboard and Security Workspace.

It renders:

- tags and endpoint filtering;
- method, path, summary and full description;
- parameters, location, type, required/default/example metadata;
- request-body schemas/content types;
- response status descriptions;
- component/data-model schemas.

It deliberately has no automatic "Try it" button. Loading documentation performs only a same-origin GET of `/openapi.json`; the viewer never executes POST analysis endpoints.

See `docs/api/README.md` for the full API contract.

## Responsive behavior

Desktop uses a persistent product rail and spacious investigation workspace. Narrow screens collapse the rail into compact navigation and stack panels/forms vertically. All primary navigation and structured controls remain keyboard reachable.

## CSP and local assets

Dashboard/API Reference use same-origin JS and inline product CSS under the FossilScope CSP. Security Workspace assets are same-origin SRIC resources. `object-src` and `frame-ancestors` remain disabled; referrer data is not sent.

The Web UI reads the same workspace/evidence model as the CLI/API. It does not expose synthetic actions, invent ownership, or bypass evidence and policy controls.
