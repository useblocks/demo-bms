"""Verification of the cell protection fault memory."""

from src.cell_protection.fault_memory import (
    RECORD_SIZE_BYTES,
    RING_CAPACITY,
    WRITE_BUDGET_MS,
    FaultMemory,
)
from src.cell_protection.types import Limit, LimitViolation


def _violation(channel: str = "C7", measured: int = 4300, ts: int = 500) -> LimitViolation:
    return LimitViolation(
        channel=channel, limit=Limit.OVERVOLTAGE, measured=measured, timestamp_ms=ts
    )


# @A fault record is written inside 20 ms carrying channel limit and value, TEST_FAULT_RECORD_WRITE, [SWREQ_FAULT_RECORD_WRITE]
def test_record_carries_the_required_fields_and_fixed_size() -> None:
    """The record identifies the cell, the limit and the measured value."""
    memory = FaultMemory()

    record = memory.write(_violation(), now_ms=515)

    assert record.channel == "C7"
    assert record.limit == "overvoltage"
    assert record.measured == 4300
    assert record.timestamp_ms == 500
    assert record.written_at_ms - record.timestamp_ms <= WRITE_BUDGET_MS
    assert len(record.encode()) == RECORD_SIZE_BYTES


# @The 64 entry ring overwrites its oldest record when full, TEST_FAULT_RECORD_RING, [SWREQ_FAULT_RECORD_WRITE]
def test_ring_overwrites_the_oldest_record() -> None:
    """A long-lived pack keeps the newest 64 faults, never more."""
    memory = FaultMemory()

    for i in range(RING_CAPACITY + 5):
        memory.write(_violation(channel=f"C{i}", ts=i * 10), now_ms=i * 10 + 5)

    assert len(memory.records) == RING_CAPACITY
    assert memory.records[0].channel == "C5"
    assert memory.records[-1].channel == f"C{RING_CAPACITY + 4}"
