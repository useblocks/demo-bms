"""Capacity fade tracker — realises ARCH_SOH_TRACKER."""

from __future__ import annotations

MIN_ANCHOR_SPREAD_PCT = 40.0


class SohTracker:
    """Reports remaining capacity as a non-increasing percentage of rated."""

    def __init__(self, reported_pct: float = 100.0) -> None:
        self._reported_pct = reported_pct
        self._rejected = 0

    @property
    def reported_pct(self) -> float:
        return self._reported_pct

    @property
    def rejected(self) -> int:
        """How many candidates the monotonic clamp discarded."""
        return self._rejected

    def candidate_from_anchors(
        self,
        soc_low_pct: float,
        soc_high_pct: float,
        counted_as: float,
        rated_capacity_as: float,
    ) -> float | None:
        """Derive a capacity candidate from two OCV rest anchors.

        Anchors closer together than 40 % SOC are refused: over a short span the
        measurement noise of the two anchors dominates the counted charge.
        """
        spread = abs(soc_high_pct - soc_low_pct)
        if spread < MIN_ANCHOR_SPREAD_PCT:
            return None
        measured_capacity_as = abs(counted_as) / (spread / 100.0)
        return measured_capacity_as / rated_capacity_as * 100.0

    # KNOWN DEFECT — intentional, see README. The comparison below is `<=` where
    # SWREQ_CAPACITY_MONOTONIC_CLAMP says a candidate is accepted only when
    # STRICTLY below the reported capacity, so a candidate equal to the reported
    # value is counted as accepted instead of rejected. The reported figure still
    # never increases, which is why this survives a casual read — the rejection
    # count is what disagrees. TEST_CAPACITY_MONOTONIC_CLAMP catches it and is RED.
    # @Discard every capacity candidate above the reported capacity, IMPL_CAPACITY_MONOTONIC_CLAMP, [SWREQ_CAPACITY_MONOTONIC_CLAMP]
    def offer(self, candidate_pct: float) -> float:
        """Accept a candidate only when it is strictly below the reported value.

        A worn pack must never look healthier than it did, so an optimistic
        single measurement is dropped instead of averaged in.
        """
        if candidate_pct <= self._reported_pct:
            self._reported_pct = candidate_pct
        else:
            self._rejected += 1
        return self._reported_pct
