from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict, Field, model_validator

from .api import create_app as create_base_app
from .evolution import VersionedArtifactObservation, diff_artifact_versions, find_stale_references
from .lifecycle import SurfaceEvidence, assess_lifecycle
from .planning import ReobservationCandidate, plan_reobservation
from .reobservation import (
    ReobservationRequest,
    deduplicate_requests,
    evaluate_reobservation,
    schedule_retry,
)


class LifecycleRequest(BaseModel):
    """Evidence records used to assess current-exposure lifecycle conservatively."""

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "examples": [
                {
                    "evidence": [
                        {
                            "value": "api.example.test/v1",
                            "kind": "CURRENT_OBSERVATION",
                            "observed_at": "2026-08-10T12:00:00Z",
                            "source": "authorized observation",
                        }
                    ]
                }
            ]
        },
    )
    evidence: list[SurfaceEvidence] = Field(
        description=(
            "Evidence-bearing surface observations. Historical-only records cannot establish "
            "current exposure without current evidence."
        )
    )


class ReobservationPlanRequest(BaseModel):
    """Candidate reobservation requests evaluated without executing network traffic."""

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "examples": [
                {
                    "requests": [
                        {
                            "request_id": "reobserve-001",
                            "target": "https://example.test/.well-known/openapi.json",
                            "mode": "PASSIVE",
                            "reason": "stale historical API documentation",
                        }
                    ],
                    "deduplicate": True,
                }
            ]
        },
    )
    requests: list[ReobservationRequest] = Field(
        description="Proposed reobservation requests. This endpoint evaluates them but sends none."
    )
    deduplicate: bool = Field(
        default=True,
        description="Collapse equivalent reobservation requests before evaluation.",
    )


class ReobservationPriorityRequest(BaseModel):
    """UNKNOWN or stale candidates ranked for future human-controlled reobservation."""

    model_config = ConfigDict(extra="forbid")
    candidates: list[ReobservationCandidate] = Field(
        description=(
            "Candidates to prioritize. Ranking does not validate exposure, ownership or a finding."
        )
    )
    maximum_requests: int = Field(
        default=50,
        ge=1,
        le=1000,
        description="Maximum number of proposed requests returned by the planner.",
        examples=[25],
    )


class ReobservationRetryRequest(BaseModel):
    """Retry scheduling input; no request is executed by this endpoint."""

    model_config = ConfigDict(extra="forbid")
    request: ReobservationRequest = Field(
        description="Existing reobservation request whose retry metadata should be updated."
    )
    base_delay_seconds: int = Field(
        default=60,
        ge=1,
        description="Base delay used for bounded exponential backoff.",
        examples=[60],
    )
    maximum_delay_seconds: int = Field(
        default=86400,
        ge=1,
        description="Maximum allowed retry delay in seconds.",
        examples=[3600],
    )

    @model_validator(mode="after")
    def valid_delay_bounds(self) -> "ReobservationRetryRequest":
        if self.maximum_delay_seconds < self.base_delay_seconds:
            raise ValueError("maximum_delay_seconds must be >= base_delay_seconds")
        return self


class EvolutionRequest(BaseModel):
    """Versioned observations used for deterministic local temporal comparison."""

    model_config = ConfigDict(extra="forbid")
    observations: list[VersionedArtifactObservation] = Field(
        description=(
            "Versioned artifact observations ordered or comparable by their temporal metadata. "
            "Comparison is local and does not prove current reachability."
        )
    )


router = APIRouter(
    prefix="/api/v1/analysis",
    tags=["analysis"],
    responses={
        422: {
            "description": "Input is structurally valid JSON but violates the analysis contract."
        }
    },
)


@router.post(
    "/lifecycle",
    summary="Assess exposure lifecycle from evidence",
    description=(
        "Classify lifecycle state from evidence-bearing observations. Historical evidence remains "
        "distinct from current exposure. The operation is analytical only: it sends no requests "
        "and creates no VALIDATED finding."
    ),
    response_description="Lifecycle assessments plus explicit proof-boundary metadata.",
)
async def lifecycle(request: LifecycleRequest) -> dict[str, object]:
    assessments = assess_lifecycle(request.evidence)
    return {
        "assessments": [item.model_dump(mode="json") for item in assessments],
        "validated_findings_created": 0,
        "historical_evidence_proves_current_exposure": False,
    }


@router.post(
    "/reobservation/prioritize",
    summary="Prioritize candidates for reobservation",
    description=(
        "Rank stale or UNKNOWN candidates for a future reobservation workflow. This endpoint only "
        "builds a bounded passive-first plan; it performs no network activity and cannot validate "
        "a finding."
    ),
    response_description="Prioritized proposed requests and explicit execution counters.",
)
async def reobservation_prioritize(
    request: ReobservationPriorityRequest,
) -> dict[str, object]:
    planned = plan_reobservation(
        request.candidates,
        maximum_requests=request.maximum_requests,
    )
    return {
        "requests": [item.model_dump(mode="json") for item in planned],
        "planned_request_count": len(planned),
        "passive_only": True,
        "executed": False,
        "requests_sent": 0,
        "validated_findings_created": 0,
    }


@router.post(
    "/reobservation/plan",
    summary="Evaluate a reobservation plan",
    description=(
        "Deduplicate and policy-evaluate proposed reobservation requests without executing them. "
        "Any later active action still has to pass Scope, Policy, Rate Limits and human approval."
    ),
    response_description="Per-request planning decisions with zero execution side effects.",
)
async def reobservation_plan(request: ReobservationPlanRequest) -> dict[str, object]:
    requests = deduplicate_requests(request.requests) if request.deduplicate else request.requests
    decisions = [evaluate_reobservation(item) for item in requests]
    return {
        "decisions": [item.model_dump(mode="json") for item in decisions],
        "executed": False,
        "requests_sent": 0,
    }


@router.post(
    "/reobservation/retry",
    summary="Schedule bounded retry metadata",
    description=(
        "Compute the next bounded exponential-backoff retry record. The endpoint updates only the "
        "returned planning record and sends no request."
    ),
    response_description="Updated retry-planning record with explicit zero-execution counters.",
)
async def reobservation_retry(request: ReobservationRetryRequest) -> dict[str, object]:
    updated = schedule_retry(
        request.request,
        base_delay_seconds=request.base_delay_seconds,
        maximum_delay_seconds=request.maximum_delay_seconds,
    )
    return {
        "request": updated.model_dump(mode="json"),
        "executed": False,
        "requests_sent": 0,
    }


@router.post(
    "/evolution/diff",
    summary="Diff versioned artifact observations",
    description=(
        "Compare local versioned observations to identify temporal changes. A detected change is "
        "evidence of evolution, not proof that an artifact is currently reachable or vulnerable."
    ),
    response_description="Deterministic temporal deltas and explicit non-validation metadata.",
)
async def evolution_diff(request: EvolutionRequest) -> dict[str, object]:
    try:
        deltas = diff_artifact_versions(request.observations)
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc
    return {
        "deltas": [item.model_dump(mode="json") for item in deltas],
        "current_exposure_proved": False,
        "validated_findings_created": 0,
    }


@router.post(
    "/evolution/stale-references",
    summary="Find stale or superseded references",
    description=(
        "Identify references that appear stale when versioned artifact observations are compared. "
        "Candidates remain hypotheses until current evidence is obtained. No request is sent."
    ),
    response_description="Stale-reference candidates with explicit current-reachability boundaries.",
)
async def evolution_stale_references(request: EvolutionRequest) -> dict[str, object]:
    try:
        candidates = find_stale_references(request.observations)
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc
    return {
        "candidates": [item.model_dump(mode="json") for item in candidates],
        "current_reachability_proved": False,
        "requests_sent": 0,
        "validated_findings_created": 0,
    }


def create_app(workspace: Path) -> FastAPI:
    app = create_base_app(workspace)
    app.include_router(router)
    return app
