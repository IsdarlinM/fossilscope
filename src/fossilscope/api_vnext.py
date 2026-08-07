from __future__ import annotations

from fastapi import APIRouter, FastAPI
from pydantic import BaseModel, ConfigDict, Field, model_validator

from .api import create_app as create_base_app
from .lifecycle import SurfaceEvidence, assess_lifecycle
from .reobservation import (
    ReobservationRequest,
    deduplicate_requests,
    evaluate_reobservation,
    schedule_retry,
)


class LifecycleRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    evidence: list[SurfaceEvidence]


class ReobservationPlanRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    requests: list[ReobservationRequest]
    deduplicate: bool = True


class ReobservationRetryRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    request: ReobservationRequest
    base_delay_seconds: int = Field(default=60, ge=1)
    maximum_delay_seconds: int = Field(default=86400, ge=1)

    @model_validator(mode="after")
    def valid_delay_bounds(self) -> "ReobservationRetryRequest":
        if self.maximum_delay_seconds < self.base_delay_seconds:
            raise ValueError("maximum_delay_seconds must be >= base_delay_seconds")
        return self


router = APIRouter(prefix="/api/v1/analysis", tags=["analysis"])


@router.post("/lifecycle")
async def lifecycle(request: LifecycleRequest) -> dict[str, object]:
    assessments = assess_lifecycle(request.evidence)
    return {
        "assessments": [item.model_dump(mode="json") for item in assessments],
        "validated_findings_created": 0,
        "historical_evidence_proves_current_exposure": False,
    }


@router.post("/reobservation/plan")
async def reobservation_plan(request: ReobservationPlanRequest) -> dict[str, object]:
    requests = deduplicate_requests(request.requests) if request.deduplicate else request.requests
    decisions = [evaluate_reobservation(item) for item in requests]
    return {
        "decisions": [item.model_dump(mode="json") for item in decisions],
        "executed": False,
        "requests_sent": 0,
    }


@router.post("/reobservation/retry")
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


def create_app() -> FastAPI:
    app = create_base_app()
    app.include_router(router)
    return app
