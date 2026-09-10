"""Verification of the thermal state evaluator."""

from src.thermal_management.evaluator import ThermalStateEvaluator


# @The thermal picture is reduced from the valid cell temperatures only, TEST_TEMP_EXTREMA, [SWREQ_TEMP_EXTREMA]
def test_extrema_and_spread_ignore_invalid_samples() -> None:
    """An implausible 90 °C reading must not become the pack's highest temperature."""
    evaluator = ThermalStateEvaluator()

    picture = evaluator.cycle(((250, False), (300, False), (900, True)))

    assert picture is not None
    assert picture.highest_dc == 300
    assert picture.lowest_dc == 250
    assert picture.spread_dk == 50


# @A cycle without any valid temperature publishes no thermal picture, TEST_TEMP_EXTREMA_UNAVAILABLE, [SWREQ_TEMP_EXTREMA]
def test_fully_invalid_cycle_reports_unavailable() -> None:
    """A fabricated 0 °C default would silently trigger the heating band."""
    evaluator = ThermalStateEvaluator()

    assert evaluator.cycle(((250, True), (300, True))) is None
    assert evaluator.picture is None


# @The cooling request follows the 35 over 30 C hysteresis band, TEST_COOLING_HYSTERESIS, [SWREQ_COOLING_HYSTERESIS]
def test_cooling_request_holds_inside_the_band() -> None:
    """Set above 35 °C, held between the thresholds, cleared at or below 30 °C."""
    evaluator = ThermalStateEvaluator()

    assert evaluator.update_cooling(340) is False
    assert evaluator.update_cooling(360) is True
    assert evaluator.update_cooling(320) is True  # inside the band: unchanged
    assert evaluator.update_cooling(300) is False
    assert evaluator.update_cooling(320) is False  # inside the band: still unchanged


# @The heating request follows the 5 under 10 C hysteresis band, TEST_HEATING_HYSTERESIS, [SWREQ_HEATING_HYSTERESIS]
def test_heating_request_holds_inside_the_band() -> None:
    """Set below 5 °C, held between the thresholds, cleared at or above 10 °C."""
    evaluator = ThermalStateEvaluator()

    assert evaluator.update_heating(60) is False
    assert evaluator.update_heating(40) is True
    assert evaluator.update_heating(80) is True  # inside the band: unchanged
    assert evaluator.update_heating(100) is False
    assert evaluator.update_heating(80) is False  # inside the band: still unchanged


# @The imbalance warning tracks the spread above 8 K, TEST_IMBALANCE_WARNING, [SWREQ_IMBALANCE_WARNING]
def test_imbalance_warning_tracks_the_spread_directly() -> None:
    """A workshop-facing warning follows the measurement without hysteresis."""
    evaluator = ThermalStateEvaluator()

    assert evaluator.update_imbalance(80) is False  # exactly 8.0 K is inside
    assert evaluator.update_imbalance(81) is True
    assert evaluator.update_imbalance(79) is False


# @A full cycle derives both requests and the warning together, TEST_THERMAL_CYCLE, [SWREQ_TEMP_EXTREMA]
def test_cycle_drives_every_output() -> None:
    """One cycle over a hot, badly spread pack sets cooling and the warning."""
    evaluator = ThermalStateEvaluator()

    evaluator.cycle(((240, False), (400, False)))

    assert evaluator.cooling_request is True
    assert evaluator.heating_request is False
    assert evaluator.imbalance_warning is True
