"""Verification of the open-circuit-voltage corrector."""

from src.state_estimation.ocv_corrector import OCV_TABLE, OcvCorrector, soc_from_ocv


# @A rest condition needs 30 continuous minutes below 1 A, TEST_REST_DETECTION, [SWREQ_REST_DETECTION]
def test_rest_requires_the_full_thirty_minutes() -> None:
    """29 minutes 59 seconds is not a rest condition; 30 minutes is."""
    corrector = OcvCorrector(rated_capacity_as=100_000.0)

    assert corrector.update_rest(0.5, dt_s=1799.0) is False
    assert corrector.update_rest(0.5, dt_s=1.0) is True
    assert corrector.at_rest is True


# @A load in the middle of the rest window restarts the timer, TEST_REST_DETECTION_RESET, [SWREQ_REST_DETECTION]
def test_load_during_rest_resets_the_timer() -> None:
    """The 30 minutes must be continuous, not cumulative."""
    corrector = OcvCorrector(rated_capacity_as=100_000.0)
    corrector.update_rest(0.5, dt_s=1700.0)

    corrector.update_rest(5.0, dt_s=1.0)
    assert corrector.rest_timer_s == 0.0

    assert corrector.update_rest(0.5, dt_s=1700.0) is False


# @The SOC is interpolated linearly between two OCV table points, TEST_OCV_TABLE_LOOKUP, [SWREQ_OCV_TABLE_LOOKUP]
def test_linear_interpolation_between_table_points() -> None:
    """A voltage halfway between two points yields the halfway state of charge."""
    assert soc_from_ocv(3680) == 50.0
    assert soc_from_ocv(3700) == 55.0
    assert soc_from_ocv(3690) == 52.5


# @Voltages outside the OCV table clamp to its ends, TEST_OCV_TABLE_CLAMP, [SWREQ_OCV_TABLE_LOOKUP]
def test_out_of_table_voltages_clamp_instead_of_extrapolating() -> None:
    """Past the table the curve is too flat for a linear guess to mean anything."""
    assert soc_from_ocv(2000) == 0.0
    assert soc_from_ocv(5000) == 100.0
    assert len(OCV_TABLE) == 21


# @A completed correction replaces the anchor of the fused estimate, TEST_OCV_CORRECTION_ANCHOR, [SWREQ_OCV_TABLE_LOOKUP]
def test_correction_moves_the_fused_estimate_anchor() -> None:
    """The counted delta is added to the corrected anchor, not to the old one."""
    corrector = OcvCorrector(rated_capacity_as=100_000.0, anchor_soc=20.0)

    assert corrector.correct(3680) == 50.0
    assert corrector.corrections == 1
    assert corrector.fused_soc(counted_delta_as=10_000.0) == 60.0
