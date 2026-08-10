# FossilScope Analysis API

The analysis API is part of the normal complete local application. Start an existing workspace with:

```bash
fossilscope web WORKSPACE
```

By default the service listens on `127.0.0.1:8767`. Open `/docs` for the offline Sentinel Forge API Reference and `/openapi.json` for the exact schema.

Do not start `fossilscope.api_vnext:create_app` directly with a generic `uvicorn --factory` command: `create_app` requires the selected workspace path and the supported CLI resolves that workspace safely.

## Endpoints

```text
POST /api/v1/analysis/lifecycle
POST /api/v1/analysis/reobservation/prioritize
POST /api/v1/analysis/reobservation/plan
POST /api/v1/analysis/reobservation/retry
POST /api/v1/analysis/evolution/diff
POST /api/v1/analysis/evolution/stale-references
```

## Safety and evidence semantics

These are analysis/planning endpoints, not active-execution endpoints:

- they send **zero target requests**;
- historical evidence does not prove current exposure;
- prioritization does not validate a finding;
- evolution/stale-reference output remains evidence or hypothesis until current evidence exists;
- `ACTIVE_HTTPS` in a proposed reobservation record describes a future mode only; execution still requires Scope -> Policy -> Rate Limits -> Approval -> Executor;
- endpoints expose explicit `requests_sent`, `executed` and/or `validated_findings_created` fields where applicable.

## Lifecycle example

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
      "notes": ["Current HTTP observation recorded during authorized research."]
    }
  ]
}
```

Valid `EvidenceKind` values are defined by the runtime schema and currently include `HISTORICAL_REFERENCE`, `CURRENT_DNS`, `CURRENT_TLS`, `CURRENT_HTTP`, `CURRENT_AUTHENTICATED`, `REDIRECT`, `RETIREMENT_RECORD`, and `TRANSFER_RECORD`.

A historical reference cannot be marked as a current direct observation.

## Reobservation plan example

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

Supported `ReobservationReason` values are published in `/openapi.json`; they include stale reference, resurrection candidate, unknown current state, OAuth/SDK evolution, acquisition review, and source conflict reasons.

`PASSIVE` requests are planning-safe. `ACTIVE_HTTPS` requests additionally require an HTTPS target and later active-execution approval/scope conditions. The analysis endpoint still does not execute either mode.

## Retry scheduling

`POST /api/v1/analysis/reobservation/retry` accepts one existing `ReobservationRequest`, `base_delay_seconds` and `maximum_delay_seconds`. Both delays must be positive and the maximum must be greater than or equal to the base. The result is retry metadata only.

## Evolution analysis

The evolution endpoints accept a list of `VersionedArtifactObservation` objects exactly as defined in OpenAPI:

- `/evolution/diff` calculates deterministic temporal deltas;
- `/evolution/stale-references` identifies stale/superseded reference candidates.

Neither endpoint establishes current reachability or creates a validated finding.

See [README.md](README.md) for the complete Local API, runtime, Workbench transport, error and OpenAPI contracts.
