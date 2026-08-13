"""Verification of the cell protection safety supervisor."""

from src.cell_protection.supervisor import SafetySupervisor
from src.cell_protection.types import CellSample, Limit, SafetyState, SampleSet


def _set(*samples: CellSample, timestamp_ms: int = 500) -> SampleSet:
    return SampleSet(timestamp_ms=timestamp_ms, samples=samples, complete=True)


def _cell(mv: int = 3600, dc: int = 250, invalid: bool = False) -> CellSample:
    return CellSample(
        channel="C1", module="M1", voltage_mv=mv, temperature_dc=dc, invalid=invalid
    )


# @Supervisor evaluates each valid sample against the four limit table entries, TEST_LIMIT_EVALUATION, test, [SWREQ_LIMIT_EVALUATION]
def test_each_limit_table_entry_is_evaluated() -> None:
    """All four entries produce a violation naming that entry."""
    assert SafetySupervisor().evaluate(_set(_cell(mv=2499))).limit is Limit.UNDERVOLTAGE
    assert SafetySupervisor().evaluate(_set(_cell(mv=4251))).limit is Limit.OVERVOLTAGE
    assert SafetySupervisor().evaluate(_set(_cell(dc=601))).limit is Limit.OVERTEMPERATURE
    assert (
        SafetySupervisor().evaluate(_set(_cell()), overcurrent=True).limit
        is Limit.OVERCURRENT
    )


# @A sample inside every limit produces no violation, TEST_LIMIT_EVALUATION_NOMINAL, test, [SWREQ_LIMIT_EVALUATION]
def test_nominal_sample_produces_no_violation() -> None:
    """The gate must not fire on healthy measurements."""
    supervisor = SafetySupervisor()

    assert supervisor.evaluate(_set(_cell(mv=2500), _cell(mv=4250))) is None
    assert supervisor.state is SafetyState.RUN
    assert supervisor.open_command is False


# @An invalid sample can never command the contactors open, TEST_IGNORE_INVALID_SAMPLES, test, [SWREQ_IGNORE_INVALID_SAMPLES]
def test_invalid_samples_are_excluded_from_evaluation() -> None:
    """A single failed sensor reading past a limit is dropped, not acted on."""
    supervisor = SafetySupervisor()

    assert supervisor.evaluate(_set(_cell(mv=5000, invalid=True))) is None
    assert supervisor.state is SafetyState.RUN

    # The same value, now plausible, does trip — proving the flag was the reason.
    assert supervisor.evaluate(_set(_cell(mv=5000))) is not None


# @A cycle of only invalid samples produces no event at all, TEST_IGNORE_INVALID_ALL, test, [SWREQ_IGNORE_INVALID_SAMPLES]
def test_fully_invalid_cycle_is_silent() -> None:
    """Losing the whole AFE chain must not be read as a limit violation."""
    supervisor = SafetySupervisor()

    result = supervisor.evaluate(
        _set(_cell(mv=5000, invalid=True), _cell(mv=1000, invalid=True))
    )

    assert result is None
    assert supervisor.state is SafetyState.RUN


# @FAULT_LATCHED is left only on a diagnostic service reset, TEST_LATCH_STATE_MACHINE, test, [SWREQ_LATCH_STATE_MACHINE]
def test_latch_survives_healthy_samples_and_clears_only_on_reset() -> None:
    """Healthy measurements must not release the latch — only a service action does."""
    supervisor = SafetySupervisor()
    supervisor.evaluate(_set(_cell(mv=4300)))
    assert supervisor.state is SafetyState.FAULT_LATCHED
    assert supervisor.open_command is True

    for _ in range(100):
        supervisor.evaluate(_set(_cell(mv=3600)))
    assert supervisor.state is SafetyState.FAULT_LATCHED
    assert supervisor.open_command is True

    assert supervisor.service_reset() is SafetyState.RUN
    assert supervisor.open_command is False


# @The latched violation keeps the first cause not the latest, TEST_LATCH_FIRST_CAUSE, test, [SWREQ_LATCH_STATE_MACHINE]
def test_latch_retains_the_first_violation() -> None:
    """The workshop needs the cause that started the fault, not the last symptom."""
    supervisor = SafetySupervisor()
    supervisor.evaluate(_set(_cell(mv=4300)))

    supervisor.evaluate(_set(_cell(dc=700)))

    assert supervisor.violation is not None
    assert supervisor.violation.limit is Limit.OVERVOLTAGE
