---
name: review-feat
description: Review every need this stage produces by scoring it against the criteria in your briefing, and submit one verdict per need.
---

# review-feat

This is the review stage for **user-facing features**: judge every need in
your briefing's `review_needs` set and submit one verdict per need to the
substance gate consumed by `ubc agent verdict-check -p <project path>` and
`ubc agent release-check --with-verdicts -p <project path>`.

This skill carries no fixed rubric and no fixed verdict shape. Both are DATA
this file never hardcodes, so either can change without ever editing it. The
rubric always reaches you as the criteria pack. The verdict shape reaches you
as a derived JSON Schema on the JSON route, and as the shape step 4 states on
the INJECTED route, which carries no schema.

Pass `-p <project path>` on every `ubc agent` command. `<project path>` is the
directory that holds the target `ubproject.toml` (the project the need under
review belongs to). A repository can contain several `ubproject.toml` files,
so without `-p` the command runs against the current directory and can target
the wrong project. Resolve `<project path>` once from the briefing you were
handed and reuse it on every call.

When these instructions say `ubc`, run the exact version-matched `ubc` the
harness named in the task, not a bare `ubc` from your PATH, and never one
you install yourself. With no path given, use the `ubc` on your PATH.

## Execution steps

1. Read your briefing. The REVIEW BRIEFING block names `produces`,
   `verdicts_dir`, `review_needs` and, on each target's line, that target's
   own `reviewed_fingerprint`. `review_needs` is the exact set to review this
   pass. It already excludes any `failing` need, which is re-authored rather
   than re-reviewed, and anything already freshly reviewed. The rubric arrives
   as the separate CRITERIA block (the axes to score, each with a
   `scoring_guide` and `max_score`, plus the pack's overall `guidance` and
   `fingerprint`).
   An INJECTED briefing therefore carries no `verdict_schema`, no
   `submit_command` and no `fingerprints` map, and needs none of them: the
   CRITERIA block plus the verdict shape step 4 states are the whole verdict
   interface, the submit command is spelled out in the INSTRUCTION block, and
   each need's own fingerprint is the `reviewed_fingerprint` on its target
   line.
   If your briefing was not already injected, run
   `ubc agent next --id <need_id> -p <project path>` (optionally
   `--stage <STAGE_ID>`) or `ubc agent review-brief <TYPE> -p <project path>`
   (or `--ids <ID,...>`) and read one JSON object instead, which DOES carry
   `submit_command`, a `fingerprints` map keyed by need id, and
   `verdict_schema`, the exact JSON shape a verdict must match.
2. For each id in `review_needs`, read `ubc agent audit --id <ID> -p <project path>`
   (the oracle, never grep `.rst` source) plus its linked context via
   `ubc agent context --id <ID> --no-code -p <project path>`.
3. Score EVERY axis your briefing's `criteria` lists, from 0 to that axis's
   `max_score`, following its `scoring_guide` and the pack's `guidance`.
   Give a one-line `reason` for every score, and a `suggestion` whenever the
   score is below max.
4. Assemble one verdict object per need: an `axes` map keyed by exactly the
   axis ids `criteria` lists, each scored entry carrying at least `score` and
   `reason`. Also record who
   produced the verdict: set top-level `agent` to your harness (e.g. `copilot`,
   `claude-code`) and `model` to your model id / slug (e.g. `claude-opus-4.8`).
   These are advisory score provenance (#2279) that never gate — include them by
   default, omitting a field only when you genuinely cannot determine it (never
   guess a slug). Submit it
   by PIPING that JSON on stdin to the submit command (a
   `ubc agent verdict-submit <ID> --fingerprint <FINGERPRINT> --criteria-fingerprint <CRITERIA_FINGERPRINT> --file - -p <project path>`
   call, in the INSTRUCTION block on the injected route and in
   `submit_command` on the JSON route): substitute the need id, its
   `<FINGERPRINT>` (that need's `reviewed_fingerprint`, or its entry in the
   `fingerprints` map on the JSON route), and `<CRITERIA_FINGERPRINT>` (the
   criteria `fingerprint`), and feed the verdict JSON on stdin. Do NOT write a
   draft file. `--fingerprint` pins the exact content you reviewed and
   `--criteria-fingerprint` the exact rubric: if the need changed after you scored
   it the submit is REJECTED (`ContentChanged`), and if the criteria pack changed
   it is REJECTED (`CriteriaChanged`) — re-review against the current
   content/criteria and resubmit rather than recording a stale pass. If your host truly cannot pipe, write the
   draft to a system temp path OUTSIDE the repository (e.g. `mktemp`), pass it to
   `--file`, and delete it after — NEVER write a draft anywhere inside the
   repository (the engine reads every `*.json` under `verdicts_dir` as a verdict,
   and `verdict-submit` REFUSES an in-repo `--file` path). That command stamps
   the schema version, the pack name, the criteria fingerprint, and the
   reviewed-content fingerprint itself, then validates before writing the verdict
   under `verdicts_dir` — do NOT hand-stamp any fingerprint yourself.
5. Report: the needs reviewed, and for each, the scores you gave.

## Operating principles

- Use `ubc agent audit --id <ID> -p <project path>` /
  `ubc agent context --id <ID> --no-code -p <project path>`, not file grepping.
  Both verbs exit 1 with "a need id is required" when the id is left off, and
  `context` exits 1 again on a project that resolves a code root unless
  `--no-code` is passed.
- Fail closed: when genuinely uncertain about an axis — including an empty
  or unreadable body — score it 0 and say why in `reason`.
- Exactly one verdict per need. Submitting again for the same id overwrites
  the previous verdict, so re-running this skill is idempotent.
- `ubc agent verdict-check -p <project path>` evaluates the WHOLE graph, so it
  reports `ok: false` and lists OTHER stages' needs as missing while those
  stages are still unreviewed. That is expected and does NOT mean your review
  of this stage failed. Confirm your stage by checking that the needs you
  reviewed appear in NONE of the problem buckets (missing, failing,
  malformed, outdated, unverifiable).
