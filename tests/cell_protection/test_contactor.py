"""Verification of the high-voltage contactor actuator."""

from src.cell_protection.contactor import DEENERGISE_BUDGET_MS, ContactorActuator


# @Both coil channels de-energise within the 10 ms budget, TEST_CONTACTOR_DEENERGISE, [SWREQ_CONTACTOR_DEENERGISE]
def test_open_deenergises_both_channels_within_budget() -> None:
    """Both channels go off in the same call, so the measured reaction fits 10 ms."""
    actuator = ContactorActuator()
    actuator.close(now_ms=0, latched=False)
    assert actuator.closed is True

    actuator.open(now_ms=1_000)

    assert actuator.channels == (False, False)
    assert actuator.closed is False
    assert actuator.reaction_ms is not None
    assert actuator.reaction_ms <= DEENERGISE_BUDGET_MS


# @A latched supervisor state blocks any close request, TEST_CONTACTOR_LATCH_BLOCK, [SWREQ_CONTACTOR_DEENERGISE]
def test_close_is_refused_while_latched() -> None:
    """The actuator refuses to re-close while the supervisor reports a latch."""
    actuator = ContactorActuator()
    actuator.open(now_ms=0)

    assert actuator.close(now_ms=10, latched=True) is False
    assert actuator.closed is False

    assert actuator.close(now_ms=20, latched=False) is True
    assert actuator.closed is True
