"""Verification of the coolant actuator interface."""

from src.thermal_management.actuator_if import CoolantActuatorInterface


# @A request goes unconfirmed after 2 s without a matching acknowledgement, TEST_ACTUATOR_ACK_TIMER, [SWREQ_ACTUATOR_ACK_TIMER]
def test_missing_acknowledgement_becomes_unconfirmed_at_two_seconds() -> None:
    """Silence is turned into an explicit verdict the power limit can act on."""
    interface = CoolantActuatorInterface()
    interface.send(cooling=True, heating=False)

    assert interface.tick(1.0) is False
    assert interface.tick(1.0) is True
    assert interface.unconfirmed is True


# @An acknowledgement carrying a different id does not stop the timer, TEST_ACTUATOR_ACK_ID_MATCH, [SWREQ_ACTUATOR_ACK_TIMER]
def test_only_a_matching_request_id_confirms() -> None:
    """A stale acknowledgement from a previous request must not confirm this one."""
    interface = CoolantActuatorInterface()
    frame = interface.send(cooling=True, heating=False)

    assert interface.acknowledge(frame.request_id + 99) is False
    assert interface.tick(2.0) is True

    assert interface.acknowledge(frame.request_id) is True
    assert interface.unconfirmed is False
    assert interface.pending_id is None


# @A new request restarts the acknowledgement timer cleanly, TEST_ACTUATOR_ACK_RESTART, [SWREQ_ACTUATOR_ACK_TIMER]
def test_a_new_request_clears_the_previous_verdict() -> None:
    """Each raised request is judged on its own acknowledgement window."""
    interface = CoolantActuatorInterface()
    interface.send(cooling=True, heating=False)
    interface.tick(2.0)
    assert interface.unconfirmed is True

    interface.send(cooling=False, heating=True)
    assert interface.unconfirmed is False
    assert interface.tick(1.9) is False
    assert len(interface.sent) == 2
