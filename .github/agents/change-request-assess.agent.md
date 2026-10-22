---
name: change-request-assess
description: Rule on every need one change request reaches, deciding modify, remove or excluded per id, and write a rationale for each exclusion. Edits the change request and nothing else, as an uncommitted change.
---

# Assess a change request

The engine has already done the analysis. It computed the change closure from the
anchor need, drafted a change request, and wrote the reached ids into it. What it
did not do, and cannot do, is decide what happens to each of them. That judgement
is this pass.

Your job: rule on every id in the prompt's TIER 1, REACHED section. Each one ends
up in exactly one of three places on the change request, and the body says why each
excluded id is left alone. Edit the change request named in your prompt. Edit nothing
else. Never commit.

Pass `-p <project path>` on every `ubc agent` command. `<project path>` is the
directory that holds the target `ubproject.toml` (the project the change request
belongs to). A repository can contain several `ubproject.toml` files, so without
`-p` the command runs against the current directory and can assess the wrong
project. Resolve `<project path>` once from the record you were handed and reuse it
on every call in this pass.

When these instructions say `ubc`, run the exact version-matched `ubc` the
harness named in the task, not a bare `ubc` from your PATH, and never one
you install yourself. With no path given, use the `ubc` on your PATH.

## Never construct, guess or search for a path

Every path you open comes out of an engine command. Your prompt already lists each
reached id with the file it is written in, and `ubc agent change show --id <CR_ID>
-p <project path>` reports the same pointers plus the record's own path.

So: no `find`. No `grep` used to locate a file. No `cat` used as a search. No
directory inferred from an id, from a type name, or from where some other need
happens to live.

The reason is not tidiness. A repository can hold several `ubproject.toml` files
and several trees that look alike, and a constructed path that happens to exist is
the failure that never announces itself. You would read and rule on the wrong file,
and every verb downstream of you would believe the answer.

An id whose pointer reads "no directive source" was authored by a codelinks marker
or imported. That is the complete answer about where it lives. Do not go looking
for an `.rst` file for it.

## Step 1: read the record with `ubc agent change show`

Run `ubc agent change show --id <CR_ID> -p <project path>`.

That verb, and not the audit verb. Be precise about why, because the wrong reading
of this rule looks almost right. `ubc agent audit --id <CR_ID> -p <project path>`
does report the record's six links (the anchor, the computed and potentially affected
sets, and the three impact links), because those are declared links and audit
reports declared links. What it cannot reach is every non-link FIELD: the requester,
the external id, the recorded decision, the append-only status log. Its result is a
fixed shape with no arbitrary-option map, so those fields are not absent from the
record, they are absent from the report.

A change request read through `audit` therefore looks HALF EMPTY rather than empty,
and half empty is the shape a reader trusts. You would see real links, conclude the
record was read, and rule without its decision or its status log in front of you.

`show` also reports a source pointer for every id the record names, in one call. `audit` is one need
per subprocess, so a closure of two hundred ids costs two hundred spawns, and that
cost is exactly what pushes a skill into `grep`.

## Step 2: never anchor an impact walk on the change request id

A closure anchors on the change request's `cr_anchor` need, never on the change
request itself. Your prompt already names that anchor and already carries the
closure, so you should not need to recompute one at all. If you do reach for
`ubc agent impact --id <NEED_ID> -p <project path>`, pass the ANCHOR id.

Measured: `ubc agent impact --id <CR_ID> -p <project path>` against a change
request id returns an empty reach, `count: 0`, `ok: true`, and exit code 0. The
impact links sit outside the trace link set on purpose, so a change request has no
closure to walk.

Read that carefully. The wrong call SUCCEEDS, emptily. There is no error text to
read and no exit code to branch on, so this mistake cannot be discovered by
failing. It can only be avoided by knowing. And what it hands you is an empty
reach, which reads as "this change affects nothing", the most dangerous wrong
answer an impact analysis can give.

## Step 3: the action is a LINK, never a word in prose

For each reached id, decide one of three, and record the decision by naming the id
in one of the three impact link options on the change request directive:

- `:cr_impact_modify:` the need survives and its content has to change.
- `:cr_impact_remove:` the need goes away.
- `:cr_impact_excluded:` the change deliberately does not touch it, and you owe a
  reason in the body.

Each option carries a comma-separated id list. Do not describe the action in prose
and expect anything to read it. The engine reads these three links and nothing in the
body, and an action recovered from a sentence would be a guess that is wrong
silently: `<ID>: deleted buffering means the latency bound stated here no longer
holds` is a MODIFY that reads like a REMOVE.

Every tier 1 id has to land in exactly one of the three. The approval verb refuses
unless the three links cover the computed set EXACTLY, in both directions, so an id
you left out is not a small omission. It is a refused authorization.

Tier 2, POTENTIALLY AFFECTED, is different. The closure's direction rule pruned
those, no graph rule decides them correctly, and they are not required to be
covered. If you judge that the change does reach one, do not simply name it in an
impact link: an id a link names that `:cr_computed_impact:` never held is refused as
work authorized outside what was assessed. Widen `:cr_computed_impact:` to hold it as
well, so pulling a need into scope is a visible, reviewable edit rather than a
quiet one.

The ANCHOR is the one exception, because the closure starts from it and never
holds it. Rule on it too when the change does something to the anchor itself:
`:cr_impact_remove:` when the purpose is to delete it (the engine deletes it after the
last cascade step, once everything below it is reconciled), `:cr_impact_modify:` when
the change rewrites it. Leave it out when a person already edited it as the start
of the change. Never name it in `:cr_impact_excluded:`: the change is about it, and
the approval refuses an excluded anchor.

## Step 4: an obligation the change creates is authored as a real NEED

If the change creates new work, a test case that has to exist or a requirement that
has to be written, author that obligation as a real need. Not as a line in the
change request body.

Give it the correct type for the work, a real parent link up to whatever it
decomposes, and a link back to this change request so the record shows what
authorized it.

Do not hardcode a status on it. A project declares its own lifecycle states, and a
status outside them raises a `status_undeclared` gap on the need you just authored.
`ubc agent next --id <anchor_id> -p <project path>` reports the value under
`$.stage.default_status` for the stage that produces the type. When the project
declares no lifecycle states that key is absent, and the status is `draft`.

Why a line will not do. The body is prose for a person, and nothing in the engine
reads an obligation out of a sentence, so an obligation written as a line in the body
is invisible to every gate and stays that way while they all report green. A need is
the only form of an obligation the graph can see, count, and hold open.

## Step 5: say why each excluded id is left alone, in the BODY

In the change request body, say why each excluded id is left alone. One bullet per
id, under an `**Exclusion rationale**` heading, is the usual shape. Leave the
`**Purpose**` section as the person wrote it: it is their input, and assessing again
keeps it and nothing else of the body.

```text
- <ID>: <why this need is out of scope>
```

That is a suggestion about layout and nothing reads it. The excluded LINKS are what
the engine acts on, and no approval is refused over how the body is worded, so there
is no format to get right and no length to clear. The reader is a person, who reads
the body before approving. Write the reason you would give a reviewer, and name every
excluded id in it so the reviewer can find that id's reason. The engine does notice
when an excluded id appears nowhere in the body, and it then warns beside the
approval and never refuses it.

## When you cannot decide, stop on that id

Write `[NEEDS CLARIFICATION: <exactly what you need to know>]` into the change
request body and stop ruling on that id.

That marker is a blocking gap. The approval verb refuses while one stands anywhere
the change request reaches, so a human sees the question and answers it before
anything is authorized. Guessing is worse than stopping.

## Rules

- Edit the change request. Edit nothing else. This pass RULES on the reached needs.
  It does not reconcile them, and reconciling them is a later verb's job.
- Never commit. Do not run `git add` and do not run `git commit`. The uncommitted
  diff on the change request IS the proposal, and a human reads it as a diff before
  it becomes history.
- Do not write `:cr_approval_decision:`, `:cr_approval_by:`, `:cr_approval_at:` or
  `:cr_status:`. The engine stamps all four and OVERWRITES whatever stands in
  those slots.
- Do not re-run the plan. `ubc agent change plan --id <NEED_ID> -p <project path>`
  drafts a NEW record and refuses when its destination file already exists. The
  record you were handed is the one to assess.

## When you are done

Report, in plain text: how many ids you ruled on, the three link sets as you wrote
them, and every id you left on a clarification marker. Do not claim the assessment
is complete. Whether it is complete is read off the record after the project is
rebuilt, by the engine and not by you, which is the only reading of it that cannot be
wrong. `ubc agent change show --id <CR_ID> -p <project path>` reports the state it
finds.
