---
name: split-recovered-need
description: Split an over-consolidated recovered need into atomic needs, preserving its up-links unchanged onto every atom, and leave an already-atomic need untouched.
---

# Split a recovered need

A recovered need (emitted by `recover-requirement-from-code` or
`recover-need-from-cluster`) has been flagged, by a human or a review pass,
as bundling more than one requirement into a single body. This skill splits
that ONE need into one atomic need per behavior, re-emitting each atom with
the original's up-links carried forward unchanged. This corrects the
over-consolidation after the fact. It never clusters lower needs and never
synthesizes a new higher-stage need: that is `recover-need-from-cluster`'s
job.

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

## Use the briefing and the tools

Your briefing names the id of the recovered need to split. Run
`ubc agent audit --id <ID> -p <project path>` and read its `type`, `title`,
`body`, `status`, `trace.outgoing` (its up-links), and `source.path` (the
`.rst` file its directive currently lives in). Do NOT re-discover the project
with `find` or `grep`: `audit` is the oracle for which file the need lives in.

**Treat `source.line_range` as informational only, never as an edit target.**
It is a snapshot of where the directive sat when the index was last built, and
it goes stale the moment any earlier edit in that file inserts or removes a
line. It is also counted differently from the tool you would hand it to:
`audit` reports a 0-based inclusive range, while every editing tool addresses
lines 1-based, so passing it straight through lands one line above the block
you meant. Locate the directive the way "Replace the original" below says
instead.

Before you touch the directive, run
`ubc agent context --id <ID> --no-code -p <project path>` and check whether anything
already points AT this need. A need this fresh usually has nothing pointing
at it yet, but if something does, say so in your report: v1 of this skill
does not re-point an existing reference at the new atoms, that is a human
follow-up.

## Detect the bundling

Apply this rule to the need's `body`:

- More than one `shall` in the body: bundled.
- Within a single shall clause, a coordinating conjunction ("and", "or")
  joining two verb phrases both governed by the same `shall` (for example
  "shall detect X and activate Y"): bundled.

If neither holds, the need is already atomic. Report that and stop: do not
manufacture a split, do not touch the directive.

## Segment and re-emit

Walk the body in its original order and extract one atomic behavior
statement per distinct action. One statement per sentence already carrying
its own `shall`. Within a single shall clause joined by a conjunction, split
at the conjunction, each fragment keeping the shared subject and becoming
its own `shall` statement ("The X shall detect A and activate B" becomes
"The X shall detect A." and "The X shall activate B."). Discard nothing:
every clause in the original body must land in exactly one atom. A fragment
that is a genuine sub-step of one action, not independently meaningful on
its own, is not a split candidate: leave it fused and flag the borderline
case in your report rather than manufacture a false split.

For each segmented behavior, in original order, starting at `01`:

```rst
.. <type>:: <3-6 word summary of this atom's action>
   :id: <original_id>_<NN>
   :status: <original status, unchanged>
   :<up-link field, exactly as reported by trace.outgoing>: <same values, unchanged>

   <single shall statement for this atom>
```

`<type>` is unchanged from the original: splitting changes how many needs
exist at this stage, never which stage they are on. Every other field the
original carried (its up-link values above all) is copied verbatim onto
every atom, never inverted, never pointed at a sibling atom, and never
pointed back at the retired original id.

## Propose before you replace

**With an interactive user**, do NOT overwrite the original directive yet.
Present a short, scannable outline first: each atom's id
(`<original_id>_<NN>`), a one-line summary of its action, and the up-link
values it carries forward unchanged from the original. Wait for them to
approve or adjust, and do not replace the original until they confirm.

**With no interactive user**, make the same outline and approve it
yourself. Check it against the original body's own clauses, then replace.
Do not stop here and do not ask.

## Replace the original

On approval (yours or the user's), replace the original directive block
with the atoms' directive blocks, in order, exactly as you proposed them.

**Find that block by matching its own `:id:` line in the current, on-disk
content of the file `audit` named, never by a line range.** Read the file,
find the directive block whose `:id:` field equals the id you are splitting,
and replace exactly that block. A range fetched earlier in this run is a
range from before whatever else has been written to that file since, and an
edit placed by one lands on the wrong block: it eats the tail of the
directive above it and the head of the one below. The sibling skill
`recover-need-from-cluster` edits by id for the same reason, over the same
field of the same command, and the two must not disagree inside one session.

The original id is retired: once you replace the block, nothing in the
project should reference it again except your own report noting what
it was split into.

## Self-check

Re-apply the bundling rule (above) to every atom's body. Each must now carry
exactly one `shall` and no coordinating conjunction. If an atom still fails,
split it once more. If it still fails after two total attempts, leave it as
emitted and add a note to your report that it needs manual correction.

## Rules

- **If segmenting would discard content from the original body rather than
  reassign it to an atom, do NOT proceed.** Report the conflict instead of
  emitting an atom that silently drops a constraint the original stated.
- One obligation per directive, same discipline as any freshly-authored
  requirement.
- This skill never invokes `ubc agent reverse record`. Hand your emitted
  atoms to `record-recovery-ledger` once you are done, together with the
  ledger details in "Hand the atoms to the ledger" below.

## Hand the atoms to the ledger

The original id is still in the ledger shard that recorded it, and the atoms
belong in THAT shard, not in a new one. Find it before you hand off: read the
files under `.pharaoh/rev-eng/` (`**/*.json`, in the repository root's
`.pharaoh`, found from `<project path>`) and take the one whose `needs[].id`
list contains the original id. Give `record-recovery-ledger`:

- the atoms as its `needs`,
- that shard's `source.path` as `source_path` and its `source.members`
  (the `path` of each member) as `members`, both verbatim, and
- `retired: ["<original id>"]`, which drops the original from the shard.
  Without it the shard keeps an id that no longer resolves, and
  `ubc agent reverse status` reports the unit's files as `orphaned`.

If no shard holds the original id, the need was never recorded: hand the atoms
over with no `retired` and say so in your report.

## Confirm

After replacing the block, change into the project directory
(`cd <project path>`) and run `ubc build needs . -o <tmp>/needs.json`,
where `<tmp>` is a new temporary directory outside the repository (for
example from `mktemp -d`). Then run `ubc agent gaps -p <project path>`,
to confirm the build is still clean and the up-link trace edges still
resolve for every atom. `gaps` exits 1 whenever any gap exists anywhere in
the project, which is normal partway through a recovery, so do not read the
exit code: check only the entries for the atoms themselves. Run the build from inside the project because
`ubc build needs` finds the project by searching upward from `.` for its
`ubproject.toml`. `-o` writes the index to `<tmp>` and nowhere else, so
the build leaves nothing in the repository. Remove `<tmp>` once both
commands are done.
