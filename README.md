# FossilScope

```text
FossilScope
imr :: v0.3.0
```

Attack Surface Archaeology + Temporal Security Graph for discovering historical capabilities without confusing historical evidence with current exposure.

> **AI proposes. Evidence proves. Humans control.**

## v0.3.0
- temporal observations, timeline/diff and explicit historical/current separation;
- passive local adapters for CT/DNS/repos/packages/OpenAPI/JS/source maps/docs/archives/security.txt/sitemaps;
- bounded opt-in HTTPS collector runtime with explicit scope, terms acknowledgement, DNS revalidation/pinning, no redirects, rate limits, cache and provenance;
- time-travel graph, lifecycle states, confidence decay, separate historical/current confidence and resurrection candidates;
- historical API/mobile archaeology, clustering and acquisition lineage;
- SRIC 0.4 shared workspace, graph, jobs/SSE, lineage and notebook/search integration;
- local API/Web UI, CLI, reports, offline demo and signed update primitive.

Historical evidence never proves current reachability. `RESURRECTED` and other correlations remain `HYPOTHESIS` until evidence supports validation.

## Quickstart
```bash
fossilscope doctor
fossilscope demo --workspace demo
fossilscope timeline demo
fossilscope fossils demo
fossilscope web demo
```

Network collection is never hidden. `collect-url` requires HTTPS, explicit `--allow` scope and `--ack-terms`.

Telemetry, cloud AI and external uploads are OFF by default. Apache-2.0.
