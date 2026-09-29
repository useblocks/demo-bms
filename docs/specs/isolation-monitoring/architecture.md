# Isolation Monitoring — Architecture

## Elements

```{arch} Isolation Monitor
:id: ARCH_ISOLATION_MONITOR
:status: draft
:satisfies: JAMA_Rollout_Demo-SYSRQ-10

The Isolation Monitor element owns the isolation picture of the pack. Once per
measurement cycle it takes the isolation resistance from the insulation
measurement circuit and the pack voltage from the acquisition chain, reduces
them to one figure — ohm per volt — and derives the isolation fault from it. It
is the only element that reads the insulation measurement circuit, and it never
commands the contactors itself: the fault is published for the vehicle to act
on.
```
