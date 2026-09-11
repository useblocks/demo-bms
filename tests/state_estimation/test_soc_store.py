"""Verification of the state-of-charge store."""

from src.state_estimation.soc_store import SocStore


def _filled() -> SocStore:
    store = SocStore()
    store.write(50.0, now_s=0.0, shutdown=True)
    store.write(52.0, now_s=60.0)
    store.write(53.0, now_s=120.0)
    return store


# @The SOC record is written on shutdown and every 60 seconds, TEST_SOC_PERSIST_WRITE, [SWREQ_SOC_PERSIST_WRITE]
def test_writes_happen_on_shutdown_and_on_the_periodic_interval() -> None:
    """A shutdown always writes; a periodic write only once 60 s have passed."""
    store = SocStore()

    assert store.write(50.0, now_s=0.0, shutdown=True) is not None
    assert store.write(51.0, now_s=10.0) is None  # interval not elapsed
    assert store.write(52.0, now_s=60.0) is not None


# @Each write targets the slot holding the lower write counter, TEST_SOC_PERSIST_ALTERNATION, [SWREQ_SOC_PERSIST_WRITE]
def test_writes_alternate_between_the_two_slots() -> None:
    """Overwriting the older slot is what keeps the newer one intact."""
    store = _filled()

    slot_a, slot_b = store.slots
    assert slot_a is not None and slot_b is not None
    assert {slot_a.write_counter, slot_b.write_counter} == {2, 3}
    assert slot_a.soc == 53.0  # third write landed back in slot 0
    assert slot_b.soc == 52.0


# @Restore returns the checksum valid slot with the higher counter, TEST_SOC_RESTORE_SLOT, [SWREQ_SOC_RESTORE_SLOT]
def test_restore_prefers_the_newest_valid_slot() -> None:
    """The newest record wins while it is valid; the older one is the fallback."""
    store = _filled()
    assert store.restore() == 53.0

    store.corrupt_slot(0)
    assert store.restore() == 52.0


# @Restore reports no stored value when neither slot is valid, TEST_SOC_RESTORE_NO_VALID_SLOT, [SWREQ_SOC_RESTORE_SLOT]
def test_restore_reports_absence_rather_than_a_default() -> None:
    """A fabricated starting value would be indistinguishable from a real one."""
    store = _filled()
    store.corrupt_slot(0)
    store.corrupt_slot(1)

    assert store.restore() is None
    assert SocStore().restore() is None
