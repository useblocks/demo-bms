"""Verification of the thermal power limit calculator."""

from src.thermal_management.power_limit import PowerLimitCalculator


# @The temperature power share ramps linearly from 55 C to 60 C, TEST_TEMP_DERATE_RAMP, [SWREQ_TEMP_DERATE_RAMP]
def test_derating_ramp_endpoints_and_midpoint() -> None:
    """Full power at 55 °C, zero at 60 °C, exactly half in the middle."""
    calc = PowerLimitCalculator()

    assert calc.temperature_share_pct(500) == 100.0
    assert calc.temperature_share_pct(550) == 100.0
    assert calc.temperature_share_pct(575) == 50.0
    assert calc.temperature_share_pct(600) == 0.0
    assert calc.temperature_share_pct(650) == 0.0


# @The ramp decreases monotonically across the derating band, TEST_TEMP_DERATE_MONOTONIC, [SWREQ_TEMP_DERATE_RAMP]
def test_ramp_is_monotonically_decreasing() -> None:
    """The driver must lose power predictably, never see it rise as it heats up."""
    calc = PowerLimitCalculator()

    shares = [calc.temperature_share_pct(dc) for dc in range(540, 611, 5)]

    assert shares == sorted(shares, reverse=True)


# @The published limit is the minimum of both derating causes, TEST_LIMIT_MINIMUM, [SWREQ_LIMIT_MINIMUM]
def test_published_limit_takes_the_minimum() -> None:
    """Either cause alone is enough to cap the power; they never cancel out."""
    calc = PowerLimitCalculator()

    assert calc.publish(highest_dc=550, unconfirmed=True) == 30.0
    assert calc.publish(highest_dc=575, unconfirmed=False) == 50.0
    assert calc.publish(highest_dc=575, unconfirmed=True) == 30.0
    assert calc.publish(highest_dc=600, unconfirmed=True) == 0.0
    assert calc.publish(highest_dc=500, unconfirmed=False) == 100.0


# @The actuator fallback share is flat at 30 percent while unconfirmed, TEST_LIMIT_ACTUATOR_SHARE, [SWREQ_LIMIT_MINIMUM]
def test_actuator_share_is_flat_and_conditional() -> None:
    """The fallback does not depend on temperature, only on the confirmation."""
    calc = PowerLimitCalculator()

    assert calc.actuator_share_pct(unconfirmed=True) == 30.0
    assert calc.actuator_share_pct(unconfirmed=False) == 100.0
