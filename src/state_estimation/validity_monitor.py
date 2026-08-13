"""Estimation validity monitor — realises ARCH_ESTIMATION_VALIDITY_MONITOR."""

from __future__ import annotations

STALENESS_LIMIT_S = 5.0


class ValidityMonitor:
    """A pure observer: it qualifies the estimate, it never modifies it."""

    def __init__(self) -> None:
        self._staleness_s = 0.0
        self._unreliable = False

    @property
    def unreliable(self) -> bool:
        return self._unreliable

    @property
    def staleness_s(self) -> float:
        return self._staleness_s

    # @Raise the unreliable verdict after 5 s without a valid current sample, IMPL_CURRENT_STALENESS_TIMER, impl, [SWREQ_CURRENT_STALENESS_TIMER]
    def tick(self, dt_s: float, current_sample_valid: bool) -> bool:
        """Advance the staleness timer and latch the unreliable verdict.

        The verdict latches on purpose: once counting has drifted for 5 seconds
        the estimate cannot be trusted again until an absolute anchor is taken,
        so returning samples alone must not clear it.
        """
        if current_sample_valid:
            self._staleness_s = 0.0
        else:
            self._staleness_s += dt_s
        if self._staleness_s > STALENESS_LIMIT_S:
            self._unreliable = True
        return self._unreliable

    def correction_completed(self) -> bool:
        """The only thing that clears the verdict: a completed OCV correction."""
        self._unreliable = False
        self._staleness_s = 0.0
        return self._unreliable
