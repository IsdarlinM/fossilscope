from datetime import datetime, timedelta, timezone

import pytest

from fossilscope.reobservation import (
    ReobservationMode,
    ReobservationReason,
    ReobservationRequest,
    ReobservationState,
    deduplicate_requests,
    evaluate_reobservation,
    schedule_retry,
)


NOW = datetime(2026, 8, 6, tzinfo=timezone.utc)


def request(
    request_id: str,
    *,
    mode: ReobservationMode = ReobservationMode.PASSIVE,
    target: str = "api.example.test",
    priority: int = 50,
) -> ReobservationRequest:
    return ReobservationRequest(
        request_id=request_id,
        asset_id="asset-1",
        target=target,
        reason=ReobservationReason.CURRENT_STATE_UNKNOWN,
        mode=mode,
        source_evidence_ids=["E-1"],
        priority=priority,
        created_at=NOW,
    )


def test_passive_reobservation_is_ready_without_network_approval() -> None:
    decision = evaluate_reobservation(request("R-1"), now=NOW)

    assert decision.executable is True
    assert decision.state is ReobservationState.READY
    assert decision.action_class == "READ_ONLY_SAFE"


def test_active_https_requires_scope_terms_and_approval() -> None:
    value = request(
        "R-2",
        mode=ReobservationMode.ACTIVE_HTTPS,
        target="https://api.example.test/status",
    )
    decision = evaluate_reobservation(value, now=NOW)

    assert decision.executable is False
    assert len(decision.blockers) == 3


def test_active_https_becomes_ready_when_all_gates_are_present() -> None:
    value = request(
        "R-3",
        mode=ReobservationMode.ACTIVE_HTTPS,
        target="https://api.example.test/status",
    )
    value.allow_patterns = ["*.example.test"]
    value.terms_acknowledged = True
    value.human_approved = True

    decision = evaluate_reobservation(value, now=NOW)

    assert decision.executable is True
    assert decision.matched_scope_pattern == "*.example.test"
    assert decision.action_class == "READ_ONLY_SENSITIVE"


def test_active_mode_rejects_non_https_targets() -> None:
    with pytest.raises(ValueError, match="requires an HTTPS target"):
        request(
            "R-4",
            mode=ReobservationMode.ACTIVE_HTTPS,
            target="http://api.example.test",
        )


def test_backoff_blocks_until_elapsed() -> None:
    value = request("R-5")
    value.not_before = NOW + timedelta(minutes=5)

    decision = evaluate_reobservation(value, now=NOW)

    assert decision.executable is False
    assert "backoff window" in decision.blockers[0]


def test_retry_is_exponential_and_fails_at_attempt_limit() -> None:
    value = request("R-6")
    value.maximum_attempts = 2
    first = schedule_retry(value, now=NOW, base_delay_seconds=10)
    second = schedule_retry(first, now=NOW, base_delay_seconds=10)

    assert first.not_before == NOW + timedelta(seconds=10)
    assert first.state is ReobservationState.QUEUED
    assert second.not_before == NOW + timedelta(seconds=20)
    assert second.state is ReobservationState.FAILED


def test_duplicate_requests_keep_highest_priority_candidate() -> None:
    low = request("LOW", priority=20)
    high = request("HIGH", priority=80)

    selected = deduplicate_requests([low, high])

    assert [item.request_id for item in selected] == ["HIGH"]


def test_completed_request_cannot_execute_again() -> None:
    value = request("R-7")
    value.state = ReobservationState.COMPLETED

    decision = evaluate_reobservation(value, now=NOW)

    assert decision.executable is False
    assert "already COMPLETED" in decision.blockers[0]
