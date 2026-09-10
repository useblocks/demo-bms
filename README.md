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
                                     │                       verifies
                                     │                           │
                                   impl                        test
                              (marker in src/)           (marker in tests/)

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
five [risks](specs/_global/risks.rst), five
[design decisions](specs/_global/decisions.rst), the imported
[test results](specs/_global/test_results.rst) and the imported
[workflow gaps](specs/_global/gaps.rst).

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

And it is **in the graph as a need**, not only in a CLI's exit code — see
[Workflow gaps, from the structural gate](#workflow-gaps-from-the-structural-gate).

## Setup

The Python side is managed by [uv](https://docs.astral.sh/uv/), so the
environment is reproducible: [.python-version](.python-version) pins the
interpreter, [uv.lock](uv.lock) pins every package down to its hash, and both
are committed.

```bash
uv sync                              # create .venv from the lock file — exact interpreter, exact pytest
git config core.hooksPath .githooks  # enable the pre-commit hook (see below)
uv run pytest -q                     # run anything inside it
```

`uv sync` needs no pre-installed Python: uv fetches the pinned interpreter
itself. Nothing is installed *from* this repository —
[pyproject.toml](pyproject.toml) declares `package = false`, and the test
modules import the production sources as `src.<stream>.<module>` from the
repository root.

The `ubc` CLI is **not** part of this environment. It ships with the ubCode IDE
extension — see [Commands](#commands). The Sphinx / ubTrace export toolchain is
not part of it either: it lives in the optional `ubtrace` extra, installed with
`uv sync --extra ubtrace` — see
[Publishing to ubTrace](#publishing-to-ubtrace).

### The pre-commit hook

[.githooks/pre-commit](.githooks/pre-commit) brings every
[derived file](#the-generated-spec-files-refresh-themselves) up to date and stages
what moved, so a commit records what CI would produce and CI has nothing left to
change. Git deliberately refuses to install hooks that arrive with a clone, so
this is the one step that cannot be automated away:

```bash
git config core.hooksPath .githooks   # once per clone
```

It re-captures `reports/gaps/gaps.json` too. `ubc` is not on `PATH`, so the hook
resolves it from `$UBC`, then `PATH`, then the newest ubCode extension install,
and warns when the version it found is not the one `UBC_VERSION` pins — a
different engine can produce a different snapshot, which is the bot commit the
hook exists to avoid. It does **not** re-run pytest to recapture
`reports/junit/testresults.xml`, for [the reason that snapshot stays a human
act](#test-results-from-a-static-xml-report).

The hook is **best-effort and never blocks a commit**: every failure path warns
and exits 0 — no `ubc` found, an unusable gap report, an importer refusing a
stale snapshot. It needs no virtualenv, since both importers are
standard-library-only. Skipping the install costs you nothing but a bot commit —
the pipeline refreshes the same files and pushes the result. A hook that could
block a commit would only teach everyone to reach for `--no-verify`.

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

The tests are plain pytest, no dependencies beyond the standard library. Two of
them fail on purpose — see [Two tests are red, on purpose](#two-tests-are-red-on-purpose):

```bash
uv run pytest -q     # 2 failed, 48 passed
```

Both imported artefacts are refreshed the same way — capture a snapshot, then turn
it into needs:

```bash
$UBC agent gaps > reports/gaps/gaps.json || true   # the gate exits 1 when it finds a gap
uv run python tools/import_gaps.py                 # -> specs/_global/gaps.rst
uv run python tools/import_test_results.py         # -> specs/_global/test_results.rst
```

Usually you do not have to: see below.

## The generated spec files refresh themselves

Two of the spec files are **generated and committed**, which is an unusual
combination worth explaining:

| file | generated by | from |
|---|---|---|
| [specs/_global/gaps.rst](specs/_global/gaps.rst) | [tools/import_gaps.py](tools/import_gaps.py) | [reports/gaps/gaps.json](reports/gaps/gaps.json) |
| [specs/_global/test_results.rst](specs/_global/test_results.rst) | [tools/import_test_results.py](tools/import_test_results.py) | [reports/junit/testresults.xml](reports/junit/testresults.xml) |

They are **committed** because a fresh clone has to carry the whole graph: gitignore
them and `ubc check`, `ubc agent *` and the IDE are blind to ~51 of the 194 needs
until somebody remembers to run a script. `ubc` has no pre-build hook, so nothing
could regenerate them on demand for the CLI and the extension the way `conf.py`
could for a Sphinx build.

Being generated *and* committed means they can go stale, and **two independent
mechanisms keep them fresh** instead of one gate that fails when they are not:

1. **the [pre-commit hook](#the-pre-commit-hook)** re-runs both importers and stages
   the result, so the commit you make is already correct;
2. **[the pipeline](#the-graph-gates-run-first)** re-captures the gap snapshot with
   `ubc`, re-runs both importers, and commits whatever changed back to the branch.

So forgetting is free. Both mechanisms cover the same two arrows, so a commit made
with the hook installed leaves CI nothing to change; CI is the backstop for the
commits that bypassed it — and for contributors with no licensed `ubc` to run.

Both importers have a `--check` mode that writes nothing and exits non-zero when
the output is stale. Nothing in CI uses it — it is there for when you want to
*ask* rather than fix.

Why the CI write-back does not loop, and what it costs: the push uses the default
`GITHUB_TOKEN`, and GitHub does not start workflow runs for events raised by that
token — so no `[skip ci]` marker is needed. The price is that the refresh commit,
which becomes the branch tip, carries no checks of its own: on `main` the tip
shows no green tick, and on a PR the checks stay on the superseded head SHA. That
would matter the moment a required status check is added to this repository;
pushing with a GitHub App or PAT token instead reverses the trade at the cost of
one extra run.

That extra run terminates only because the regeneration is **deterministic**:
`ubc agent gaps` output carries no timestamp, hostname or path, and both importers
are pure functions of committed inputs, so a second run finds an empty diff. This
is the real reason the pipeline does **not** run pytest to regenerate
`reports/junit/testresults.xml` — see [Test results, from a static XML
report](#test-results-from-a-static-xml-report).

## Traceability, as a page

[traceability.rst](traceability.rst) is the aggregate view of the graph, and
every line of it is **derived** — nothing on it is hand-maintained, so it cannot
drift from the specs the way a hand-drawn matrix does:

- **the V, per stream** — four `needflow` diagrams, each rooted at that stream's
  user story with `:root_direction: incoming`, so the whole chain below it
  (`req -> arch -> swreq -> impl` / `test -> test_result`) is one picture. Cell
  balancing's diagram stops one level down, which is [the deliberate
  gap](#the-deliberate-gap) showing itself rather than hiding;
- **level by level** — a `needtable` per type carrying the links *out* of that
  level and the links *in* from the level below (`traces_to` / `satisfied_by`,
  `satisfies` / `refined_by`, `refines` / `implements_back` + `verifies_back`,
  …). An empty incoming cell is a coverage gap, visible without running a
  report;
- **gaps, in red** — every level table also carries a `gaps` column, and every
  diagram a red `gap` node hanging off the need it is about. Those are the
  structural gate's own findings, imported back into the graph — see
  [Workflow gaps, from the structural gate](#workflow-gaps-from-the-structural-gate).
  An empty incoming cell says *something might be missing*; a red node says
  *`ubc agent gaps` agrees, and here is which obligation*.

The diagrams are rendered by **graphviz** (`flow_engine = "graphviz"` in
[ubproject.toml](ubproject.toml)), not PlantUML: no Java, no vendored jar, and
the graphviz engine emits a PNG plus an HTML image map — a plain `<img>` with
clickable nodes. That is what survives the ubTrace export, where scripts do not
run and the viewer resolves `<img>` assets only. `dot` must therefore be on
`PATH`; [conf.py](conf.py) fails the build with an explicit message when it is
not, and the workflow installs it.

This page is why the export is worth publishing at all: the needs themselves
carry their links in both directions on their own pages, but nothing *aggregates*
them until something asks the graph a question.

## Publishing to ubTrace

The sources have a **second consumer**. `ubc build needs` compiles
`specs/**/*.rst` plus the one-line codelinks markers in `src/` and `tests/` into
`needs.json` for the CLI and the IDE; [conf.py](conf.py) compiles the *same*
sources through Sphinx into the artefact that
[upload_ubtrace.sh](upload_ubtrace.sh) ships to
[team.useblocks.com](https://team.useblocks.com). Both sides produce the same
193 needs, because neither side owns the data model: the need types, the link
types and the extra options are declared once in
[ubproject.toml](ubproject.toml) and read from there by both — `needs_from_toml`
for the needs, `src_trace_config_from_toml` for the code markers. There is no
second copy of the ontology to keep in sync.

```bash
uv sync --extra ubtrace   # the export toolchain (sphinx-needs, sphinx-codelinks, ubt-sphinx)

uv run --extra ubtrace sphinx-build -b ubtrace -W --keep-going . _build/ubtrace
UBTRACE_INGEST_TOKEN=<token> bash upload_ubtrace.sh
```

`uv run --extra ubtrace sphinx-build -b html . _build/html` renders the same
sources as an ordinary Sphinx site, which is the faster loop while editing.

The `ubtrace` extra is **not** part of the default environment: plain `uv sync`
still installs only the interpreter and pytest. It resolves `ubt-sphinx` (and
its `ubt-runtime` dependency) from the private useblocks index declared as
`[[tool.uv.index]]` in [pyproject.toml](pyproject.toml) — the public PyPI copies
are yanked, so without that index the extra does not resolve at all. Every other
dependency falls through to PyPI.

The ingest token needs **Ingest** permission on the target project. *Where* the
artefact goes is configured in exactly one place, `ubtrace_organization` /
`ubtrace_project` / `ubtrace_version` in [conf.py](conf.py) — currently
`useblocks-rollout` / `rollout-demo-bms` / `main`. The builder writes its output
into `_build/ubtrace/<org>/<project>/<version>/`, and
[upload_ubtrace.sh](upload_ubtrace.sh) *discovers* that path instead of
declaring a second copy of the three values: it publishes whatever the build
produced, and refuses rather than guessing if the build tree holds more than one
version (`UBTRACE_VERSION` picks one, which is how CI publishes a tag).

[.github/workflows/ubtrace.yml](.github/workflows/ubtrace.yml) does all of this
on every push to `main` (publishing as `main`) and on every `v*.*.*` tag
(publishing under the tag name, alongside `main`). A pull request builds the
artefact but never uploads it, so a change that breaks the export is caught
before it lands rather than after it publishes. The workflow needs one
repository secret, `UBTRACE_INGEST_TOKEN`, plus the two ubCode licence secrets
the graph gates need (below).

### The graph gates run first

The workflow has **two jobs**, and `publish` does not start until `graph-gates`
passes. That job runs the `ubc` CLI itself on the runner, via
[useblocks/ubc-action](https://github.com/useblocks/ubc-action) — a composite
action that does nothing but download the binary from `download.useblocks.com`
and put it on `PATH`:

| Step | Blocking? | What it does |
|---|---|---|
| `ubc check` | yes | the specs parse — nothing validated them *as specs* before, the Sphinx build only proved they render |
| refresh the imported artefacts | yes, but only on *breakage* | re-captures [reports/gaps/gaps.json](reports/gaps/gaps.json) from `ubc agent gaps` and re-runs both importers. Fails if `ubc` produces no usable report, or if an importer rejects a **freshly captured** snapshot — never merely because the committed files were stale |
| commit the refresh | yes | pushes what changed back to the branch |
| `ubc agent trace` / `verdict-check` | **no** | reported into the log only |

**What gets published is always one commit.** `graph-gates` names the commit it
validated — the refresh commit when it made one, the triggering commit otherwise —
and `publish` checks out that SHA and asserts it landed on it. Nothing is ever
built from a checkout plus regenerated files carried in beside it, so a version on
team.useblocks.com always corresponds to a commit that exists in this repository.
Where a refresh cannot be pushed (fork PR, tag build, dispatched republish), the
commit is published *as committed*, stale generated files and all — republishing a
tag as something the tag never contained would be worse than republishing it
unchanged.

**Two runs of the same ref never publish at once.** Each job carries its own
concurrency group rather than the workflow carrying one, because they want
opposite policies: `graph-gates` cancels the superseded run (it publishes nothing,
and cancelling it also stops the run before it can reach `publish`), while
`publish` queues and is never cancelled — the upload is a single
`curl -F file=@… ?overwrite=true`, and a request killed halfway is a truncated
archive arriving at an endpoint that overwrites the live version. A
workflow-level `cancel-in-progress` cannot express that split: it cancels the
whole run, upload included.

Every run writes a **job summary** to the run page —
[tools/gate_summary.py](tools/gate_summary.py) renders the gate results, the open
structural gaps, the full trace matrix and the verdict state as markdown tables, so
what the gates found is one click from the commit rather than buried in step logs.
It runs with `if: always()` and is written so that it cannot itself fail: a summary
is worth most exactly when a gate has failed, which is also when its inputs are
likely to be missing or half-written, so every unreadable input renders as a note
instead of an exception.

**It needs a ubCode license.** `ubc` is commercial software and this repository is
private, so the free open-source mode does not apply — ubCode grants that only to
projects under an [OSI licence](https://opensource.org/licenses) in a *publicly
reachable* Git repo, and it probes the remote to decide. Unlicensed, `ubc` caps
indexing at **5 files and 100 needs**; this project has 22 and 194, so every gate
fails with `exceeds maximum without license`. Two repository secrets are required,
and **both** of them — useblocks keys are user-based, so the key does not activate
without the e-mail it was issued to:

| Secret | Becomes |
|---|---|
| `UBCODE_LICENSE_KEY` | `UBCODE_LICENSE_KEY` |
| `UBCODE_LICENSE_USER` | `UBCODE_LICENSE_USER` |

The first step of the job checks they exist and fails naming them, because the
error you get otherwise talks about file counts and never mentions a secret. See
the [licence docs](https://ubcode.useblocks.com/usage/ublicense.html); keys come
from support@useblocks.com. Note the runner is ephemeral, so ubc's three-day
licence cache is always cold and every run performs one online activation.

Three things about it are deliberate:

1. **The ubc version is pinned in the workflow, not left to the action.** The
   action's own default is `0.27.0` and its only tag, `0.1`, is two commits older
   still. `UBC_VERSION` at the top of the workflow has to track whatever
   `ubc --version` says in your ubCode extension, because that is the engine that
   produced the committed snapshots. The action itself is pinned to a full commit
   SHA — a composite action is plain YAML executed inside your job, so a moving
   ref is a moving payload.
2. **`ubc agent gaps` is captured, not obeyed.** It exits non-zero whenever it
   finds a gap, and this project [has one on purpose](#the-deliberate-gap), so its
   exit code would fail every run. The step requires the output to parse as a gap
   report — that is what proves the binary ran — and only then copies it over the
   committed snapshot. It is captured to a temporary file first: redirecting
   straight into the committed file would truncate it before `ubc` wrote a byte,
   so a crashed binary would leave an empty snapshot for the next step to commit.
3. **`trace` and `verdict-check` never block.** `trace` exits non-zero on that same
   deliberate gap, and `verdict-check` goes red the moment anyone edits a
   requirement — which is [the live demo the README recommends](#review-verdicts),
   not a reason to break `main`.

It is also what lets the pipeline **fix** the imported chains instead of
complaining about them: in `reality → snapshot → generated RST → published
artefact`, the first two arrows are re-derived on every run and committed back —
see [The generated spec files refresh
themselves](#the-generated-spec-files-refresh-themselves).

One detail worth knowing: **scripts do not run in the ubTrace export**, so the
three `.. mermaid::` component diagrams cannot be rendered by the browser there.
When the mermaid CLI (`mmdc`) is on `PATH`, [conf.py](conf.py) pre-renders them
to SVG images instead, and the workflow installs it for exactly that reason.

That renderer drives a headless Chromium, which is the one fragile part of the
build: on Ubuntu 23.10+ (so on `ubuntu-latest`) Chromium's sandbox needs
unprivileged user namespaces that AppArmor restricts, and it aborts with "No
usable sandbox!". [mermaid-puppeteer.json](mermaid-puppeteer.json) passes
`--no-sandbox` to get past that — it only ever renders this repository's own
three diagrams. As a second line of defence the workflow *renders a probe
diagram* after installing `mmdc` and uninstalls it again if that fails, which
drops [conf.py](conf.py) back to the raw output: three degraded diagrams and a
published artefact, rather than a failed publish. The diagrams are a nicety; the
traceability artefact is the point.

## Test results, from a static XML report

The suite is **not re-run on every build.**
[reports/junit/testresults.xml](reports/junit/testresults.xml) is a committed
snapshot of one real pytest run, and
[tools/import_test_results.py](tools/import_test_results.py) turns it into one
`test_result` need per JUnit `<testcase>`, each linking `results_for` up to the
`test` need whose execution it records.

```bash
uv run python tools/import_test_results.py            # regenerate the needs from the XML
uv run python tools/import_test_results.py --check    # ask instead: exit non-zero if stale
```

**The snapshot stays a human act**, and this is the one link of the two imported
chains that the pipeline deliberately does not re-derive. JUnit XML stamps a fresh
`timestamp`, `time` and `hostname` on every run, and the importer carries them into
`:test_run_label:` and `:runtime_s:` on all 50 `test_result` needs — so running
pytest in CI would rewrite every one of them on every push, forever, with no
change in meaning. The generated RST *is* refreshed there; the XML it derives from
is not. Capture it by hand when the outcomes actually change:

```bash
uv run pytest -q --junitxml=reports/junit/testresults.xml   # 2 failed, 48 passed
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
`test_run_label`), so they are queryable rather than buried in prose.

### Two tests are red, on purpose

`uv run pytest -q` reports **2 failed, 48 passed**, and the committed report
records those two as `outcome: failed`. The failures are real — the report is not
hand-edited, so running the suite live during a demo tells the same story the
graph does.

Each one is a single-operator boundary defect, planted in the production source
and marked there with a `KNOWN DEFECT` comment:

| Defect | Where | What is wrong |
|---|---|---|
| `IMPL_IMBALANCE_WARNING` | [src/thermal_management/evaluator.py](src/thermal_management/evaluator.py) | `>=` where `SWREQ_IMBALANCE_WARNING` says the warning is set only *above* 8 K, so a spread of exactly 8.0 K raises it |
| `IMPL_CAPACITY_MONOTONIC_CLAMP` | [src/state_estimation/soh_tracker.py](src/state_estimation/soh_tracker.py) | `<=` where `SWREQ_CAPACITY_MONOTONIC_CLAMP` says a candidate is accepted only when *strictly* below, so an equal candidate counts as accepted |

**This is the sharpest beat in the repo.** Both defects leave every structural
gate fully satisfied: the requirement is traced, the architecture satisfies it,
the software requirement refines it, an implementation implements it and a test
verifies it. `ubc agent gaps` is happy. Nothing structural is missing. The only
thing that says the system does not do what the requirement says is the
**recorded outcome** — which is exactly the difference between *traced* and
*verified*, and exactly what a traceability matrix alone cannot tell you.

Ask the graph which requirements have failing evidence and who to blame:

```cypher
MATCH (tr:test_result)-[:results_for]->(t:test)-[:verifies]->(s:swreq)
      -[:refines]->(:arch)-[:satisfies]->(r:req)-[:traces_to]->(u:user_story)
WHERE tr.outcome <> 'passed'
OPTIONAL MATCH (i:impl)-[:implements]->(s)
RETURN u.id AS story, r.id AS req, s.id AS swreq,
       i.id AS impl, tr.outcome AS outcome
```

Four requirements come back red from two failures — the imbalance defect sits
under an architecture element that three requirements share, so one operator
reaches further than it looks. That fan-out is the argument for the graph.

To make the repo fully green instead, flip `>=` back to `>` and `<=` back to
`<`, then re-run the suite and the importer.

### The coverage report

[reports/traceability_coverage.html.j2](reports/traceability_coverage.html.j2) —
render it with `ubc report traceability_coverage.html.j2`, or from the VS Code
Reports view ("Generate & Preview" / "Open in Browser"). Script-free inline SVG,
so the editor preview, a browser and print all look the same.

It answers three questions: what is structurally *missing* from the graph, how many
system requirements have a full chain down to a test, and of those, how many are
backed by passing versus failing tests. Right now: **1 open structural gap**,
**18 / 19** with a chain (94.7 %), and **14 verified vs 4 failing** (3.5 : 1). Both
the gap and the requirement with no evidence are `REQ_CELL_BALANCING_WINDOW`, and
the report shows them as separate facts — the structural half says the rung is
missing, the evidence half says no outcome reaches it. That is the distinction the
page exists to draw.

**One thing to know if you write your own report template.** A template *cannot
walk links.* `ubc report` builds each need in the Jinja context from that need's
scalar fields — `id`, `type`, `title`, `status`, `tags`, `doctype` and the
declared `[[needs.extra_options]]`. Every link field (`satisfies`, `refines`,
`verifies`, `results_for`, …) is **absent**, and incoming links are never
materialised in `needs.json` at all. Reading `n.verifies` yields undefined, and
the idiomatic `(n.verifies or [])` guard turns that into an empty list — so a
link-based coverage template renders perfectly cleanly and reports **0 %
everywhere**. That failure is silent; nothing errors.

This project works around it by moving the answer from a link into a field:
`tools/import_test_results.py` resolves `test → swreq → arch → req` from the spec
sources and stamps the result on each generated `test_result` as `chain_reqs`.
The template then reads a field, which it can see. Derived data, on a derived
need, regenerated on every import — nothing hand-maintained.

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

## Workflow gaps, from the structural gate

`ubc agent gaps` reports every structural hole in the graph as JSON and exits
non-zero. That is a fine gate and a poor *view*: it tells you
`REQ_CELL_BALANCING_WINDOW` has no incoming `satisfies` in a terminal, a long way
from the requirement page where someone is actually reading.

So the findings are imported back **into** the graph.
[reports/gaps/gaps.json](reports/gaps/gaps.json) is a committed snapshot of one
real `ubc agent gaps` run, and [tools/import_gaps.py](tools/import_gaps.py) turns
it into one `gap` need per finding, each linking `gap_for` down to the need the
gate attributed it to:

```bash
$UBC agent gaps > reports/gaps/gaps.json || true
uv run python tools/import_gaps.py            # -> specs/_global/gaps.rst
uv run python tools/import_gaps.py --check    # ask instead: exit non-zero if stale
```

Unlike the JUnit snapshot, **this one the pipeline does re-capture** — `ubc agent
gaps` is deterministic, so re-running it changes the file only when the graph
really changed. Both arrows of this chain are maintained in CI; see
[The generated spec files refresh themselves](#the-generated-spec-files-refresh-themselves).

This is the **exact mirror of `test_result`** on the other arm of the V, and
deliberately so:

| | `test_result` | `gap` |
|---|---|---|
| records | what *happened* when a test ran | what the *gate* found when it ran |
| imported from | `reports/junit/testresults.xml` | `reports/gaps/gaps.json` |
| by | `tools/import_test_results.py` | `tools/import_gaps.py` |
| links | `results_for` → the `test` | `gap_for` → the need with the gap |
| authored by a human or an agent | never | never |

Once a gap is a need, it shows up everywhere the graph does — and it is **red**
(`#EF4444`, the strongest colour in the ontology) in all of them:

- as a red node hanging off its requirement in the `needflow` diagrams on
  [traceability.rst](traceability.rst);
- in the `gaps` column of every level table on the same page;
- as a red-barred need on its own page, and on the incoming-links list of the need
  it is about;
- as the **Open structural gaps** tile and table at the top of
  [the coverage report](#the-coverage-report);
- in the ubTrace export, where the `gap_for` edge is traversable like any other.

The five `gap_*` extra options (`gap_category`, `gap_link`, `gap_shortfall`,
`gap_need_id`, `gap_need_type`) exist for the same reason `chain_reqs` does: a
report template can read fields but cannot follow links, so the `gap_for` link and
the `gap_need_id` field carry the same fact for two different consumers.

Three things about this arrangement are worth knowing before you demo it:

1. **The gap type is produced by no workflow stage, on purpose.** `ubc agent
   config-validate` says so as a warning (`type_unproduced`), and that warning is
   correct: nothing *authors* a gap. It also carries no trace edge and sits in
   `orphan_exempt_types`, because an obligation to carry a gap would make a clean
   graph fail the gap gate — the gate must not grade its own findings.
2. **Importing gaps does not create gaps.** Re-running `ubc agent gaps` after an
   import returns the same list; only `summary.total_needs` moves, which is why
   the generated page deliberately does not quote it. The output is also stable
   run-to-run, which is what lets CI compare it — see
   [The graph gates run first](#the-graph-gates-run-first).
3. **A gap disappears by being fixed.** The ids are derived from the need plus the
   gate that reported it, so re-importing an unchanged snapshot rewrites the same
   bytes, and a resolved gap vanishes instead of lingering under a stale id. Give
   `REQ_CELL_BALANCING_WINDOW` an architecture element, re-snapshot, re-import, and
   [specs/_global/gaps.rst](specs/_global/gaps.rst) becomes an empty page that says
   so.

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
