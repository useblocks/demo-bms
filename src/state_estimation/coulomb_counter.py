"""Coulomb counter — realises ARCH_COULOMB_COUNTER."""

from __future__ import annotations

TICK_S = 0.01
TICK_MS = 10


class CoulombCounter:
    """Trapezoidal charge integral of the pack, in ampere-seconds."""

    def __init__(self) -> None:
        self._accumulated_as = 0.0
        self._throughput_as = 0.0
        self._previous_a: float | None = None

    @property
    def accumulated_as(self) -> float:
        """Signed accumulated charge since initialisation, in ampere-seconds."""
        return self._accumulated_as

    @property
    def throughput_as(self) -> float:
        """Absolute charge moved since the last ``reset_throughput`` call."""
        return self._throughput_as

    def reset_throughput(self) -> None:
        self._throughput_as = 0.0

    # @Integrate the pack current trapezoidally on every 10 ms tick, IMPL_CHARGE_INTEGRATION, [SWREQ_CHARGE_INTEGRATION]
    def tick(self, current_a: float, tick_s: float = TICK_S) -> float:
        """Add one tick's charge to the accumulator.

        The first tick after initialisation contributes nothing: the trapezoid
        needs two samples, and inventing a zero predecessor would bias the
        integral by half a tick on every wake-up.
        """
        if self._previous_a is None:
            self._previous_a = current_a
            return self._accumulated_as
        charge_as = (self._previous_a + current_a) / 2.0 * tick_s
        self._accumulated_as += charge_as
        self._throughput_as += abs(charge_as)
        self._previous_a = current_a
        return self._accumulated_as
