# FossilScope Local API

FossilScope exposes a loopback-only FastAPI application for the selected local workspace. The supported way to start it is:

```bash
fossilscope web WORKSPACE
```

The default listener is `127.0.0.1:8767`. Non-loopback binding is rejected until authenticated TLS mode exists.

Open:

- `/` — FossilScope temporal dashboard.
- `/workbench` — Sentinel Forge Security Workspace generated from the installed CLI contract.
- `/docs` — offline, read-only Sentinel Forge API Reference.
- `/openapi.json` — machine-readable OpenAPI schema.

The API Reference does **not** expose automatic "Try it" controls. It only reads `/openapi.json`; it never executes POST analysis operations on behalf of the viewer.

## Evidence contract

The API follows the same research model as the CLI:

- historical evidence and current exposure are distinct;
- candidate/confidence scores are research prioritization, not vulnerability severity;
- UNKNOWN remains UNKNOWN when required evidence is missing;
- correlation or temporal similarity cannot manufacture a `VALIDATED` finding;
- analysis/reobservation planning endpoints send zero target requests;
- active execution remains behind Scope Engine -> Policy Engine -> Rate Limits -> Approval -> Executor.

## Temporal research endpoints

| Method | Path | Purpose |
|---|---|---|
| GET | `/api/timeline` | Return temporal observations in the current workspace. |
| GET | `/api/candidates` | Return explainable fossil candidates and prioritization scores. |
| GET | `/api/lifecycle` | Return evidence-derived lifecycle states. |
| GET | `/api/graph` | Return the product-native temporal security graph snapshot. |
| GET | `/api/clusters` | Return evidence-linked historical clusters. |
| GET | `/api/time-travel?at=...` | Reconstruct the temporal view at an ISO-8601 instant. |
| GET | `/api/resurrections?min_gap_days=180` | Identify disappearance/reappearance candidates after a bounded gap. |
| GET | `/api/confidence-v2?value=...&stale_after_days=365` | Explain source evidence and temporal confidence decay for an observed value. |

### Query parameters

`/api/time-travel`

- `at` — required ISO-8601 timestamp, for example `2026-08-10T12:00:00Z`.

`/api/resurrections`

- `min_gap_days` — integer >= 1; default `180`.

`/api/confidence-v2`

- `value` — required observed artifact value.
- `stale_after_days` — integer >= 1; default `365`.

## Shared research-runtime endpoints

| Method | Path | Purpose |
|---|---|---|
| GET | `/api/search?q=...&limit=50` | Search indexed SRIC temporal-graph records. |
| GET | `/api/jobs` | List persisted SRIC research jobs. |
| GET | `/api/jobs/events?cursor=0&once=false` | Stream job activity using Server-Sent Events. |
| GET | `/api/notebook` | List evidence-aware SRIC research notebook entries. |
| GET | `/api/evidence-lineage/{artifact_id}` | Explain provenance/lineage; missing records return explicit `UNKNOWN`. |

`limit` is bounded to 1..500. `cursor` is zero-based and cannot be negative. Use `once=true` when a bounded single SSE poll is preferable to a continuing stream.

## Analysis endpoints

All endpoints below are local computation/planning operations. They do **not** make target requests.

| Method | Path | Purpose |
|---|---|---|
| POST | `/api/v1/analysis/lifecycle` | Assess current-exposure lifecycle from evidence records. |
| POST | `/api/v1/analysis/reobservation/prioritize` | Rank stale/UNKNOWN candidates for future passive-first reobservation. |
| POST | `/api/v1/analysis/reobservation/plan` | Deduplicate and policy-evaluate proposed reobservation requests. |
| POST | `/api/v1/analysis/reobservation/retry` | Compute bounded exponential-backoff retry metadata. |
| POST | `/api/v1/analysis/evolution/diff` | Compare versioned artifact observations. |
| POST | `/api/v1/analysis/evolution/stale-references` | Identify stale/superseded reference candidates. |

### Lifecycle request example

This example uses the exact `SurfaceEvidence` field names and enum values implemented by FossilScope:

```json
{
  "evidence": [
    {
      "evidence_id": "evidence-current-http-001",
      "asset_id": "asset-api-example",
      "kind": "CURRENT_HTTP",
      "source_id": "authorized-observation-001",
      "source_group": "direct-http-observation",
      "observed_at": "2026-08-10T12:00:00Z",
      "direct_observation": true,
      "counter_evidence_ids": [],
      "notes": [
        "Current HTTP observation recorded during authorized research."
      ]
    }
  ]
}
```

The response contains `assessments` plus:

```json
{
  "validated_findings_created": 0,
  "historical_evidence_proves_current_exposure": false
}
```

### Reobservation plan request example

```json
{
  "requests": [
    {
      "request_id": "reobserve-001",
      "asset_id": "asset-api-example",
      "target": "https://example.test/.well-known/openapi.json",
      "reason": "STALE_REFERENCE",
      "mode": "PASSIVE",
      "source_evidence_ids": ["evidence-historical-001"],
      "priority": 70
    }
  ],
  "deduplicate": true
}
```

The response contains planning decisions and explicitly reports `executed: false` and `requests_sent: 0`.

### Active reobservation semantics

`ReobservationMode` contains `PASSIVE` and `ACTIVE_HTTPS`, but the analysis API only evaluates/plans requests. An `ACTIVE_HTTPS` record must be an HTTPS target and later execution still needs explicit scope, terms acknowledgement, human approval and the active-executor safety chain. Creating or evaluating the record does not send the request.

## Standalone/runtime endpoints

| Method | Path | Purpose |
|---|---|---|
| GET | `/api/v1/capabilities` | Discover installed/compatible Sentinel Forge capabilities. |
| GET | `/api/v1/runtime-compatibility` | Report installed SRIC version, required modules and compatibility reasons. |

Sibling Sentinel Forge products remain optional integrations rather than hidden runtime dependencies.

## Security Workspace transport

SRIC mounts a fixed-runner transport for the local Security Workspace. These endpoints are part of the Web UI contract and are visible in OpenAPI:

| Method | Path | Purpose |
|---|---|---|
| GET | `/api/v1/console/catalog` | Exact installed CLI command catalog and execution safety metadata. |
| POST | `/api/v1/console/jobs` | Submit one fixed-runner Web operation; CSRF token and approval gates apply. |
| GET | `/api/v1/console/jobs` | List Web-console jobs. |
| GET | `/api/v1/console/jobs/{job_id}` | Read one Web-console job. |
| POST | `/api/v1/console/jobs/{job_id}/cancel` | Request cancellation; CSRF token required. |
| GET | `/api/v1/console/jobs/{job_id}/events` | Stream output/status with SSE. |
| GET | `/api/v1/workbench/catalog` | Structured Security Workspace feature catalog generated from the CLI. |
| GET | `/api/v1/workbench/coverage` | CLI/Web parity and feature coverage contract. |

The browser does not choose an executable and cannot supply free-form command paths. The backend uses the fixed SRIC runner with `shell=False` and disabled stdin. Mutating operations require approval according to their classification.

## Errors

Product-level API handlers use bounded errors:

- malformed FastAPI/Pydantic input: HTTP 422;
- analysis contract violations: HTTP 422;
- missing research entity handled by the application: HTTP 404;
- invalid/missing Security Workspace CSRF token: HTTP 403;
- conflicting/rejected Web execution state: HTTP 409 where applicable.

Unexpected details must not leak secrets. `SENTINEL_DEBUG=1` is a local developer-only diagnostic mode and is not a production default.

## OpenAPI and schemas

`/openapi.json` is the source of truth for current request/response schemas. The `/docs` page renders:

- operation tags;
- method and path;
- summary and full description;
- parameter location, type, required/default/example metadata;
- request-body content types and schemas;
- response status descriptions and response schema references;
- component/data-model schemas.

The reference UI uses only same-origin assets and system/local fonts. It does not depend on Swagger CDN, Google Fonts or an Internet connection.

## Example reads

```bash
curl http://127.0.0.1:8767/api/timeline
curl "http://127.0.0.1:8767/api/search?q=oauth&limit=25"
curl http://127.0.0.1:8767/api/v1/runtime-compatibility
curl http://127.0.0.1:8767/openapi.json
```

For POST analysis examples, prefer the generated schema and the examples embedded in `/docs`; do not convert planning endpoints into active probing automation.
