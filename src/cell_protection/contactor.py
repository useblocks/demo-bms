"""High-voltage contactor actuator — realises ARCH_CONTACTOR_ACTUATOR."""

from __future__ import annotations

DEENERGISE_BUDGET_MS = 10


class ContactorActuator:
    """Dual-channel low-side coil driver; either channel off opens the circuit."""

    def __init__(self) -> None:
        self._channel_a_energised = False
        self._channel_b_energised = False
        self._last_command_ms: int | None = None
        self._deenergised_at_ms: int | None = None

    @property
    def channels(self) -> tuple[bool, bool]:
        return (self._channel_a_energised, self._channel_b_energised)

    @property
    def closed(self) -> bool:
        """The circuit is closed only while BOTH channels are energised."""
        return self._channel_a_energised and self._channel_b_energised

    @property
    def reaction_ms(self) -> int | None:
        """Measured interval from the open command to both channels off."""
        if self._last_command_ms is None or self._deenergised_at_ms is None:
            return None
        return self._deenergised_at_ms - self._last_command_ms

    # @De-energise both coil channels within 10 ms of the open command, IMPL_CONTACTOR_DEENERGISE, [SWREQ_CONTACTOR_DEENERGISE]
    def open(self, now_ms: int) -> int:
        """Drive both coil channels to their de-energised level.

        Both channels are written in the same call, so the measured reaction is
        the call itself rather than a scheduled follow-up cycle, which keeps the
        10 ms component budget inside the 50 ms system budget.
        """
        self._last_command_ms = now_ms
        self._channel_a_energised = False
        self._channel_b_energised = False
        self._deenergised_at_ms = now_ms
        return now_ms - self._last_command_ms

    def close(self, now_ms: int, latched: bool) -> bool:
        """Energise both channels, unless the supervisor reports a latch."""
        if latched:
            return False
        self._channel_a_energised = True
        self._channel_b_energised = True
        self._deenergised_at_ms = None
        self._last_command_ms = now_ms
        return True
