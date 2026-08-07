from __future__ import annotations

import fnmatch
import hashlib
from datetime import datetime, timedelta, timezone
from enum import StrEnum
from typing import Sequence
from urllib.parse import urlsplit

from pydantic import BaseModel, ConfigDict, Field, model_validator


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class ReobservationMode(StrEnum):
    PASSIVE = "PASSIVE"
    ACTIVE_HTTPS = "ACTIVE_HTTPS"


class ReobservationReason(StrEnum):
    STALE_REFERENCE = "STALE_REFERENCE"
    RESURRECTION_CANDIDATE = "RESURRECTION_CANDIDATE"
    CURRENT_STATE_UNKNOWN = "CURRENT_STATE_UNKNOWN"
    OAUTH_OR_SDK_EVOLUTION = "OAUTH_OR_SDK_EVOLUTION"
    ACQUISITION_REVIEW = "ACQUISITION_REVIEW"
    SOURCE_CONFLICT = "SOURCE_CONFLICT"


class ReobservationState(StrEnum):
    QUEUED = "QUEUED"
    BLOCKED = "BLOCKED"
    READY = "READY"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class ReobservationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    request_id: str
    asset_id: str
    target: str
    reason: ReobservationReason
    mode: ReobservationMode = ReobservationMode.PASSIVE
    source_evidence_ids: list[str] = Field(default_factory=list)
    priority: int = Field(default=50, ge=0, le=100)
    allow_patterns: list[str] = Field(default_factory=list)
    terms_acknowledged: bool = False
    human_approved: bool = False
    created_at: datetime = Field(default_factory=utcnow)
    not_before: datetime | None = None
    attempts: int = Field(default=0, ge=0)
    maximum_attempts: int = Field(default=3, ge=1, le=20)
    state: ReobservationState = ReobservationState.QUEUED
    limitations: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def active_requirements(self) -> "ReobservationRequest":
        if self.mode is ReobservationMode.ACTIVE_HTTPS:
            parsed = urlsplit(self.target)
            if parsed.scheme.lower() != "https" or not parsed.hostname:
                raise ValueError("ACTIVE_HTTPS reobservation requires an HTTPS target")
        return self

    def deduplication_key(self) -> str:
        canonical = "\x00".join(
            [self.asset_id, self.target.casefold(), self.reason.value, self.mode.value]
        )
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


class ReobservationDecision(BaseModel):
    model_config = ConfigDict(extra="forbid")

    request_id: str
    state: ReobservationState
    executable: bool
    action_class: str
    blockers: list[str] = Field(default_factory=list)
    matched_scope_pattern: str | None = None
    next_attempt_at: datetime | None = None
    limitations: list[str] = Field(default_factory=list)


def _scope_match(target: str, patterns: Sequence[str]) -> str | None:
    parsed = urlsplit(target)
    host = (parsed.hostname or "").casefold()
    for pattern in patterns:
        normalized = pattern.casefold().strip()
        if fnmatch.fnmatchcase(host, normalized):
            return pattern
    return None


def evaluate_reobservation(
    request: ReobservationRequest,
    *,
    now: datetime | None = None,
) -> ReobservationDecision:
    reference = now or utcnow()
    blockers: list[str] = []
    matched: str | None = None

    if request.state in {
        ReobservationState.COMPLETED,
        ReobservationState.CANCELLED,
    }:
        blockers.append(f"request is already {request.state.value}")
    if request.attempts >= request.maximum_attempts:
        blockers.append("maximum attempts reached")
    if request.not_before is not None and reference < request.not_before:
        blockers.append("backoff window has not elapsed")

    if request.mode is ReobservationMode.PASSIVE:
        action_class = "READ_ONLY_SAFE"
    else:
        action_class = "READ_ONLY_SENSITIVE"
        matched = _scope_match(request.target, request.allow_patterns)
        if matched is None:
            blockers.append("target is not matched by an explicit allow pattern")
        if not request.terms_acknowledged:
            blockers.append("provider or target terms were not acknowledged")
        if not request.human_approved:
            blockers.append("human approval is required for active HTTPS reobservation")

    executable = not blockers
    state = ReobservationState.READY if executable else ReobservationState.BLOCKED
    return ReobservationDecision(
        request_id=request.request_id,
        state=state,
        executable=executable,
        action_class=action_class,
        blockers=blockers,
        matched_scope_pattern=matched,
        limitations=[
            "A successful observation updates current-state evidence; it does not validate a vulnerability.",
            "Redirects, DNS changes and destination changes must be re-evaluated by SRIC Scope and Policy before execution.",
        ],
    )


def schedule_retry(
    request: ReobservationRequest,
    *,
    now: datetime | None = None,
    base_delay_seconds: int = 60,
    maximum_delay_seconds: int = 86400,
) -> ReobservationRequest:
    if base_delay_seconds < 1 or maximum_delay_seconds < base_delay_seconds:
        raise ValueError("invalid retry delay bounds")
    attempts = request.attempts + 1
    delay = min(maximum_delay_seconds, base_delay_seconds * (2 ** max(0, attempts - 1)))
    reference = now or utcnow()
    state = (
        ReobservationState.FAILED
        if attempts >= request.maximum_attempts
        else ReobservationState.QUEUED
    )
    return request.model_copy(
        update={
            "attempts": attempts,
            "not_before": reference + timedelta(seconds=delay),
            "state": state,
        }
    )


def deduplicate_requests(
    requests: Sequence[ReobservationRequest],
) -> list[ReobservationRequest]:
    selected: dict[str, ReobservationRequest] = {}
    for request in requests:
        key = request.deduplication_key()
        current = selected.get(key)
        if current is None or (request.priority, -request.attempts, request.created_at) > (
            current.priority,
            -current.attempts,
            current.created_at,
        ):
            selected[key] = request
    return sorted(
        selected.values(),
        key=lambda item: (-item.priority, item.created_at, item.request_id),
    )
