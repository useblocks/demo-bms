"""Cell protection safety supervisor — realises ARCH_SAFETY_SUPERVISOR."""

from __future__ import annotations

from .types import (
    OVERTEMPERATURE_DC,
    OVERVOLTAGE_MV,
    UNDERVOLTAGE_MV,
    CellSample,
    Limit,
    LimitViolation,
    SafetyState,
    SampleSet,
)


class SafetySupervisor:
    """The single decision point: limit table plus the latched safety state."""

    def __init__(self) -> None:
        self._state = SafetyState.RUN
        self._violation: LimitViolation | None = None

    @property
    def state(self) -> SafetyState:
        return self._state

    @property
    def open_command(self) -> bool:
        """The contactor-open command the actuator consumes."""
        return self._state is SafetyState.FAULT_LATCHED

    @property
    def violation(self) -> LimitViolation | None:
        return self._violation

    # @Evaluate every valid sample against the static limit table each cycle, IMPL_LIMIT_EVALUATION, [SWREQ_LIMIT_EVALUATION]
    def evaluate(
        self, sample_set: SampleSet, overcurrent: bool = False
    ) -> LimitViolation | None:
        """Compare one cycle's samples against the four limit-table entries.

        Returns the first violation found, checking the per-cell limits in
        channel order before the pack-wide overcurrent condition.
        """
        for sample in candidate_samples(sample_set.samples):
            limit = _violated_limit(sample)
            if limit is not None:
                measured = (
                    sample.temperature_dc
                    if limit is Limit.OVERTEMPERATURE
                    else sample.voltage_mv
                )
                return self._raise(
                    LimitViolation(
                        channel=sample.channel,
                        limit=limit,
                        measured=measured,
                        timestamp_ms=sample_set.timestamp_ms,
                    )
                )
        if overcurrent:
            return self._raise(
                LimitViolation(
                    channel="pack",
                    limit=Limit.OVERCURRENT,
                    measured=0,
                    timestamp_ms=sample_set.timestamp_ms,
                )
            )
        return None

    # @Leave FAULT_LATCHED only on a diagnostic service reset, IMPL_LATCH_STATE_MACHINE, [SWREQ_LATCH_STATE_MACHINE]
    def service_reset(self) -> SafetyState:
        """The only transition out of ``FAULT_LATCHED``.

        Samples returning inside their limits deliberately do not clear the
        latch — that is what stops an intermittent condition from re-closing the
        high-voltage circuit without a service action.
        """
        self._state = SafetyState.RUN
        self._violation = None
        return self._state

    def _raise(self, violation: LimitViolation) -> LimitViolation:
        if self._state is SafetyState.RUN:
            self._violation = violation
            self._state = SafetyState.FAULT_LATCHED
        return violation


# @Exclude samples flagged invalid from limit evaluation, IMPL_IGNORE_INVALID_SAMPLES, [SWREQ_IGNORE_INVALID_SAMPLES]
def candidate_samples(samples: tuple[CellSample, ...]) -> tuple[CellSample, ...]:
    """Keep only the samples the supervisor is allowed to judge.

    A single failed sensor must not be able to command the contactors open, so
    an implausible reading is dropped here rather than compared against a limit.
    """
    return tuple(s for s in samples if not s.invalid)


def _violated_limit(sample: CellSample) -> Limit | None:
    if sample.voltage_mv < UNDERVOLTAGE_MV:
        return Limit.UNDERVOLTAGE
    if sample.voltage_mv > OVERVOLTAGE_MV:
        return Limit.OVERVOLTAGE
    if sample.temperature_dc > OVERTEMPERATURE_DC:
        return Limit.OVERTEMPERATURE
    return None
