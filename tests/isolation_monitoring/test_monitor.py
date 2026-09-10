"""Verification of the isolation monitor."""

from src.isolation_monitoring.monitor import isolation_fault, isolation_ratio


# @The isolation ratio is resistance over pack voltage and invalid below 50 V, TEST_ISOLATION_RATIO, test, [SWREQ_ISOLATION_RATIO]
def test_ratio_is_resistance_over_voltage_and_invalid_below_fifty_volts() -> None:
    """A 400 kΩ barrier on a 400 V pack is 1000 Ω/V; a de-energised pack has no ratio."""
    ratio = isolation_ratio(resistance_ohm=400_000.0, pack_voltage_v=400.0)
    assert ratio.valid is True
    assert ratio.ohm_per_volt == 1000.0

    assert isolation_ratio(resistance_ohm=400_000.0, pack_voltage_v=49.9).valid is False


# @The isolation fault is set strictly below 500 ohm per volt and only on a valid ratio, TEST_ISOLATION_FAULT_FLAG, test, [SWREQ_ISOLATION_FAULT_FLAG]
def test_fault_is_set_strictly_below_the_limit_on_valid_ratios_only() -> None:
    """Exactly 500 Ω/V is still compliant; an invalid ratio never raises the fault."""
    assert isolation_fault(isolation_ratio(199_999.0, 400.0)) is True  # 499.9975 Ω/V
    assert isolation_fault(isolation_ratio(200_000.0, 400.0)) is False  # exactly 500 Ω/V
    assert isolation_fault(isolation_ratio(1_000.0, 10.0)) is False  # invalid: 10 V pack
