"""Cell bleed driver — realises ARCH_CELL_BLEED_DRIVER."""

from __future__ import annotations

MAX_CONCURRENT_CHANNELS = 4


class CellBleedDriver:
    """Reduces a requested bleed set to the set the shunt hardware may carry.

    Two hardware limits do the reducing: adjacent shunt resistors share a thermal
    path on the AFE board, and the board's dissipation budget caps how many
    channels may be energised at once.
    """

    def __init__(self) -> None:
        self._energised: frozenset[int] = frozenset()

    @property
    def energised(self) -> frozenset[int]:
        """The channels currently bleeding."""
        return self._energised

    # @Energise at most four non-adjacent bleed channels, IMPL_BLEED_CHANNEL_LIMIT, impl, [SWREQ_BLEED_CHANNEL_LIMIT]
    def request(self, excess_by_channel: dict[int, int]) -> frozenset[int]:
        """Energise the admissible subset of ``channel -> excess over pack minimum``.

        Channels are admitted greediest-first — largest excess, ties broken by
        ascending index — so the spread closes at the fastest rate the two limits
        allow, and the cells that lose the tie are served on a later cycle.
        """
        ordered = sorted(excess_by_channel, key=lambda ch: (-excess_by_channel[ch], ch))
        admitted: list[int] = []
        for channel in ordered:
            if len(admitted) == MAX_CONCURRENT_CHANNELS:
                break
            if any(abs(channel - taken) == 1 for taken in admitted):
                continue
            admitted.append(channel)
        self._energised = frozenset(admitted)
        return self._energised

    # @Clear every energised bleed channel on release, IMPL_BLEED_ALL_CLEAR, impl, [SWREQ_BLEED_ALL_CLEAR]
    def release(self) -> None:
        """De-energise everything, whatever was last requested.

        Deliberately not expressed as ``request({})``: "stop bleeding now" has to
        be independent of the selection logic, so a defect in selection can never
        keep a channel energised through a release.
        """
        self._energised = frozenset()
