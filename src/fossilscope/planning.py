from __future__ import annotations

import hashlib
from enum import StrEnum
from typing import Sequence

from pydantic import BaseModel, ConfigDict, Field

from .reobservation import (
    ReobservationMode,
    ReobservationReason,
    ReobservationRequest,
    deduplicate_requests,
)


class CurrentExposureState(StrEnum):
    CURRENTLY_REACHABLE = "CURRENTLY_REACHABLE"
    CURRENTLY_UNREACHABLE = "CURRENTLY_UNREACHABLE"
    REACHABILITY_UNKNOWN = "REACHABILITY_UNKNOWN"
    HISTORICAL_ONLY = "HISTORICAL_ONLY"
    DISCOVERED = "DISCOVERED"


class ReobservationCandidate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    asset_id: str
    target: str
    exposure_state: CurrentExposureState
    evidence_ids: list[str] = Field(default_factory=list)
    age_days: int = Field(default=0, ge=0)
    current_reference: bool = False
    auth_relevance: bool = False
    source_conflict: bool = False
    acquisition_context: bool = False


def _priority(candidate: ReobservationCandidate) -> int:
    score = 20
    if candidate.exposure_state is CurrentExposureState.REACHABILITY_UNKNOWN:
        score += 30
    elif candidate.exposure_state is CurrentExposureState.HISTORICAL_ONLY:
        score += 15
    elif candidate.exposure_state is CurrentExposureState.CURRENTLY_UNREACHABLE:
        score += 5
    if candidate.current_reference:
        score += 15
    if candidate.auth_relevance:
        score += 15
    if candidate.source_conflict:
        score += 15
    if candidate.acquisition_context:
        score += 5
    score += min(10, candidate.age_days // 180)
    return max(0, min(100, score))


def _reason(candidate: ReobservationCandidate) -> ReobservationReason:
    if candidate.source_conflict:
        return ReobservationReason.SOURCE_CONFLICT
    if candidate.acquisition_context:
        return ReobservationReason.ACQUISITION_REVIEW
    if candidate.exposure_state is CurrentExposureState.REACHABILITY_UNKNOWN:
        return ReobservationReason.CURRENT_STATE_UNKNOWN
    return ReobservationReason.STALE_REFERENCE


def plan_reobservation(
    candidates: Sequence[ReobservationCandidate],
    *,
    maximum_requests: int = 50,
) -> list[ReobservationRequest]:
    """Prioritize passive evidence refresh without asserting present-day exposure."""

    if maximum_requests < 1:
        raise ValueError("maximum_requests must be at least 1")
    requests: list[ReobservationRequest] = []
    for candidate in candidates:
        digest = hashlib.sha256(
            f"{candidate.asset_id}\x00{candidate.target}\x00{_reason(candidate).value}".encode()
        ).hexdigest()[:16]
        requests.append(
            ReobservationRequest(
                request_id=f"REOBS-{digest.upper()}",
                asset_id=candidate.asset_id,
                target=candidate.target,
                reason=_reason(candidate),
                mode=ReobservationMode.PASSIVE,
                source_evidence_ids=sorted(set(candidate.evidence_ids)),
                priority=_priority(candidate),
                limitations=[
                    "Research priority is not vulnerability severity or exploitability.",
                    "The planner is passive-first; active HTTPS re-observation requires a separate explicitly approved request.",
                ],
            )
        )
    return deduplicate_requests(requests)[:maximum_requests]
