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


# @The sustained-load share draws 200 A while the 10 s average current is at or above 200 A, TEST_SUSTAINED_LOAD_LIMIT, [SWREQ_SUSTAINED_LOAD_LIMIT]
def test_sustained_load_share_holds_the_current_at_the_limit() -> None:
    """Full power below a 200 A average; at or above it the share draws 200 A."""
    calc = PowerLimitCalculator()

    # Just below the limit, full power stays available for a short peak.
    calc.observe_current(199.0, 0)
    assert calc.sustained_load_share_pct() == 100.0

    # At the limit, the share is 200 A of the 320 A full power draws.
    calc.observe_current(201.0, 1000)
    assert calc.sustained_load_share_pct() == 62.5

    # Above the limit, the share stays at 200 A of 320 A.
    calc.observe_current(320.0, 2000)
    assert calc.sustained_load_share_pct() == 62.5

    # A peak older than 10 s leaves the trailing average.
    windowed = PowerLimitCalculator()
    windowed.observe_current(1000.0, 0)
    windowed.observe_current(100.0, 1000)
    windowed.observe_current(100.0, 11000)
    assert windowed.sustained_load_share_pct() == 100.0

    # A sustained full-power demand settles at 200 A instead of above it.
    held = PowerLimitCalculator()
    currents: list[float] = []
    for tick in range(600):
        currents.append(held.sustained_load_share_pct() / 100.0 * 320.0)
        held.observe_current(currents[-1], tick * 100)
    assert currents[-101:] == [200.0] * 101
