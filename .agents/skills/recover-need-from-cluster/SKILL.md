---
name: recover-need-from-cluster
description: Synthesize the higher-stage need or needs a cluster of already-recovered lower needs supports, together with the diffuse intent signal in the git surface, authoring the up-link each cluster member needs to cite, partitioning the members when the cluster holds several capabilities, and marking an intent-gap rather than fabricating when no intent source grounds the stage.
---

# Recover a need from a cluster

This is a synthesis stage of reverse recovery: one stage above already-recovered
lower needs (for example, requirements already recovered by
`recover-requirement-from-code`), with no direct code grounding of its own.
You read a precomputed cluster of lower needs plus whatever intent signal is
available (commit messages, PR or issue text), and synthesize the higher-stage
needs that both are grounded in. You do not cluster the lower needs yourself:
the engine already grouped them deterministically before handing you the
cluster.

**How MANY needs to author is your judgement, and the engine takes as many as
you record.** Usually a cluster is one thing and the answer is one need. When
the cluster plainly holds several separate capabilities, author one need PER
capability instead of one need restating all of them: a single need covering
everything a module does is not intent, it is a table of contents. Partition the
members so every member cites exactly the one it belongs to, never several, and
never invent a capability to split on. When you do split, the split has to come
from what the members SAY, not from their count.

This stage has a prerequisite. The requirement stage must already be recovered
and recorded in the ledger for the modules in scope, because that record is
where your inputs come from. A briefing whose `targets` list is empty, or whose
`blocked` field names a stage, is not a work order: report the `blocked` text
verbatim and stop. Do not walk the filesystem to invent a decomposition, and do
not run `ubc agent reverse plan` for another stage to fill the gap. Recovering
this stage before its requirements is not supported.

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

Your briefing carries one target from `ubc agent reverse plan`'s output (its
`members`, the precomputed cluster of lower-need ids, and its
`recovered_into`), plus the brief's own `route_path`, `known_streams`,
`default_status`, `authoring` and `author_skill`. If you were not handed this already, run
`ubc agent reverse plan <scope> --stage <STAGE_ID> --source <LOWER_ID> ...`
(repeat `--source` once per lower-need id) and read the one entry in
`targets` whose `members` match.

**You choose the target document. The engine does not.** `route_path` is the
stage's configured route with its `{stream}` placeholder left in, for example
`specs/{stream}/overview.rst`. A stream is a coordinate in the needs graph,
not a folder, and deciding which one a cluster belongs to is a judgment about
what the clustered needs are FOR. `known_streams` lists the slugs this project
already uses.

**Read your own target's `source_path` first.** It is `needs:<module>`, minted
from the module its members were recovered from, so it usually names the stream
outright: a cluster keyed `needs:auth` belongs to `auth`. Two keys do not answer
it. `needs:unscoped` means the ledger could not place those ids at all, and a
nested key such as `needs:needs:auth` is an upper rung over a lower cluster, so
read the innermost segment (`auth`). When the key does not settle it, `audit`
reports each member's own `source.path`, and a cluster whose members already
live under one stream almost always belongs to it.

Put your slug in place of `{stream}`, author at the path that gives, and hand
that concrete path back as `target_rst`. `ubc agent reverse record` refuses one
that still carries `{stream}`.

**Unless the target carries a `recovered_into`, in which case that is the
document.** A cluster key is stable, so a non-null `recovered_into` means this
same cluster has been synthesized before and that path is where its needs were
authored, read from the ledger rather than guessed. Author this pass there too
and hand that same path back. Choosing differently does not give you a second
document: the ledger records ONE destination per source and takes the newer
one, so the needs the earlier pass authored would be recorded as living in your
new document while their text stays where it is. `ubc agent reverse record`
warns when a re-record does that and names the needs it just re-homed. It is
`null` for a cluster synthesized for the first time, which leaves the choice
entirely yours, and `null` again when the earlier pass recorded a destination
that cannot be authored into, which the brief reports under `unusable_targets`.
The action is the same either way. Test for `null`, never for an absent key: the
engine always serializes it.

For the type this stage produces and its id prefix, run
`ubc agent next --stage <STAGE_ID> -p <project path>` and read `produces` and
`route.id_prefix`, and read nothing else out of that payload for THIS stage.
`ubc agent next` answers for FORWARD authoring, so the same payload also
carries a `skill` naming the stage's forward authoring skill rather than this
one. Everything else you need about this stage is already on your briefing, so
read it there. Its `gate` is the one key you do read from a payload other than
your own for this work: run `next` again for a MEMBER's stage
to get that stage's `gate.link` and `gate.up_type`, which is the up-link field
the member's own directive must carry. Follow this skill wherever the rest of
either payload disagrees with it.

## The project decides the shape, not this skill

Three keys of your briefing carry what varies from one project to the next.
None of them is written into this skill, and none of them is yours to guess.

**`default_status` is the status every need you author opens in.** Write
`:status: <that value>`. When the key is ABSENT the project declares no
lifecycle states, and the value is `draft`, which is what a forward authoring
run is given on such a project. A synthesized need opens exactly where a
hand-authored one opens, because both go through review before anything trusts
them. What marks it as machine-recovered is the ledger entry `record` writes
afterwards, never a word in the status field, so do not invent a status of your
own to mark it and do not carry one over from an example. This is about the
needs YOU author. A member's own `:status:` is left exactly as `audit` reports
it, the same as every other field of its directive except its up-link.

**`authoring` is the project's own directive for this stage**, and it is where
"how many" and "what shape" are answered. Follow it. It is written for forward
authoring, so where it names an input you do not have, the shape and the
coverage it asks for still hold and the cluster is your input instead. The key
is absent when the stage declares no directive, and this skill's own rules are
then the whole answer.

**`author_skill` names the skill a forward run at this stage would use.** It is
a POINTER, not something to run. Do not load it and do not follow it: it is
written for authoring from stated intent, it forbids the member reads this stage
depends on, and it waits for an approval nobody may be there to give. It is on
your briefing so that a person comparing what you synthesized against what this
project authors by hand knows which document to open.

For each member id, run
`ubc agent audit --id <ID> -p <project path>` to read its `type`, `title`,
`body`, `status`, `trace.outgoing` (its existing up-links), and its
`source.path` (the `.rst` file its directive currently lives in). `audit`
is the oracle for which file a member lives in: do not re-discover the
project with `find` or `grep`. Treat `source.line_range` as informational
only. It goes stale the moment any earlier edit in the same file inserts
or removes a line, so it is never a safe edit target: see "Edit members
by id, never by line range" below for how to locate the directive you
are about to change.

## Check the project's id convention before you mint

`route.id_prefix` is only the fixed lead of a valid id, not the full
pattern the synthesized need's id must satisfy. The project's own
`id_regex` governs what may follow that lead, and none of the
`reverse plan`, `next`, or `audit` verbs reject an id that violates
it: audit even echoes an invalid id back to you as though it were fine.
Before you mint the synthesized need's id, read the project's `id_regex`
(`ubc config <project path>`, under `needs.id_regex`,
or the `[needs]` table in `ubproject.toml` directly) and check the id
against it. Build the id as the reported prefix followed by a descriptive
word, never followed by a number: a digit right after the prefix is
exactly what an `id_regex` requiring a letter there (for example
`^[A-Z]+_[A-Z][A-Z0-9_]*$`) rejects. If the synthesized need still seems
to have been silently dropped after you author it, run `ubc build index
<project path> --show-warnings` to see the id and other validation
diagnostics that none of the `ubc agent` commands above surface.

## Gather intent, without fabricating it

**Your briefing's `intent_refs` is the reference list. Do not re-derive one.**
The engine pulled those issue and change-request references out of the commit
messages that touched this brief's targets, and each carries an `id`, an
`origin` naming the rule that matched it, and, when the text named one, an
`owner` and a `repo`. Re-deriving them yourself drops the cross-repository
ones and the project-key allowlist you cannot see. An empty list is the
ordinary answer for a repository whose commits name nothing.

Run `ubc agent reverse sources <scope> -p <project path>` (the `scope` is your
briefing's own) to see which intent kinds are available: `commit_history`,
`change_requests`, `issues`. Each available row names its `provider`, and for
the two forge kinds that provider is an installed SKILL rather than the
engine. Hand `intent_refs` to the skill the row names and use what it resolves.
A row that reports unavailable has a `detail` saying why, and that detail is
usually the fix.

That is the whole of the intent gathering this skill does. Do not shell out to
a forge CLI yourself, and do not walk the git history: the cluster you were
handed is a set of lower-need ids, not files, so there is no path to run a log
against. Where none of it produces text, use only what your driving tool
already placed in your prompt.

## Grounded synthesis

1. Identify the theme or themes the resolved members share: what capability,
   taken together, do they compose? This is the mandatory grounding source, and
   every synthesized need traces back to it. Most clusters compose ONE theme.
   When the members plainly compose several, name each one and treat each as its
   own grounding source, with the members it actually covers.
2. Check each intent snippet against that theme: does it name the same
   theme, in its own words, not merely a topically nearby one? Snippets that
   pass ground the synthesized title and body, and their language should be
   preferred over an internal term implied only by the members.
3. If no snippet passes (including when none is available at all), mark the
   synthesis with an explicit intent gap rather than inventing a plausible
   commit or PR reference to fill it. Do not hold back emission for lack of
   intent signal: synthesize from the member theme alone, and record the
   gap in your report so a human or the review step can weigh it.
4. **Never fabricate.** The synthesized body may state only what the
   combined member bodies and, when present, the qualifying intent snippets
   actually support. Narrow the body rather than add a capability, a
   constraint, or a scope that is absent from both.

### The merge test, on every pair, before you author

Deciding HOW MANY needs a cluster supports is the judgement this stage exists
for, and it is the one most easily got wrong in both directions. One need
restating everything a module does is a table of contents. A need per operation
is the requirements rung written twice.

One question settles both, and it is asked of PAIRS, not of counts:

> Would someone who asked for one of these two necessarily be asking for the
> other as well?

**Yes means they are one capability.** Merge them. "Insert a node" and "remove a
node" fail this: nobody wants a tree they can add to but not take from, so both
are "change the tree's structure". "Serialize" and "deserialize" fail it too:
one without the other stores data nothing can read back.

**No means they are two.** "Walk the tree in depth-first order" and "copy a
subtree into another tree" pass: either is useful to someone who does not want
the other.

Then ask the same question inside each need you kept:

> Is there a part of this one that someone could want WITHOUT the rest?

Yes means it is two needs, and the split goes exactly there. A title that needs
several verbs to say what it covers is the usual sign, though it is only a sign:
"serialize and deserialize" is two verbs and one capability, while "build, edit,
traverse and persist" is four verbs and four.

Report both numbers, `0` included: how many pairs you merged, and how many needs
you split. Counting is what makes the check happen.

Where your briefing's `authoring` directive says something different about how
many, the directive wins: it is the project speaking about its own graph, and
this test is the default for a project that says nothing. The test still decides
WHERE a split falls, because a directive states a policy and never which two
behaviours belong together.

## Output shape

Each synthesized need, at the path you substituted into `route_path`. Author
them into the same document, one after another, when a cluster produced more
than one:

```rst
.. <type>:: <short_title>
   :id: <ID with the reported prefix>
   :status: <the briefing's `default_status`, or `draft` when it carries none>

   <Synthesized capability statement, grounded in the cluster and, where
   available, the qualifying intent signal.>
```

It carries NO down-link to the members. A higher need never points down at
the needs it summarizes: it only ever appears as the target of their
up-links, the other direction entirely.

When the cluster produced more than one need, each member cites exactly the ONE
it belongs to, never two and never all of them. A member that appears to belong
to several means the split was drawn in the wrong place: redraw it, or collapse
back to one need, rather than linking the member twice.

For each resolved member, edit its own directive in place, inside the
`.rst` file at the `source.path` `audit` reported, with every existing
field unchanged except its up-link field (the trace link named in your
briefing for the member's own stage, resolved the same way `ubc agent
next --stage <STAGE_ID>` reports it as `gate.link` / `gate.up_type` for
that stage), extended to include the new need's id (deduplicated,
existing order preserved, appended if new). See "Edit members by id,
never by line range" below for how to locate the block you are about to
change:

```rst
.. <member_type>:: <member_title>
   :id: <member_id>
   :status: <member_status>
   :<link_field>: <existing values...>, <new_id>

   <member_body unchanged>
```

### Edit members by id, never by line range

Cluster members often share one authored file, because the stage below
routes by stream and a cluster is usually one stream's worth of work.
They do not always: a project whose lower stage routes per module, or
whose members were recovered in separate passes, spreads them over
several files. Read each member's own `source.path` rather than assuming
either shape. Wherever two members DO share a file, adding the up-link
field to one of them shifts every later member's real line position in
it, so a line range fetched once (from `audit`, or anywhere else) goes
stale the instant you make the first edit there. Editing by a
pre-computed range then lands on the wrong block and corrupts the file.

Locate each member's directive by matching its own `:id: <member_id>`
line in the file's current, on-disk content instead, never by an offset
computed earlier in this run. Process one member at a time: read the
file, find the directive block whose `:id:` field equals the member you
are about to edit, edit only that block, then move to the next member.
Never batch a set of line-range edits computed up front, and never reuse
a range you fetched before an earlier edit in the same file.

## Propose before you author

**With an interactive user**, do NOT write any RST yet. Present a short,
scannable outline first: the synthesized need's id and title, the theme it
grounds in, which intent snippets (if any) it cites, whether it carries an
intent gap, and the list of member ids whose up-link you will extend. Wait
for them to approve or adjust, and do not author until they confirm.

**With no interactive user**, make the same outline and approve it yourself.
Check it against the members' own bodies and the intent snippets you cited,
then author. Do not stop here and do not ask.

On approval (yours or the user's), author exactly what you proposed.

## Rules

- Sphinx-needs convention is child cites parent: a member's up-link points
  up at the synthesized need, never the reverse, and members are never
  linked to each other.
- If the members do not share one coherent theme even after discarding
  outliers, emit the best-supported synthesis over the members that do
  share it and say so in your report. This skill does not refuse on
  incoherence.
- **A field the project's own schema requires, that this evidence cannot
  ground, is not yours to invent.** Leave it out of what you author, and say
  plainly in your report which field you left out and why the evidence could
  not ground it.
- This skill never invokes `ubc agent reverse record`. Hand your emitted
  need to `record-recovery-ledger` once you are done. If the synthesized
  need itself later turns out to bundle more than one capability, that is
  `split-recovered-need`'s job, not this skill's.
