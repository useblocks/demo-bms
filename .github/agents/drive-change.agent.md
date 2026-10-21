---
name: drive-change
description: Drive ONE step of a change request's lifecycle, then stop and report what comes next and who owns it. Never runs the lifecycle end to end, because three of its steps belong to a person, and never starts a second agent to do the work.
---

# Drive the next change-request step

Use this skill to advance ONE change request by exactly one step, then stop and
hand control back to the user. Do not run the lifecycle end to end. Work the single
next step, report what it produced, name what comes next and who owns it, and stop.

This single-step boundary is a hard rule, and the steps that belong to a person are
the reason for it. A change request is AUTHORIZED by a person, the edits it produces
are read as a diff by a person before they become history, and closing it out is
final and is a person's call. A gate whose whole value is that a human passed it
cannot be automated away. A skill that walked the lifecycle for you would walk
straight through them, and the record left behind would say a person approved
something no person ever read.

If the wording you were given is ambiguous ("run the change", "handle CR_3"),
interpret it as: work the ONE next step, then stop.

Pass `-p <project path>` on every `ubc agent` command. `<project path>` is the
directory that holds the target `ubproject.toml` (the project the change request
belongs to). A repository can contain several `ubproject.toml` files, so without
`-p` the command runs against the current directory and can drive the wrong
project. Resolve `<project path>` once from the change request or file you were
handed and reuse it on every call in this step.

When these instructions say `ubc`, run the exact version-matched `ubc` the
harness named in the task, not a bare `ubc` from your PATH, and never one
you install yourself. With no path given, use the `ubc` on your PATH.

## You do the work yourself, in this session

`assess` and `execute` can hand their work to a separate headless process that the
project configures. Inside this session that process is a hidden second agent. The
user's panel shows none of its progress, the shell timeout of one tool call can kill
it halfway through a stage, and a project that configures no runner cannot start it
at all.

So in this session you NEVER run the headless form of `ubc agent change assess` or
`ubc agent change execute`, which is the form with neither `--print` nor `--done`.
With `--print` the verb prints, as plain text, exactly what the headless process
would have been given (one stage at a time, for `execute`), and writes nothing. You
carry that out yourself, here, where the user can watch. `execute` also has `--done`,
which runs nothing and records that you did.

Read the FIRST line of what a `--print` prints:

- `=== WORKING DIRECTORY ===` means there is work. The line after it names the
  project root, and every command and path in the text is relative to it.
- `NO ACTION (` is the stop signal. There is nothing to carry out. An `execute --print`
  follows it with the `--done` command that records that.
- Anything else is a refusal printed as JSON with `"ok": false`. Report its `reason`
  and stop. The verb is telling you the state is not what you assumed.

## Step 1: find out where it stands

Run `ubc agent change list -p <project path>` for every change request in the
project with its state. Narrow to one state with `ubc agent change list --status
<STATE> -p <project path>`, whose value set is closed: an unknown value is refused
rather than answered with an empty list, because a typo that reads as "nothing is
open" is the most dangerous wrong answer that verb can give.

Then run `ubc agent change show --id <CR_ID> -p <project path>` for the one you are
driving. Read its state, its anchor, its three impact link sets and its status log
out of that payload. Do not reach for `ubc agent audit --id <CR_ID> -p <project
path>` instead: it reports declared links and cannot reach a single non-link FIELD,
so a change request read through it looks half empty rather than empty.

Nothing in this lifecycle needs you to find a file. Every path you open comes from
the output of one of these verbs.

## Step 2: take the ONE step the state calls for

| where it stands | the one next step | who owns it |
| --- | --- | --- |
| no change request exists for the edit yet | `ubc agent change plan --id <ANCHOR_ID> --cr-id CR_<TOPIC> --purpose "<what the change is for>" -p <project path>`, anchored on the need the change is AIMED AT | you |
| raised, nothing decided (`draft`) | `ubc agent change assess --print --id <CR_ID> -p <project path>`, then carry out the instruction it prints | you |
| assessed, the three impact links cover the computed set | `ubc agent change approve --id <CR_ID> --by <WHO> --decision <DECISION> -p <project path>` | a PERSON |
| approved | `ubc agent change execute --print --id <CR_ID> -p <project path>` prints step 1: carry it out, run the command its footer names, and so on, one step at a time, until the footer names `ubc agent change execute --done --id <CR_ID> --by <WHO> -p <project path>`, which records it | you |
| executed | the person reads the diff the cascade left and commits it or sends it back. Then show `ubc agent change close --dry-run --id <CR_ID> -p <project path>`, and close it with `--by <WHO>` instead of `--dry-run` if the person says so | a PERSON |
| closed | nothing. Nothing follows `closed` | nobody |
| rejected or deferred | nothing. The record stands as the only trace the refusal left | nobody |
| a PERSON asks to assess it again (assessed, approved, rejected or deferred) | `ubc agent change reassess --id <CR_ID> --by <WHO> -p <project path>` reopens it as a fresh draft (purpose kept, rulings and decision withdrawn). Then take the `draft` row | you, on the person's word |

Take the one step the row names. Do not take the row below it as well.

### Planning: propose an id with `--cr-id`

Give a new change request an id that says what it is FOR. Propose `--cr-id
CR_<TOPIC>`, where `<TOPIC>` is a few uppercase words joined by underscores that name
the purpose of the change, for example `CR_KEYPAD_SIX_DIGIT_PIN`. Without `--cr-id`
the engine mints an id from the date and four hex digits, which names nothing and
which nobody can read aloud.

Take the topic from what the person told you the change is for, never from the ids of
the needs it touches. When the topic is unclear, ask the person what the change is
for before you plan, and plan with their answer.

Pass that answer as `--purpose` too, in a sentence or two. It is written under the
record's `**Purpose**` heading in the body, where the person goes on editing it in
markup. Every step of the work quotes the body, and assessing again keeps it. A
record planned without one asks for it there with a TODO for the person to replace.

A bad id is refused and nothing is written. It has to start with the prefix the
project declares for change requests (`CR_` in the shipped profile), carry no
whitespace or path separator, match the project's `id_regex`, and not be the id of a
need that already exists. The refusal names the rule it broke, so fix the id and run
`plan` again.

### The anchor is never the change request id

`plan` takes the id of the need the change is AIMED AT. Every other verb takes the
change request id, and the engine reads the anchor off the record itself.

Getting that backwards does not fail loudly. The impact links sit outside the trace
link set on purpose, so a closure walked from a change request id is EMPTY and
reports success: `count: 0`, `ok: true`, exit code 0. An empty reach reads as "this
change affects nothing", so the wrong id gives you a confident wrong answer rather
than an error.

### Assessing: carry out what `assess --print` prints

Run `ubc agent change assess --print --id <CR_ID> -p <project path>` and read the
text after the working-directory line. It names the change request and the file it is
written in, the anchor, and every need the change reaches with the file each one is
written in, and it tells you what to write. Do exactly that. You edit the change
request and nothing else, and you leave the edit uncommitted.

There is no `--done` for an assessment. The edit to the change request is the record,
and the engine reads it back. When you are finished, run `ubc agent change show --id
<CR_ID> -p <project path>` and report the state it finds: `assessed` once the three
impact links cover the computed set. Do not claim the assessment is complete from
your own reading of what you wrote.

### Executing: one step at a time, then record it

Run `ubc agent change execute --print --id <CR_ID> -p <project path>`. It prints ONE
step, step 1. After the working-directory line comes
`=== STEP <n>/<N>: <stage> (anchor <ID>) ===`, the full instruction for that stage,
and a footer headed `=== NEXT COMMAND ===` that names the exact command to run next.
Carry the step out yourself, then run the command the footer names. That prints the
next step, and so on, until the footer names `ubc agent change execute --done` instead
of another step.

- One step at a time. Finish a step before you run the command that prints the next
  one, and never merge two steps into one pass. Never print the next step early: each
  step is built from the project as it stands when you print it, so the next step
  quotes the edits you just made, and one printed early quotes text that is about to
  change. An earlier step's edits are already in the text a later step quotes.
- Run the command a footer names exactly as printed, apart from the `<WHO>` on the
  last one. It carries the project, the flags the first call used and the number of
  the next step. Do not retype it, renumber it or print a step out of order.
- `N` in `STEP <n>/<N>` is the number of steps in the whole cascade, and it is the
  same on every call. If it is not, the change request or the project changed under
  the cascade. Stop and report it, because the step numbers can no longer be trusted.
- Each step bounds you to the approved scope it states. A need the scope does not name
  is not yours to touch, and the step tells you what to write when one has to change.
- Leave every edit uncommitted. Do not `git add` and do not `git commit`.

If a step cannot be carried out, stop there and report which step and why. Do NOT run
the next step's command or `--done`: `--done` says the steps were carried out, the
engine cannot check that, and a record that says so when it is not true is worse than
a record that is still `approved`. A `[NEEDS CLARIFICATION]` marker that a step told
you to write on one artefact is different. It is a legitimate outcome of that step,
so name the artefact in your report, and know that `close` will not pass while the
marker stands.

When the last step is carried out, its footer names `ubc agent change execute --done
--id <CR_ID> --by <WHO> -p <project path>`. Run it with the person's name in place of
`<WHO>`. It appends `executed` to the status log, the same entry a headless run would
have appended, and it runs nothing. `<WHO>` is the person this session works for. Do
not supply your own name, your harness name, or a placeholder. When you do not know
who that is, ask. Leaving `--by` out records the repository's git identity.

### `execute` with nothing downstream to reconcile

An anchor can sit at a leaf of the workflow, with no stage cascading from the stage
that produces it. `execute` then reads the approved scope to decide which of two
situations it is in, and both are answers rather than dead ends.

If every id the approval authorizes carries the anchor's own type, all the
authorized work is at the anchor and a person has already done it. `execute --print`
answers with the line `NO ACTION (nothing_to_cascade)`, followed by the `execute
--done` command, and writes nothing. There is no step to carry out. Run that command
as above to record it, then name the diff as the next thing a person reads.

If the approval authorizes work away from the anchor's own stage, no cascade from
there can reach it. The verb refuses with `reason: "no_downstream_stages"` and exit
1, and names the types it could not place. Report it and stop. The change was
anchored on the wrong need, and re-anchoring it is a decision, not a retry.

### The human gates

**Approval.** `ubc agent change approve --id <CR_ID> --by <WHO> --decision
<DECISION> -p <project path>` records who authorized the change. `--by` is
required, because an authorization with no approver on it authorizes nothing. Do
not supply your own name, your harness name, or a placeholder. Ask the user who is
recording the decision and what they decide, and run it with their answer.

An APPROVAL refuses unless the impact analysis names at least one id, the three
impact links cover the computed set exactly, and no `[NEEDS CLARIFICATION]` marker
stands anywhere the change request reaches. It names every failing condition at
once, with the ids on each side, so a refusal is a work list rather than a puzzle.
Report it and stop. Fixing the assessment is the assess step, which is a different
step.

It never refuses over how the body is worded. An excluded id the body does not
mention anywhere comes back as an `excluded_without_mention` warning beside the
stamp that was written. Pass that on to the person, because it is an exclusion with
no reason on record.

A `rejected` or `deferred` decision passes NONE of those gates. It is a person
declining to proceed, and it owes no complete impact analysis, so a half-baked or
unclear change request can be refused exactly as it stands. Never tell a user their
change request has to be finished before it can be turned down.

A `rejected` decision is recorded and KEPT. A rejected change request produces no
commits at all, so git holds no trace of it, and that record is the only place the
refusal survives. Never treat a rejection as something to tidy away.

`--by` is refused when it is blank. A status transition owes a person, so a blank
one is not written at all rather than written empty, which would leave a record no
later verb can read or repair.

**The uncommitted diff.** No verb in this group runs git. `plan` writes a draft,
`approve` stamps a record, `execute` leaves the edits it handed out, and `remove`
excises needs, and every one of them leaves the result in the working tree for a
person to read as a diff. Do not `git add` and do not `git commit` on their behalf.
Show the user what changed, say which verb produced it, and stop.

**Closing.** `ubc agent change close --id <CR_ID> --by <WHO> -p <project path>` is
final. It appends `closed` and nothing follows it, so closing is the person's call.
It is the move a record owes once it is `executed`, which is where the editor's
Changes panel offers Close too. First run it with `--dry-run` instead of `--by`: it
runs the four checks and writes nothing. They are `state`, `removed_ids_absent`,
`no_links_to_removed` and `no_clarification_markers`, and all four are reported
whether they hold or not. Show them to the person and say which failed. Run the real
close only when the person tells you to, with their name in `--by`. Do not supply
your own name, your harness name, or a placeholder.

## Step 3: report and stop

Report to the user:

- which step you took, and the verb you ran.
- what it produced, read off its own JSON or its own printed text rather than off
  your expectation.
- what comes next, named as the exact next step from the table above.
- who owns that next step: you, or a person.

Then stop. The user decides when the next step is driven.

Before ending, run this hard-stop check:

- Did I take exactly one step? If no, stop and correct course.
- Did I run `assess` or `execute` without `--print` or `--done`? If yes, say so
  plainly. A second, hidden agent did work in this session, and the user never saw it.
- Did I run `execute --done` without carrying out every step it printed? If yes, say
  so plainly. The record now says work was done that was not, and a person has to
  decide what to do about it.
- Did I print a step before I finished the one before it? If yes, say so plainly. That
  step quoted text my earlier step was about to change, so it has to be printed again
  and carried out again.
- Did I run `approve` or the real `close` without asking a person for the decision and
  the name? If yes, say so plainly. That record now names a person who did not decide,
  and a human has to decide what to do about it.
- Did I commit anything? If yes, say so plainly. The diff was the proposal.
- Did I name the next step and who owns it, and return control? If no, do it now.

## Notes

- The engine stamps `:cr_approval_decision:`, `:cr_approval_by:`, `:cr_approval_at:` and
  `:cr_status:` at approval, OVERWRITING whatever stands in those slots. Later
  `execute --done` and `close` stamps append to `:cr_status:` and leave the approval
  alone. Never hand-write any of them.
- `close` fails its `state` check for a change request that is not at `approved` or
  `executed`. A rejected or deferred one carries exactly the impact links it carried as
  a proposal, so there is nothing there to close out, and an already closed one is
  final. When any check fails nothing is written, and the report names the state it
  found.
- To remove a need the change deletes, use `ubc agent change remove --id <NEED_ID>
  -p <project path>` rather than editing the file. It refuses a marker-authored
  need, refuses a span containing another need unless both are named, and verifies
  the directive header before excising.
