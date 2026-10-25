# Isolation Monitoring — User Stories

This stream is authored in **Markdown (MyST)** end to end — user story,
requirement, architecture and software requirements — while the other four
streams are reStructuredText. `ubc` and Sphinx index both into the same graph;
the requirements below link to RST needs and RST needs link back to them
without either side noticing the format.

```{user_story} Detect a loss of high-voltage isolation before it becomes a touch hazard
:id: US_ISOLATION_MONITORING
:status: draft

As a fleet operator, I want the battery management system to watch the
insulation between the high-voltage pack and the vehicle chassis, so that a
degrading isolation barrier is reported before anyone can touch a live part.

The capability is observable from the vehicle. The pack raises an isolation
fault whenever the barrier has degraded below the minimum that the applicable
safety standard sets for its voltage.

Out of scope for this story: protecting cells from over-voltage or
over-temperature, and opening the contactors — those reactions belong to the
cell-protection story.
```
