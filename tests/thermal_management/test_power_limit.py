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


# @The published limit is the minimum of all three derating causes, TEST_LIMIT_MINIMUM, [SWREQ_LIMIT_MINIMUM]
def test_published_limit_takes_the_minimum() -> None:
    """Any one cause alone is enough to cap the power; they never cancel out."""
    calc = PowerLimitCalculator()

    assert calc.publish(highest_dc=550, unconfirmed=True) == 30.0
    assert calc.publish(highest_dc=575, unconfirmed=False) == 50.0
    assert calc.publish(highest_dc=575, unconfirmed=True) == 30.0
    assert calc.publish(highest_dc=600, unconfirmed=True) == 0.0
    assert calc.publish(highest_dc=500, unconfirmed=False) == 100.0

    # The sustained-load share can be the smallest of the three and so bind...
    assert (
        calc.publish(highest_dc=500, unconfirmed=False, sustained_load_pct=40.0) == 40.0
    )
    # ...or sit above a smaller temperature or actuator share and not bind.
    assert (
        calc.publish(highest_dc=575, unconfirmed=False, sustained_load_pct=80.0) == 50.0
    )
    assert (
        calc.publish(highest_dc=550, unconfirmed=True, sustained_load_pct=70.0) == 30.0
    )


# @The actuator fallback share is flat at 30 percent while unconfirmed, TEST_LIMIT_ACTUATOR_SHARE, [SWREQ_LIMIT_MINIMUM]
def test_actuator_share_is_flat_and_conditional() -> None:
    """The fallback does not depend on temperature, only on the confirmation."""
    calc = PowerLimitCalculator()

    assert calc.actuator_share_pct(unconfirmed=True) == 30.0
    assert calc.actuator_share_pct(unconfirmed=False) == 100.0


# @The sustained-load share holds the 10 s average current at or below 250 A, TEST_SUSTAINED_LOAD_LIMIT, [SWREQ_SUSTAINED_LOAD_LIMIT]
def test_sustained_load_share_holds_the_average_at_the_limit() -> None:
    """Only the trailing 10 s counts, and an average of 250 A needs no derating."""
    calc = PowerLimitCalculator()

    # A sustained current at the limit needs no derating.
    calc.observe_current(250.0, 0)
    assert calc.sustained_load_share_pct() == 100.0

    # Above the limit, the share scales the trailing average back to 250 A.
    calc.observe_current(750.0, 1000)
    assert calc.sustained_load_share_pct() == 50.0

    # A peak older than 10 s leaves the trailing average.
    windowed = PowerLimitCalculator()
    windowed.observe_current(1000.0, 0)
    windowed.observe_current(100.0, 1000)
    windowed.observe_current(100.0, 11000)
    assert windowed.sustained_load_share_pct() == 100.0
