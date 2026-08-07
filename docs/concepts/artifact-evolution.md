# API, OAuth and SDK evolution

FossilScope 0.3.1 compares passive versioned observations of API specifications, OAuth clients, SDKs, documentation and mobile artifacts.

The diff records added and removed:

- endpoints;
- OAuth redirect URIs;
- OAuth scopes;
- references embedded in SDKs or documentation.

Changes are `OBSERVED` artifact differences and never prove current exposure. Sources sharing one upstream group do not count as independent confirmation.

A stale-reference candidate becomes `HYPOTHESIS` only when a current artifact still references a value removed from a historical version. Without current corroboration it remains `UNKNOWN`. No network request is sent.

CLI:

```bash
fossilscope evolution-diff observations.json
fossilscope stale-references observations.json
```

Loopback API:

```text
POST /api/v1/analysis/evolution/diff
POST /api/v1/analysis/evolution/stale-references
```
