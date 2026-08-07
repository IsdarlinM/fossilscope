from fossilscope.lifecycle import (
    EvidenceKind,
    ExposureLifecycle,
    SurfaceEvidence,
    assess_lifecycle,
)
from sric.models import ClaimStatus


def evidence(
    evidence_id: str,
    kind: EvidenceKind,
    *,
    asset: str = "api.example.test",
    source: str | None = None,
    group: str | None = None,
    direct: bool = False,
    **controls: bool,
) -> SurfaceEvidence:
    return SurfaceEvidence(
        evidence_id=evidence_id,
        asset_id=asset,
        kind=kind,
        source_id=source or evidence_id,
        source_group=group,
        direct_observation=direct,
        **controls,
    )


def test_historical_reference_does_not_prove_current_exposure() -> None:
    result = assess_lifecycle(
        [evidence("H-1", EvidenceKind.HISTORICAL_REFERENCE)]
    )[0]

    assert result.lifecycle is ExposureLifecycle.HISTORICAL_ONLY
    assert result.status is ClaimStatus.OBSERVED
    assert result.resurrection_candidate is False
    assert "current application response" in result.missing_evidence


def test_dns_only_does_not_prove_application_reachability() -> None:
    result = assess_lifecycle(
        [
            evidence("H-1", EvidenceKind.HISTORICAL_REFERENCE),
            evidence("D-1", EvidenceKind.CURRENT_DNS, direct=True),
        ]
    )[0]

    assert result.lifecycle is ExposureLifecycle.CURRENT_DNS
    assert result.resurrection_candidate is False
    assert "current TLS or HTTP evidence" in result.missing_evidence


def test_wildcard_dns_forces_unknown_current_state() -> None:
    result = assess_lifecycle(
        [
            evidence("H-1", EvidenceKind.HISTORICAL_REFERENCE),
            evidence(
                "D-1",
                EvidenceKind.CURRENT_DNS,
                direct=True,
                wildcard_dns=True,
            ),
        ]
    )[0]

    assert result.lifecycle is ExposureLifecycle.UNKNOWN_CURRENT_STATE
    assert result.status is ClaimStatus.UNKNOWN
    assert "wildcard DNS" in result.controls_triggered


def test_direct_http_can_only_create_resurrection_hypothesis() -> None:
    result = assess_lifecycle(
        [
            evidence("H-1", EvidenceKind.HISTORICAL_REFERENCE),
            evidence("HTTP-1", EvidenceKind.CURRENT_HTTP, direct=True),
        ]
    )[0]

    assert result.lifecycle is ExposureLifecycle.CURRENT_HTTP
    assert result.resurrection_candidate is True
    assert result.status is ClaimStatus.HYPOTHESIS
    assert result.confidence <= 0.79


def test_parking_and_transfer_disqualify_resurrection() -> None:
    parked = assess_lifecycle(
        [
            evidence("H-1", EvidenceKind.HISTORICAL_REFERENCE),
            evidence(
                "HTTP-1",
                EvidenceKind.CURRENT_HTTP,
                direct=True,
                parked=True,
            ),
        ]
    )[0]
    transferred = assess_lifecycle(
        [
            evidence("H-2", EvidenceKind.HISTORICAL_REFERENCE, asset="old.test"),
            evidence(
                "T-1",
                EvidenceKind.TRANSFER_RECORD,
                asset="old.test",
                transferred=True,
            ),
        ]
    )[0]

    assert parked.lifecycle is ExposureLifecycle.PARKED
    assert parked.resurrection_candidate is False
    assert transferred.lifecycle is ExposureLifecycle.TRANSFERRED
    assert transferred.resurrection_candidate is False


def test_duplicate_upstream_sources_are_reported() -> None:
    result = assess_lifecycle(
        [
            evidence(
                "D-1",
                EvidenceKind.CURRENT_DNS,
                source="feed-a",
                group="same-upstream",
                direct=True,
            ),
            evidence(
                "D-2",
                EvidenceKind.CURRENT_DNS,
                source="feed-b",
                group="same-upstream",
                direct=True,
            ),
        ]
    )[0]

    assert result.independent_source_groups == 1
    assert result.duplicate_source_groups == ["same-upstream"]


def test_assets_are_assessed_independently() -> None:
    results = assess_lifecycle(
        [
            evidence("H-1", EvidenceKind.HISTORICAL_REFERENCE, asset="one.test"),
            evidence("D-2", EvidenceKind.CURRENT_DNS, asset="two.test", direct=True),
        ]
    )

    assert [result.asset_id for result in results] == ["one.test", "two.test"]
