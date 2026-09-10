# Isolation Monitoring — Software Requirements

```{swreq} The isolation monitor component shall compute the isolation ratio as resistance over pack voltage and report it invalid below 50 V
:id: SWREQ_ISOLATION_RATIO
:status: draft
:refines: ARCH_ISOLATION_MONITOR

The isolation monitor component shall compute the isolation ratio as the
measured isolation resistance in ohms divided by the measured pack voltage in
volts, and shall report the ratio as invalid whenever the pack voltage is below
50 V. An invalid ratio carries no value a consumer may compare against a limit.
```

```{swreq} The isolation monitor component shall set the isolation fault flag when a valid isolation ratio is below 500 Ω/V and clear it otherwise
:id: SWREQ_ISOLATION_FAULT_FLAG
:status: draft
:refines: ARCH_ISOLATION_MONITOR

The isolation monitor component shall set the isolation fault flag in every
cycle whose isolation ratio is valid and strictly below 500 Ω/V, and shall
clear it in every other cycle — including every cycle whose ratio is invalid,
so a de-energised pack never reports an isolation fault.
```
