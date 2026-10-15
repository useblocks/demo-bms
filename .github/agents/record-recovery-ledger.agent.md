---
name: record-recovery-ledger
description: Wrap a finished recovery emission into the engine's RecoveryResult shape and run `ubc agent reverse record` to write the project's advisory ledger, the only legal way a recovery run's provenance reaches disk.
---

# Record a recovery ledger entry

`recover-requirement-from-code`, `recover-need-from-cluster`, and
`split-recovered-need` all write RST directly. None of them touch the
project's advisory recovery ledger (`.pharaoh/rev-eng/`): that ledger is
written ONLY by `ubc agent reverse record`, and this skill is the one place
in the loop that calls it. Run this skill once, as the terminal step, after
a recovery emission's RST is on disk and its author has approved it.

Pass `-p <project path>` on every `ubc agent` command. `<project path>` is the
directory that holds the target `ubproject.toml`. Resolve it once from the
briefing you were handed and reuse it on every call.

When these instructions say `ubc`, run the exact version-matched `ubc` the
harness named in the task, not a bare `ubc` from your PATH, and never one
you install yourself. With no path given, use the `ubc` on your PATH.

## Running with no interactive user

Whether this run has an interactive user, one who can read a question and send
an answer back, is stated in your prompt by whoever dispatched it. Read that
statement rather than working it out for yourself: from in here a headless
harness looks exactly like an attended one, and guessing has cost whole runs.
**When nothing in your prompt states it, take it that there is no interactive
user.** That default is deliberate, and the two mistakes are not the same size.
Deciding something a human would have decided leaves an artefact they can read,
correct or delete. Waiting for an answer nobody will send ends the run with
nothing on disk at all, and reports success while doing it.

**With no interactive user**, every decision this skill routes to a human is
yours to make. Check the thing you were about to ask about against the evidence
it rests on, state in your report that you decided it yourself and on what
grounds, then carry the work through to the end. Never ask a question nobody is
there to answer, and never finish holding a proposal you did not act on: a run
that reports an outline and writes nothing is the same outcome as a run that
never started.

**With an interactive user**, follow every approval step as written and wait
for the answer.

A human confirming the emission is NOT a precondition for running this skill.
The approval that gates it is the recovering skill's own, given by whoever ran
it, and with no interactive user that is the recovering agent's self-review.
Leaving authored RST on disk with no ledger entry behind it is the worse
outcome by a distance: `reverse plan` re-offers the source forever, and the
next pass re-authors the same behaviours under fresh ids.

## Read back what was actually authored

Build the needs index first, so the RST the recovery skill just wrote is
materialized into a `needs.json` you can read. Change into the project
directory (`cd <project path>`) and run `ubc build needs . -o <tmp>/needs.json`,
where `<tmp>` is a new temporary directory outside the repository (for example
from `mktemp -d`). Run it from inside the project because `ubc build needs`
finds the project by searching upward from `.` for its `ubproject.toml`, so
from outside the project it finds another project or none. `-o` writes the
index to `<tmp>` and nowhere else, so the build leaves nothing in the
repository. Read that same file wherever this skill reads `needs.json`. Remove
`<tmp>` once the `needs` array below is built.

Then read each authored need back from the graph, never from what you remember
writing: the graph is the oracle, and the payload is built from what it says.

- **Up to about ten ids**, run `ubc agent audit --id <ID> -p <project path>`
  once per id and read its authoritative `type` and `body`.
- **Beyond that**, read `<tmp>/needs.json`, the file you just built, rather
  than paying one process launch per id. A unit-scale recovery reaches 60 to
  80 ids, and one `audit` call each is the wrong shape. This is a sanctioned
  bulk read-back, not a workaround, and the keys are NOT `audit`'s, which is
  the part nothing else states: each need sits at
  `versions[<current_version>].needs[<id>]`, its type is `type` as in `audit`,
  and its body is `content` where `audit` calls it `body`.
- **If a need has no `content` key**, do not read that as an empty body. The
  key is omitted for an empty body, and a project can drop it from the file
  entirely through its own `[needs]` JSON field settings. Fall back to
  `ubc agent audit --id <ID>` for that need and say in your report that you
  did.

Do not mix the two forms inside one recovery, except for the per-need fallback
above. `content` and `body` are the same text today, and a run that drew some
bodies from one and some from the other would record a `content_baseline`
computed over each shape, so any future divergence between them would read as
part of the unit having been hand-edited.

If the read-back finds nothing, whichever form you used, the recovery emitted
nothing and this skill stops here. **Do not call `ubc agent reverse record`
with an empty `needs` array.** A recovery that found nothing is a real
outcome, and recording it marks the source recovered with nothing recovered
from it: the engine refuses the call outright, and if it did not,
`reverse plan` would skip that source forever and `reverse status` would count
it as covered.

Run `ubc agent reverse record --schema` at any point to print the payload
contract this skill builds, including which keys are required and what each
path is measured from. It needs no `-p` and records nothing.

## Build the `needs` array

One entry per recovered id, in the shape the engine's `RecoveredNeed` payload
expects:

- `id`: the need's id, unchanged.
- `type`: the need's `type`, exactly as the read-back reports it.
- `body`: the need's body, exactly as the read-back reports it (`body` from
  `audit`, `content` from `<tmp>/needs.json`).
- `source_span` (optional): a two-element `[start, end]` array, a 0-based
  inclusive line range in the SOURCE file the requirement traces to, not the
  RST. Omit the key entirely when you have no real line range to report:
  `recover-requirement-from-code`'s own rules ban line numbers in the
  requirement body, so this is normally absent for a bottom-stage extraction.
  Never emit it as `null`. Absence, not `null`, is what the engine reads as
  "unknown".
- `confidence` (optional): a numeric confidence, only when you genuinely
  have one to report. Never invent a plausible-looking number. Normally
  omitted.

## Wrap into a `RecoveryResult`

```json
{
  "source_path": "<your target's source_path, unchanged>",
  "target_rst": "<the document you authored into, route_path with {stream} substituted>",
  "members": ["<every file this act covered, only when source_path is a directory>"],
  "retired": ["<ids this record replaces, only after a split>"],
  "run": {
    "agent": "<the RECOVERING skill's name, not this one>",
    "model": "<your own model id, e.g. claude-opus-4.8>",
    "sources": ["<evidence kinds this run drew on, e.g. \"code\">"]
  },
  "needs": [
    { "id": "<ID>", "type": "<type>", "body": "<body>" }
  ]
}
```

`source_path` is your recovery target's own field, carried through
unchanged: for an extraction-stage emission that is the source file path,
and for a synthesis-stage emission it is the target's own `source_path`,
which is a `cluster:<cluster-key>` marker rather than a real file, and that is
expected.

`members` goes with a DIRECTORY `source_path` and with nothing else. A
directory is how the engine offers a multi-file recovery unit: several files
recovered in one act, keyed by the directory they share. Pass back the member
list your target carried, verbatim. Do not list the directory yourself, and do
not add files you were not given: the engine already left out the files an
earlier pass recovered, and putting them back records them a second time under
this key.

Omit `members` entirely when `source_path` names a single file, and when it is
a `cluster:` marker. A single file's own path already names the one file it
covers. A marker names no file at all, and a synthesis target's own `members`
are lower-need IDS, not source files, so pass that target's `source_path`
through and leave its `members` behind. `record` refuses all three
mismatches, so this is not a matter of tidiness.

`retired` goes with a split and with nothing else. `split-recovered-need`
replaces a recovered need with atoms (`<id>_01`, `<id>_02`, ...), and the
original id no longer exists. The ledger keeps every id a re-record does not
mention, so without `retired` the original stays in the shard, resolves
nowhere, and `ubc agent reverse status` reports the unit's files as
`orphaned`. For a split, record the atoms under the shard that holds the
original id: its `source_path` and `members`, verbatim from the shard under
`.pharaoh/rev-eng/` (the one whose `needs[].id` contains the original), and
`retired: ["<original id>"]`. The engine drops the retired ids from that shard,
and warns when one is not in it, which means you picked the wrong shard.
Omit `retired` for every other recovery.

`target_rst` is the document the recovering skill actually authored into. It
is NOT copied from the target, because no target carries one: `plan` reports
the stage's `route_path` with its `{stream}` placeholder left in, and the
recovering skill chose the slug and substituted it. Carry that concrete path
through. `record` refuses a `target_rst` that still holds `{stream}` (or the
deprecated `{feature}` alias) and names the placeholder it found.

**The two are measured from different places, so a correct pair can look
mismatched.** `source_path` is relative to the REPOSITORY root (the directory
holding `.git`), since the engine stores it as the ledger's key and uses it as
a git pathspec. `target_rst` is relative to the PROJECT directory (the one
holding `ubproject.toml`). They coincide only when the project sits at the
repository root, so on a project at `<repo>/sub/` the correct pair looks
mismatched (`sub/src/auth/token.rs` next to `specs/auth/requirements.rst`) and
is not. Do not trim `source_path` to match `target_rst`. `record` refuses a
`source_path` it can tell arrived in the project-relative form and names the
one you meant, but it cannot catch every case, and a wrong key that gets
through is stored silently and never matches the file again.

`target_rst` must be relative and must stay inside the project directory.
`record` refuses one that is blank, one that resolves to the project
directory itself, and one that escapes it. It must also name the document the
recovering skill authored, which is on disk by now, so `record` refuses a
`target_rst` naming no file in the project `-p` resolved. When it does, the
document is most likely in another project, for example one whose
`ubproject.toml` sits below the directory you passed: pass that project's
directory as `-p` and record again.

`run.sources` lists the evidence kinds the recovery actually drew on. A
structure recovery reads its module's code or tests, so it lists whichever of
`code` and `tests` it read. Of `commit_history`, `change_requests` and
`issues`, list only those selected for this run, which the recovery's prompt
names. Never list one that is not selected, even when a reference led you to a
pull request or an issue. Where the prompt also names the file kinds selected
for this run, list only those of `code`, `tests`, `docs`, `adrs` and `ci`. When
the prompt says nothing about which kinds are selected, list every kind the
recovery actually drew on. Evidence kinds belong in `run.sources`, not in a
target.

`needs` is the key name whatever the recovering skill called its own list.
`record` reads no synonym for it, and every key the payload carries that is not
named above is ignored and reported back as a warning.

## Write the temp file and call the CLI

Write the `RecoveryResult` JSON to a temp file OUTSIDE the repository (for
example via `mktemp`), never inside it. The only file this skill means to leave
in the repository is the shard `record` writes. Your payload, a note, a script
and the needs index all stay outside it, which is why the build above writes
into `<tmp>`. Then run:

```
ubc agent reverse record --input <tempfile> -p <project path>
```

Capture stdout, stderr, and the exit code.

- Exit 0: parse stdout as JSON (`{"shard_path": "...", "need_count": N}`, the
  engine's `RecordOutcome`) and report it to the user. Delete the temp file.
  When the outcome also carries a `warnings` array, the shard WAS written and
  each entry names something worth acting on: a key the payload carried that
  `record` does not read (so whatever it held was not recorded), or a need id
  another shard already holds (so two shards now claim one id). Report every
  warning verbatim rather than summarizing them away.
- Non-zero exit: read what stderr names. A payload error names the exact
  place, in the form `root['needs'][40] does not state the required key
  'type'`, so **correct that one field and retry once, then stop.** Report the
  failure, quoting stderr's first line, whether the retry succeeded or not.
  Never report the ledger write as complete when it was not.

Retrying once is the whole difference between a repairable mistake and a
permanent one. The RST is already on disk by the time this skill runs, so
abandoning the payload leaves needs authored with no ledger entry behind them:
`reverse plan` re-offers that source forever, and the next pass re-authors the
same behaviours under fresh ids that nothing will ever notice are duplicates.
One retry, on the field the message named, and no further: a second failure
means the payload is wrong in a way this loop cannot see, and a human has to
look at it.

One non-zero exit has a specific remedy rather than an upstream fix. When
stderr says the shard `cannot be read`, a shard for that source is already on
disk and this ubc cannot interpret it (a merge conflict in a committed shard is
the usual cause). `record` refuses to write over it, because treating
unreadable bytes as an empty slot would destroy whatever was recorded there.
Clearing it is the only way forward, and **the refusal ends with the exact
command that clears it**, in this form:

```
ubc agent reverse forget --source <the source path that message names> -p <project path>
```

**Run the command the message gives, verbatim. Do not rebuild it from the
`source_path` you just tried to record.** The two are not always the same
string: a shard written before the ledger's coordinate move answers to a
different spelling of the same source, and passing the one you already have
exits 1 and changes nothing, which is a loop back to this step. The message
knows which spelling reaches the file. You do not.

Report what `forget` returns before recording again. It deletes provenance,
never RST, and its `warnings` array states what changes: the needs stay in the
authored document, `reverse plan` re-offers that source immediately, and a
second extraction run over it mints FRESH ids for the same behaviours. Ask the
user before re-running extraction over a source you just forgot.

## Rules

- This skill never edits RST. If the recovery emission itself was wrong,
  fix it upstream (re-run the recovering skill, or `split-recovered-need`
  for an over-consolidated result) and only then record it here.
- Invoke this skill once per finished recovery emission, not once per id
  inside it: one `ubc agent reverse record` call writes one shard for the
  whole target.
- Never fabricate a `RecordOutcome` when the CLI call itself did not
  succeed.
- Every key not named in the payload above is IGNORED by `record` and reported
  back as a warning. Adding a plausible-looking extra field does not record it,
  it only produces a warning, so build the payload from the shape above rather
  than from what the target you were handed happens to carry.
