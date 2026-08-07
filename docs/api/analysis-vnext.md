# Analysis API

Run the extended local API on loopback:

```bash
python -m uvicorn fossilscope.api_vnext:create_app --factory --host 127.0.0.1 --port 8765
```

Additional endpoints:

```text
POST /api/v1/analysis/lifecycle
POST /api/v1/analysis/reobservation/plan
POST /api/v1/analysis/reobservation/retry
```

Reobservation endpoints plan and schedule work only. They never send requests. Active execution remains behind SRIC Scope, Policy, rate limits, approval and destination revalidation.
