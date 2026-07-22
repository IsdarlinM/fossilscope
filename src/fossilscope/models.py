from __future__ import annotations
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any
from pydantic import BaseModel, ConfigDict, Field
from sric.models import ClaimStatus


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class FossilType(StrEnum):
    GHOST_ENDPOINT = "GHOST_ENDPOINT"
    GHOST_DOMAIN = "GHOST_DOMAIN"
    LEGACY_AUTH_PATH = "LEGACY_AUTH_PATH"
    DEPRECATED_API = "DEPRECATED_API"
    ORPHANED_CLIENT = "ORPHANED_CLIENT"
    OLD_SDK_REFERENCE = "OLD_SDK_REFERENCE"
    STALE_DOCUMENTATION = "STALE_DOCUMENTATION"
    ACQUISITION_REMAINDER = "ACQUISITION_REMAINDER"
    OLD_STORAGE_REFERENCE = "OLD_STORAGE_REFERENCE"
    HISTORICAL_TRUST_RELATIONSHIP = "HISTORICAL_TRUST_RELATIONSHIP"


class Observation(BaseModel):
    model_config = ConfigDict(extra="forbid")
    observation_id: str
    entity_type: str
    value: str
    source: str
    observed_at: datetime = Field(default_factory=utcnow)
    first_seen: datetime | None = None
    last_seen: datetime | None = None
    current_reachable: bool | None = None
    auth_relevance: bool = False
    sensitivity_hint: bool = False
    current_reference: bool = False
    evidence_ids: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class Relationship(BaseModel):
    model_config = ConfigDict(extra="forbid")
    relationship_id: str
    source_value: str
    target_value: str
    relationship_type: str
    observed_at: datetime = Field(default_factory=utcnow)
    valid_from: datetime | None = None
    valid_to: datetime | None = None
    evidence_ids: list[str] = Field(default_factory=list)
    confidence: float = Field(ge=0, le=1)


class FossilCandidate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    candidate_id: str
    value: str
    fossil_type: FossilType
    status: ClaimStatus = ClaimStatus.HYPOTHESIS
    score: float = Field(ge=0, le=1)
    components: dict[str, float]
    evidence_ids: list[str] = Field(default_factory=list)
    counter_evidence: list[str] = Field(default_factory=list)
    explanation: list[str] = Field(default_factory=list)
