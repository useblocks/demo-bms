"""State-of-charge store — realises ARCH_SOC_STORE."""

from __future__ import annotations

from dataclasses import dataclass

PERIODIC_WRITE_INTERVAL_S = 60.0


@dataclass
class Slot:
    """One of the two alternating non-volatile records."""

    soc: float
    write_counter: int
    checksum: int

    def valid(self) -> bool:
        return self.checksum == checksum_of(self.soc, self.write_counter)


def checksum_of(soc: float, write_counter: int) -> int:
    """A cheap additive checksum over the two persisted fields."""
    return (int(round(soc * 100)) + write_counter * 7919) & 0xFFFF


class SocStore:
    """Two-slot alternating persistence, so a power loss leaves one intact."""

    def __init__(self) -> None:
        self._slots: list[Slot | None] = [None, None]
        self._last_write_s = 0.0

    @property
    def slots(self) -> tuple[Slot | None, Slot | None]:
        return (self._slots[0], self._slots[1])

    def due(self, now_s: float) -> bool:
        return now_s - self._last_write_s >= PERIODIC_WRITE_INTERVAL_S

    # @Write the alternating two-slot SOC record on shutdown and every 60 s, IMPL_SOC_PERSIST_WRITE, [SWREQ_SOC_PERSIST_WRITE]
    def write(self, soc: float, now_s: float, shutdown: bool = False) -> Slot | None:
        """Persist the SOC into the slot holding the lower write counter.

        Overwriting the lower-counter slot is what guarantees the higher-counter
        one survives the write: an interrupted write can only ever corrupt the
        older of the two records.
        """
        if not shutdown and not self.due(now_s):
            return None
        target = self._stale_index()
        counter = self._highest_counter() + 1
        slot = Slot(soc=soc, write_counter=counter, checksum=checksum_of(soc, counter))
        self._slots[target] = slot
        self._last_write_s = now_s
        return slot

    # @Restore the SOC from the checksum-valid slot with the higher counter, IMPL_SOC_RESTORE_SLOT, [SWREQ_SOC_RESTORE_SLOT]
    def restore(self) -> float | None:
        """Return the newest checksum-valid stored SOC, or ``None`` if neither is.

        Reporting ``None`` rather than a default is deliberate: a fabricated
        starting value would look exactly like a real one to everything
        downstream.
        """
        candidates = [s for s in self._slots if s is not None and s.valid()]
        if not candidates:
            return None
        return max(candidates, key=lambda s: s.write_counter).soc

    def corrupt_slot(self, index: int) -> None:
        """Test/diagnostic hook: flip a stored checksum to simulate a bad write."""
        slot = self._slots[index]
        if slot is not None:
            slot.checksum ^= 0xFFFF

    def _highest_counter(self) -> int:
        return max((s.write_counter for s in self._slots if s is not None), default=0)

    def _stale_index(self) -> int:
        if self._slots[0] is None:
            return 0
        if self._slots[1] is None:
            return 1
        return 0 if self._slots[0].write_counter <= self._slots[1].write_counter else 1
