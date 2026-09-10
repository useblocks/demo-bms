"""Isolation monitor — realises ARCH_ISOLATION_MONITOR.

The one stream of this project whose specification is authored in Markdown
(MyST) rather than reStructuredText — see ``specs/isolation-monitoring/``. The
code is plain Python either way: the one-line markers below are what make these
two functions ``impl`` needs, exactly as in the RST-specified streams.
"""

from __future__ import annotations

from dataclasses import dataclass

#: Below this pack voltage the ratio is meaningless: the divisor is tiny and the
#: barrier is not under a hazardous voltage anyway.
MIN_PACK_VOLTAGE_V = 50.0
#: ISO 6469-1 minimum for a DC high-voltage system.
ISOLATION_LIMIT_OHM_PER_V = 500.0


@dataclass(frozen=True)
class IsolationRatio:
    """The isolation barrier normalised to the voltage it has to hold off."""

    ohm_per_volt: float
    valid: bool


# @Compute the isolation ratio in ohm per volt and mark it invalid below 50 V pack voltage, IMPL_ISOLATION_RATIO, impl, [SWREQ_ISOLATION_RATIO]
def isolation_ratio(resistance_ohm: float, pack_voltage_v: float) -> IsolationRatio:
    """Normalise the measured resistance to the pack voltage."""
    if pack_voltage_v < MIN_PACK_VOLTAGE_V:
        return IsolationRatio(ohm_per_volt=0.0, valid=False)
    return IsolationRatio(ohm_per_volt=resistance_ohm / pack_voltage_v, valid=True)


# @Set the isolation fault flag when a valid ratio is below 500 ohm per volt, IMPL_ISOLATION_FAULT_FLAG, impl, [SWREQ_ISOLATION_FAULT_FLAG]
def isolation_fault(ratio: IsolationRatio) -> bool:
    """Strictly below the limit, and only on a ratio that could be computed."""
    return ratio.valid and ratio.ohm_per_volt < ISOLATION_LIMIT_OHM_PER_V
