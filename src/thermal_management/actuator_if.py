"""Coolant actuator interface — realises ARCH_COOLANT_ACTUATOR_IF."""

from __future__ import annotations

from dataclasses import dataclass

ACK_TIMEOUT_S = 2.0


@dataclass(frozen=True)
class SetpointFrame:
    """What goes out to the pump and the heater."""

    request_id: int
    cooling: bool
    heating: bool


class CoolantActuatorInterface:
    """Owns the request/acknowledgement conversation, nothing else."""

    def __init__(self) -> None:
        self._next_request_id = 1
        self._pending_id: int | None = None
        self._waiting_s = 0.0
        self._unconfirmed = False
        self.sent: list[SetpointFrame] = []

    @property
    def unconfirmed(self) -> bool:
        return self._unconfirmed

    @property
    def pending_id(self) -> int | None:
        return self._pending_id

    def send(self, cooling: bool, heating: bool) -> SetpointFrame:
        """Raise a request and start its acknowledgement timer."""
        frame = SetpointFrame(
            request_id=self._next_request_id, cooling=cooling, heating=heating
        )
        self._next_request_id += 1
        self._pending_id = frame.request_id
        self._waiting_s = 0.0
        self._unconfirmed = False
        self.sent.append(frame)
        return frame

    def acknowledge(self, request_id: int) -> bool:
        """Stop the timer only on an acknowledgement carrying the same id."""
        if self._pending_id is not None and request_id == self._pending_id:
            self._pending_id = None
            self._waiting_s = 0.0
            self._unconfirmed = False
            return True
        return False

    # @Report a request unconfirmed after 2 s without a matching acknowledgement, IMPL_ACTUATOR_ACK_TIMER, impl, [SWREQ_ACTUATOR_ACK_TIMER]
    def tick(self, dt_s: float) -> bool:
        """Advance the acknowledgement timer of the pending request.

        Silence is turned into an explicit verdict here rather than left implicit,
        because the power limit calculator has no other way to learn that pack
        temperature can no longer be influenced.
        """
        if self._pending_id is None:
            return self._unconfirmed
        self._waiting_s += dt_s
        if self._waiting_s >= ACK_TIMEOUT_S:
            self._unconfirmed = True
        return self._unconfirmed
