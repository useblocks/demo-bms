---
name: change-request
description: Reconcile ONE downstream stage's artefacts with a changed upstream. The change-request cascade carries a human's edit down the full V and runs this skill once per downstream stage, as a headless pass or as a step handed to the agent already in a session. Show the blast radius, then modify only the artefacts the change made inconsistent, inside the approved scope, as uncommitted changes for human approval.
---

# Change request

A human has EDITED one need (the anchor) and that edit is being propagated DOWN the
V. The cascade derives the downstream stages of the anchor's stage and takes ONE
reconcile pass per stage, rebuilding the graph between passes so each pass sees the
upstream already reconciled. A headless run spawns each pass as its own process. In
a session, the agent already running takes the passes itself, one step at a time,
and the printed step ends with the command that prints the next. Either way THIS
pass reconciles ONE stage.

Your prompt's CHANGED-UPSTREAM section carries the new, authoritative content this
stage must become consistent with. Your job for THIS stage: MODIFY its existing
artefacts so they match the changed upstream. Change ONLY what the edit actually
invalidated. Do not rewrite anything that still matches, and do not re-author
artefacts wholesale. Author a brand-new artefact ONLY when a genuinely new upstream
item now requires one. Never commit.

Pass `-p <project path>` on every `ubc agent` command. `<project path>` is the
directory that holds the target `ubproject.toml` (the project the anchor need
belongs to). A repository can contain several `ubproject.toml` files, so
without `-p` the command runs against the current directory and can reconcile
the wrong project. Resolve `<project path>` once from the anchor need or file
you were handed and reuse it on every call in this pass.

Do NOT re-discover the project with `find`, `grep`, or `cat`. Use
`ubc agent impact --id <anchor_id> -p <project path>` for the blast radius and
`ubc agent audit --id <id> -p <project path>` for an artefact's body and its
source path + line range. For ad-hoc need queries use `ubc query filter
<query>`. Prefer the `ubc` CLI over the ubCode MCP query tools
because the CLI is more capable. These give structured, reliable data. The only files
you read or edit are this stage's own artefacts, at the exact paths `audit`
reports.

When these instructions say `ubc`, run the exact version-matched `ubc` the
harness named in the task, not a bare `ubc` from your PATH, and never one
you install yourself. With no path given, use the `ubc` on your PATH.

## Step 1: blast radius

Run `ubc agent impact --id <anchor_id> -p <project path>` for the originally-edited
anchor named in the prompt and read its JSON. Note what the change reaches
DOWN (children, code, impl and test needs) so the impact on THIS stage is
named, not guessed. Call out any `stale_gaps` already attributed to the anchor
or anything it reaches. They are debt the change either fixes or inherits.

## Step 2: stay inside the approved scope

When a change request authorizes this cascade, your prompt carries a section whose
first line begins:

```text
=== APPROVED SCOPE (
```

The rest of that line names the change request id and repeats that this is a
boundary. Match the opening, never a longer literal. The section header is NOT
`=== APPROVED SCOPE ===`, so looking for that string finds nothing on a prompt that
carries a real approval, and you take the no-authorization branch further down,
which is the precise failure this section exists to close.

That section is the BOUNDARY of this pass, not a hint and not an opening
suggestion. It names three sets and one destination, each on its own line, and each
line's label is written out in full:

- `MODIFY (this stage may edit these in place):` the ids of this stage's own
  artefacts you may edit.
- `REMOVE (this stage may delete these):` the ids of this stage's own artefacts the
  change deletes.
- `GOING AWAY anywhere in the graph (stop pointing at these):` every id the change
  removes, at any stage. These are the targets you must stop pointing at. The need
  that keeps a dead pointer is usually at a different stage from the need that was
  deleted, which is why this list reaches you at all. When the need this cascade
  starts from is on it, the change removes the very need it is aimed at: reconcile
  this stage as if that need no longer exists, and leave its deletion alone, which
  the engine does after the last step.
- `PURPOSE (what the change is for):` the change request's own statement of why
  the change is made. Read it before you decide what an id in your sets needs.
- where a brand-new artefact of this stage goes, as a resolved path and an id
  prefix, in the sentence that follows the three lists.

An EMPTY list is a real instruction, not a missing one.
`MODIFY (this stage may edit these in place): (none)` says this stage is authorized
to change nothing, which is a different statement from a section that was left out.

If you conclude that an artefact OUTSIDE those sets has to change, do not edit it.
Write `[NEEDS CLARIFICATION: <the id and why it has to change>]` and stop on that
artefact. Widening an approved scope is a human's decision, not yours.

That stop is the entire point of the rule.

When the prompt carries no line beginning `=== APPROVED SCOPE (` at all, this
cascade is propagating a human's edit with no authorization record behind it.
Reconcile what the change actually invalidated, and invent no boundary of your own.
Read that absence off the opening above rather than off any longer string, or an
approval that IS present reads to you as absent and every constraint it carries is
gone.

### Where a brand-new artefact goes

Author one ONLY when a genuinely new upstream item now requires it. When you do,
the approved-scope section already carries the resolved route and the id prefix for
this stage, in the sentence after its three lists. Use both verbatim rather than
placing the file yourself, and
link the new artefact back to the change request, so the record shows what
authorized it.

Either value can report that it resolved to nothing, and it says so in words. "no
route resolves, so a new artefact needs a human to place it" means exactly that:
stop and say so, do not pick a directory. "the type declares no prefix" means the
project fixes no lead for this type's ids.

## Step 3: reconcile this stage's artefacts

The prompt tells you which stage you are reconciling and gives you, for a NEED
stage, the EXISTING artefacts of this stage and the CHANGED UPSTREAM they trace up
to. For a CODE stage it gives the CHANGED CONTRACT and the source target directory.

For each existing artefact of this stage:

- compare it against the changed upstream. Decide whether the edit made it
  inconsistent.
- if it is STILL consistent, leave it alone and do not touch it.
- if the edit made it INCONSISTENT, MODIFY it in place so it matches the new
  upstream. For a NEED stage, get the artefact's `.rst` path and line range from
  `ubc agent audit --id <id> -p <project path>` (its `source` field) and edit only
  that need's body. For a MARKER-AUTHORED stage (an implementation or
  verification arm), the artefact
  is a one-line codelinks marker in the production or test source, in the exact
  shape your prompt's CHANGED CONTRACT section shows: edit the marker (its title,
  its outgoing link target) and the code beneath it so it still realises the
  changed upstream, KEEPING the marker so the need it materialises stays linked.

Leave every edit as an UNCOMMITTED working-tree change. Do not `git add` and do not
commit. The diff on each artefact IS the proposal, which the human reviews and
approves.

If you cannot tell HOW an artefact should change to stay consistent with the new
upstream, do NOT guess. Write `[NEEDS CLARIFICATION: <what you need to know>]` into
its body and stop. The clarification gate flags it for the human, who answers it.

## Step 4: a removal goes through `ubc agent change remove`

When the approved scope names an id under REMOVE, do not excise the lines yourself.
Run `ubc agent change remove --id <NEED_ID> -p <project path>`, repeating `--id`
once per id you are removing at this stage. It edits the reStructuredText and
leaves the result uncommitted, exactly as your own edits are left.

Hand-editing skips three refusals, and each of them exists because that failure has
already happened:

- It refuses a MARKER-AUTHORED need. The refusal reports the marker's own path and
  line range, because those ARE known, and explains that the extent of the CODE
  beneath the marker is recorded nowhere. Excising a guessed block of a source file
  is unrecoverable.
- It refuses a need whose span CONTAINS another need, naming the inner one, unless
  that inner id is named for removal too. Measured: deleting a need by exactly the
  line range `audit` reports also destroyed a need nested inside it, taking a
  project from six needs to four with `release-check` still reporting `ok: true`
  and an empty `new_gaps`.
- It verifies the first line of the span against the expected directive header
  before touching the file, so a line range that has gone stale excises nothing
  rather than excising the wrong thing.

Every check runs over the whole requested set BEFORE the first line is touched, so
repeating `--id` for a nested pair is how you authorize that pair, and a set
carrying one bad id changes no file at all. An absent id is a named error, never a
no-op. A document the removal empties is LEFT on disk, because deleting it could
break a toctree and that is a human decision.

The removal takes the needs away. It does not take away the links pointing at them.
Fix every reference this stage owns to an id on the GOING AWAY list, in this same
pass.

## The cascade handles the next stage

You reconcile ONE stage. The next downstream stage is a SEPARATE pass, taken after
the graph is rebuilt so it sees your reconciled output. A headless run starts that
pass as its own process. In a session it is the next step, which the footer of the
step you were given prints once this one is done. Either way you do not recurse or
reconcile the next stage's artefacts in this pass. Reconcile your stage well and
stop.

## After approval

Once the human accepts the downstream edits, the normal loop closes them out:
because each edit staled that need's and its children's verdicts,
`ubc agent release-check --with-verdicts -p <project path>` reddens on the
`outdated` downstream. Re-running `ubc agent run -p <project path>` (which
re-reviews and records fresh verdicts carrying the new fingerprints) returns
the gate to green. The change is not "done" until that re-review lands.
The gate enforces it.
