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

Three of these levels are **not authored in this repository**, and that is the
point of the Connectivity-as-Code showcase:

| Level | Master | Arrives as |
|---|---|---|
| `req` — system requirements | Jama Connect, project 59 | acquired by `ubc script sync-jama` |
| `sysml_part` — system architecture | the MBSE tool | `docs/models/bms.sysml`, SysML v2 |
| `swc`, `port_if` — software components | the AUTOSAR tool | `docs/models/bms.arxml`, ARXML |

```
Jama req ◀──satisfies── SysML v2 part          (model owns the link)
    ▲
    └──satisfies[fingerprint]── arch ◀──realizes── AUTOSAR component
                                  ▲               (model owns the link)
                                  └──refines── swreq ◀── impl / test
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

## The system requirements live in Jama

The top of the V is **not authored in this repository**. The 20 system
requirements are owned by the Jama Connect project
[Rollout_Demo](https://useblocks-partner.jamacloud.com/perspective.req#/projects/59/)
and acquired from there by [tools/sync_alm.py](tools/sync_alm.py). Everything
below them — architecture, software requirements, code, tests — is authored here
and links up into the acquired set.

```
Jama project 59 ──from-jama──> docs/_build/alm/needs.json   (raw, thrown away)
                                          │
                              tools/sync_alm.py  (harden + render)
                                          │
              ┌───────────────────────────┴───────────────────────────┐
          mode rst                                              mode external
  docs/specs/_global/alm_requirements.rst                docs/alm/external.json
       20 real `.. req::` blocks                       [[needs.external_needs]]
       ordinary local needs                            read-only by construction
                          ▲                                        ▲
                          └──── arch satisfies · risk mitigates ────┘
```

**Exactly one of the two exists at a time.** Switching modes writes one and
deletes the other, and rewrites the `sync-jama` region of
[docs/ubproject.toml](docs/ubproject.toml) so only the live source is configured
— two sources for the same need ids would collide, and a configured source whose
file is missing is a warning this project treats as fatal.

```bash
ubc script sync-jama            # acquire, KEEPING the mode the tree is in
ubc script sync-jama:rst        # acquire as RST   — round trip — and SWITCH
ubc script sync-jama:external   # acquire as JSON  — read-only  — and SWITCH
```

`sync-jama` and `sync-jama:rst` do the same thing while the tree is already in
rst mode. They differ only when it is not: the bare form keeps the current mode,
the suffixed forms force one.

There is no offline path. `from-jama`'s raw export lands under `_build/`
(gitignored) and is deleted once hardened, so acquiring means reaching Jama.

Credentials are the Jama OAuth client id and secret. They live in `docs/.env`,
which is gitignored; [docs/.env.example](docs/.env.example) records the two
variable names:

```bash
cp docs/.env.example docs/.env && $EDITOR docs/.env
ubc script sync-jama --path docs        # that is all — the sync reads the file
```

**No `source` needed.** `ubc script` does not read `.env` files and neither does
ubConnect, so `tools/sync_alm.py` reads it itself and the child process inherits
it. It looks in `docs/.env`, then `.env` at the repository root, then wherever
`ALM_ENV_FILE` points; a variable already exported in the shell always wins, so a
CI secret is never clobbered by a stale local file.

`docs/` rather than the repository root because that is the ubc project root —
where `ubproject.toml` lives and where `ubc script` runs.

A normal build never needs any of this: the acquired artefact is committed, so a
clone with no credentials still builds, it just cannot re-acquire.

`ALM_OFFLINE=1` in front of any of the four skips the network — `ubc script`
forwards no arguments of its own, so that is how a mode switch happens on a
laptop with no Jama reachable.

### The demo: delete the system level, get it back

```bash
ubc script reset --path docs       # arm it: roll back, delete, clear caches
ubc check docs                     # 35 errors, 67 warnings — everything dangles
ubc script sync-jama --path docs   # re-acquire from Jama
ubc check docs                     # No errors found — byte-identical
```

That is the whole claim of Connectivity-as-Code in one command: **the local copy
is disposable, the ALM is not.**

Because the acquired artefact is normalised — `tools/sync_alm.py` strips the
timestamp `from-jama` stamps on every run and sorts the keys — a sync that
changed nothing produces an **empty** `git diff`. So when the diff is not empty,
something really did move in Jama. That is the change notification the ALM never
sent.

### Resetting between runs

[tools/reset_demo.py](tools/reset_demo.py), wired as a script, puts the tree back
to the starting position:

```bash
ubc script reset:dry --path docs   # print the plan, change nothing
ubc script reset --path docs       # do it (asks first)
ALM_RESET_YES=1 ubc script reset --path docs   # ...without the prompt
```

1. `git reset --hard HEAD` — a requirement someone edited live, a link someone
   broke, a staged experiment: all rolled back.
2. deletes the acquired artefact, so `sync-jama` has something to do.
3. clears `.ub_cache`, `_build`, `__pycache__` and the gitignored `needs.json`
   outputs, so the first `ubc check` of the demo is a real one.

**It discards uncommitted work.** It prints what it is about to destroy and asks
before doing it. Three things it deliberately leaves alone:

| Left alone | Why |
|---|---|
| `docs/alm/crosswalk.json` | the only file the sync cannot rebuild — it holds what Jama does not model |
| `.venv/`, `.env`, untracked files | the cache list is an explicit allowlist, never `git clean -fdx` |
| Jama itself | a local reset cannot undo an edit made in the ALM — change it back in the Jama UI |

### Suspect links: a change in Jama flags what it touched

Every `:satisfies:` link from the architecture to a Jama requirement **pins the
fingerprint** of the requirement it was reviewed against:

```rst
:satisfies: JAMA_Rollout_Demo-SYSRQ-4[fingerprint=="0824db15"]
```

The sync stamps each requirement with 8 hex characters derived from its title and
text (whitespace-insensitive, so a Jama re-wrap raises nothing). When the text
changes in Jama, the next sync moves the fingerprint, and every link still pinned
to the old value fails the sphinx-needs condition — `needs.link_condition_failed`
in `ubc check`, in `sphinx-build -W`, and in the ubCode **Diagnostics** view in
VS Code. That is a suspect link, computed rather than remembered.

```bash
ubc script suspects --path docs         # what changed, and what it reaches
ubc script suspects:accept --path docs  # re-baseline after review
```

```
2 suspect link(s) — 1 requirement changed in Jama since they were reviewed

JAMA_Rollout_Demo-SYSRQ-4   fingerprint now d5efb53d
  SUSPECT  ARCH_CURRENT_PATH_MONITOR   reviewed against 0824db15   specs/cell-protection/architecture.rst:52
  SUSPECT  ARCH_SAFETY_SUPERVISOR      reviewed against 0824db15   specs/cell-protection/architecture.rst:64
  reaches  2 architecture, 4 software requirements, 4 implementations, 8 tests,
           2 AUTOSAR components, 1 SysML v2 part
```

`suspects:accept` rewrites the pinned values and nothing else, so its git diff is
the review record: which link a human confirmed against which version of which
requirement. Only links this repository owns are pinned; a SysML part or an
AUTOSAR component belongs to its model and is reported as reached, never
rewritten.

A second, independent detector comes for free. `ubc agent verdict-check`
fingerprints each review verdict **one hop out**, so when a Jama requirement
changes, the verdicts of the requirement and of every architecture element that
satisfies it go `outdated` by themselves. A pinned link clears with
`suspects:accept`; an outdated verdict clears only with a fresh review — the two
never mask each other.

### The nightly sync

[.github/workflows/sync-jama.yml](.github/workflows/sync-jama.yml) runs the sync
at 02:30 UTC on weekdays. An unchanged Jama gives an empty diff and the job ends;
a change becomes a pull request `sync/jama` whose description carries the diff,
the suspect-link report and the review gate. Nothing lands on main unreviewed, and
the merge is what `ubtrace.yml` then publishes to ubTrace.

It skips with a notice — not a red run — until these repository secrets exist:
`JAMA_USERNAME`, `JAMA_PASSWORD`, `UBCONNECT_LICENSE_KEY`, `UBCONNECT_LICENSE_USER`,
`UBCODE_LICENSE_KEY`, `UBCODE_LICENSE_USER`. Add `SYNC_BOT_TOKEN` (a PAT or GitHub
App token) if the graph gates should run on the bot's pull request: GitHub does
not trigger workflows from a pull request opened with the default token.

**Not yet run in CI.** The workflow is validated locally (YAML, `bash -n`, and the
pull-request description rendered against a simulated Jama change); its first real
run needs the secrets above.

### The two modes

Same 20 requirements, same Jama project, two different things in the repository.

|  | `rst` | `external` |
|---|---|---|
| The one file | `docs/specs/_global/alm_requirements.rst` | `docs/alm/external.json` |
| Lands as | `.. req::` blocks in a generated RST page | nothing — loaded from JSON |
| Need kind | ordinary local needs | external needs, read-only by construction |
| Editable locally | yes, the file is normal RST | **no**, there is no local text at all |
| A reference to one opens | the page in this project | the item in Jama |
| Round trip back to Jama | possible | not possible |
| `ubc` resolves the links | yes | yes — verified with `ubc query cypher` |

The `[[needs.external_needs]]` entry exists only in `external` mode — the sync
writes it into the marked `sync-jama` region of
[docs/ubproject.toml](docs/ubproject.toml) and removes it again on the way back.

Pick `rst` when the requirements are still moving and someone may want to propose
a change from the repository side. Pick `external` when the ALM is the baseline
and local drift must be impossible.

### What the ALM cannot carry

Three things the migration had to solve, all of them normal for an ALM bridge:

| Problem | Where it is solved |
|---|---|
| Jama mints the id (`Rollout_Demo-SYSRQ-4`) and it is read-only there | ids are Jama's, prefixed `JAMA_`; the pre-migration name survives as `:legacy_id:` |
| Jama returns picklists as numbers (`status: 292`) | `[jama_status_labels]` in `docs/ubproject.toml` |
| Jama models no streams and no user stories | re-attached from `docs/alm/crosswalk.json`, keyed on the stable `globalId` |

Requirements flow **down only**. There is deliberately no `[ubconnect.to_jama]`
block anywhere in this repository, so a back-flow is not merely discouraged, it
is unconfigured — the one-time migration that seeded the Jama project ran from a
throw-away config outside this repository.

The acquired artefact is committed, so a normal build never needs Jama to be
reachable; only the sync talks to it, and **its diff is the change notification
Jama never sent**. Run the sync nightly or on merge requests, never per build —
the Jama REST API degrades under continuous sync load.

## System models: SysML v2 and AUTOSAR

The system architecture and the software components are **bridged in from their
modelling tools**, read-only. `docs/models/` holds the tools' exports; the
repository never edits them:

| File | Model | Becomes |
|---|---|---|
| [docs/models/bms.sysml](docs/models/bms.sysml) | SysML v2 textual notation | 6 `sysml_part` needs, 20 `satisfies` links to the Jama requirements |
| [docs/models/bms.arxml](docs/models/bms.arxml) | AUTOSAR classic R4.x | 15 `swc` + 15 `port_if` needs, `realizes` links to the architecture |

[tools/import_models.py](tools/import_models.py) reads both and writes
`docs/models/sysml.json` and `docs/models/autosar.json`, loaded through
`[[needs.external_needs]]`. Every model element opens the model file at the line
that defines it. The links come **from the model**, because the model owns them:

- SysML v2 mirrors each requirement by its Jama id as the element short name —
  `requirement <'JAMA_Rollout_Demo-SYSRQ-4'> packOvercurrent;` — and says which
  subsystem answers it: `satisfy packOvercurrent by cellProtection;`
- AUTOSAR carries the trace in a special data group on each component,
  `<SDG GID="useblocks.Traceability"><SD GID="realizes">ARCH_…</SD></SDG>` —
  the place the AUTOSAR standard defines for tool-specific data.

```bash
ubc script import-models --path docs   # re-read both models (no network)
ubc script trace --path docs           # one requirement through every tool
```

```
sysml_v2               architecture               autosar                      sw_requirement              code
SYSML_CELL_PROTECTION  ARCH_CURRENT_PATH_MONITOR  AR_SWC_CURRENT_PATH_MONITOR  SWREQ_OVERCURRENT_DEBOUNCE  IMPL_OVERCURRENT_DEBOUNCE
SYSML_CELL_PROTECTION  ARCH_SAFETY_SUPERVISOR     AR_SWC_SAFETY_SUPERVISOR     SWREQ_LIMIT_EVALUATION      IMPL_LIMIT_EVALUATION
```

**What this is and is not.** Neither ubConnect nor Sphinx-Needs has a SysML v2 or
an AUTOSAR connector today. The importer is the *pattern*: any model exported as
structured text becomes needs in ~100 lines, and from then on it takes part in
everything the graph does — the trace above, the suspect-link blast radius,
ubTrace. The ARXML reader is complete for what it reads. The SysML v2 reader
handles the subset of the textual notation this model uses and names any line it
cannot place; a production bridge reads the model through the SysML v2 API.

A SysML part's `satisfies` does **not** close the deliberate cell-balancing gap:
the coverage rule counts incoming `satisfies` from `arch` only, so the system model
can cover a requirement the software architecture has not reached yet.

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

[`JAMA_Rollout_Demo-SYSRQ-2`](docs/specs/_global/alm_requirements.rst) —
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

**In VS Code**, the whole ALM loop is in the command palette — `Tasks: Run Task`
lists acquiring from Jama in either mode, the suspect-link report and its accept,
the model import, the cross-tool trace and the showcase reset
([.vscode/tasks.json](.vscode/tasks.json)). Suspect links also appear in the
ubCode sidebar's **Diagnostics** view with *Go to Source*; the inline squiggles
cover syntax problems only.


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
UBC=/home/lrhenisch/.vscode/extensions/useblocks.ubcode-0.31.2-linux-x64/server/cli/ubc

$UBC check docs                             # parse the sources, report RST problems
$UBC build needs docs -o needs.json         # compile the graph into needs.json
$UBC agent status -p docs                      # every stage's state at once
$UBC agent gaps -p docs                        # the trace gate, whole graph
$UBC agent gaps --scope US_CELL_BALANCING -p docs   # ...narrowed to one stream
$UBC agent verdict-check -p docs               # the substance gate (reads verdicts)

$UBC agent audit   --id JAMA_Rollout_Demo-SYSRQ-8 -p docs  # one need, as data
$UBC agent context --id ARCH_SAFETY_SUPERVISOR --no-code -p docs   # its neighbourhood
$UBC agent impact  --id JAMA_Rollout_Demo-SYSRQ-3 -p docs  # what a change reaches
$UBC agent next    --id JAMA_Rollout_Demo-SYSRQ-2 -p docs  # the single next action
$UBC agent prompt  --id JAMA_Rollout_Demo-SYSRQ-2 -p docs  # ...as an agent briefing
```

The tests are plain pytest, no dependencies beyond the standard library. Two of
them fail on purpose — see [Two tests are red, on purpose](#two-tests-are-red-on-purpose):

```bash
uv run pytest -q     # 2 failed, 50 passed
```

The system level is acquired from Jama rather than authored — see
[The system requirements live in Jama](#the-system-requirements-live-in-jama):

```bash
ubc script reset --path docs              # arm the showcase (asks first)
ubc script reset:dry --path docs          # ...print the plan, change nothing
ubc script sync-jama --path docs          # acquire, keeping the current mode
ubc script sync-jama:rst --path docs      # ...as RST, the complete round trip
ubc script sync-jama:external --path docs # ...as read-only JSON
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
`var.*`. [`JAMA_Rollout_Demo-SYSRQ-3`](docs/specs/_global/alm_requirements.rst)
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

[docs/traceability.rst](docs/traceability.rst) is the aggregate view of the graph, and
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
[docs/ubproject.toml](docs/ubproject.toml)), not PlantUML: no Java, no vendored jar, and
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
repository secret, `UBTRACE_INGEST_TOKEN`, plus the two ubCode licence secrets
the graph gates need (below).

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

**It needs a ubCode license.** `ubc` is commercial software and this repository is
private, so the free open-source mode does not apply — ubCode grants that only to
projects under an [OSI licence](https://opensource.org/licenses) in a *publicly
reachable* Git repo, and it probes the remote to decide. Unlicensed, `ubc` caps
indexing at **5 files and 100 needs**; this project has 26 and 205, so every gate
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

One detail worth knowing: **scripts do not run in the ubTrace export**, so the
three `.. mermaid::` component diagrams cannot be rendered by the browser there.
When the mermaid CLI (`mmdc`) is on `PATH`, [docs/conf.py](docs/conf.py) pre-renders them
to SVG images instead, and the workflow installs it for exactly that reason.

That renderer drives a headless Chromium, which is the one fragile part of the
build: on Ubuntu 23.10+ (so on `ubuntu-latest`) Chromium's sandbox needs
unprivileged user namespaces that AppArmor restricts, and it aborts with "No
usable sandbox!". [docs/mermaid-puppeteer.json](docs/mermaid-puppeteer.json) passes
`--no-sandbox` to get past that — it only ever renders this repository's own
three diagrams. As a second line of defence the workflow *renders a probe
diagram* after installing `mmdc` and uninstalls it again if that fails, which
drops [docs/conf.py](docs/conf.py) back to the raw output: three degraded diagrams and a
published artefact, rather than a failed publish. The diagrams are a nicety; the
traceability artefact is the point.

## Test results, from a static XML report

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
the gap and the requirement with no evidence are `JAMA_Rollout_Demo-SYSRQ-2`, and
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
results is `JAMA_Rollout_Demo-SYSRQ-2` — the deliberate gap, showing up as an
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
`JAMA_Rollout_Demo-SYSRQ-2` has no incoming `satisfies` in a terminal, a long way
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
  [docs/traceability.rst](docs/traceability.rst);
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
   `JAMA_Rollout_Demo-SYSRQ-2` an architecture element, re-snapshot, re-import, and
   [docs/specs/_global/gaps.rst](docs/specs/_global/gaps.rst) becomes an empty page that says
   so.

## Review verdicts

The substance gate is data, not prose. Each reviewed type is wired to a criteria
pack in [docs/quality/](docs/quality/) — `requirement.toml` (used by both `req` and
`swreq`), `arch.toml`, `feat.toml`, `decision.toml` — and every verdict under
`docs/.pharaoh/verdicts/` was produced by an independent reviewer context scoring
those axes, then stamped by `ubc agent verdict-submit`.

**Carried over, not re-reviewed, when the requirements moved to Jama.** The 20
requirement verdicts were recorded against the `REQ_*` ids, and the 15
architecture verdicts against links to them; the migration changed both ids, so
the gate reported 20 missing and 15 outdated. Their axes and summaries were
re-submitted unchanged through `ubc agent verdict-submit`, which re-stamps the
fingerprints — justified because the reviewed title and text of all 20
requirements is byte-identical before and after the round trip through Jama
(checked against the pre-migration commit). The `agent` / `model` provenance is
the original reviewer's.

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
