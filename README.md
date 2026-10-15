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

Declared in [docs/ubproject.toml](docs/ubproject.toml) under `[workflow]`. Six mandatory
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
# @De-energise both coil channels within 10 ms of the open command, IMPL_CONTACTOR_DEENERGISE, [SWREQ_CONTACTOR_DEENERGISE]
```

Title, id, and the link up to the software requirement — the need *type* is not
spelled out. It is the last field of the marker grammar and carries a default
per codelinks project (`[codelinks.projects.*.analyse.oneline_comment_style]` in
[docs/ubproject.toml](docs/ubproject.toml)): everything under `src/` is an
`impl`, everything under `tests/` is a `test`, by construction.

Those markers only materialise where a `.. src-trace::` directive names their
project — see [docs/arms/implementation.rst](docs/arms/implementation.rst) and
[docs/arms/verification.rst](docs/arms/verification.rst).

## Repository layout

```
docs/                     the ubCode project AND the Sphinx source directory
  ubproject.toml          ontology, workflow, codelinks — the one configuration
  conf.py                 Sphinx reads ubproject.toml; nothing is declared twice
  specs/                  the needs, one directory per stream (RST and Markdown)
  arms/                   the two `.. src-trace::` pages that materialise src/ and tests/
  quality/                review criteria packs
  variants/               variant data for the 150 % model
  schemas.json            ontology schema
  .pharaoh/               review verdicts and the agent install manifest
  reports/                report templates and the committed evidence snapshots (JUnit, gaps)
src/  tests/              production and test code, carrying the one-line need markers
  ubproject.redirect.toml one per code tree: "the project is in ../docs"
tools/                    the importers that turn the snapshots into needs
```

Documentation and source code are not mixed at the repository root. That is how
real projects are laid out, and it is the layout the redirect file was invented
for: `ubc` finds a file's configuration by walking **up** from the file until it
meets a `ubproject.toml`, so a marker in `src/` or `tests/` would reach the root
and find nothing. [src/ubproject.redirect.toml](src/ubproject.redirect.toml) and
[tests/ubproject.redirect.toml](tests/ubproject.redirect.toml) send that walk
into `docs/` — for the codelinks markers, and for the VS Code extension editing
a source file. The agent workflow (`ubc agent`, Pharaoh) resolves its project
the same way and keeps its state, `docs/.pharaoh/`, under the project root. The
one consumer that does not follow a redirect (ubc 0.33) is the MCP server, so
[.mcp.json](.mcp.json) points it at `docs/ubproject.toml` explicitly with
`--default-config`.

The other half of the reason is file discovery. With the project at the root,
both Sphinx and ubCode globbed the **whole repository** for `*.rst` (and now
`*.md`), and every new top-level folder — a virtualenv, a cache, a worktree
under `.claude/`, the host-integration directories — had to be excluded by name
in *two* places, or it became a source: a Claude Code worktree under
`.claude/worktrees/` was a second copy of every spec as far as Sphinx was
concerned. Now the source root ubc discovers documents from *is* `docs/`, and
Sphinx's `exclude_patterns` is back to its default plus `_build` and
`.ub_cache`. Isolation of concerns: the docs tree contains only docs, so nothing
outside it can ever leak in.

Three practical consequences. Builds run from the repository root with `docs`
as the source directory (`sphinx-build -b html docs _build/html`). There is
deliberately **no configuration at the repository root**, and a bare `ubc check`
there finds no project and passes silently — so name the project: `ubc check
docs`, `ubc build html docs`, `-p docs` on every `ubc agent` verb, and
`ubc script --path docs <name>` (or simply run `ubc` inside `docs/`; script
output lands in `docs/_build/`). And `-p docs` is not just convenience for
`review-brief` and `verdict-submit`: they print and resolve `verdicts_dir`
relative to `-p`, and the review skills reuse that path.

## Streams

One directory per root user story. Four are decomposed all the way to code and
tests — one of them authored in Markdown rather than RST — and the fifth is
deliberately not.

| Stream | Root story | Depth | What it is good for demoing |
|---|---|---|---|
| [docs/specs/cell-protection/](docs/specs/cell-protection/) | `US_CELL_PROTECTION` | full V | safety-critical reactions, timing budgets, a latched fault state |
| [docs/specs/state-estimation/](docs/specs/state-estimation/) | `US_STATE_ESTIMATION` | full V | accuracy budgets, persistence, a fused estimator |
| [docs/specs/thermal-management/](docs/specs/thermal-management/) | `US_THERMAL_MANAGEMENT` | full V | hysteresis vs. ramps, derating, actuator failsafe |
| [docs/specs/cell-balancing/](docs/specs/cell-balancing/) | `US_CELL_BALANCING` | **requirement only** | **the gap view, and driving the agent workflow live** |
| [docs/specs/isolation-monitoring/](docs/specs/isolation-monitoring/) | `US_ISOLATION_MONITORING` | full V, **in Markdown (MyST)** | RST and Markdown in one graph |

Global, cross-stream artefacts live in [docs/specs/_global/](docs/specs/_global/):
five [risks](docs/specs/_global/risks.rst), five
[design decisions](docs/specs/_global/decisions.rst), the imported
[test results](docs/specs/_global/test_results.rst) and the imported
[workflow gaps](docs/specs/_global/gaps.rst).

### The deliberate gap

[`REQ_CELL_BALANCING_WINDOW`](docs/specs/cell-balancing/requirements.rst) —
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
uv sync          # create .venv from the lock file — exact interpreter, exact pytest
uv run pytest -q # run anything inside it
```

`uv sync` is the only setup step. It needs no pre-installed Python: uv fetches
the pinned interpreter itself. Nothing is installed *from* this repository —
[pyproject.toml](pyproject.toml) declares `package = false`, and the test
modules import the production sources as `src.<stream>.<module>` from the
repository root.

The `ubc` CLI is **not** part of this environment. It ships with the ubCode IDE
extension — see [Commands](#commands). The Sphinx / ubTrace export toolchain is
not part of it either: it lives in the optional `ubtrace` extra, installed with
`uv sync --extra ubtrace` — see
[Publishing to ubTrace](#publishing-to-ubtrace).

## Commands

The version-matched CLI is what the IDE extension ships; a bare `ubc` on `$PATH`
may be a different build.

```bash
# The CLI bundled with your ubCode extension — version and platform vary:
UBC=~/.vscode/extensions/useblocks.ubcode-<version>-<platform>/server/cli/ubc

$UBC check docs                             # parse the sources, report RST problems
$UBC build needs docs -o needs.json         # compile the graph into needs.json
$UBC agent status -p docs                      # every stage's state at once
$UBC agent gaps -p docs                        # the trace gate, whole graph
$UBC agent gaps --scope US_CELL_BALANCING -p docs   # ...narrowed to one stream
$UBC agent verdict-check -p docs               # the substance gate (reads verdicts)

$UBC agent audit   --id REQ_FAULT_LATCH -p docs          # one need, as data
$UBC agent context --id ARCH_SAFETY_SUPERVISOR --no-code -p docs   # its neighbourhood
$UBC agent impact  --id REQ_CELL_VOLTAGE_LIMITS -p docs  # what a change reaches
$UBC agent next    --id REQ_CELL_BALANCING_WINDOW -p docs # the single next action
$UBC agent prompt  --id REQ_CELL_BALANCING_WINDOW -p docs # ...as an agent briefing
```

The tests are plain pytest, no dependencies beyond the standard library. Two of
them fail on purpose — see [Two tests are red, on purpose](#two-tests-are-red-on-purpose):

```bash
uv run pytest -q     # 2 failed, 50 passed
```

Both imported artefacts are refreshed the same way — capture a snapshot, then turn
it into needs:

```bash
$UBC agent gaps -p docs > docs/reports/gaps/gaps.json || true   # the gate exits 1 when it finds a gap
uv run python tools/import_gaps.py                 # -> docs/specs/_global/gaps.rst
uv run python tools/import_gaps.py --check         # CI guard: fail if it is stale
```

## Variants: the 150 % model

The specification describes more than one product. The pack chemistry is the
axis: [docs/variants/nmc.json](docs/variants/nmc.json) is the default profile and
[docs/variants/lfp.json](docs/variants/lfp.json) the alternative, wired through
`[needs] variant_data_file` in [docs/ubproject.toml](docs/ubproject.toml) and exposed as
`var.*`. [`REQ_CELL_VOLTAGE_LIMITS`](docs/specs/cell-protection/requirements.rst)
is the one requirement that reads it: its limits are `:variant:` references
resolved from the profile, its `chemistry` field is injected with
`<{ var.pack.chemistry }>`, and an `.. if::` block on the same page only
renders for the LFP profile. Nothing else in the graph depends on the variant,
so the diff between the two builds is exactly that one need:

```bash
ubc script --path docs variant-diff   # ubc diff -c "needs.variant_data_file = 'variants/lfp.json'"
ubc script --path docs needs:lfp      # the LFP graph as docs/needs.lfp.json
```

To flip the **whole project** — the IDE, every command, the Sphinx build — swap
the commented `variant_data_file` line in [docs/ubproject.toml](docs/ubproject.toml)
instead; the extension re-indexes on save and the cell-protection page reads
3.65 V. Two resolution rules to know (ubc 0.33): a path given with `-c` is
resolved against the **working directory**, not the toml, and a variant data
file that is not found resolves *silently* — no warning, every `var.*` value
empty — which is why the scripts above run in `docs/`. Sphinx is the other way
round: `-D needs_variant_data_file=variants/lfp.json` resolves against the
source directory, so it works from the repository root, and a wrong path fails
the build loudly.
Per-variant *file* selection (`[[source.variant_sources]]`) is deliberately not
used: the Sphinx side honours it only with `sphinx-mounts` installed, and the
`-W` publish must build the same document set as `ubc`. The implementation and
verification arms in this repository are the NMC build.

ubTrace gets every variant: `[ubtrace.variants]` in
[docs/ubproject.toml](docs/ubproject.toml) lists each one with its data file and
its ubTrace `dimensions`, and CI builds and uploads one artefact per entry.

## Markdown next to RST

[docs/specs/isolation-monitoring/](docs/specs/isolation-monitoring/) is a complete stream
— user story, requirement, architecture element, software requirements —
authored in Markdown (MyST) instead of reStructuredText, traced to
[src/isolation_monitoring/](src/isolation_monitoring/) and its tests through
the same one-line markers as every other stream. `ubc` routes `docs/specs/**/*.md`
to its MyST parser (`[parse.parsers.md]` in docs/ubproject.toml, scoped so no other
Markdown in the repository is ever parsed as a document); Sphinx renders it
through `myst_parser`. The importers under [tools/](tools/) read both
spellings, so a gap or a test chain resolves through a Markdown need exactly as
through an RST one.

## Traceability, as a page

[docs/specs/_global/traceability.rst](docs/specs/_global/traceability.rst) is the aggregate view of the graph, and
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
[docs/ubproject.toml](docs/ubproject.toml)), not PlantUML, because
the graphviz engine emits a PNG plus an HTML image map — a plain `<img>` with
clickable nodes. That is what survives the ubTrace export, where scripts do not
run and the viewer resolves `<img>` assets only. `dot` must therefore be on
`PATH`; [docs/conf.py](docs/conf.py) fails the build with an explicit message when it is
not, and the workflow installs it.

This page is why the export is worth publishing at all: the needs themselves
carry their links in both directions on their own pages, but nothing *aggregates*
them until something asks the graph a question.

## Publishing to ubTrace

The sources have a **second consumer**. `ubc build needs` compiles
`docs/specs/**/*.rst` plus the one-line codelinks markers in `src/` and `tests/` into
`needs.json` for the CLI and the IDE; [docs/conf.py](docs/conf.py) compiles the *same*
sources through Sphinx into the artefact that
[upload_ubtrace.sh](upload_ubtrace.sh) ships to
[team.useblocks.com](https://team.useblocks.com). Both sides produce the same
205 needs, because neither side owns the data model: the need types, the link
types and the extra options are declared once in
[docs/ubproject.toml](docs/ubproject.toml) and read from there by both — `needs_from_toml`
for the needs, `src_trace_config_from_toml` for the code markers. There is no
second copy of the ontology to keep in sync.

```bash
uv sync --extra ubtrace   # the export toolchain (sphinx-needs, sphinx-codelinks, ubt-sphinx)

uv run --extra ubtrace sphinx-build -b ubtrace -W --keep-going docs _build/ubtrace
UBTRACE_INGEST_TOKEN=<token> bash upload_ubtrace.sh
```

`uv run --extra ubtrace sphinx-build -b html docs _build/html` renders the same
sources as an ordinary Sphinx site, which is the faster loop while editing.

The `ubtrace` extra is **not** part of the default environment: plain `uv sync`
still installs only the interpreter and pytest. It resolves `ubt-sphinx` (and
its `ubt-runtime` dependency) from the private useblocks index declared as
`[[tool.uv.index]]` in [pyproject.toml](pyproject.toml) — the public PyPI copies
are yanked, so without that index the extra does not resolve at all. Every other
dependency falls through to PyPI.

The ingest token needs **Ingest** permission on the target project. *Where* the
artefact goes is configured in exactly one place, `ubtrace_organization` /
`ubtrace_project` / `ubtrace_version` in [docs/conf.py](docs/conf.py) — currently
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
repository secret, `UBTRACE_INGEST_TOKEN`. It needs no ubCode licence secret:
this repository is public and MIT-licensed, so `ubc` runs in its free
open-source mode (below).

### The graph gates run first

The workflow has **two jobs**, and `publish` does not start until `graph-gates`
passes. That job runs the `ubc` CLI itself on the runner, via
[useblocks/ubc-action](https://github.com/useblocks/ubc-action) — a composite
action that does nothing but download the binary from `download.useblocks.com`
and put it on `PATH`:

| Step | Blocking? | What it defends |
|---|---|---|
| `ubc check` | yes | the specs parse — nothing validated them *as specs* before, the Sphinx build only proved they render |
| gap snapshot vs. reality | yes | [docs/reports/gaps/gaps.json](docs/reports/gaps/gaps.json) still matches what `ubc agent gaps` actually reports |
| `import_gaps.py --check` / `import_test_results.py --check` | yes | the generated RST still matches its snapshot |
| `ubc agent trace` / `verdict-check` | **no** | reported into the log only |

Every run writes a **job summary** to the run page —
[tools/gate_summary.py](tools/gate_summary.py) renders the gate results, the open
structural gaps, the full trace matrix and the verdict state as markdown tables, so
what the gates found is one click from the commit rather than buried in step logs.
It runs with `if: always()` and is written so that it cannot itself fail: a summary
is worth most exactly when a gate has failed, which is also when its inputs are
likely to be missing or half-written, so every unreadable input renders as a note
instead of an exception.

**No ubCode license is needed.** This repository is public and MIT-licensed, so
`ubc` runs in its free open-source mode — ubCode grants that to projects under an
[OSI licence](https://opensource.org/licenses) in a *publicly reachable* Git repo,
and it probes the remote to decide. Without it, `ubc` caps indexing at **5 files
and 100 needs**; this project has 26 and 205, so the gates would fail with
`exceeds maximum without license`. The workflow passes no licence credentials and
none need to be configured. See the
[licence docs](https://ubcode.useblocks.com/usage/ublicense.html). Note the runner
is ephemeral, so ubc's licence cache is always cold and every run performs one
online licence check.

Three things about it are deliberate:

1. **The ubc version is pinned in the workflow, not left to the action.** The
   action's own default is `0.27.0` and its only tag, `0.1`, is two commits older
   still. `UBC_VERSION` at the top of the workflow has to track whatever
   `ubc --version` says in your ubCode extension, because that is the engine that
   produced the committed snapshots. The action itself is pinned to a full commit
   SHA — a composite action is plain YAML executed inside your job, so a moving
   ref is a moving payload.
2. **`ubc agent gaps` is compared, not obeyed.** It exits non-zero whenever it
   finds a gap, and this project [has one on purpose](#the-deliberate-gap), so its
   exit code would fail every run. The gate requires the output to parse as a gap
   report — that is what proves the binary ran — and then requires it to be
   byte-identical to the committed snapshot.
3. **`trace` and `verdict-check` never block.** `trace` exits non-zero on that same
   deliberate gap, and `verdict-check` goes red the moment anyone edits a
   requirement — which is [the live demo the README recommends](#review-verdicts),
   not a reason to break `main`.

This closes the last open link in both imported chains. `reality → snapshot →
generated RST → published artefact` was only gated from the second arrow onwards;
until `ubc` could run on the runner, nothing in CI could tell whether the
committed snapshot still described reality.

One detail worth knowiOne detail worth knowing: **scripts do not run in the ubTrace export**, so the
three `.. needuml::` component diagrams under `docs/specs/*/architecture.rst`
are rendered by PlantUML at build time and embedded as plain SVG `<img>` tags
(`plantuml_output_format = "svg_img"` in [docs/conf.py](docs/conf.py)). Each architecture
element is drawn with `{{flow("ARCH_…")}}`, so its title, id and colour come from
the need itself and cannot drift from the spec. The price of `<img>` is that the
need links inside the SVG are not clickable. `plantuml` (and therefore Java) must
be on `PATH`; [docs/conf.py](docs/conf.py) fails the build with an explicit message when
it is not, and the workflow installs a pinned release jar.

a static XML report

The suite is **not re-run on every build.**
[docs/reports/junit/testresults.xml](docs/reports/junit/testresults.xml) is a committed
snapshot of one real pytest run, and
[tools/import_test_results.py](tools/import_test_results.py) turns it into one
`test_result` need per JUnit `<testcase>`, each linking `results_for` up to the
`test` need whose execution it records.

```bash
uv run python tools/import_test_results.py            # regenerate the needs from the XML
uv run python tools/import_test_results.py --check    # CI guard: fail if it is stale
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

`uv run pytest -q` reports **2 failed, 50 passed**, and the committed report
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

[docs/reports/traceability_coverage.html.j2](docs/reports/traceability_coverage.html.j2) —
render it with `ubc report traceability_coverage.html.j2`, or from the VS Code
Reports view ("Generate & Preview" / "Open in Browser"). Script-free inline SVG,
so the editor preview, a browser and print all look the same.

It answers three questions: what is structurally *missing* from the graph, how many
system requirements have a full chain down to a test, and of those, how many are
backed by passing versus failing tests. Right now: **1 open structural gap**,
**19 / 20** with a chain (95.0 %), and **15 verified vs 4 failing**. Both
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
[docs/reports/gaps/gaps.json](docs/reports/gaps/gaps.json) is a committed snapshot of one
real `ubc agent gaps` run, and [tools/import_gaps.py](tools/import_gaps.py) turns
it into one `gap` need per finding, each linking `gap_for` down to the need the
gate attributed it to:

```bash
$UBC agent gaps > docs/reports/gaps/gaps.json || true
uv run python tools/import_gaps.py            # -> docs/specs/_global/gaps.rst
uv run python tools/import_gaps.py --check    # CI guard: fail if it is stale
```

This is the **exact mirror of `test_result`** on the other arm of the V, and
deliberately so:

| | `test_result` | `gap` |
|---|---|---|
| records | what *happened* when a test ran | what the *gate* found when it ran |
| imported from | `docs/reports/junit/testresults.xml` | `docs/reports/gaps/gaps.json` |
| by | `tools/import_test_results.py` | `tools/import_gaps.py` |
| links | `results_for` → the `test` | `gap_for` → the need with the gap |
| authored by a human or an agent | never | never |

Once a gap is a need, it shows up everywhere the graph does — and it is **red**
(`#EF4444`, the strongest colour in the ontology) in all of them:

- as a red node hanging off its requirement in the `needflow` diagrams on
  [docs/specs/_global/traceability.rst](docs/specs/_global/traceability.rst);
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
   [docs/specs/_global/gaps.rst](docs/specs/_global/gaps.rst) becomes an empty page that says
   so.

## Review verdicts

The substance gate is data, not prose. Each reviewed type is wired to a criteria
pack in [docs/quality/](docs/quality/) — `requirement.toml` (used by both `req` and
`swreq`), `arch.toml`, `feat.toml`, `decision.toml` — and every verdict under
`docs/.pharaoh/verdicts/` was produced by an independent reviewer context scoring
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

## License

[MIT](LICENSE) © useblocks GmbH
