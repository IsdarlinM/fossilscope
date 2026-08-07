# Current exposure lifecycle

FossilScope separates historical presence from present exposure.

- `HISTORICAL_ONLY`: historical evidence exists; no current signal is established.
- `CURRENT_DNS`: a current DNS answer exists; application reachability is unknown.
- `CURRENT_TLS`: a current TLS endpoint was observed; application identity/HTTP behavior is still unproven.
- `CURRENT_HTTP`: a current application response was directly observed.
- `CURRENT_AUTHENTICATED`: an authorized authenticated interaction was directly observed.
- `REDIRECTED`: the historical location redirects elsewhere.
- `PARKED`, `SINKHOLED`, `TRANSFERRED`, `RETIRED`: explicit controls that prevent a resurrection claim.
- `UNKNOWN_CURRENT_STATE`: available data is ambiguous or controlled by wildcard/shared/default infrastructure.

A resurrection candidate requires historical evidence and a current application response. It remains `HYPOTHESIS`. Source mirrors are grouped by upstream origin, and wildcard DNS, shared infrastructure and default virtual hosts are retained as counter-signals rather than discarded.
