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

**How MANY needs to author is the project's `authoring` directive's call when it
states one, and your judgement when it does not. The engine takes as many as
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
`produces`, `id_prefix`, `default_status`, `authoring`, `author_skill` and
`author_skill_path`. If you were not handed this already, run
`ubc agent reverse plan <scope> --stage <STAGE_ID> --source <LOWER_ID> ...`
(repeat `--source` once per lower-need id) and read the one entry in
`targets` whose `members` match.

**You choose the target document. The engine does not.** `route_path` is the
stage's configured route with its `{stream}` placeholder left in, for example
`specs/{stream}/overview.rst`. A stream is the folder under the route that
holds one functional area's needs. Choose one per target, from the functional
area its cluster belongs to, which is a judgment about what the clustered needs
are FOR. Targets about different areas go to different streams, and several
streams in one run is normal. Never put the whole scope under one stream unless
every target belongs to the same area. `known_streams` lists the streams this
project already uses. Reuse one when a target belongs to it, rather than
authoring a synonym beside it.

**Read your own target's `source_path` first.** It is `cluster:<module>`, minted
from the module its members were recovered from, so it usually names the stream
outright: a cluster keyed `cluster:auth` belongs to `auth`. Two keys do not answer
it. `cluster:unscoped` means the ledger could not place those ids at all, and a
nested key such as `cluster:cluster:auth` is an upper rung over a lower cluster, so
read the innermost segment (`auth`). When the key does not settle it, `audit`
reports each member's own `source.path`, and a cluster whose members already
live under one stream almost always belongs to it.

Put a target's stream in place of `{stream}`, author at the path that gives,
and hand that concrete path back as its `target_rst`.
`ubc agent reverse record` refuses one that still carries `{stream}`.

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

**The brief's `produces` and `id_prefix` name the need type you author and the
prefix its ids start with.** Read them there. `id_prefix` is absent when that
type declares no prefix, and the project's `id_regex` below is then the whole
rule for an id. Do not guess either value.

Only when you were handed no brief, or a brief that carries no `produces`, run
`ubc agent next --stage <STAGE_ID> -p <project path>` and read `produces` and
`route.id_prefix`, and read nothing else out of that payload for THIS stage.
`ubc agent next` answers for FORWARD authoring, so the same payload also
carries a `skill` naming the stage's forward authoring skill rather than this
one. Everything else you need about this stage is already on your briefing, so
read it there.

`ubc agent next` has one more use here, for a MEMBER's stage rather than your
own: run it with `--stage` set to that stage to get its `gate.link` and
`gate.up_type`, which is the up-link field the member's own directive must
carry. Follow this skill wherever the rest of that payload disagrees with it.

## The project decides the shape, not this skill

The keys below carry what varies from one project to the next. None of them
is written into this skill, and none of them is yours to guess.

**`default_status` is the status every need you author opens in.** Write
`:status: <that value>`. When the key is ABSENT the project declares no
lifecycle states, and the value is `draft`, which is what a forward authoring
run is given on such a project. A synthesized need opens exactly where a
hand-authored one opens, because both go through review before anything trusts
them. What marks it as recovered is the ledger entry `record` writes
afterwards, never a word in the status field, so do not invent a status of your
own to mark it and do not carry one over from an example. This is about the
needs YOU author. A member's own `:status:` is left exactly as `audit` reports
it, the same as every other field of its directive except its up-link.

**`authoring` is the project's own directive for this stage.** It decides how
many needs you author, what they must cover and what shape they take. Follow
it. This skill decides how you work. The directive is written for forward
authoring, so it can name an input this run does not have, such as a use case
or a user story. Where it does, your target's cluster of recovered needs is
that input. The key is absent when the stage declares no directive, and this
skill's own rules are then the whole answer.

**`author_skill` names this project's forward-authoring skill for this stage,
and `author_skill_path` is where it is installed.** Read it for the output
shape only: it shows what a need of this stage looks like in this project, so
yours can look the same. Do not run it and do not follow it as instructions. It
is written for authoring from stated intent, it forbids the member reads this
stage depends on, and it waits for an approval nobody may be there to give.
When the brief names an `author_skill` and no `author_skill_path`, it is not
installed, so there is no file to read. Do not search for it.

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

`id_prefix` is only the fixed lead of a valid id, not the full
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

**Resolve a reference only when its kind is selected for this run.** Your
prompt names the selected evidence kinds, and a run with none selected resolves
nothing. `commit_history` means the commit messages behind your targets. The
pull requests and issues they name are `change_requests` and `issues`, which
are separate kinds. So a pull request or merge request is resolved only when
`change_requests` is selected, an issue only when `issues` is selected, and a
reference whose kind the text does not say only when one of the two is. Every
other reference is context only: keep it as an identifier and do not look it
up.

Run `ubc agent reverse sources <scope> -p <project path>` (the `scope` is your
briefing's own) to see which intent kinds are available: `commit_history`,
`change_requests`, `issues`. Each available row names its `provider`, and for
the two forge kinds that provider is an installed SKILL rather than the
engine. Resolve a selected kind with the skill its row names, and hand that
skill only the references you may resolve. Use the forge CLI only for a
selected kind no installed skill claims. A Jira key (its `origin` is
`jira-key`) is resolved only with a skill that covers Jira, never with a forge
skill or a forge CLI. A row that reports unavailable has a `detail` saying why,
and that detail is usually the fix.

That is the whole of the intent gathering this skill does. Do not walk the git
history: the cluster you were handed is a set of lower-need ids, not files, so
there is no path to run a log against. Where none of it produces text, use only
what your driving tool already placed in your prompt.

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

Where your briefing's `authoring` directive says how many needs to author, what
they must cover or what shape they take, the directive decides it. It is the
project speaking about its own graph, and this test is the default for a project
that says nothing. The test still decides WHERE a split falls, because a
directive states a policy and never which two behaviours belong together.

## Output shape

Each synthesized need, at the path you substituted into `route_path`. Author
them into the same document, one after another, when a cluster produced more
than one:

```rst
.. <type>:: <short_title>
   :id: <ID with the reported prefix>
   :status: <the briefing's `default_status`, or `draft` when it carries none>
   :<the briefing's `provenance_field`>: <the values already recorded on the members, comma-separated>

   <Synthesized capability statement, grounded in the cluster and, where
   available, the qualifying intent signal.>
```

**`provenance_field` names the field that records where a need came from.**
When the key is present, write that field with the values already recorded on
the needs `members` lists, comma-separated, deduplicated, in the order the
members are listed. Read each value off the member's own directive at the
`source.path` `audit` reported, the same file the up-link edit step opens.
This stage reads no source file itself, so it never builds a path the way the
extraction and structure rungs do. When no member carries the field, write
nothing.

When the key is ABSENT the project's ontology declares no such field. Write
none, and do not invent one: an undeclared option is a diagnostic on the
project's own build.

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
