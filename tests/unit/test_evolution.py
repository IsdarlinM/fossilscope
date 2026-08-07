import hashlib
from datetime import datetime, timedelta, timezone

import pytest

from fossilscope.evolution import (
    ArtifactKind,
    VersionedArtifactObservation,
    diff_artifact_versions,
    find_stale_references,
)
from sric.models import ClaimStatus

T0 = datetime(2025, 1, 1, tzinfo=timezone.utc)


def observation(
    observation_id: str,
    version: str,
    when: datetime,
    *,
    endpoints: list[str] | None = None,
    redirect_uris: list[str] | None = None,
    scopes: list[str] | None = None,
    references: list[str] | None = None,
    historical: bool = True,
    source_group: str | None = None,
    artifact_kind: ArtifactKind = ArtifactKind.SDK,
) -> VersionedArtifactObservation:
    return VersionedArtifactObservation(
        observation_id=observation_id,
        artifact_id="sdk-one",
        artifact_kind=artifact_kind,
        version_label=version,
        observed_at=when,
        content_sha256=hashlib.sha256(observation_id.encode()).hexdigest(),
        endpoints=endpoints or [],
        redirect_uris=redirect_uris or [],
        oauth_scopes=scopes or [],
        references=references or [],
        source_id=f"source-{observation_id}",
        source_group=source_group,
        evidence_ids=[f"E-{observation_id}"],
        historical=historical,
    )


def test_version_diff_reports_api_oauth_and_reference_changes() -> None:
    before = observation(
        "old",
        "1.0.0",
        T0,
        endpoints=["/v1/old", "/v1/stable"],
        redirect_uris=["https://old.example/callback"],
        scopes=["read"],
        references=["legacy.example"],
    )
    after = observation(
        "new",
        "2.0.0",
        T0 + timedelta(days=30),
        endpoints=["/v1/stable", "/v2/new"],
        redirect_uris=["https://new.example/callback"],
        scopes=["read", "write"],
    )
    delta = diff_artifact_versions([after, before])[0]
    assert delta.added_endpoints == ["/v2/new"]
    assert delta.removed_endpoints == ["/v1/old"]
    assert delta.added_scopes == ["write"]
    assert delta.removed_redirect_uris == ["https://old.example/callback"]
    assert delta.status is ClaimStatus.OBSERVED
    assert "not proof of current exposure" in delta.limitations[0]


def test_same_upstream_does_not_count_as_two_independent_sources() -> None:
    before = observation("old", "1.0.0", T0, source_group="provider")
    after = observation("new", "2.0.0", T0 + timedelta(days=1), source_group="provider")
    delta = diff_artifact_versions([before, after])[0]
    assert delta.source_independence_groups == 1


def test_current_artifact_reference_creates_stale_hypothesis() -> None:
    old = observation("old", "1.0.0", T0, endpoints=["https://legacy.example/api"])
    new = observation("new", "2.0.0", T0 + timedelta(days=30))
    current_docs = observation(
        "docs-current",
        "current",
        T0 + timedelta(days=60),
        references=["https://legacy.example/api"],
        historical=False,
    )
    candidate = find_stale_references([old, new, current_docs])[0]
    assert candidate.status is ClaimStatus.HYPOTHESIS
    assert candidate.still_referenced_by_observation_ids == ["docs-current"]
    assert "not proof" in candidate.limitations[0]


def test_removed_value_without_current_reference_remains_unknown() -> None:
    old = observation("old", "1.0.0", T0, endpoints=["/legacy"])
    new = observation("new", "2.0.0", T0 + timedelta(days=30))
    candidate = find_stale_references([old, new])[0]
    assert candidate.status is ClaimStatus.UNKNOWN
    assert candidate.missing_evidence


def test_explicit_empty_delta_set_is_respected() -> None:
    old = observation("old", "1.0.0", T0, endpoints=["/legacy"])
    new = observation("new", "2.0.0", T0 + timedelta(days=30))
    assert find_stale_references([old, new], deltas=[]) == []


def test_same_artifact_id_cannot_change_artifact_kind() -> None:
    old = observation("old", "1.0.0", T0, artifact_kind=ArtifactKind.SDK)
    new = observation(
        "new",
        "2.0.0",
        T0 + timedelta(days=1),
        artifact_kind=ArtifactKind.DOCUMENTATION,
    )
    with pytest.raises(ValueError, match="inconsistent artifact_kind"):
        diff_artifact_versions([old, new])


def test_versioned_observation_requires_evidence_valid_hash_and_aware_time() -> None:
    with pytest.raises(ValueError, match="require evidence_ids"):
        VersionedArtifactObservation(
            observation_id="invalid",
            artifact_id="artifact",
            artifact_kind=ArtifactKind.API_SPEC,
            version_label="1",
            content_sha256=hashlib.sha256(b"x").hexdigest(),
            source_id="source",
        )
    with pytest.raises(ValueError, match="64-character"):
        VersionedArtifactObservation(
            observation_id="invalid",
            artifact_id="artifact",
            artifact_kind=ArtifactKind.API_SPEC,
            version_label="1",
            content_sha256="bad",
            source_id="source",
            evidence_ids=["E-1"],
        )
    with pytest.raises(ValueError, match="timezone-aware"):
        observation("naive", "1", datetime(2026, 1, 1))
