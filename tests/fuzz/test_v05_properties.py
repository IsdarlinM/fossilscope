from __future__ import annotations

from hypothesis import given, strategies as st

from fossilscope.planning import CurrentExposureState, ReobservationCandidate, plan_reobservation
from fossilscope.reobservation import ReobservationMode


_target = st.from_regex(r"https://[a-z0-9-]{1,16}\.example\.test/[a-z0-9/-]{0,24}", fullmatch=True)
_state = st.sampled_from(list(CurrentExposureState))


@given(st.lists(st.tuples(_target, _state), min_size=1, max_size=30), st.integers(min_value=1, max_value=30))
def test_generated_reobservation_plans_are_passive_and_bounded(
    generated: list[tuple[str, CurrentExposureState]],
    maximum_requests: int,
) -> None:
    candidates = [
        ReobservationCandidate(
            asset_id=f"asset-{index}",
            target=target,
            exposure_state=state,
            age_days=index * 30,
            current_reference=index % 2 == 0,
        )
        for index, (target, state) in enumerate(generated)
    ]
    requests = plan_reobservation(candidates, maximum_requests=maximum_requests)
    assert len(requests) <= maximum_requests
    assert all(request.mode is ReobservationMode.PASSIVE for request in requests)
    assert all("active HTTPS" in " ".join(request.limitations) for request in requests)
