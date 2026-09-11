"""Verification of the battery state publisher."""

from src.state_estimation.publisher import FRAME_PERIOD_MS, StatePublisher


# @The battery state frame is sent every 100 ms, TEST_STATE_FRAME_PERIOD, [SWREQ_STATE_FRAME_PERIOD]
def test_frame_is_sent_once_per_period() -> None:
    """A cycle call inside the period sends nothing; at the period it sends."""
    publisher = StatePublisher()

    assert publisher.cycle(now_ms=0) is not None
    assert publisher.cycle(now_ms=50) is None
    assert publisher.cycle(now_ms=FRAME_PERIOD_MS) is not None
    assert len(publisher.sent) == 2


# @A producer that did not update does not suppress the frame, TEST_STATE_FRAME_REPEATS_LAST, [SWREQ_STATE_FRAME_PERIOD]
def test_stale_producer_values_are_repeated_not_skipped() -> None:
    """The bus sees a fixed cadence even when an estimator misses a cycle."""
    publisher = StatePublisher()
    publisher.update(soc_pct=64.0, capacity_pct=97.0, unreliable=False)

    first = publisher.cycle(now_ms=0)
    second = publisher.cycle(now_ms=100)
    third = publisher.cycle(now_ms=200)

    assert first is not None and second is not None and third is not None
    assert [f.soc_pct for f in (first, second, third)] == [64.0, 64.0, 64.0]
    assert [f.timestamp_ms for f in (first, second, third)] == [0, 100, 200]


# @A frame carries the latest SOC capacity and validity values, TEST_STATE_FRAME_CONTENT, [SWREQ_STATE_FRAME_PERIOD]
def test_frame_carries_the_latest_values() -> None:
    """An update between two frames is visible in the next frame."""
    publisher = StatePublisher()
    publisher.update(soc_pct=64.0, capacity_pct=97.0, unreliable=False)
    publisher.cycle(now_ms=0)

    publisher.update(soc_pct=63.5, unreliable=True)
    frame = publisher.cycle(now_ms=100)

    assert frame is not None
    assert frame.soc_pct == 63.5
    assert frame.capacity_pct == 97.0
    assert frame.unreliable is True
