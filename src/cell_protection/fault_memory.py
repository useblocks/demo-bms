"""Cell protection fault memory — realises ARCH_FAULT_MEMORY."""

from __future__ import annotations

from dataclasses import dataclass

from .types import LimitViolation

RING_CAPACITY = 64
RECORD_SIZE_BYTES = 16
WRITE_BUDGET_MS = 20


@dataclass(frozen=True)
class FaultRecord:
    """The fixed 16-byte record layout, as a decoded value object."""

    channel: str
    limit: str
    measured: int
    timestamp_ms: int
    written_at_ms: int

    def encode(self) -> bytes:
        """Pack into the fixed on-flash layout: 4 + 2 + 4 + 4 + 2 bytes."""
        return (
            _channel_id(self.channel).to_bytes(4, "big")
            + _limit_id(self.limit).to_bytes(2, "big")
            + int(self.measured).to_bytes(4, "big", signed=True)
            + (self.timestamp_ms & 0xFFFFFFFF).to_bytes(4, "big")
            + (self.written_at_ms - self.timestamp_ms & 0xFFFF).to_bytes(2, "big")
        )


class FaultMemory:
    """A 64-entry ring of fixed-size records in non-volatile memory."""

    def __init__(self) -> None:
        self._ring: list[FaultRecord] = []

    @property
    def records(self) -> tuple[FaultRecord, ...]:
        return tuple(self._ring)

    # @Append a 16-byte fault record within 20 ms of the violation event, IMPL_FAULT_RECORD_WRITE, [SWREQ_FAULT_RECORD_WRITE]
    def write(self, violation: LimitViolation, now_ms: int) -> FaultRecord:
        """Append one record, overwriting the oldest once the ring is full.

        The record carries the violation's own timestamp, not the write time, so
        the workshop reads back when the limit was crossed rather than when the
        flash write completed.
        """
        record = FaultRecord(
            channel=violation.channel,
            limit=violation.limit.value,
            measured=violation.measured,
            timestamp_ms=violation.timestamp_ms,
            written_at_ms=now_ms,
        )
        if len(self._ring) >= RING_CAPACITY:
            self._ring.pop(0)
        self._ring.append(record)
        assert len(record.encode()) == RECORD_SIZE_BYTES
        return record


def _channel_id(channel: str) -> int:
    return sum(channel.encode()) & 0xFFFFFFFF


def _limit_id(limit: str) -> int:
    order = ("undervoltage", "overvoltage", "overtemperature", "overcurrent")
    return order.index(limit) if limit in order else 0xFFFF
