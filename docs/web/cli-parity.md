# Web/CLI feature parity

FossilScope 0.5.7 mounts the shared SRIC Web Feature Workbench at `/workbench` and retains `/console` as the advanced argv-oriented surface.

The native temporal dashboard remains the quick evidence view and now exposes visible **All Features** and **Advanced Console** navigation. This closes the previous discoverability gap where the root page exposed only Temporal Security Graph, Fossil Candidates and Lifecycle.

The Workbench derives its catalog from `fossilscope.cli_all`. Every public command and every ordered CLI parameter is represented as a structured responsive Web control. `/api/v1/workbench/coverage` reports exact parity.

Execution uses the fixed `sric.web_console_runner` with `shell=False`, disabled stdin, CSRF protection, secret redaction, bounded/cancellable jobs and SSE output. FossilScope passive-first behavior, scope, terms acknowledgement and active collection approval gates remain authoritative.

The release tests invoke help for every public command, verify all options/required arguments, compare the complete ordered CLI parameter tree with the Workbench schema, verify dashboard navigation and smoke-test the native temporal APIs. Active/destructive actions are gate-tested rather than executed merely for coverage.
