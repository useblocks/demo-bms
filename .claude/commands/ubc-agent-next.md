---
name: ubc-agent-next
description: Resolve and act on the single next workflow action, then stop.
---

Run `ubc agent prompt -p <project path>` and follow what it prints. That is the
instruction for the ONE next action. Do one step, then stop and hand control
back to the user.

Without an anchor the verb resolves the stream from your working tree's CHANGED
FILES, and it needs at least one changed need file among them to seed a stream.
Only a fully clean tree falls back to the branch merge-base. The cascade keys on
files, not on needs, so any dirty file suppresses that fallback even when it
carries no need: a single fresh verdict is enough, which is why the confirm
re-run in step 5 keeps its `--id`.

When nothing seeds a stream, STDOUT tells you what happened. Non-empty stdout
means the verb resolved something, and step 2 branches on the PREFIX of its
first line. EMPTY stdout means it printed only an error, so READ that error:
the words `needs an anchor need to brief from` are the ask, answered by
supplying the need id you are driving, as
`ubc agent prompt --id <need_id> -p <project path>`, reusing that SAME id for
the rest of the step. Empty stdout carrying ANY OTHER stderr text is a real
failure (for example a wrong `-p`, or an `--id` that is not a need in the
graph), so fix what that text names instead of re-running with an anchor.
Anchoring on some downstream need you picked yourself narrows the stream to
that seed.

Pass `-p <project path>` on every `ubc agent` command. `<project path>` is the
directory that holds the target `ubproject.toml`. A repository can contain
several `ubproject.toml` files, so without `-p` the command runs against the
current directory and can target the wrong project. Resolve it once from the
need you were handed and reuse it on every call.

When these instructions say `ubc`, run the exact version-matched `ubc` the
harness named in the task, not a bare `ubc` from your PATH, and never one
you install yourself. With no path given, use the `ubc` on your PATH.

## Act on the instruction

1. Run `ubc agent prompt -p <project path>`, or
   `ubc agent prompt --id <need_id> -p <project path>` when it asks for an
   anchor. Its output is plain text, not JSON. It executes nothing and needs no
   runner configured.
2. EMPTY stdout means the verb printed only an error, so READ that error and
   fix what it names. Otherwise branch on the PREFIX of the FIRST line.
   `NO ACTION (` is the stop signal. `=== WORKING DIRECTORY ===` means there IS
   an action, and the line after it names the resolved project root. A first
   line carrying NEITHER prefix is not a resolved action, so report it verbatim
   and stop.
   On the `NO ACTION (` branch the text under that line names the one action
   the state calls for, which may itself be a command to run as your NEXT step.
   Report it and stop. On the `=== WORKING DIRECTORY ===` branch, run every
   command the instruction gives you FROM the directory that second line names,
   and resolve every relative path AGAINST it.
3. Follow the instruction as written. The engine has already picked the arm
   (author, review, or fix the needs that failed review), so do not re-derive
   which one applies and do not widen the task.
4. On a review arm, hold to the rule the printed instruction states. Run this
   review in a context separate from the one that authored the needs under
   review, so no author grades its own output: the engine cannot observe which
   context you use, so nothing enforces this for you. Where your harness has
   subagents or tasks, that separate context is one of them.
   Then submit each verdict by PIPING its JSON to the command the
   instruction quotes, with `-p <project path>` appended. If your harness cannot
   pipe stdin, write the draft to a temp path OUTSIDE the repository and pass it
   with `--file`. Never write into the verdicts directory, and never stamp a
   fingerprint by hand: `ubc agent verdict-submit` stamps the fingerprints the
   gate checks, and a hand-written verdict counts as outdated forever.
5. Confirm, then STOP. Re-run
   `ubc agent prompt --id <need_id> -p <project path>` with the SAME id this step
   was driven with, to check the stage actually advanced. Pass `--id` here even
   when step 1 needed no anchor: a review leaves an uncommitted verdict JSON, and
   an anchor-free call sees that as a change carrying no need, resolves no
   stream, and exits non-zero. `ubc agent next --id <need_id> -p <project path>`
   answers the same question as JSON. Report what now comes next and hand control
   back. Work the next step only when the user asks for it.

## The `next` report

`ubc agent next --id <need_id> -p <project path>` is the JSON report behind the
same decision. Read it when you want the state rather than the instruction.

- `$.ok` is the envelope, `$.stage` is the at-most-one stage (a single object or
  `null`, never an array), `$.reason` says why there is none.
- If `$.stage` is set, read `$.stage.id`, `$.stage.produces`,
  `$.stage.route.resolved_path` (falling back to `$.stage.route.path` when no
  stream resolved), and `$.stage.skill`. The output field names are not the
  `ubproject.toml` key names, so read the JSON paths.
- `$.stage.gates_to_pass` says what is still open. A synthetic `review` token
  means the artefact is authored and the pending action is to review it. When
  `review` sits alongside other gates, the structural gates close first.
- If `$.stage` is `null`, read `$.reason`:
  - `empty`: the workflow configuration derives no stages. Define
    `[[workflow.stages]]`. This is a configuration state, not "nothing authored
    yet": a fully populated project reports it too.
  - `done`: no stage of this stream is actionable. Check `$.open_streams` before
    calling the project finished, since `done` is vacuous for an anchor no stage
    produces.
  - `blocked`: a dependency stage is unmet. Resolve it first.
  - `id_not_found`: the `--id` is not a need in the graph. Fix the id.
  - `stage_not_found`: the `--stage` is not a stage of this workflow. Fix the
    stage name.
- The last two reasons come with `$.ok` false and a non-zero exit. Never read
  either as progress.
