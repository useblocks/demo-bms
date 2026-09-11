"""Pack current path monitor — realises ARCH_CURRENT_PATH_MONITOR."""

from __future__ import annotations

from .types import OVERCURRENT_A, OVERCURRENT_PERSISTENCE_MS

SAMPLE_PERIOD_MS = 1


class CurrentPathMonitor:
    """Debounces the pack current so the supervisor sees a settled condition."""

    def __init__(self) -> None:
        self._above_ms = 0
        self._overcurrent = False

    @property
    def overcurrent(self) -> bool:
        return self._overcurrent

    @property
    def above_threshold_ms(self) -> int:
        return self._above_ms

    # @Report overcurrent only after 100 ms continuously above 350 A, IMPL_OVERCURRENT_DEBOUNCE, [SWREQ_OVERCURRENT_DEBOUNCE]
    def update(self, current_a: float, period_ms: int = SAMPLE_PERIOD_MS) -> bool:
        """Advance the debounce timer with one 1 ms current sample.

        Discharge is positive. Any sample at or below the threshold resets the
        timer, so an acceleration inrush that falls back inside 100 ms never
        reports an overcurrent condition.
        """
        if current_a > OVERCURRENT_A:
            self._above_ms += period_ms
        else:
            self._above_ms = 0
        self._overcurrent = self._above_ms >= OVERCURRENT_PERSISTENCE_MS
        return self._overcurrent
