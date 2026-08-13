"""Cell measurement acquisition — realises ARCH_CELL_MEASUREMENT_ACQ."""

from __future__ import annotations

from dataclasses import replace
from statistics import median

from .types import (
    ACQUISITION_CYCLE_MS,
    MEDIAN_DEVIATION_LIMIT_MV,
    CellSample,
    SampleSet,
)


class Acquisition:
    """Reads the AFE chain and publishes one validated sample set per cycle."""

    def __init__(self, channels: tuple[str, ...]) -> None:
        self._channels = channels
        self._last_publish_ms: int | None = None

    # @Publish one complete validated sample set per 10 ms cycle, IMPL_CELL_SAMPLE_CYCLE, impl, [SWREQ_CELL_SAMPLE_CYCLE]
    def publish(self, raw: tuple[CellSample, ...], timestamp_ms: int) -> SampleSet:
        """Build the cycle's sample set and tag its completeness.

        A set is complete only when every configured channel contributed exactly
        one sample. The timestamp is the one the 50 ms reaction budget is
        measured from, so it is carried on the set rather than re-read later.
        """
        seen = [s.channel for s in raw]
        complete = sorted(seen) == sorted(self._channels) and len(seen) == len(set(seen))
        validated = mark_module_validity(raw)
        self._last_publish_ms = timestamp_ms
        return SampleSet(
            timestamp_ms=timestamp_ms, samples=validated, complete=complete
        )

    def due(self, now_ms: int) -> bool:
        """True when a new cycle is owed at ``now_ms``."""
        if self._last_publish_ms is None:
            return True
        return now_ms - self._last_publish_ms >= ACQUISITION_CYCLE_MS


# @Mark a cell voltage invalid beyond 250 mV from its module median, IMPL_MODULE_MEDIAN_VALIDITY, impl, [SWREQ_MODULE_MEDIAN_VALIDITY]
def mark_module_validity(samples: tuple[CellSample, ...]) -> tuple[CellSample, ...]:
    """Set ``invalid`` per module on deviation from that module's median.

    The median is taken per module, not per pack, so a whole module sitting low
    does not make every one of its cells look implausible.
    """
    by_module: dict[str, list[CellSample]] = {}
    for sample in samples:
        by_module.setdefault(sample.module, []).append(sample)

    out: list[CellSample] = []
    for module_samples in by_module.values():
        module_median = median(s.voltage_mv for s in module_samples)
        for sample in module_samples:
            deviation = abs(sample.voltage_mv - module_median)
            out.append(replace(sample, invalid=deviation > MEDIAN_DEVIATION_LIMIT_MV))
    return tuple(sorted(out, key=lambda s: s.channel))
