# Plan: simulate an external DOORS requirement source, import it with ubConnect, and map it with Pharaoh

Status: **import + ontology + mapping DONE (2026-09-16).** Remaining: refresh the
four stale review verdicts, refresh the committed gaps snapshot, seed the
`release-check` baseline, and the v2 change-request beat.

Decisions taken during implementation, each forced by something the repo already
enforced rather than chosen freely:

| Question | Answer | Forced by |
|---|---|---|
| Opaque vs readable ids | **Opaque** `SYS_1011` | `id_regex` had to be relaxed either way; deriving ids from the customer's headings would churn every `covers` link on an upstream rename |
| `_global/` vs `_external/` | **`_external/`** | `_global/` is cross-cutting material this project authors; the DOORS layer is neither |
| Which stream left open | **cell-balancing** | already the immature stream (req, no arch), so "behind on architecture and on customer traceability" is one story |
| Forward `covers` rule in schemas.json | **shape only, no `required`** | asserting presence fails `sphinx-build -W`, and the only escape suppresses `sn_schema_error.local_required` for EVERY required-property rule |

The licence blocker was resolved locally: Stefan removed the `check_license`
call from `from_csv` in his ubConnect checkout, so the real CLI runs from source
via `ubconnect-dev`. That edit is **local and uncommitted** in
`~/git/useblocks/ubconnect` — it is not part of this repo and must not be relied
on by anyone else. See the licence section below for what a clean setup needs.

## Goal

Give the demo a credible *upstream*: an OEM system-requirement specification that
lives in DOORS, is exported as CSV, is imported by **ubConnect** into the needs
graph, and whose mapping onto the project's own V-model is done with the
**Pharaoh** agent workflow rather than by hand.

The punchline is the mapping backlog: the external spec contains capabilities this
project has never covered, and the graph says so out loud.

## Confirmed decisions

| Question | Decision |
|---|---|
| Where imported requirements sit | **New top type `sys_req` above `user_story`**, DOORS-owned, never agent-authored. |
| Gating | **Gated trace edge + baselined debt** — unmapped requirements are real gaps, captured into a `release-check` baseline so CI stays green and the demo burns the backlog down live. |
| Second beat | **Yes** — a v2 export (one reworded, one new requirement) drives `ubc agent impact` and the `change-request` cascade. |
| Export format | **CSV** (`ubconnect csv from-csv`), matching `SPLed/doc/ubconnect/csv/`. ReqIF stays available as a later variant. |

## ⚠ Blocker to resolve first: the ubConnect licence

Diagnosed against the local checkout at `~/git/useblocks/ubconnect`. **Not a code
defect** — ubConnect is a *different Cryptolens product* from ubCode:

| | Product id | Source |
|---|---|---|
| ubCode (your key) | **25221** | `ubc license show` |
| ubConnect prod | **25222** | `python/ubconnect/src/ubconnect/license.py` → `PRODUCT_PROD` |
| ubConnect dev | **29960** | same file → `PRODUCT_DEV`, reached via `--license-stage dev` |

I put your ubCode licence into ubConnect's own config location
(`~/Library/Application Support/ubconnect/ubconnect.toml`, same `[license] key/user`
format). The error moved from "No license key or license file provided" to:

```
Requires active license: Could not find the key.
```

That string appears nowhere in `ublicense` — it is Cryptolens' **server** response,
meaning the key does not exist under product 25222. So the config path and file
format are right; only the key is wrong for this product. The gate itself is
deliberate, specified as `comp_req:: Require active license before conversion` in
`docs-internal/source/spec/feature/csv_import.rst`, so there is no supported bypass.

**Two routes:**

1. A ubConnect **prod** key (product 25222).
2. A ubConnect **dev** key (product 29960) with `--license-stage dev` — plausibly the
   intended route here, since the binary in `~/bin` is `0.19.1-dev1`.

**This blocks exactly one step** (`ubconnect csv from-csv`). Everything else can be
built and verified without it, and the checkout lets me validate `import.toml`
against the real `FromCSVConfig` Pydantic model rather than against the docs.
Mitigation, worth doing regardless: the generated `needs.json` is **committed**, so
the demo replays for anyone without a ubConnect licence — the idiom this repo
already uses for `reports/junit/` and `reports/gaps/`.

### Unrelated real bug found in ubconnect (worth a one-line PR)

`python/ubconnect/src/ubconnect/license.py` — `PRODUCT_PROD` carries
`product_id = "25222"`, but its docstring says *"As configured in
https://app.cryptolens.io/Product/Detail/**25221**"*. 25221 is ubCode's product, so
the URL is a copy-paste leftover pointing at the wrong product. Unchanged since the
`8affdaa Basic ubconnect skeleton` commit. Behaviour is correct; only the comment
misleads — which is exactly what cost time here.

## Current baseline (measured)

- `ubc agent gaps`: **205 needs, 1 gap** (`REQ_CELL_BALANCING_WINDOW`, the deliberate one).
- 5 streams, one `user_story` each; 20 `req`, 15 `arch`, 25 `swreq`.
- No gap baseline file exists yet (the release-please plan that would have added one is shelved).

## The pipeline

```
docs/external/doors/bms_sysreqs_v1.csv      mock DOORS export (hand-written)
        │  ubconnect csv from-csv -c import.toml
        ▼
docs/external/doors/needs.json              ubConnect output   (COMMITTED)
        │  python3 tools/import_sysreqs.py
        ▼
docs/specs/_global/system_requirements.rst  sys_req needs      (COMMITTED, generated)
```

A converter script is needed because `from-csv` emits **only** `needs.json` (unlike
`from-reqif`, which can emit RST directly). That is not a workaround — it is this
repo's established idiom for external evidence entering the graph, matching
`tools/import_gaps.py` and `tools/import_test_results.py`, including their
`--check` staleness guard.

## Files to create

| File | Purpose |
|---|---|
| `docs/external/doors/bms_sysreqs_v1.csv` | Mock DOORS export, baseline |
| `docs/external/doors/bms_sysreqs_v2.csv` | Mock DOORS export, changed baseline (beat 2) |
| `docs/external/doors/import.toml` | `[ubconnect.from_csv]` config |
| `docs/external/doors/needs.json` | ubConnect output, committed |
| `tools/import_sysreqs.py` | `needs.json` → RST, with `--check` |
| `docs/specs/_global/system_requirements.rst` | Generated `sys_req` needs |
| `.claude/skills/map-external-requirements/SKILL.md` | The mapping skill (mirrored into `.agents/skills/`) |
| `docs/reports/gaps/accepted-gaps.json` | The ratcheting baseline of accepted debt |

## Files to change

| File | Change |
|---|---|
| `docs/ubproject.toml` | New `sys_req` type, `covers` link, `sys_reqs` stage, trace edge on `user_stories`, `orphan_exempt_types`, a `[scripts]` entry |
| `docs/schemas.json` | `id-prefix-sys_req`, `trace-user_story-covers`, `coverage-sys_req-covers-back` |
| `docs/index.rst` | Toctree entry for the new page |
| `docs/specs/*/user_stories.*` | The mapping itself: a `:covers:` option per story |

## The mock export

Deliberately shaped like a real DOORS classic CSV export, not like our needs:

```csv
Module,Absolute Number,Object Identifier,Object Heading,Object Text,Object Type,Status,ASIL,Verification Method,Satisfied By
/BMS/System Requirements,1042,BMS-SYS-1042,Cell overvoltage protection,"The battery management system shall ...",Requirement,Approved,ASIL C,Test,
```

- **Ids are numeric and opaque** (`SYS_1042`, not `SYS_CELL_OVERVOLTAGE`). This is
  deliberate: nobody can eyeball-map `SYS_1042` onto `US_CELL_PROTECTION`, which is
  precisely what makes the Pharaoh mapping step worth watching. Say the word if you
  would rather have readable ids for stage-demo legibility.
- **DOORS statuses are foreign** (`Approved`, `Proposed`, `Rework`). The project's
  `[needs.fields.status]` enum is strictly `draft | review | approved`, so the
  converter maps them; it does not widen the vocabulary.
- **~24 requirements**: roughly 19 that map onto the five existing streams, and
  **5 that map onto nothing at all** (OTA update, cybersecurity, service
  diagnostics, and two more). Those five are the point — they are the capability
  gap the external spec exposes.

## Ontology changes

```toml
[[needs.types]]
directive = "sys_req"
title = "System Requirement"
prefix = "SYS_"
color = "#94A3B8"     # slate: "not authored here"
style = "artifact"    # VERIFY: unmapped shapes log "Unknown node style",
                      # which -W in ubtrace.yml turns into a failed publish.
                      # Fall back to "file" if unmapped.

[needs.links.covers]
incoming = "covered_by"
outgoing = "covers"
```

A `user_story` **covers** a `sys_req`. Reading the gap out loud — "SYS_1042 has no
incoming `covered_by`" — is exactly "this customer requirement is unmapped".

```toml
[[workflow.stages]]
id = "sys_reqs"
produces = "sys_req"
# NO author_skill, deliberately: this stage is externally owned. The engine must
# never be able to author a customer requirement — it may only map onto one.

[workflow.stages.route]
granularity = "single"
path = "specs/_global/system_requirements.rst"
scope = "global"
```

and `user_stories` gains `depends_on = ["sys_reqs"]` plus:

```toml
[[workflow.stages.trace]]
direction = "both"
link = "covers"
min = 1
up = "sys_req"
```

`direction = "both"` is what creates the backlog in **both** directions: every user
story owes an up-link, and every system requirement owes coverage.

## Expected gap arithmetic

| Point in the demo | Gaps |
|---|---|
| Today | 1 |
| After import, before mapping | ~30 (1 + 24 uncovered `sys_req` + 5 unlinked `user_story`) |
| After Pharaoh maps the five streams | ~6 (1 + the 5 genuinely uncovered requirements) |

Step 2's ~30 go into `docs/reports/gaps/accepted-gaps.json` as accepted debt, so
`ubc agent release-check --baseline` stays green; the ratchet then refuses to
re-admit anything the mapping fixed.

## The Pharaoh showcase

**Beat 1 — the mapping.** A new skill, `map-external-requirements`, driven by
`ubc agent run --skill map-external-requirements` (the engine's documented
targeted-intent path). It reads the uncovered `sys_req` needs and the existing
stories via `ubc agent context`, proposes a `:covers:` option on each story, and
leaves the edit **uncommitted** for human approval — which is the engine's whole
approval model, and the honest answer to "can I trust an agent with my
traceability".

Why a new skill rather than `draft-requirement`: mapping is not authoring. The
existing draft skills create needs; this one only adds links, and must be
forbidden from inventing a `sys_req`.

**Beat 2 — the changed baseline.** Import `bms_sysreqs_v2.csv`, in which one mapped
requirement is reworded and one new one appears. Then:

- `ubc diff` shows what the new export changed;
- `ubc agent impact --id SYS_<reworded>` prints the blast radius down the V — every
  req, arch, swreq, impl and test that depends on it;
- `ubc agent run --skill change-request` cascades the edit down that radius, one
  stage at a time, again uncommitted.

## Verification

0. **`import.toml` against the real model** — the checkout lets me validate it with
   `FromCSVConfig` (`python/ubconnect/src/ubconnect/config/csv_config.py`) directly,
   no licence needed, so the config is known-good before the licensed run. Source
   already confirms the surface the plan relies on: `links` is a
   `dict[str, list[str]]` (relation → one or more columns), `id_prefix = ""` is
   preserved rather than coerced to `CSV_`, and `static_fields` / `mapping` merge
   over defaults rather than replacing them.
1. `ubc agent config-validate` and `ubc agent doctor` — config preflight before anything is authored.
2. `ubc check docs > /dev/null; echo $?` — note the repo's own warning: a piped `ubc check` reports `tail`'s exit code, not its own.
3. `ubc schema validate`.
4. `ubc agent gaps` at each of the three points in the table above, to confirm the arithmetic.
5. `python3 tools/import_sysreqs.py --check` — staleness guard.
6. `uv run --extra ubtrace sphinx-build -W --keep-going` — the `-W` build is what catches an unmapped `style` shape.

## Open questions for you

1. **The licence.** Do you have a ubConnect **prod** key (product 25222), or a **dev**
   key (29960) we can use with `--license-stage dev` on this `-dev1` build? Without
   one I can build and verify everything except the single `ubconnect` invocation,
   and would hand-write the `needs.json` it would have produced (clearly marked) so
   the rest is provable. Running the converter as a library out of your checkout
   would skip the gate, but that is a licensing call for you to make, not me.
2. **Opaque vs readable ids** — `SYS_1042` (authentic, better mapping demo) or
   `SYS_CELL_OVERVOLTAGE` (legible on a projector)?
3. **How far to take the mapping.** Should Pharaoh map all five streams, or should I
   leave one stream unmapped so there is something live to run on stage?
4. **`_global` vs a new `_external` folder** for the generated page. I chose
   `_global/` for consistency with `decisions` / `risks` / `test_results` / `gaps`.
