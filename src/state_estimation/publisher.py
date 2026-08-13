"""Battery state publisher — realises ARCH_STATE_PUBLISHER."""

from __future__ import annotations

from dataclasses import dataclass

FRAME_PERIOD_MS = 100
FRAME_TOLERANCE_MS = 10


@dataclass(frozen=True)
class BatteryStateFrame:
    """The vehicle-facing frame this component owns."""

    soc_pct: float
    capacity_pct: float
    unreliable: bool
    timestamp_ms: int


class StatePublisher:
    """Sends the battery state frame on its own cycle, independent of producers."""

    def __init__(self) -> None:
        self._soc_pct = 0.0
        self._capacity_pct = 100.0
        self._unreliable = True
        self._last_sent_ms: int | None = None
        self.sent: list[BatteryStateFrame] = []

    def update(
        self,
        soc_pct: float | None = None,
        capacity_pct: float | None = None,
        unreliable: bool | None = None,
    ) -> None:
        """Take whatever a producer offers; none of it is mandatory per cycle."""
        if soc_pct is not None:
            self._soc_pct = soc_pct
        if capacity_pct is not None:
            self._capacity_pct = capacity_pct
        if unreliable is not None:
            self._unreliable = unreliable

    # @Send the battery state frame every 100 ms regardless of producer updates, IMPL_STATE_FRAME_PERIOD, impl, [SWREQ_STATE_FRAME_PERIOD]
    def cycle(self, now_ms: int) -> BatteryStateFrame | None:
        """Send a frame when one is due, repeating the last held values.

        Repeating a stale value rather than skipping the frame is what decouples
        the publication period from estimator run time: the bus sees a fixed
        cadence even when a producer misses a cycle.
        """
        if self._last_sent_ms is not None and now_ms - self._last_sent_ms < FRAME_PERIOD_MS:
            return None
        frame = BatteryStateFrame(
            soc_pct=self._soc_pct,
            capacity_pct=self._capacity_pct,
            unreliable=self._unreliable,
            timestamp_ms=now_ms,
        )
        self._last_sent_ms = now_ms
        self.sent.append(frame)
        return frame
