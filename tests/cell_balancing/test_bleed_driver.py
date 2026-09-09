"""Verification of the cell bleed driver."""

from src.cell_balancing.bleed_driver import CellBleedDriver


# @At most four bleed channels are energised at once, TEST_BLEED_CHANNEL_CAP, test, [SWREQ_BLEED_CHANNEL_LIMIT]
def test_energised_set_is_capped_at_four_channels() -> None:
    """Six well-separated channels are requested; the board carries four."""
    driver = CellBleedDriver()

    energised = driver.request({0: 60, 2: 55, 4: 50, 6: 45, 8: 40, 10: 35})

    assert energised == frozenset({0, 2, 4, 6})


# @Two adjacent bleed channels are never energised together, TEST_BLEED_NO_ADJACENT, test, [SWREQ_BLEED_CHANNEL_LIMIT]
def test_adjacent_channels_are_never_energised_together() -> None:
    """Adjacent shunts share a thermal path, so the neighbour waits a cycle."""
    driver = CellBleedDriver()

    energised = driver.request({0: 60, 1: 59, 2: 58, 3: 57})

    assert energised == frozenset({0, 2})


# @Bleed channels are admitted greediest-first with ties by index, TEST_BLEED_ADMISSION_ORDER, test, [SWREQ_BLEED_CHANNEL_LIMIT]
def test_channels_are_admitted_by_descending_excess_then_index() -> None:
    """The largest excess wins the thermal slot; equal excesses go to the lower index."""
    driver = CellBleedDriver()

    energised = driver.request({0: 30, 1: 90, 5: 30, 9: 30})

    assert energised == frozenset({1, 5, 9})


# @Release clears every energised bleed channel, TEST_BLEED_RELEASE, test, [SWREQ_BLEED_ALL_CLEAR]
def test_release_clears_every_channel_and_survives_the_last_request() -> None:
    """"Stop bleeding now" must not depend on what selection last returned."""
    driver = CellBleedDriver()
    driver.request({0: 60, 2: 55})

    driver.release()

    assert driver.energised == frozenset()
