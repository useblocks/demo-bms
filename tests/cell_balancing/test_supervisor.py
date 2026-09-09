"""Verification of the balancing supervisor."""

from src.cell_balancing.supervisor import BalancingSupervisor

COOL = ((250, False), (260, False))  # 25.0 / 26.0 °C — inside the band
HOT = ((250, False), (500, False))  # 50.0 °C — outside the band
TIGHT = (3_600_000, 3_615_000)  # 15 mV apart — at the target
WIDE = (3_600_000, 3_660_000)  # 60 mV apart — needs balancing


def _open_session(supervisor: BalancingSupervisor) -> None:
    """Drive the rising edge of the charge-session-ended input."""
    supervisor.cycle(0, False, 0, COOL, WIDE)
    supervisor.cycle(0, True, 0, COOL, WIDE)


# @A balancing session opens on the charge-session-ended rising edge, TEST_BALANCING_SESSION_OPEN, test, [SWREQ_BALANCING_SESSION_WINDOW]
def test_session_opens_on_the_edge_and_not_on_the_held_level() -> None:
    """A held-true flag must not restart the session and discard qualifying time."""
    supervisor = BalancingSupervisor()
    _open_session(supervisor)

    supervisor.cycle(600, True, 0, COOL, WIDE)
    supervisor.cycle(600, True, 0, COOL, WIDE)

    assert supervisor.state.open is True
    assert supervisor.state.qualifying_s == 1200


# @A session closes as met once the settled spread reaches 20 mV, TEST_BALANCING_SESSION_MET, test, [SWREQ_BALANCING_SESSION_WINDOW]
def test_session_closes_as_met_on_the_target_spread() -> None:
    """The pack is settled and inside 20 mV, so the session is done and reports met."""
    supervisor = BalancingSupervisor()
    _open_session(supervisor)

    for _ in range(3):  # 30 minutes of rest — the pack settles
        supervisor.cycle(600, True, 0, COOL, TIGHT)

    assert supervisor.state.open is False
    assert supervisor.state.outcome == "met"


# @A session closes as missed after 8 hours of qualifying time, TEST_BALANCING_SESSION_MISSED, test, [SWREQ_BALANCING_SESSION_WINDOW]
def test_session_closes_as_missed_when_the_window_runs_out() -> None:
    """A pack still 60 mV apart after the window reports the deadline as missed."""
    supervisor = BalancingSupervisor()
    _open_session(supervisor)

    for _ in range(8):
        supervisor.cycle(3600, True, 0, COOL, WIDE)

    assert supervisor.state.open is False
    assert supervisor.state.outcome == "missed"


# @A disturbed cycle pauses the qualifying clock instead of resetting it, TEST_BALANCING_CLOCK_PAUSES, test, [SWREQ_BALANCING_PRECONDITION_GATE]
def test_qualifying_time_pauses_while_a_precondition_is_broken() -> None:
    """Driving the pack, or heating it out of band, costs the clock nothing already earned."""
    supervisor = BalancingSupervisor()
    _open_session(supervisor)
    supervisor.cycle(600, True, 0, COOL, WIDE)

    supervisor.cycle(600, True, 20_000, COOL, WIDE)  # 20 A — not at rest
    supervisor.cycle(600, True, 0, HOT, WIDE)  # out of the temperature band

    assert supervisor.state.qualifying_s == 600


# @A broken precondition demands the bleed channels be released, TEST_BALANCING_RELEASE_DEMAND, test, [SWREQ_BALANCING_PRECONDITION_GATE]
def test_release_is_demanded_whenever_a_precondition_breaks() -> None:
    """Bleeding a pack that is being driven or is out of band is not allowed."""
    supervisor = BalancingSupervisor()
    _open_session(supervisor)

    assert supervisor.release_required(0, COOL) is False
    assert supervisor.release_required(20_000, COOL) is True
    assert supervisor.release_required(0, HOT) is True


# @Only cells more than 20 mV above the pack minimum are requested, TEST_BALANCING_TARGET_SELECTION, test, [SWREQ_BALANCING_TARGET_SELECTION]
def test_only_cells_above_the_target_band_are_selected() -> None:
    """The excess is measured against the lowest cell, and 20 mV exactly is inside."""
    supervisor = BalancingSupervisor()
    _open_session(supervisor)
    voltages = (3_600_000, 3_620_000, 3_660_000)  # +0 mV, +20 mV, +60 mV

    for _ in range(2):
        supervisor.cycle(900, True, 0, COOL, voltages)
    requested = supervisor.cycle(900, True, 0, COOL, voltages)

    assert requested == {2: 60_000}


# @An unsettled pack yields no bleed request at all, TEST_BALANCING_UNSETTLED, test, [SWREQ_BALANCING_TARGET_SELECTION]
def test_no_cell_is_selected_before_the_pack_has_settled() -> None:
    """Polarisation voltages would name whichever cell was last loaded hardest."""
    supervisor = BalancingSupervisor()
    _open_session(supervisor)

    requested = supervisor.cycle(600, True, 0, COOL, WIDE)  # 10 min of rest only

    assert supervisor.state.settled is False
    assert requested == {}
