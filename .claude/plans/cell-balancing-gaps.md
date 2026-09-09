# Plan: close the two open gaps on `REQ_CELL_BALANCING_WINDOW`

Status: **proposal** (drafted 2026-09-09, nothing implemented)

## Where the gaps come from

The last `ubTrace publish` run — [run #17](https://github.com/useblocks/rollout-demo-bms/actions/runs/34372761292),
job *Graph gates (ubc)* — passed, and its *The gap snapshot still matches reality*
step confirmed that `reports/gaps/gaps.json` is byte-identical to what
`ubc agent gaps` reports today. So the committed snapshot **is** the current
state, and it says:

```
total_needs: 195, total_gaps: 2, ok: false
```

Both gaps sit on the same need, `REQ_CELL_BALANCING_WINDOW` in
[specs/cell-balancing/requirements.rst](../../specs/cell-balancing/requirements.rst):

| # | Category | Link | Shortfall | Owning stage |
|---|---|---|---|---|
| 1 | `trace_backward` | `satisfies` | 0 of 1 | `archs` |
| 2 | `review` | `review` | 0 of 1 | `reqs` (review arm) |

Neither is a tooling defect. Both are real, and they have **different causes**,
which is why they need two different remedies.

### Gap 1 — nothing `satisfies` the requirement

`[[workflow.stages]] id = "archs"` declares a **bidirectional** trace edge
(`link = "satisfies"`, `up = "req"`, `min = 1`), so every `req` owes an incoming
`satisfies` from at least one `arch`. The `cell-balancing` stream contains only
`user_stories.rst` and `requirements.rst` — no `architecture.rst`, and therefore
no `arch` element pointing at the requirement. The stream is deliberately
undecomposed (the file says so in its own note), so this gap is the intended
demo gap, not an accident.

Because the edge is bidirectional, the gate attributes the shortfall to the
`archs` stage rather than to the requirement's own stage, so
`ubc agent next --id REQ_CELL_BALANCING_WINDOW` will name `archs` as the stage
that owes the artefact.

### Gap 2 — the review gate is not satisfied

A verdict for this need **does exist** at
`.pharaoh/verdicts/REQ_CELL_BALANCING_WINDOW.json` — six scored axes, a written
summary, `parent_fit: 2`. It does not count, because the verdict carries a
`reviewed_fingerprint` of the need it graded, and the requirement body has since
been edited (its last line, *"Change this requirement to see if the gates catch
the change."*, is the edit). A verdict whose fingerprint no longer matches the
need is `outdated`, and an outdated verdict is worth zero to the gate — exactly
the behaviour the README advertises under *Review verdicts*, point 2.

So this gap is **not** "nobody reviewed it". It is "the review that exists graded
different text". Confirm with `ubc agent verdict-check -p .`, which reports the
verdict's state rather than just its presence.

## Proposed remedy

Work the two gaps in this order. Gap 2 first: the review's own findings change
what the architecture in gap 1 has to be designed against, so closing gap 1 first
risks designing to a requirement that the re-review then moves.

### Step 1 — re-review the requirement (closes gap 2)

Drive it through the harness rather than by hand:

```
ubc agent prompt --id REQ_CELL_BALANCING_WINDOW -p .
```

This resolves to the `reqs` stage review arm and prints the `review-requirement`
briefing, whose axes come from [quality/requirement.toml](../../quality/requirement.toml).
Two rules from `.claude/commands/ubc-agent-next.md` that matter here:

- Run the review in a **context separate** from the one that authored or edited
  the requirement — a subagent or a fresh task. Nothing enforces this; the engine
  cannot see which context you used.
- Submit by piping the verdict JSON to `ubc agent verdict-submit -p .`. Never
  write into `.pharaoh/verdicts/` directly and never stamp a fingerprint by hand,
  or the verdict counts as outdated forever.

The existing verdict is not wasted: its `feasibility`, `unambiguity` and
`verifiability` axes each scored 1 and carry concrete suggestions (bound the
initial spread the 8-hour window applies to, quantify "at rest", say what happens
when a precondition breaks mid-window). Those findings are still valid against
the current text.

**Decision needed before this step:** do we re-review the requirement as written,
or first amend it to take up those three suggestions? Amending is the better
engineering answer — an unbounded entry spread against an 8-hour deadline is a
genuine hardware implication, and it is the kind of thing that should be settled
before any architecture is drawn. But amending is a *change* to a reviewed need,
so it must go through `change-request` so the cascade is visible, and it will
invalidate the verdict again — meaning the review has to be the last action
either way.

### Step 2 — author the architecture (closes gap 1)

```
ubc agent prompt --id REQ_CELL_BALANCING_WINDOW -p .
```

With the review gate closed, the same command now resolves to the `archs` stage,
routed to `specs/cell-balancing/architecture.rst` (per-root, per-stream), with the
`draft-arch` skill. The artefact owes:

- One or more `arch` needs, each `:satisfies: REQ_CELL_BALANCING_WINDOW`. One
  element per distinct responsibility — realistically a balancing-decision
  element (which cells to bleed, from settled voltages) and a balancing-actuator
  element (driving the shunt paths, and the safety interlocks around them),
  though the drafting step should decide that, not this plan.
- A `.. mermaid::` component overview, matching the three existing streams.
  `[workflow.diagram]` has `enabled = false` (no gate) but `format = "mermaid"`,
  so the format is project policy even though nothing enforces it.

Follow the shape of [specs/thermal-management/architecture.rst](../../specs/thermal-management/architecture.rst):
a *Component overview* diagram, then an *Elements* section.

### Step 3 — review the architecture

Authoring an `arch` immediately opens a new review gap against the `archs`
stage's own `review-arch` skill. This is expected and is not a regression — a
newly authored need that nobody has graded is honestly reported as a gap. Same
separate-context rule, same `verdict-submit` path.

### Step 4 — refresh the snapshots and the generated page

The gap report is a **committed snapshot**, and CI diffs it byte-for-byte:

```
ubc agent gaps > reports/gaps/gaps.json
python3 tools/import_gaps.py
```

Gap ids are derived from the need plus the gate that reported it, so a resolved
gap vanishes rather than lingering under a stale id. Verify locally with the same
two commands CI runs:

```
python3 tools/import_gaps.py --check
python3 tools/import_test_results.py --check
```

## Scope boundary — what this plan deliberately stops short of

Closing gaps 1 and 2 leaves the `cell-balancing` stream still undecomposed below
architecture: `swreqs`, `code` and `tests` will each open their own gaps the
moment an `arch` exists, because all three carry bidirectional trace edges.
Running the stream all the way to green means:

`archs` → review → `swreqs` → review → `code` (impl markers in `src/`) → `tests`
(test markers in `tests/`) → re-snapshot.

That is a much larger change than the two gaps asked about, and it would **remove
the repo's only real structural gap** — the thing
[specs/_global/gaps.rst](../../specs/_global/gaps.rst), the red nodes in every
`needflow`, and the non-empty `gaps` column on `/traceability` all exist to
demonstrate. The README calls this stream deliberately undecomposed for exactly
that reason.

**Recommendation:** treat this as a decision for the repo owners rather than
something to just do.

| Option | Effect |
|---|---|
| **A. Fix gap 2 only** (re-review) | Restores the substance gate to honest green, keeps the structural demo gap intact. Smallest change. |
| **B. Fix both gaps** | Adds the architecture layer; the demo gap moves *down* one level (to `swreqs`) rather than disappearing — arguably a better demo, since it shows the workflow advancing. |
| **C. Decompose the stream fully** | `ubc agent gaps` goes green and `ok: true`. The gap view becomes an empty page. Only worth doing if the demo is being retired or re-seeded elsewhere. |

Option **B** is the recommendation: it is what the problem statement literally
asks for, it leaves the demo with a live gap to show, and it exercises the
harness end-to-end on a real stream.

## Effect on CI

None of the four steps changes the workflow. `graph-gates` blocks on three
things — `ubc check`, the gap snapshot matching reality, and the importers'
`--check` modes — and step 4 is what keeps the second and third green.
`ubc agent trace` and `ubc agent verdict-check` stay informational: they exit
non-zero on the deliberate gap and on any edited requirement, which is why the
workflow reports them into the job summary rather than gating on them.
