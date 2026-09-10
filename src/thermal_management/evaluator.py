"""Thermal state evaluator — realises ARCH_THERMAL_STATE_EVALUATOR."""

from __future__ import annotations

from dataclasses import dataclass

COOL_ON_DC = 350  # 35.0 °C, in tenths of a degree Celsius
COOL_OFF_DC = 300
HEAT_ON_DC = 50
HEAT_OFF_DC = 100
IMBALANCE_LIMIT_DK = 80  # 8.0 K


@dataclass(frozen=True)
class ThermalPicture:
    """The three figures the whole stream is derived from."""

    highest_dc: int
    lowest_dc: int
    spread_dk: int


class ThermalStateEvaluator:
    """Owns the thermal picture, both hysteresis bands and the imbalance verdict."""

    def __init__(self) -> None:
        self._cooling = False
        self._heating = False
        self._imbalance = False
        self._picture: ThermalPicture | None = None

    @property
    def picture(self) -> ThermalPicture | None:
        """``None`` means the thermal picture is unavailable this cycle."""
        return self._picture

    @property
    def cooling_request(self) -> bool:
        return self._cooling

    @property
    def heating_request(self) -> bool:
        return self._heating

    @property
    def imbalance_warning(self) -> bool:
        return self._imbalance

    def cycle(self, temperatures_dc: tuple[tuple[int, bool], ...]) -> ThermalPicture | None:
        """Run one 100 ms cycle over ``(temperature, invalid)`` pairs."""
        picture = self._reduce(temperatures_dc)
        self._picture = picture
        if picture is None:
            return None
        self._cooling = self.update_cooling(picture.highest_dc)
        self._heating = self.update_heating(picture.lowest_dc)
        self._imbalance = self.update_imbalance(picture.spread_dk)
        return picture

    # @Reduce the valid cell temperatures to highest lowest and spread, IMPL_TEMP_EXTREMA, [SWREQ_TEMP_EXTREMA]
    def _reduce(
        self, temperatures_dc: tuple[tuple[int, bool], ...]
    ) -> ThermalPicture | None:
        """Compute the three figures from the samples with a cleared invalid flag.

        A cycle with no valid sample publishes nothing at all rather than a
        default: a fabricated 0 °C would silently trigger the heating band.
        """
        valid = [t for t, invalid in temperatures_dc if not invalid]
        if not valid:
            return None
        highest, lowest = max(valid), min(valid)
        return ThermalPicture(
            highest_dc=highest, lowest_dc=lowest, spread_dk=highest - lowest
        )

    # @Raise the cooling request above 35 C and withdraw it at or below 30 C, IMPL_COOLING_HYSTERESIS, [SWREQ_COOLING_HYSTERESIS]
    def update_cooling(self, highest_dc: int) -> bool:
        """Schmitt-trigger the cooling request across the 35/30 °C band.

        Between the two thresholds the request keeps whatever value it had, which
        is what stops it chattering while the pack sits at the limit.
        """
        if highest_dc > COOL_ON_DC:
            self._cooling = True
        elif highest_dc <= COOL_OFF_DC:
            self._cooling = False
        return self._cooling

    # @Raise the heating request below 5 C and withdraw it at or above 10 C, IMPL_HEATING_HYSTERESIS, [SWREQ_HEATING_HYSTERESIS]
    def update_heating(self, lowest_dc: int) -> bool:
        """Schmitt-trigger the heating request across the 5/10 °C band."""
        if lowest_dc < HEAT_ON_DC:
            self._heating = True
        elif lowest_dc >= HEAT_OFF_DC:
            self._heating = False
        return self._heating

    # KNOWN DEFECT — intentional, see README. The comparison below is `>=` where
    # SWREQ_IMBALANCE_WARNING says the warning is set only when the spread
    # EXCEEDS 8 K, so a spread of exactly 8.0 K raises it. This is a classic
    # boundary error: the code is one operator away from the requirement, the
    # trace gate is fully satisfied, and only the recorded test outcome shows it.
    # TEST_IMBALANCE_WARNING catches it and is RED.
    # @Set the thermal imbalance warning above an 8 K spread, IMPL_IMBALANCE_WARNING, [SWREQ_IMBALANCE_WARNING]
    def update_imbalance(self, spread_dk: int) -> bool:
        """Set or clear the imbalance warning from this cycle's spread alone.

        Deliberately un-hysteresised: this output is a workshop-facing warning,
        not an actuator request, so it should track the measurement directly.
        """
        self._imbalance = spread_dk >= IMBALANCE_LIMIT_DK
        return self._imbalance
