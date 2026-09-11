"""Verification of the estimation validity monitor."""

from src.state_estimation.validity_monitor import ValidityMonitor


# @The unreliable verdict is raised after 5 s without a valid current sample, TEST_CURRENT_STALENESS_TIMER, [SWREQ_CURRENT_STALENESS_TIMER]
def test_verdict_is_raised_only_past_five_seconds() -> None:
    """Exactly 5 s is still inside the budget; anything beyond it is not."""
    monitor = ValidityMonitor()

    for _ in range(5):
        assert monitor.tick(1.0, current_sample_valid=False) is False
    assert monitor.staleness_s == 5.0

    assert monitor.tick(0.1, current_sample_valid=False) is True
    assert monitor.unreliable is True


# @A valid sample resets the staleness timer before the limit, TEST_CURRENT_STALENESS_RESET, [SWREQ_CURRENT_STALENESS_TIMER]
def test_a_valid_sample_resets_the_timer() -> None:
    """Intermittent gaps below the limit must not raise the verdict."""
    monitor = ValidityMonitor()

    monitor.tick(4.0, current_sample_valid=False)
    monitor.tick(0.1, current_sample_valid=True)
    assert monitor.staleness_s == 0.0

    assert monitor.tick(4.0, current_sample_valid=False) is False


# @Only a completed OCV correction clears the unreliable verdict, TEST_CURRENT_STALENESS_LATCH, [SWREQ_CURRENT_STALENESS_TIMER]
def test_returning_samples_do_not_clear_the_verdict() -> None:
    """Once counting has drifted, only an absolute anchor restores trust."""
    monitor = ValidityMonitor()
    monitor.tick(6.0, current_sample_valid=False)
    assert monitor.unreliable is True

    for _ in range(100):
        monitor.tick(0.1, current_sample_valid=True)
    assert monitor.unreliable is True

    assert monitor.correction_completed() is False
    assert monitor.unreliable is False
