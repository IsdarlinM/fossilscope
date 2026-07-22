# FossilScope

```text
FossilScope
imr :: v0.2.0
```

Attack Surface Archaeology + Temporal Security Graph for finding capabilities and relationships that may have survived beyond their expected lifecycle.

> **AI proposes. Evidence proves. Humans control.**

## What works in v0.2.0

- temporal observations with `first_seen`, `last_seen`, `observed_at` and source/evidence provenance;
- historical/current separation so archived evidence is never presented as current exposure;
- passive JSON ingestion and local artifact URL/domain extraction without network requests;
- timeline and temporal diff;
- explainable fossil scoring using staleness, source diversity, reachability evidence, auth relevance, sensitivity hints and current references;
- fossil types including deprecated APIs, ghost endpoints/domains, orphaned clients, stale docs and historical trust relationships;
- explicit counter-evidence and `HYPOTHESIS` status for candidates;
- local FastAPI + responsive timeline/candidate Web UI;
- offline synthetic demo, scope checks, plugin inspection, AI-disabled mode and signed-update primitive through SRIC.

- time-travel temporal graph, explicit fossil lifecycle, confidence decay, acquisition lineage and explainable clustering;
- historical OpenAPI diff and passive local source adapters for CT, DNS, repositories, packages, OpenAPI, JS/source maps, docs, archives, security.txt and sitemaps;
- SRIC 0.3 jobs/SSE, evidence lineage, notebook/search and shared temporal graph primitives;

## Five-minute start

```bash
fossilscope doctor
fossilscope demo --workspace demo
fossilscope fossils demo
fossilscope timeline demo
fossilscope web demo
```

Offline lab:

```bash
fossilscope init lab
fossilscope import lab examples/lab/temporal-observations.json
fossilscope fossils lab
```

## Passive by default

v0.2.0 does not perform unbounded crawling or autonomous active validation. Historical references, present-day references and confirmed current reachability remain distinct facts.

## Safety and privacy

Use only authorized data/systems. Telemetry, cloud AI and external uploads are off by default. Active validation must remain scoped, policy-controlled and human-approved when added/used.

## Documentation

See `docs/` and `ROADMAP.md` for architecture, threat model, CLI, formats, plugins, integrations and deferred adapters/collectors.

## License

Apache-2.0.
