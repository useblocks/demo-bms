---
name: drive-workflow
description: Author the NEXT workflow stage (one step) with the ubc agent heartbeat verbs, then report what is next. Does NOT run the whole workflow.
---

# Drive the next workflow stage

Use this skill to advance the workflow by exactly ONE stage, then stop and hand
control back to the user. Do NOT loop through the whole workflow: work the single next
action, run its independent review, confirm it, report what comes next, and stop.
The user decides when to drive the next stage.

This single-stage boundary is a hard safety rule. If the wording is ambiguous
(for example, "follow the loop"), interpret it as: complete one full stage cycle
(`prompt`, act on it, review, `gaps`, `next`, report) and then stop.

Pass `-p <project path>` on every `ubc agent` command. `<project path>` is the
directory that holds the target `ubproject.toml` (the project the need you are
driving belongs to). A repository can contain several `ubproject.toml` files,
so without `-p` the command runs against the current directory and can target
the wrong project. Resolve `<project path>` once from the need or file you
were handed and reuse it on every call in this stage.

When these instructions say `ubc`, run the exact version-matched `ubc` the
harness named in the task, not a bare `ubc` from your PATH, and never one
you install yourself. With no path given, use the `ubc` on your PATH.

## Steps (one stage, then stop)

1. Run `ubc agent prompt --id <need_id> -p <project path>`. Its output IS your
   instruction for this stage: the engine has already resolved which single
   action comes next and written out how to do it, as plain text rather than
   JSON. Every other `ubc` call in this skill verifies the result. None of them
   is there to discover more work.
   `<need_id>` is a need id, not a stage name. An `--id` that is not a need
   exits non-zero: fix the id, do not infer that the stage is resolved.
   `prompt` executes nothing and spawns nothing, so it needs no runner
   configured.
2. EMPTY stdout means the verb printed only an error, so READ that error and
   fix what it names. Otherwise branch on the PREFIX of the FIRST line.
   `NO ACTION (` is the stop signal. `=== WORKING DIRECTORY ===` means there IS
   an action, and the line after it names the resolved project root.
   `STOP (unreadable_sources)` means ubc could not read one or more sources, so
   the needs they define are missing from the graph. A first line carrying NONE
   of those three prefixes is not a resolved action, so report it verbatim and
   stop.
   On the `NO ACTION (` branch there is nothing to author or review. The
   parenthesised token names the state, and the text under it names the one
   action that state calls for. For `choice_required`, read the pending decision
   in `choices[]`, ask the user to choose exactly one of its `options[].id`
   values, and never infer or select an answer yourself. Wait for the user's
   answer, then run `ubc agent choose <decision-id> <value> --id <NEED_ID> -p <project path>`
   and read `ubc agent next --id <NEED_ID> -p <project path>` again before doing
   any work. If the answer is not one of the listed values, ask again and do not
   save an answer. For every other `NO ACTION` state, follow the named action.
   That action may itself be a command to run, and running it is your NEXT step,
   not part of this one. Nothing is authored within THIS step. Report what the
   text named, and stop.
   On the `STOP (unreadable_sources)` branch, do EXACTLY what the text says:
   fix each source it lists as its fix lines say (re-save a file that is not
   UTF-8 as UTF-8 without changing its content, for an include the file the
   message names; a needs.json fetched from a URL is fixed where it is
   published, or its source removed; a file that cannot be read at all is
   restored or removed), run `ubc check` until it reports none of them, then
   run `ubc agent prompt` again. Never author, review or rewrite a
   need while this branch is present: the design an instruction would order
   written may already be on the unreadable page, and writing it again
   duplicates it.
   On the `=== WORKING DIRECTORY ===` branch, run every command the instruction
   gives you FROM the directory that second line names, and resolve every
   relative path it gives you AGAINST that same directory.
3. Follow the instruction as written. It is already resolved to ONE arm (author
   a need, review the needs a stage produced, fix needs that failed their
   review, or fix the diagnostics `ubc` reports on a stage's needs), so do not
   re-derive which arm applies and do not widen the task. A
   `FIX (diagnostics):` instruction lists each finding with its file and line:
   edit the need, its option or the code marker in place. Never delete a need
   to silence a finding, and never author a new need or review on that pass. A
   fix that needs a value or a decision you cannot take from the need, its
   links or the code (an owner, a safety level, which of two needs keeps a
   duplicate id) is not yours to invent: stop and ask the user, and never make
   one up to clear the gate.
   When you genuinely need one more need's detail, run
   `ubc agent audit --id <ID> -p <project path>`, and for its neighbourhood run
   `ubc agent context --id <ID> --no-code -p <project path>`. Prefer those over
   reading files.
4. INDEPENDENT review. When the instruction is a review pass, hold to the rule
   the engine states in the prompt it prints. Run this review in a context
   separate from the one that authored the needs under review, so no author
   grades its own output: the engine cannot observe which context you use, so
   nothing enforces this for you. Dispatch that separate context as a subagent
   or task, never the one that authored the artefact. The reviewer re-derives
   its judgment from `ubc agent audit --id <ID> -p <project path>` for every
   need under review, builds the scored verdict JSON, and SUBMITS it.
   Driving through `prompt`, as the steps above do, the printed review
   instruction ALREADY carries the submit command and the fingerprint rules in
   its own sections. Follow it verbatim and call nothing extra to find them.
   Reading the JSON fallback instead, take the command from
   `$.stage.review_brief.submit_command` and fill its `<ID>`, `<FINGERPRINT>`
   and `<CRITERIA_FINGERPRINT>` holes from that same brief (`fingerprints` keyed
   by need id, and `criteria.fingerprint`).
   Either way, append `-p <project path>` as this file requires on every call,
   and PIPE the verdict JSON in on stdin. If your harness cannot pipe stdin,
   write the draft to a temp path OUTSIDE the repository and pass that path with
   `--file`.
   What is never allowed is writing into the verdicts directory, or stamping a
   fingerprint by hand. `ubc agent verdict-submit` stamps the schema, the pack,
   and both fingerprints itself, and it refuses a draft path INSIDE the
   repository. A hand-written verdict carries no criteria fingerprint, which the
   gate reads as OUTDATED forever, so the stage stays held no matter how good
   the scores are.
   Pass your OWN harness name and model id into the reviewer's dispatch prompt
   so each verdict carries top-level `agent` (for example `claude-code` or
   `copilot`) and `model`. That is advisory score provenance, never gating. The
   fresh reviewer context cannot observe them itself. Omit a field only when it
   is genuinely undeterminable, and never guess a slug.
5. Subagent guidance (best-effort). If your harness supports independent
   subagents, work each need the instruction names as its own fresh subagent,
   and on a review pass use a DIFFERENT subagent for the review than the one
   that authored the artefact. This keeps each item in clean context and stops
   an author from rubber-stamping its own work. If your harness has no
   subagents, do the items in sequence in this chat. This is soft, best-effort
   guidance conditional on subagent support. It reduces bias. It does not
   guarantee independence.
6. Confirm. Run `ubc agent gaps --scope <need_id> -p <project path>` (the same
   anchor need id) to check the stage closed its trace obligations for that
   stream, then run `ubc agent next --id <need_id> -p <project path>` again.
   `gaps` gates trace coverage and the diagnostics on workflow needs, and does
   not read verdicts, so a green `gaps` alone does not mean the stage advances. For a review-required stage the
   engine holds the stage until the independent verdict is fresh and passing,
   so this re-run of `next` is what confirms the advance.
7. **STOP. Do not start the next stage.** Report to the user: what you produced,
   whether its trace gate is green, whether an independent reviewer wrote a
   passing verdict, and what that closing `next` read now names. The user
   re-runs the drive when they want the next stage worked.

Before ending, run this hard-stop check:

- Did I work exactly one stage? If no, stop and correct course.
- If the instruction was a review pass, did an INDEPENDENT reviewer (a fresh
  context, not the author) SUBMIT a passing verdict for every need under review,
  by piping it to `ubc agent verdict-submit` rather than writing a file? If no,
  do it now. A verdict written straight to disk never turns the gate green.
- Did I run `gaps` for confirmation? If no, do it now. A green `gaps` is
  necessary but not sufficient: it gates trace coverage and diagnostics, and
  does not read verdicts.
  The authoritative advance condition is a fresh passing verdict plus the final
  `next` read.
- Could ubc read every source? If a first line was `STOP (unreadable_sources)`,
  a source could not be read: a page, an include target, a codelinks source or
  a needs.json that is not UTF-8, or a file that cannot be read at all. Fix it
  as the STOP text says (re-save a local file as UTF-8), never re-author its
  needs.
- Did I avoid starting the next stage? If no, stop immediately.
- Did I report the next stage name and return control to the user? If no, do it now.

## Fallback: reading the `next` payload yourself

`ubc agent prompt` is the instruction source for this skill. Use this section
only when your harness reads the JSON of
`ubc agent next --id <need_id> -p <project path>` directly instead.

`$.arm` is always present and names the one row below that applies.
`$.stage` is one object or `null`, never an array. `id`, `produces`, `skill`,
`review`, `route`, `gates_to_pass` and `verdicts_dir` are ALWAYS present, so
test their VALUE (`== null`, or `""` for `$.stage.verdicts_dir`, whose resolved value
is then `$.stage.review_brief.verdicts_dir`). `gate`, `id_prefix`, `authoring`,
`review_needs`, `fingerprints`, `review_brief`, `diagnostics` and
`diagnostics_omitted` are omitted when they have no content, so a missing key
reads as empty, never as a payload you failed to understand. `default_status` is omitted on the same rule but does NOT read as
empty: it names the `:status:` a brand-new need of this stage's type opens in,
and on an anchored call (every call here carries `--id`) it is absent only when
the project declares no lifecycle states, where that status is `draft`. An empty
`states` list counts as none, so read the key's presence, never the presence of
a `[workflow.lifecycle]` table. Read these JSON paths, not the `ubproject.toml`
key names: the configured authoring skill arrives as `$.stage.skill`, the review
skill as `$.stage.review`.

| payload | the one action |
| --- | --- |
| `$.arm` is `"none"`, `$.reason` is `"empty"` | The workflow configuration derives no stages. Define `[[workflow.stages]]`. NOT "author the first artefact": a fully populated project reports `empty` too. |
| `$.arm` is `"none"`, `$.reason` is `"done"` | No open stage remains on THIS stream. Every call here carries `--id`, and an ANCHORED call reports `done`, never `empty`, so `done` also covers a project that derives no stages at all. Before reporting a green finish, run the whole-graph census `ubc agent status -p <project path>`: if it lists NO stages, define `[[workflow.stages]]` instead. A non-empty `$.open_streams` means other roots still carry gaps, so report those roots and STOP. Resuming one of them is the NEXT step, run as `ubc agent prompt --id <root> -p <project path>`. |
| `$.arm` is `"none"`, `$.reason` is `"gaps"` | The stream carries gaps that NO workflow stage owns, because no stage produces those needs' type. `$.unattributed_gaps` lists them, each with the `gap` record and the `gate` it fails. No stage clears them, so authoring is not the answer: close each one on the need itself (answer a clarification marker in the need body, add a missing link to it), or declare a `[[workflow.stages]]` entry producing that type. Never read this as `done`. |
| `$.arm` is `"none"`, `$.reason` is `"blocked"` | Resolve the dependency stage first. Inspect the stream with `ubc agent gaps --scope <anchor_id> -p <project path>` and the whole graph with `ubc agent status -p <project path>`. |
| `$.stage` is `null`, `$.reason` is `"choice_required"` | Find the pending decision in `$.choices[]`; ask the user to select one of its exact `options[].id` values. Persist it with `ubc agent choose <decision-id> <value> --id <NEED_ID> -p <project path>`, then read `next --id <NEED_ID>` again before proceeding. |
| `$.decision_refusal` is present | Stop and report the typed refusal. Do not infer a decision or continue past invalid ownership or an unresolved answer. |
| `$.reason` is `"unreadable_sources"` | STOP. ubc could not read the files `$.unreadable_sources` lists, each with its `path`, `line`, `code` and `message`, so the needs they define are missing from the graph. Fix each one: re-save a file that is not UTF-8 as UTF-8 without changing its content (for an include, the file the message names); an entry with a `url` is a needs.json fetched from that URL, fixed where it is published or its source removed from the project; a `read_error` with a `null` line is a file that cannot be read at all, restored or removed. Then run `ubc check` until it reports none of them, and re-run `next`. Never author, review or rewrite a need until then: the design the graph seems to lack may be on the unreadable page. |
| `$.ok` is `false`, or a non-zero exit | Do NOT infer progress. Report the refusal or reason verbatim and stop. For `unknown_gate: <name>`, report that reason and stop. Otherwise fix the rejected id or stage name. |
| `$.arm` is `"fix_diagnostics"` | FIX the findings in `$.stage.diagnostics`, do NOT author or review. `$.stage.diagnostics` lists at most 50 findings and `$.stage.diagnostics_omitted` counts the rest, so fix the listed ones and re-run `next` for the next batch. Each entry names the finding's `path` and `line`, its code in `link`, its `message`, and the need in `id` (for a need that failed to build, such as a code marker that failed to parse, `id` is the file). Edit the need, its option or the code marker in place, and never delete a need to silence a finding. Then run `ubc check` until none of them remain. If a fix needs a value or a decision you cannot take from the need, its links or the code (an owner, a safety level, which of two needs keeps a duplicate id), stop and ask the user; never make one up to clear the gate. A finding that is intended is the user's call: stop and ask them to allow its code under `[workflow.diagnostics]` or to ignore it under `[lint]`. |
| `$.arm` is `"author"` | AUTHOR, structural gates first. Invoke the skill named by `$.stage.skill`, however your harness loads skills, and hand it `$.stage.route.resolved_path`, `$.stage.id_prefix`, `$.stage.authoring` and `$.stage.gate.link`, each when the payload carries it, because the authoring skills are told NOT to re-discover the project. Hand it the new need's `:status:` too: `$.stage.default_status`, or `draft` when the payload carries no such key. The skills ask for the status they were TOLD to open the need in, and you are the only thing telling them on this route. Copy the trace link field name from `$.stage.gate.link` verbatim, never a synonym. A `null` `$.stage.skill` names no skill: author from the payload's own route and gate, and invent no skill name. |
| `$.arm` is `"review"` | REVIEW exactly the ids `$.stage.review_needs` lists, do NOT author. Their content fingerprints are in `$.stage.fingerprints`, and step 4 above already carries the submit rules for this JSON route, `$.stage.review_brief.submit_command` among them. |
| `$.arm` is `"refix"` | The verdicts exist and are FAILING. RE-AUTHOR those needs. Their ids are in `$.stage.review_brief.fresh_skipped` while the verdicts are still fresh, and in `$.stage.review_brief.review_needs` once the need changed after it failed. Each id's verdict under `$.stage.review_brief.verdicts_dir` says why, in the `reason` and optional `suggestion` on each entry of its `axes` map, plus an optional top-level `summary`. Re-authoring invokes the same skill as the AUTHOR row, so hand it the same facts, `$.stage.default_status` (or `draft`) among them: this stage's payload carries that key exactly as an authoring stage's does, and the skill asks for the status whether it is writing the need for the first time or rewriting it. |

`$.arm` is the engine's own choice, the same one `ubc agent prompt` acts on,
so read it and never re-derive it from `$.stage.gates_to_pass`,
`$.stage.review_needs` or the verdicts. Take the one action the matching row
names, then rejoin the steps above at the independent review. The table yields
exactly one action and never chains into a second stage.

## Notes

- `ubc agent status -p <project path>` shows every stage's state at once (the
  heartbeat).
- `$.stage.review` names the exact review skill for the stage. Use its value
  verbatim, do not build a `review-<stage>` name. It is `null` on a stage that
  carries no review, and that null value is the test.
- `ubc agent gaps -p <project path>` is the whole-graph gate. It exits non-zero
  while gaps remain. It gates trace coverage and the diagnostics on workflow
  needs, and does not read verdicts, so on a review-required stage a green
  `gaps` is necessary but not sufficient. The
  `next` re-run after a fresh passing verdict is the authoritative advance
  signal.
- Flags follow the verb's job. `gaps` and `trace` gate the whole graph and
  narrow to one stream with `--scope <need_id>`. `status` and `release-check`
  take no anchor at all: they reject `--scope` as well as `--id`. None of those
  four accepts `--id`. The per-need verbs (`next`, `prompt`, `context`,
  `impact`, `audit`) take one need with `--id <need_id>`. A non-zero `next` or
  `prompt` means the `--id` was rejected, or, when you passed one, the
  `--stage`. Read the error and the `reason` before assuming the stage is
  resolved.
- Never skip a stage: the trace edges in `[workflow]` are what the gates enforce.
- To drive a SPECIFIC stage (one that is not the recommended next, such as a
  global stage or a parallel arm stage), pass `--stage <STAGE_ID>` to either
  `ubc agent prompt --id <need_id> -p <project path>` or
  `ubc agent next --id <need_id> -p <project path>`. Both target that stage
  instead of the recommendation, and the need id still anchors the briefing.
  An unknown stage exits non-zero on both. `prompt` names the stage it
  rejected, in the error it prints on stderr. `next` reports
  `"reason": "stage_not_found"` in its JSON and prints nothing else, so it
  never names the stage back to you.
  Only `prompt` checks whether the named stage can RUN. For a stage whose own
  `depends_on` is not met yet it answers `NO ACTION (blocked)`, which is the
  stop branch of step 2 above, never an authoring order. `next --stage` does
  not check: it reports `"ok": true` with a resolved `$.stage.route` for a
  blocked stage exactly as it does for a ready one, and its payload carries no
  state field to tell the two apart. So never act on a `next --stage` payload
  alone. Run `prompt --stage <STAGE_ID>` for the same stage first, and go ahead
  only if it did not answer `NO ACTION (`.
  A briefing is not always the FIRST artefact of its stage. When the named
  stage already reads `done` for this stream, the briefing says so in a line
  above its instruction, and for a stage that authors a need that line says
  what it orders is an ADDITIONAL artefact, not the first one. Read that line
  before you author. Everything else is unchanged: one stage, then stop.
