from __future__ import annotations

from datetime import datetime, timezone
from enum import StrEnum
from typing import Sequence

from pydantic import BaseModel, ConfigDict, Field, model_validator
from sric.models import ClaimStatus


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class ArtifactKind(StrEnum):
    API_SPEC = "API_SPEC"
    OAUTH_CLIENT = "OAUTH_CLIENT"
    SDK = "SDK"
    DOCUMENTATION = "DOCUMENTATION"
    MOBILE_ARTIFACT = "MOBILE_ARTIFACT"


class VersionedArtifactObservation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    observation_id: str
    artifact_id: str
    artifact_kind: ArtifactKind
    version_label: str
    observed_at: datetime = Field(default_factory=utcnow)
    content_sha256: str
    endpoints: list[str] = Field(default_factory=list)
    redirect_uris: list[str] = Field(default_factory=list)
    oauth_scopes: list[str] = Field(default_factory=list)
    references: list[str] = Field(default_factory=list)
    source_id: str
    source_group: str | None = None
    evidence_ids: list[str] = Field(default_factory=list)
    historical: bool = True

    @model_validator(mode="after")
    def validate_observation(self) -> "VersionedArtifactObservation":
        if self.observed_at.tzinfo is None or self.observed_at.utcoffset() is None:
            raise ValueError("observed_at must be timezone-aware")
        if len(self.content_sha256) != 64:
            raise ValueError("content_sha256 must be a 64-character digest")
        try:
            bytes.fromhex(self.content_sha256)
        except ValueError as exc:
            raise ValueError("content_sha256 must be hexadecimal") from exc
        if not self.evidence_ids:
            raise ValueError("versioned artifact observations require evidence_ids")
        return self


class EvolutionDelta(BaseModel):
    model_config = ConfigDict(extra="forbid")

    artifact_id: str
    artifact_kind: ArtifactKind
    before_observation_id: str
    after_observation_id: str
    before_version: str
    after_version: str
    status: ClaimStatus = ClaimStatus.OBSERVED
    added_endpoints: list[str] = Field(default_factory=list)
    removed_endpoints: list[str] = Field(default_factory=list)
    added_redirect_uris: list[str] = Field(default_factory=list)
    removed_redirect_uris: list[str] = Field(default_factory=list)
    added_scopes: list[str] = Field(default_factory=list)
    removed_scopes: list[str] = Field(default_factory=list)
    added_references: list[str] = Field(default_factory=list)
    removed_references: list[str] = Field(default_factory=list)
    evidence_ids: list[str] = Field(default_factory=list)
    source_independence_groups: int = 0
    limitations: list[str] = Field(default_factory=list)


class StaleReferenceCandidate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    candidate_id: str
    artifact_id: str
    reference: str
    removed_in_version: str
    still_referenced_by_observation_ids: list[str]
    status: ClaimStatus
    evidence_ids: list[str] = Field(default_factory=list)
    missing_evidence: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)


def diff_artifact_versions(
    observations: Sequence[VersionedArtifactObservation],
) -> list[EvolutionDelta]:
    grouped: dict[str, list[VersionedArtifactObservation]] = {}
    for observation in observations:
        grouped.setdefault(observation.artifact_id, []).append(observation)

    output: list[EvolutionDelta] = []
    for artifact_id in sorted(grouped):
        values = sorted(
            grouped[artifact_id],
            key=lambda item: (item.observed_at, item.version_label, item.observation_id),
        )
        kinds = {item.artifact_kind for item in values}
        if len(kinds) > 1:
            raise ValueError(
                f"artifact_id {artifact_id} has inconsistent artifact_kind values"
            )
        for before, after in zip(values, values[1:]):
            groups = {
                before.source_group or before.source_id,
                after.source_group or after.source_id,
            }
            output.append(
                EvolutionDelta(
                    artifact_id=artifact_id,
                    artifact_kind=after.artifact_kind,
                    before_observation_id=before.observation_id,
                    after_observation_id=after.observation_id,
                    before_version=before.version_label,
                    after_version=after.version_label,
                    added_endpoints=sorted(set(after.endpoints) - set(before.endpoints)),
                    removed_endpoints=sorted(set(before.endpoints) - set(after.endpoints)),
                    added_redirect_uris=sorted(
                        set(after.redirect_uris) - set(before.redirect_uris)
                    ),
                    removed_redirect_uris=sorted(
                        set(before.redirect_uris) - set(after.redirect_uris)
                    ),
                    added_scopes=sorted(set(after.oauth_scopes) - set(before.oauth_scopes)),
                    removed_scopes=sorted(set(before.oauth_scopes) - set(after.oauth_scopes)),
                    added_references=sorted(set(after.references) - set(before.references)),
                    removed_references=sorted(set(before.references) - set(after.references)),
                    evidence_ids=sorted(set(before.evidence_ids) | set(after.evidence_ids)),
                    source_independence_groups=len(groups),
                    limitations=[
                        "Version differences are observed artifact changes, not proof of current exposure.",
                        "Removal from one artifact may reflect documentation or packaging changes rather than service retirement.",
                    ],
                )
            )
    return output


def find_stale_references(
    observations: Sequence[VersionedArtifactObservation],
    deltas: Sequence[EvolutionDelta] | None = None,
) -> list[StaleReferenceCandidate]:
    differences = list(
        diff_artifact_versions(observations) if deltas is None else deltas
    )
    current_references: dict[str, list[VersionedArtifactObservation]] = {}
    for observation in observations:
        if not observation.historical:
            for reference in observation.references:
                current_references.setdefault(reference, []).append(observation)

    output: list[StaleReferenceCandidate] = []
    for delta in differences:
        removed = sorted(
            set(delta.removed_endpoints)
            | set(delta.removed_redirect_uris)
            | set(delta.removed_references)
        )
        for reference in removed:
            current = current_references.get(reference, [])
            missing: list[str] = []
            if not current:
                missing.append("current artifact still referencing the removed value")
                status = ClaimStatus.UNKNOWN
            else:
                status = ClaimStatus.HYPOTHESIS
            output.append(
                StaleReferenceCandidate(
                    candidate_id=(
                        f"stale:{delta.artifact_id}:{delta.after_version}:{reference}"
                    ),
                    artifact_id=delta.artifact_id,
                    reference=reference,
                    removed_in_version=delta.after_version,
                    still_referenced_by_observation_ids=sorted(
                        item.observation_id for item in current
                    ),
                    status=status,
                    evidence_ids=sorted(
                        set(delta.evidence_ids)
                        | {
                            evidence
                            for item in current
                            for evidence in item.evidence_ids
                        }
                    ),
                    missing_evidence=missing,
                    limitations=[
                        "A stale reference is not proof that the target is reachable or controlled by the same organization.",
                        "Current reobservation must pass Scope and Policy before any active check.",
                    ],
                )
            )
    return output
