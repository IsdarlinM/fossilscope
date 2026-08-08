# Re-observation Planning in FossilScope 0.5

FossilScope 0.5 separates historical relevance, current exposure state and re-observation priority.

`plan_reobservation()` produces passive requests only. It favors assets whose current state is unknown, are still referenced, have authorization relevance, contain source conflicts or need acquisition-era review. Age can increase research priority but does not establish current exposure.

The priority is a research scheduling signal, not vulnerability severity or exploitability.

## Active observation

Active HTTPS re-observation remains a separate workflow with explicit scope and approval requirements. The passive planner cannot silently opt an asset into an active request.

## Import safety

Direct JSON import now uses the same bounded regular-file loader as other structured imports. Symlinks and inputs beyond the configured import size limit are rejected before parsing.
