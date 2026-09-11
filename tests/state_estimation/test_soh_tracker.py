"""Verification of the capacity fade tracker."""

from src.state_estimation.soh_tracker import SohTracker


# @A capacity candidate above the reported value is discarded, TEST_CAPACITY_MONOTONIC_CLAMP, [SWREQ_CAPACITY_MONOTONIC_CLAMP]
def test_reported_capacity_never_increases() -> None:
    """An optimistic measurement must not make a worn pack look healthier."""
    tracker = SohTracker()

    assert tracker.offer(98.0) == 98.0
    assert tracker.offer(99.5) == 98.0
    assert tracker.rejected == 1
    assert tracker.offer(95.0) == 95.0
    assert tracker.offer(95.0) == 95.0  # equal is not strictly below
    assert tracker.rejected == 2


# @A long run of candidates forms a non increasing sequence, TEST_CAPACITY_MONOTONIC_SEQUENCE, [SWREQ_CAPACITY_MONOTONIC_CLAMP]
def test_reported_sequence_is_monotonic_under_noise() -> None:
    """Noisy candidates in both directions still yield a non-increasing series."""
    tracker = SohTracker()
    noisy = [99.0, 101.0, 97.5, 98.9, 96.0, 96.4, 94.2]

    reported = [tracker.offer(c) for c in noisy]

    assert reported == sorted(reported, reverse=True)
    assert reported[-1] == 94.2


# @Anchors closer than 40 percent SOC yield no capacity candidate, TEST_CAPACITY_ANCHOR_SPREAD, [SWREQ_CAPACITY_MONOTONIC_CLAMP]
def test_narrow_anchor_spread_is_refused() -> None:
    """Over a short span the anchor noise dominates the counted charge."""
    tracker = SohTracker()

    assert (
        tracker.candidate_from_anchors(
            soc_low_pct=40.0,
            soc_high_pct=60.0,
            counted_as=20_000.0,
            rated_capacity_as=100_000.0,
        )
        is None
    )

    assert tracker.candidate_from_anchors(
        soc_low_pct=20.0,
        soc_high_pct=70.0,
        counted_as=50_000.0,
        rated_capacity_as=100_000.0,
    ) == 100.0
