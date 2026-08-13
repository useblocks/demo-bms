# Battery Management System — ubCode / ubTrace demo project

A small but complete everything-as-code project for demoing **ubCode**, **ubTrace**
and the agent workflow. The domain is a Battery Management System (BMS): the
controller that keeps a high-voltage traction battery inside its safe operating
window, reports how much charge is left, and keeps the pack at a usable
temperature.

Nothing here is a real product. Everything here is *shaped* like a real product:
real limits, real timing budgets, real trade-offs, real code, real tests, and
review verdicts that were actually scored rather than rubber-stamped.

## The V-model in this project

Declared in [ubproject.toml](ubproject.toml) under `[workflow]`. Six mandatory
stages plus two optional ones:

```
user_story ──traces_to──> req ──satisfies──> arch ──refines──> swreq
                                                                 │
                                     ┌───────────implements──────┤
                                     │                           │
                                   impl                        test
                              (marker in src/)           (marker in tests/)
                                                                 └──verifies──┘

optional:  risk ──mitigates──> req        decision ──affects──> arch
           test_result ──results_for──> test
```

Both lower arms hang off `swreq`, not off `arch`: the software requirement is the
last level that states testable behaviour, so it is the level code realises and
the level a test can assert against.

`impl` and `test` are **needs-in-source**. A one-line codelinks marker in the
production or test source *is* the need:

```python
# @De-energise both coil channels within 10 ms of the open command, IMPL_CONTACTOR_DEENERGISE, impl, [SWREQ_CONTACTOR_DEENERGISE]
```

Those markers only materialise where a `.. src-trace::` directive names their
project — see [src/code_trace.rst](src/code_trace.rst) and
[tests/code_trace.rst](tests/code_trace.rst).

## Streams

One directory per root user story. Three are decomposed all the way to code and
tests; the fourth is deliberately not.

| Stream | Root story | Depth | What it is good for demoing |
|---|---|---|---|
| [specs/cell-protection/](specs/cell-protection/) | `US_CELL_PROTECTION` | full V | safety-critical reactions, timing budgets, a latched fault state |
| [specs/state-estimation/](specs/state-estimation/) | `US_STATE_ESTIMATION` | full V | accuracy budgets, persistence, a fused estimator |
| [specs/thermal-management/](specs/thermal-management/) | `US_THERMAL_MANAGEMENT` | full V | hysteresis vs. ramps, derating, actuator failsafe |
| [specs/cell-balancing/](specs/cell-balancing/) | `US_CELL_BALANCING` | **requirement only** | **the gap view, and driving the agent workflow live** |

Global, cross-stream artefacts live in [specs/_global/](specs/_global/):
five [risks](specs/_global/risks.rst) and five
[design decisions](specs/_global/decisions.rst).

### The deliberate gap

[`REQ_CELL_BALANCING_WINDOW`](specs/cell-balancing/requirements.rst) —
*"the BMS shall reduce the cell voltage spread to 20 mV or less within 8 hours of
a charge session ending"* — has **no architecture, no software requirements, no
implementation and no tests** beneath it. On purpose.

It is the one non-artificial gap in the graph, so:

- the gap view has something real to show, not a contrived stub;
- `ubc agent next` has a genuine next action to resolve;
- the agent workflow can be driven live, from a requirement whose downstream
  artefacts really do not exist yet.

Everything else in the graph is trace-complete and carries a fresh, passing
review verdict, so this one gap is the only thing the gates complain about.

## Commands

The version-matched CLI is what the IDE extension ships; a bare `ubc` on `$PATH`
may be a different build.

```bash
UBC=/home/lrhenisch/.vscode/extensions/useblocks.ubcode-0.31.2-linux-x64/server/cli/ubc

$UBC check                                  # parse the sources, report RST problems
$UBC build needs                            # compile the graph into needs.json
$UBC agent status -p .                      # every stage's state at once
$UBC agent gaps -p .                        # the trace gate, whole graph
$UBC agent gaps --scope US_CELL_BALANCING -p .   # ...narrowed to one stream
$UBC agent verdict-check -p .               # the substance gate (reads verdicts)

$UBC agent audit   --id REQ_FAULT_LATCH -p .          # one need, as data
$UBC agent context --id ARCH_SAFETY_SUPERVISOR --no-code -p .   # its neighbourhood
$UBC agent impact  --id REQ_CELL_VOLTAGE_LIMITS -p .  # what a change reaches
$UBC agent next    --id REQ_CELL_BALANCING_WINDOW -p . # the single next action
$UBC agent prompt  --id REQ_CELL_BALANCING_WINDOW -p . # ...as an agent briefing
```

The tests are plain pytest, no dependencies beyond the standard library:

```bash
python3 -m pytest -q
```

## Test results, from a static XML report

The suite is **not re-run on every build.**
[reports/junit/testresults.xml](reports/junit/testresults.xml) is a committed
snapshot of one real pytest run, and
[tools/import_test_results.py](tools/import_test_results.py) turns it into one
`test_result` need per JUnit `<testcase>`, each linking `results_for` up to the
`test` need whose execution it records.

```bash
python3 tools/import_test_results.py            # regenerate the needs from the XML
python3 tools/import_test_results.py --check    # CI guard: fail if it is stale
```

The mapping is deterministic, not fuzzy. Every test function carries a marker
above it, so the pair *(test module, function name)* identifies exactly one
`test` need, and the importer joins that pairing against the report's
`classname` / `name` attributes. A `<testcase>` it cannot resolve is a hard
error, never a silent drop.

`test_result` is a separate type from `test` on purpose: a `test` need is the
test case that **exists** (part of the spec, authored as a marker in the source),
a `test_result` is what **happened** the last time it ran. That separation is
what lets the report be replaced by a newer run without touching a single spec
file, and what lets a newly added test legitimately exist with no result yet.
The outcome, runtime and run id are need **fields** (`outcome`, `runtime_s`,
`test_run`), so they are queryable rather than buried in prose.

### The whole V in one query

The point of all of this is that the evidence chain closes inside the graph.
Requirement → architecture → software requirement → test → recorded outcome:

```cypher
MATCH (u:user_story)<-[:traces_to]-(r:req)
OPTIONAL MATCH (r)<-[:satisfies]-(:arch)<-[:refines]-(:swreq)
              <-[:verifies]-(:test)<-[:results_for]-(tr:test_result)
RETURN u.id AS story, r.id AS req,
       count(tr) AS results,
       sum(CASE WHEN tr.outcome = 'passed' THEN 1 ELSE 0 END) AS passed
ORDER BY results, req
```

Run it through the `ubc` MCP server (`query_cypher`). The requirement with zero
results is `REQ_CELL_BALANCING_WINDOW` — the deliberate gap, showing up as an
absence of evidence rather than as a special case anyone had to write down.

> **One quirk worth knowing before you demo.** `ubc agent audit` does not render
> trace edges that touch a codelinks-materialised need, so a `test_result`'s
> `results_for` and a `test`'s incoming `results` both show as empty in that one
> view. The link is real everywhere else: `ubc agent status` counts it (50 / 50
> parents covered), `needs.json` carries it, the gates enforce it, and Cypher
> traverses it. Use `status` or a query, not `audit`, to show that arm.

## Review verdicts

The substance gate is data, not prose. Each reviewed type is wired to a criteria
pack in [quality/](quality/) — `requirement.toml` (used by both `req` and
`swreq`), `arch.toml`, `feat.toml`, `decision.toml` — and every verdict under
`.pharaoh/verdicts/` was produced by an independent reviewer context scoring
those axes, then stamped by `ubc agent verdict-submit`.

Two consequences worth knowing before you demo:

1. **The scores are not all perfect, and that is the point.** Reviewers recorded
   real findings — a requirement that bundles undervoltage and overvoltage, a
   plausibility rule that can mask a genuinely collapsed cell, an overcurrent
   comparison that two architecture elements both appear to own. Each is a
   scored axis with a written suggestion. Only `parent_fit` (and
   `context_present`, for decisions) carries a required floor, so the gate is
   green while the findings stay visible.
2. **A verdict expires when the need changes.** Edit any requirement body and
   its verdict goes `outdated` — a stale green cannot survive an edit. That is
   the cleanest thing in this repo to demonstrate live.
