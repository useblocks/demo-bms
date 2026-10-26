"""Thermal power limit calculator — realises ARCH_POWER_LIMIT_CALCULATOR."""

from __future__ import annotations

from collections import deque

DERATE_START_DC = 550  # 55.0 °C
DERATE_END_DC = 600  # 60.0 °C
ACTUATOR_FALLBACK_SHARE_PCT = 30.0
CONTINUOUS_DISCHARGE_LIMIT_A = 250.0
AVERAGING_WINDOW_S = 10.0


class PowerLimitCalculator:
    """Publishes the permitted discharge power the vehicle sees."""

    def __init__(self) -> None:
        self._published_pct = 100.0
        self._current_samples: deque[tuple[int, float]] = deque()

    @property
    def published_pct(self) -> float:
        return self._published_pct

    # @Ramp the temperature-driven power share from 100 percent at 55 C to zero at 60 C, IMPL_TEMP_DERATE_RAMP, [SWREQ_TEMP_DERATE_RAMP]
    def temperature_share_pct(self, highest_dc: int) -> float:
        """The linear derating ramp over the 55–60 °C band.

        A ramp rather than a single cut-off is the point: the driver loses power
        predictably instead of the pack dropping out without warning.
        """
        if highest_dc <= DERATE_START_DC:
            return 100.0
        if highest_dc >= DERATE_END_DC:
            return 0.0
        span = DERATE_END_DC - DERATE_START_DC
        return 100.0 * (DERATE_END_DC - highest_dc) / span

    def actuator_share_pct(self, unconfirmed: bool) -> float:
        """The flat fallback share while the actuator has not confirmed."""
        return ACTUATOR_FALLBACK_SHARE_PCT if unconfirmed else 100.0

    def observe_current(self, current_a: float, timestamp_ms: int) -> None:
        """Record one pack discharge current sample for the sustained-load average.

        Samples older than the averaging window are dropped, so the average always
        covers the trailing 10 s. A short peak is averaged with the rest of the
        window, which keeps a brief burst of drive power available.
        """
        self._current_samples.append((timestamp_ms, current_a))
        cutoff_ms = timestamp_ms - int(AVERAGING_WINDOW_S * 1000)
        while self._current_samples and self._current_samples[0][0] < cutoff_ms:
            self._current_samples.popleft()

    # @Compute the sustained-load share that holds the 10 s average current at or below 250 A, IMPL_SUSTAINED_LOAD_LIMIT, [SWREQ_SUSTAINED_LOAD_LIMIT]
    def sustained_load_share_pct(self) -> float:
        """The share that holds the 10 s average pack current at the limit.

        A sustained current at or below the continuous discharge limit needs no
        derating, so the share is 100 %; above it the share is the fraction that
        scales the average back to the limit.
        """
        if not self._current_samples:
            return 100.0
        average_a = sum(current for _, current in self._current_samples) / len(
            self._current_samples
        )
        if average_a <= CONTINUOUS_DISCHARGE_LIMIT_A:
            return 100.0
        return CONTINUOUS_DISCHARGE_LIMIT_A / average_a * 100.0

    # @Publish the minimum of the temperature actuator and sustained-load power shares, IMPL_LIMIT_MINIMUM, [SWREQ_LIMIT_MINIMUM]
    def publish(
        self,
        highest_dc: int,
        unconfirmed: bool,
        sustained_load_pct: float = 100.0,
    ) -> float:
        """Combine the three independent causes of derating by taking the minimum.

        Taking the minimum, not a product or an average, is what stops the three
        causes from cancelling each other out — any one alone is enough to cap
        the power. The sustained-load share is passed in rather than computed
        here.
        """
        self._published_pct = min(
            self.temperature_share_pct(highest_dc),
            self.actuator_share_pct(unconfirmed),
            sustained_load_pct,
        )
        return self._published_pct
