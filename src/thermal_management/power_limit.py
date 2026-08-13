"""Thermal power limit calculator — realises ARCH_POWER_LIMIT_CALCULATOR."""

from __future__ import annotations

DERATE_START_DC = 550  # 55.0 °C
DERATE_END_DC = 600  # 60.0 °C
ACTUATOR_FALLBACK_SHARE_PCT = 30.0


class PowerLimitCalculator:
    """Publishes the permitted discharge power the vehicle sees."""

    def __init__(self) -> None:
        self._published_pct = 100.0

    @property
    def published_pct(self) -> float:
        return self._published_pct

    # @Ramp the temperature-driven power share from 100 percent at 55 C to zero at 60 C, IMPL_TEMP_DERATE_RAMP, impl, [SWREQ_TEMP_DERATE_RAMP]
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

    # @Publish the minimum of the temperature and actuator power shares, IMPL_LIMIT_MINIMUM, impl, [SWREQ_LIMIT_MINIMUM]
    def publish(self, highest_dc: int, unconfirmed: bool) -> float:
        """Combine both independent causes of derating by taking the minimum.

        Taking the minimum, not a product or an average, is what stops the two
        causes from cancelling each other out — either alone is enough to cap the
        power.
        """
        self._published_pct = min(
            self.temperature_share_pct(highest_dc),
            self.actuator_share_pct(unconfirmed),
        )
        return self._published_pct
