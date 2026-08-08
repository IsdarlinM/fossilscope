# CLI presentation

FossilScope 0.5.3 uses the shared Sentinel Forge CLI presentation contract from SRIC Core.

Interactive console sessions show a subdued green ASCII banner ordered as `FossilScope :: v0.5.3`, `Developer: IsdarlinM`, then `Map historical attack surface and separate history from current exposure.` The banner is written to interactive stderr, keeping stdout suitable for JSON, graph exports, redirection, and automation.

Use `fossilscope --no-color COMMAND` to disable ANSI/Rich colors. The installed console entrypoint also normalizes `fossilscope COMMAND --no-color`. The standard `NO_COLOR` environment variable is honored.

Typer/Rich command and help presentation is colorized by default. `--no-color` changes presentation only; it does not alter temporal evidence, lifecycle assessments, re-observation planning, workspace resolution, or API responses.
