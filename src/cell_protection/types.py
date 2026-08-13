"""Shared data types of the cell-protection stream.

No need marker lives here: this module carries no behaviour of its own, only the
records the behaviour-bearing modules exchange.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Limit(str, Enum):
    """The four entries of the static limit table."""

    UNDERVOLTAGE = "undervoltage"
    OVERVOLTAGE = "overvoltage"
    OVERTEMPERATURE = "overtemperature"
    OVERCURRENT = "overcurrent"


UNDERVOLTAGE_MV = 2500
OVERVOLTAGE_MV = 4250
OVERTEMPERATURE_DC = 600  # tenths of a degree Celsius
OVERCURRENT_A = 350
OVERCURRENT_PERSISTENCE_MS = 100
ACQUISITION_CYCLE_MS = 10
MEDIAN_DEVIATION_LIMIT_MV = 250


@dataclass(frozen=True)
class CellSample:
    """One cell's voltage and temperature for one acquisition cycle."""

    channel: str
    module: str
    voltage_mv: int
    temperature_dc: int
    invalid: bool = False


@dataclass(frozen=True)
class SampleSet:
    """One acquisition cycle's worth of samples."""

    timestamp_ms: int
    samples: tuple[CellSample, ...]
    complete: bool


@dataclass(frozen=True)
class LimitViolation:
    """The event the supervisor emits on the first violated limit."""

    channel: str
    limit: Limit
    measured: int
    timestamp_ms: int


class SafetyState(str, Enum):
    RUN = "RUN"
    FAULT_LATCHED = "FAULT_LATCHED"
