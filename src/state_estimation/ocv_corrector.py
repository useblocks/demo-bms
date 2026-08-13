"""Open-circuit-voltage corrector — realises ARCH_OCV_CORRECTOR."""

from __future__ import annotations

REST_CURRENT_THRESHOLD_A = 1.0
REST_DURATION_S = 1800.0

#: The 21-point open-circuit-voltage table: (mean cell voltage in mV, SOC in %).
OCV_TABLE: tuple[tuple[int, float], ...] = (
    (3000, 0.0),
    (3350, 5.0),
    (3450, 10.0),
    (3510, 15.0),
    (3550, 20.0),
    (3580, 25.0),
    (3600, 30.0),
    (3620, 35.0),
    (3640, 40.0),
    (3660, 45.0),
    (3680, 50.0),
    (3700, 55.0),
    (3730, 60.0),
    (3770, 65.0),
    (3810, 70.0),
    (3860, 75.0),
    (3910, 80.0),
    (3970, 85.0),
    (4030, 90.0),
    (4110, 95.0),
    (4200, 100.0),
)


class OcvCorrector:
    """Owns the absolute SOC anchor and the fused estimate that is published."""

    def __init__(self, rated_capacity_as: float, anchor_soc: float = 50.0) -> None:
        self._rated_capacity_as = rated_capacity_as
        self._anchor_soc = anchor_soc
        self._rest_timer_s = 0.0
        self._at_rest = False
        self._corrections = 0

    @property
    def at_rest(self) -> bool:
        return self._at_rest

    @property
    def rest_timer_s(self) -> float:
        return self._rest_timer_s

    @property
    def corrections(self) -> int:
        return self._corrections

    # @Report a rest condition after 30 minutes below 1 A absolute current, IMPL_REST_DETECTION, impl, [SWREQ_REST_DETECTION]
    def update_rest(self, current_a: float, dt_s: float) -> bool:
        """Advance the rest timer by one tick and report the rest condition.

        Any tick at or above the threshold resets the timer to zero, so the
        30 minutes must be continuous — a brief load in the middle restarts it.
        """
        if abs(current_a) < REST_CURRENT_THRESHOLD_A:
            self._rest_timer_s += dt_s
        else:
            self._rest_timer_s = 0.0
        self._at_rest = self._rest_timer_s >= REST_DURATION_S
        return self._at_rest

    def correct(self, mean_cell_voltage_mv: float) -> float:
        """Replace the anchor with the value the settled cell voltage implies."""
        self._anchor_soc = soc_from_ocv(mean_cell_voltage_mv)
        self._corrections += 1
        return self._anchor_soc

    def fused_soc(self, counted_delta_as: float) -> float:
        """The published estimate: the anchor plus the counter's delta."""
        delta_pct = counted_delta_as / self._rated_capacity_as * 100.0
        return max(0.0, min(100.0, self._anchor_soc + delta_pct))


# @Interpolate the SOC linearly in the 21-point OCV table, IMPL_OCV_TABLE_LOOKUP, impl, [SWREQ_OCV_TABLE_LOOKUP]
def soc_from_ocv(mean_cell_voltage_mv: float) -> float:
    """Map a settled mean cell voltage to a state of charge in percent.

    Voltages outside the table clamp to its ends rather than extrapolating: past
    the table the curve is too flat for a linear guess to mean anything.
    """
    if mean_cell_voltage_mv <= OCV_TABLE[0][0]:
        return 0.0
    if mean_cell_voltage_mv >= OCV_TABLE[-1][0]:
        return 100.0
    for (v_low, soc_low), (v_high, soc_high) in zip(OCV_TABLE, OCV_TABLE[1:]):
        if v_low <= mean_cell_voltage_mv <= v_high:
            span = v_high - v_low
            share = (mean_cell_voltage_mv - v_low) / span
            return soc_low + share * (soc_high - soc_low)
    raise AssertionError("OCV table is not monotonic")
