"""Verification of the cell measurement acquisition component."""

from src.cell_protection.acquisition import Acquisition, mark_module_validity
from src.cell_protection.types import CellSample


def _sample(channel: str, module: str, mv: int, dc: int = 250) -> CellSample:
    return CellSample(channel=channel, module=module, voltage_mv=mv, temperature_dc=dc)


# @Acquisition publishes one complete sample set per 10 ms cycle, TEST_CELL_SAMPLE_CYCLE, test, [SWREQ_CELL_SAMPLE_CYCLE]
def test_complete_sample_set_every_cycle() -> None:
    """A set covering every configured channel is complete and carries the cycle time.

    Also checks the negative case, because "complete" is only meaningful if an
    incomplete set is actually reported as incomplete.
    """
    acq = Acquisition(channels=("C1", "C2", "C3"))
    raw = (
        _sample("C1", "M1", 3600),
        _sample("C2", "M1", 3610),
        _sample("C3", "M1", 3605),
    )

    full = acq.publish(raw, timestamp_ms=1_000)
    assert full.complete is True
    assert full.timestamp_ms == 1_000
    assert {s.channel for s in full.samples} == {"C1", "C2", "C3"}

    partial = acq.publish(raw[:2], timestamp_ms=1_010)
    assert partial.complete is False

    duplicated = acq.publish(raw[:2] + (raw[1],), timestamp_ms=1_020)
    assert duplicated.complete is False


# @Acquisition cycle is due only after the 10 ms period elapsed, TEST_CELL_SAMPLE_CYCLE_PERIOD, test, [SWREQ_CELL_SAMPLE_CYCLE]
def test_cycle_is_due_only_after_ten_milliseconds() -> None:
    """The 10 ms period is enforced by the component, not by its caller."""
    acq = Acquisition(channels=("C1",))
    assert acq.due(0) is True

    acq.publish((_sample("C1", "M1", 3600),), timestamp_ms=0)
    assert acq.due(9) is False
    assert acq.due(10) is True


# @Cell voltage beyond 250 mV from the module median is flagged invalid, TEST_MODULE_MEDIAN_VALIDITY, test, [SWREQ_MODULE_MEDIAN_VALIDITY]
def test_module_median_deviation_marks_sample_invalid() -> None:
    """One implausible cell is flagged; its plausible neighbours are not."""
    samples = (
        _sample("C1", "M1", 3600),
        _sample("C2", "M1", 3610),
        _sample("C3", "M1", 3605),
        _sample("C4", "M1", 4000),
    )

    flagged = {s.channel: s.invalid for s in mark_module_validity(samples)}

    assert flagged["C4"] is True
    assert flagged["C1"] is False
    assert flagged["C2"] is False
    assert flagged["C3"] is False


# @The plausibility median is taken per module not per pack, TEST_MODULE_MEDIAN_SCOPE, test, [SWREQ_MODULE_MEDIAN_VALIDITY]
def test_median_is_scoped_to_the_module() -> None:
    """A whole module sitting low must not make all of its cells look invalid."""
    samples = (
        _sample("C1", "M1", 3600),
        _sample("C2", "M1", 3605),
        _sample("C3", "M2", 3100),
        _sample("C4", "M2", 3105),
    )

    flagged = {s.channel: s.invalid for s in mark_module_validity(samples)}

    assert not any(flagged.values())
