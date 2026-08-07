from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone
from enum import StrEnum
from typing import Sequence

from pydantic import BaseModel, ConfigDict, Field, model_validator
from sric.calibration import ConfidenceSignal, score_confidence, skeptic_review
from sric.models import ClaimStatus


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class EvidenceKind(StrEnum):
    HISTORICAL_REFERENCE = "HISTORICAL_REFERENCE"
    CURRENT_DNS = "CURRENT_DNS"
    CURRENT_TLS = "CURRENT_TLS"
    CURRENT_HTTP = "CURRENT_HTTP"
    CURRENT_AUTHENTICATED = "CURRENT_AUTHENTICATED"
    REDIRECT = "REDIRECT"
    RETIREMENT_RECORD = "RETIREMENT_RECORD"
    TRANSFER_RECORD = "TRANSFER_RECORD"


class ExposureLifecycle(StrEnum):
    HISTORICAL_ONLY = "HISTORICAL_ONLY"
    CURRENT_DNS = "CURRENT_DNS"
    CURRENT_TLS = "CURRENT_TLS"
    CURRENT_HTTP = "CURRENT_HTTP"
    CURRENT_AUTHENTICATED = "CURRENT_AUTHENTICATED"
    REDIRECTED = "REDIRECTED"
    PARKED = "PARKED"
    SINKHOLED = "SINKHOLED"
    TRANSFERRED = "TRANSFERRED"
    RETIRED = "RETIRED"
    UNKNOWN_CURRENT_STATE = "UNKNOWN_CURRENT_STATE"


class SurfaceEvidence(BaseModel):
    model_config = ConfigDict(extra="forbid")

    evidence_id: str
    asset_id: str
    kind: EvidenceKind
    source_id: str
    source_group: str | None = None
    observed_at: datetime = Field(default_factory=utcnow)
    direct_observation: bool = False
    wildcard_dns: bool = False
    shared_infrastructure: bool = False
    default_virtual_host: bool = False
    parked: bool = False
    sinkholed: bool = False
    transferred: bool = False
    counter_evidence_ids: list[str] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def direct_current_observations_are_evidence(self) -> "SurfaceEvidence":
        if self.direct_observation and self.kind is EvidenceKind.HISTORICAL_REFERENCE:
            raise ValueError(
                "historical references cannot be marked as current direct observations"
            )
        return self


class LifecycleAssessment(BaseModel):
    model_config = ConfigDict(extra="forbid")

    asset_id: str
    lifecycle: ExposureLifecycle
    status: ClaimStatus
    resurrection_candidate: bool = False
    confidence: float = Field(ge=0.0, le=1.0)
    evidence_ids: list[str] = Field(default_factory=list)
    counter_evidence_ids: list[str] = Field(default_factory=list)
    independent_source_groups: int = 0
    duplicate_source_groups: list[str] = Field(default_factory=list)
    controls_triggered: list[str] = Field(default_factory=list)
    missing_evidence: list[str] = Field(default_factory=list)
    alternative_explanations: list[str] = Field(default_factory=list)
    skeptic_verdict: str


def _lifecycle(
    items: Sequence[SurfaceEvidence],
) -> tuple[ExposureLifecycle, list[str]]:
    controls: list[str] = []
    if any(
        item.transferred or item.kind is EvidenceKind.TRANSFER_RECORD
        for item in items
    ):
        return ExposureLifecycle.TRANSFERRED, ["ownership transfer evidence"]
    if any(item.sinkholed for item in items):
        return ExposureLifecycle.SINKHOLED, ["sinkhole indicators"]
    if any(item.parked for item in items):
        return ExposureLifecycle.PARKED, ["parking indicators"]
    if any(item.kind is EvidenceKind.RETIREMENT_RECORD for item in items):
        return ExposureLifecycle.RETIRED, ["retirement record"]

    if any(item.wildcard_dns for item in items):
        controls.append("wildcard DNS")
    if any(item.shared_infrastructure for item in items):
        controls.append("shared infrastructure")
    if any(item.default_virtual_host for item in items):
        controls.append("default virtual host")

    kinds = {item.kind for item in items}
    if EvidenceKind.CURRENT_AUTHENTICATED in kinds:
        return ExposureLifecycle.CURRENT_AUTHENTICATED, controls
    if EvidenceKind.CURRENT_HTTP in kinds:
        return ExposureLifecycle.CURRENT_HTTP, controls
    if EvidenceKind.REDIRECT in kinds:
        return ExposureLifecycle.REDIRECTED, controls
    if EvidenceKind.CURRENT_TLS in kinds:
        return ExposureLifecycle.CURRENT_TLS, controls
    if EvidenceKind.CURRENT_DNS in kinds:
        has_non_dns_direct_observation = any(
            item.direct_observation and item.kind is not EvidenceKind.CURRENT_DNS
            for item in items
        )
        if controls and not has_non_dns_direct_observation:
            return ExposureLifecycle.UNKNOWN_CURRENT_STATE, controls
        return ExposureLifecycle.CURRENT_DNS, controls
    if EvidenceKind.HISTORICAL_REFERENCE in kinds:
        return ExposureLifecycle.HISTORICAL_ONLY, controls
    return ExposureLifecycle.UNKNOWN_CURRENT_STATE, controls


def assess_lifecycle(
    evidence: Sequence[SurfaceEvidence],
) -> list[LifecycleAssessment]:
    """Separate historical evidence from current exposure conservatively.

    Current DNS alone never proves application reachability. Wildcards, parking,
    sinkholes, shared infrastructure, default virtual hosts and transfer evidence
    prevent automatic resurrection claims.
    """

    grouped: dict[str, list[SurfaceEvidence]] = defaultdict(list)
    for item in evidence:
        grouped[item.asset_id].append(item)

    assessments: list[LifecycleAssessment] = []
    for asset_id in sorted(grouped):
        items = grouped[asset_id]
        lifecycle, controls = _lifecycle(items)
        kinds = {item.kind for item in items}
        historical = EvidenceKind.HISTORICAL_REFERENCE in kinds
        current_application = bool(
            kinds
            & {
                EvidenceKind.CURRENT_HTTP,
                EvidenceKind.CURRENT_AUTHENTICATED,
            }
        )
        disqualifying = lifecycle in {
            ExposureLifecycle.PARKED,
            ExposureLifecycle.SINKHOLED,
            ExposureLifecycle.TRANSFERRED,
            ExposureLifecycle.RETIRED,
            ExposureLifecycle.UNKNOWN_CURRENT_STATE,
        }
        resurrection = (
            historical
            and current_application
            and not disqualifying
            and not controls
        )

        missing: list[str] = []
        alternatives: list[str] = []
        if historical and not current_application:
            missing.append("current application response")
        if lifecycle is ExposureLifecycle.CURRENT_DNS:
            missing.extend(
                ["current TLS or HTTP evidence", "application identity evidence"]
            )
        if lifecycle is ExposureLifecycle.CURRENT_TLS:
            missing.extend(
                ["current HTTP evidence", "application identity evidence"]
            )
        if controls:
            alternatives.extend(
                [
                    "The signal may belong to shared or catch-all infrastructure.",
                    "The responding service may not be the historical application.",
                ]
            )

        signals: list[ConfidenceSignal] = []
        for item in items:
            positive = item.kind in {
                EvidenceKind.CURRENT_TLS,
                EvidenceKind.CURRENT_HTTP,
                EvidenceKind.CURRENT_AUTHENTICATED,
            }
            contribution = 0.18 if positive else 0.08
            if item.kind in {
                EvidenceKind.TRANSFER_RECORD,
                EvidenceKind.RETIREMENT_RECORD,
            }:
                contribution = -0.45
            if item.parked or item.sinkholed or item.transferred:
                contribution = -0.5
            if (
                item.wildcard_dns
                or item.shared_infrastructure
                or item.default_virtual_host
            ):
                contribution = min(contribution, -0.2)
            signals.append(
                ConfidenceSignal(
                    signal=item.kind.value,
                    contribution=contribution,
                    reason="Temporal surface evidence",
                    source_id=item.source_id,
                    source_group=item.source_group,
                    evidence_ids=[item.evidence_id],
                    observed_at=item.observed_at,
                    direct_observation=item.direct_observation,
                    source_quality=0.9 if item.direct_observation else 0.65,
                    specificity=0.9 if positive else 0.6,
                    temporal_half_life_days=30 if positive else 730,
                )
            )
        breakdown = score_confidence(
            signals,
            base_confidence=0.05,
            maximum=0.79,
        )
        counter = sorted(
            {
                counter_id
                for item in items
                for counter_id in item.counter_evidence_ids
            }
        )
        review = skeptic_review(
            breakdown,
            alternative_explanations=alternatives,
            counter_evidence_ids=counter,
            missing_required_evidence=missing,
        )

        if resurrection:
            status = ClaimStatus.HYPOTHESIS
            confidence = min(review.adjusted_confidence, 0.79)
        elif lifecycle in {
            ExposureLifecycle.CURRENT_HTTP,
            ExposureLifecycle.CURRENT_AUTHENTICATED,
            ExposureLifecycle.CURRENT_TLS,
            ExposureLifecycle.CURRENT_DNS,
            ExposureLifecycle.REDIRECTED,
            ExposureLifecycle.HISTORICAL_ONLY,
            ExposureLifecycle.PARKED,
            ExposureLifecycle.SINKHOLED,
            ExposureLifecycle.TRANSFERRED,
            ExposureLifecycle.RETIRED,
        }:
            status = ClaimStatus.OBSERVED
            confidence = min(review.adjusted_confidence, 0.69)
        else:
            status = ClaimStatus.UNKNOWN
            confidence = min(review.adjusted_confidence, 0.49)

        groups = {item.source_group or item.source_id for item in items}
        duplicates = sorted(
            group
            for group in groups
            if sum(
                (item.source_group or item.source_id) == group
                for item in items
            )
            > 1
        )
        assessments.append(
            LifecycleAssessment(
                asset_id=asset_id,
                lifecycle=lifecycle,
                status=status,
                resurrection_candidate=resurrection,
                confidence=round(confidence, 6),
                evidence_ids=sorted(item.evidence_id for item in items),
                counter_evidence_ids=counter,
                independent_source_groups=len(groups),
                duplicate_source_groups=duplicates,
                controls_triggered=controls,
                missing_evidence=sorted(set(missing)),
                alternative_explanations=sorted(set(alternatives)),
                skeptic_verdict=review.verdict.value,
            )
        )
    return assessments
