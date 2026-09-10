"""Verification of the pack current path monitor."""

from src.cell_protection.current_monitor import CurrentPathMonitor


# @Overcurrent is reported only after 100 ms continuously above 350 A, TEST_OVERCURRENT_DEBOUNCE, [SWREQ_OVERCURRENT_DEBOUNCE]
def test_overcurrent_needs_the_full_persistence_window() -> None:
    """99 ms above the limit is not enough; the 100th millisecond is."""
    monitor = CurrentPathMonitor()

    for _ in range(99):
        assert monitor.update(400.0) is False
    assert monitor.above_threshold_ms == 99

    assert monitor.update(400.0) is True
    assert monitor.overcurrent is True


# @An inrush falling back inside 100 ms resets the overcurrent timer, TEST_OVERCURRENT_INRUSH_RESET, [SWREQ_OVERCURRENT_DEBOUNCE]
def test_short_inrush_does_not_trip() -> None:
    """A normal acceleration peak must not be treated as a fault."""
    monitor = CurrentPathMonitor()

    for _ in range(80):
        monitor.update(500.0)
    assert monitor.overcurrent is False

    monitor.update(350.0)  # at the limit, not above it
    assert monitor.above_threshold_ms == 0

    for _ in range(80):
        assert monitor.update(500.0) is False
