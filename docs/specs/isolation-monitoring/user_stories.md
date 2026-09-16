# Isolation Monitoring — User Stories

This stream is authored in **Markdown (MyST)** end to end — user story,
requirement, architecture and software requirements — while the other four
streams are reStructuredText. `ubc` and Sphinx index both into the same graph;
the requirements below link to RST needs and RST needs link back to them
without either side noticing the format.

```{user_story} Detect a loss of high-voltage isolation before it becomes a touch hazard
:id: US_ISOLATION_MONITORING
:status: draft
:covers: SYS_1051, SYS_1052

As a fleet operator, I want the battery management system to watch the
insulation between the high-voltage pack and the vehicle chassis, so that a
degrading isolation barrier is reported before anyone can touch a live part.

The capability is observable from the vehicle. The dashboard shows an isolation
fault, and the diagnostic interface reports the measured isolation resistance,
so a workshop can confirm the finding with a hand-held insulation tester.

Out of scope for this story: protecting cells from over-voltage or
over-temperature, and opening the contactors — those reactions belong to the
cell-protection story.
```
