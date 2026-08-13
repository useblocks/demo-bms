"""Verification of the coulomb counter."""

from src.state_estimation.coulomb_counter import CoulombCounter


# @Charge is integrated trapezoidally on every 10 ms tick, TEST_CHARGE_INTEGRATION, test, [SWREQ_CHARGE_INTEGRATION]
def test_trapezoidal_integration_over_three_ticks() -> None:
    """Each tick adds the mean of this and the previous sample times the period."""
    counter = CoulombCounter()

    assert counter.tick(0.0) == 0.0  # first tick has no predecessor
    assert counter.tick(10.0) == 0.05  # (0 + 10) / 2 * 0.01
    assert round(counter.tick(10.0), 6) == 0.15  # + (10 + 10) / 2 * 0.01


# @A ramping current integrates to the exact trapezoid area, TEST_CHARGE_INTEGRATION_RAMP, test, [SWREQ_CHARGE_INTEGRATION]
def test_linear_ramp_matches_the_analytic_area() -> None:
    """A linear ramp is the case trapezoidal integration is exact for."""
    counter = CoulombCounter()
    counter.tick(0.0)
    for step in range(1, 101):
        counter.tick(float(step))

    # Area under i(t) = t over 100 ticks of 0.01 s: 0.5 * 100 * (100 * 0.01)
    assert round(counter.accumulated_as, 6) == round(0.5 * 100 * 1.0, 6)


# @Throughput accumulates the absolute charge in both directions, TEST_CHARGE_THROUGHPUT, test, [SWREQ_CHARGE_INTEGRATION]
def test_throughput_counts_charge_and_discharge_alike() -> None:
    """The net integral cancels out; the throughput must not."""
    counter = CoulombCounter()
    counter.tick(10.0)
    counter.tick(10.0)
    counter.tick(-10.0)
    counter.tick(-10.0)

    assert round(counter.accumulated_as, 6) == 0.0
    assert counter.throughput_as > 0.0

    counter.reset_throughput()
    assert counter.throughput_as == 0.0
