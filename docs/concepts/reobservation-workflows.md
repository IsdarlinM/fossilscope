# Reobservation workflows

FossilScope reobservation is passive by default.

`ReobservationRequest` supports stale references, resurrection candidates, unknown current state, OAuth/SDK evolution, acquisition review and source conflicts. Requests have deterministic deduplication keys, priority, bounded attempts and exponential backoff.

## Passive mode

Passive requests are classified `READ_ONLY_SAFE` and may use already acquired/local datasets or provider adapters that do not contact a target.

## Active HTTPS mode

An active request is only eligible when all conditions are present:

- HTTPS target;
- explicit hostname allow pattern;
- acknowledged provider/target terms;
- human approval;
- attempt and backoff budgets not exceeded.

The planner never sends the request. Execution must still pass SRIC Scope, Policy, rate limits, redirect/DNS destination revalidation and the approved collector executor.

A successful reobservation updates current-state evidence. It never validates a vulnerability.

CLI examples:

```bash
fossilscope lifecycle-assess evidence.json
fossilscope reobserve-plan requests.json
fossilscope reobserve-retry request.json --base-delay 60 --max-delay 86400
```
