"""Balancing supervisor — realises ARCH_BALANCING_SUPERVISOR."""

from __future__ import annotations

from dataclasses import dataclass

TARGET_SPREAD_UV = 20_000  # 20 mV, the spread the session is closed on
REST_CURRENT_MA = 500  # 0.5 A, the magnitude at or below which the pack is at rest
TEMP_MIN_DC = 150  # 15.0 °C, in tenths of a degree Celsius
TEMP_MAX_DC = 450  # 45.0 °C
SETTLING_S = 30 * 60  # continuous rest before the voltages are settled
WINDOW_S = 8 * 60 * 60  # qualifying time the session is allowed


@dataclass(frozen=True)
class SessionState:
    """What the supervisor publishes about the balancing session each cycle."""

    open: bool
    qualifying_s: int
    settled: bool
    outcome: str | None  # "met", "missed", or None while the session runs


class BalancingSupervisor:
    """Owns the balancing session: when it runs, how long, and which cells bleed."""

    def __init__(self) -> None:
        self._open = False
        self._qualifying_s = 0
        self._rest_s = 0
        self._outcome: str | None = None
        self._charge_ended_previous = False

    @property
    def state(self) -> SessionState:
        return SessionState(
            open=self._open,
            qualifying_s=self._qualifying_s,
            settled=self._rest_s >= SETTLING_S,
            outcome=self._outcome,
        )

    def cycle(
        self,
        dt_s: int,
        charge_ended: bool,
        pack_current_ma: int,
        temperatures_dc: tuple[tuple[int, bool], ...],
        voltages_uv: tuple[int, ...],
    ) -> dict[int, int]:
        """Run one supervisor cycle and return the requested ``channel -> excess``.

        An empty mapping means "bleed nothing", which the caller passes straight
        to the driver; a broken precondition additionally calls the driver's
        release path, which is why :meth:`release_required` exists separately.
        """
        self._track_session_start(charge_ended)
        at_rest = abs(pack_current_ma) <= REST_CURRENT_MA
        self._rest_s = self._rest_s + dt_s if at_rest else 0

        if not self._open:
            return {}

        if self._accumulate(dt_s, at_rest, temperatures_dc):
            return {}

        return self._select(voltages_uv)

    def release_required(
        self, pack_current_ma: int, temperatures_dc: tuple[tuple[int, bool], ...]
    ) -> bool:
        """True when the bleed channels must be cleared this cycle."""
        return not self._open or not self._preconditions_met(
            pack_current_ma, temperatures_dc
        )

    # @Open a balancing session at charge end and close it on the target spread, IMPL_BALANCING_SESSION_WINDOW, impl, [SWREQ_BALANCING_SESSION_WINDOW]
    def _track_session_start(self, charge_ended: bool) -> None:
        """Open a session on the rising edge of the charge-session-ended input.

        The edge, not the level: a controller that holds the flag true while the
        vehicle stands would otherwise re-open the session on every cycle and
        throw the accumulated qualifying time away each time.
        """
        if charge_ended and not self._charge_ended_previous:
            self._open = True
            self._qualifying_s = 0
            self._rest_s = 0
            self._outcome = None
        self._charge_ended_previous = charge_ended

    def _close(self, outcome: str) -> None:
        self._open = False
        self._outcome = outcome

    # @Accumulate qualifying time only while the pack is at rest and in the temperature band, IMPL_BALANCING_PRECONDITION_GATE, impl, [SWREQ_BALANCING_PRECONDITION_GATE]
    def _accumulate(
        self,
        dt_s: int,
        at_rest: bool,
        temperatures_dc: tuple[tuple[int, bool], ...],
    ) -> bool:
        """Advance the session clock; return True when this cycle may not bleed.

        A disturbed cycle PAUSES the clock rather than resetting it. Resetting
        would let a pack that is briefly woken every few hours never finish, and
        lapsing would report a deadline met that was never earned.
        """
        if not (at_rest and self._temperatures_in_band(temperatures_dc)):
            return True
        self._qualifying_s += dt_s
        if self._qualifying_s >= WINDOW_S:
            self._close("missed")
            return True
        return False

    def _preconditions_met(
        self, pack_current_ma: int, temperatures_dc: tuple[tuple[int, bool], ...]
    ) -> bool:
        return abs(pack_current_ma) <= REST_CURRENT_MA and self._temperatures_in_band(
            temperatures_dc
        )

    @staticmethod
    def _temperatures_in_band(temperatures_dc: tuple[tuple[int, bool], ...]) -> bool:
        """Every sample with a cleared invalid flag lies inside 15–45 °C.

        Invalid samples are skipped rather than failing the band: an open sensor
        reads as an implausible value, and letting that stop balancing entirely
        would trade a real capacity loss for a measurement fault.
        """
        return all(
            TEMP_MIN_DC <= temperature <= TEMP_MAX_DC
            for temperature, invalid in temperatures_dc
            if not invalid
        )

    # @Request bleeding only for cells more than 20 mV above the pack minimum, IMPL_BALANCING_TARGET_SELECTION, impl, [SWREQ_BALANCING_TARGET_SELECTION]
    def _select(self, voltages_uv: tuple[int, ...]) -> dict[int, int]:
        """Pick the cells to bleed from settled voltages, and close on the target.

        Before the pack has settled the mapping is empty: acting on polarisation
        voltages would name whichever cell was last loaded hardest rather than
        whichever cell actually holds the most charge.
        """
        if not voltages_uv or self._rest_s < SETTLING_S:
            return {}
        lowest = min(voltages_uv)
        if max(voltages_uv) - lowest <= TARGET_SPREAD_UV:
            self._close("met")
            return {}
        return {
            channel: voltage - lowest
            for channel, voltage in enumerate(voltages_uv)
            if voltage - lowest > TARGET_SPREAD_UV
        }
