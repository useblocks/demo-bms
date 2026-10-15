---
name: recover-architecture-from-code
description: Recover the architecture elements a codebase already has, in the count and shape the project's own authoring directive calls for, together satisfying every requirement recovered from that module, naming what each module is responsible for and how it relates to its neighbours without claiming a boundary the code does not show.
---

# Recover architecture from code

This is the structure stage of reverse recovery: one stage BELOW the
requirement stage, grounded directly in code. Unlike the stages above it,
almost nothing here has to be inferred. A requirement had to be read out of
behaviour. A module boundary is written down, and the recovery ledger already
records one entry per module, carrying that module's path and the requirement
ids recovered from it. So the decomposition and the trace edges arrive
with your briefing. What is left for you is naming what each module is
RESPONSIBLE for, and saying how the elements relate.

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

You were handed ONE target from `ubc agent reverse plan <scope> --stage
<STAGE_ID>`: its `source_path`, its `members` and its
`recovered_into`, plus the brief's own `route_path`, `known_streams`,
`produces`, `id_prefix`, `default_status`, `provenance_field`, `authoring`,
`diagram_format`, `author_skill` and `author_skill_path`. If you were not
handed it, run that command and read the entry whose `source_path` names the
module you were asked for.

**`source_path` is `structure:<module path>`, and the path behind the prefix is
real.** Strip the prefix and read that module: its files, its public interface,
what it imports and what imports it. That reading is the whole evidence base
for the element you are about to author. The prefix is there so this stage's
record cannot collide with the requirements already recorded at the same module
path.

**`members` are requirement IDS, not files.** They are the requirements
recovered from this module, and they are the half nothing outside the ledger
knows. The file list you can get yourself, by listing the module directory.

**You choose the target document. The engine does not.** `route_path` is the
stage's configured route with its `{stream}` placeholder left in, for example
`specs/{stream}/architecture.rst`. A stream is the folder under the route that
holds one functional area's needs. Choose one per target, from the functional
area its module belongs to, which is a judgment about what the module is FOR.
Targets about different areas go to different streams, and several streams in
one run is normal. Never put the whole scope under one stream unless every
target belongs to the same area. `known_streams` lists the streams this project
already uses, and your `source_path` usually names one outright: a module at
`src/auth` belongs to `auth`. Put a target's stream in place of `{stream}`,
author there, and hand that concrete path back as its `target_rst`. `ubc agent
reverse record` refuses one that still carries `{stream}`.

**Unless the target carries a `recovered_into`, in which case that is the
document.** A module key is stable, so a non-null `recovered_into` means this
module has been recovered at this stage before and that path is where its
elements were authored. Author this pass there too and hand the same path back.
Test for `null`, never for an absent key: the engine always serializes it.

## The project decides the shape, not this skill

The keys below carry what varies from one project to the next. None of them
is written into this skill, and none of them is yours to guess.

**`default_status` is the status every element you author opens in.** Write
`:status: <that value>`. When the key is ABSENT the project declares no
lifecycle states, and the value is `draft`, which is what a forward authoring
run is given on such a project. A recovered element opens exactly where a
hand-authored one opens, because both go through review before anything trusts
them. What marks it as recovered is the ledger entry `record` writes
afterwards, never a word in the status field, so do not invent a status of your
own to mark it and do not carry one over from an example.

**`provenance_field` names the field that records where an element came
from.** When the key is present, write that field with the files of the module
you read, comma-separated. Build each one by joining your target's
`source_repo_path` with the file name, and nothing else. Do not shorten a path
and do not turn it into a URL. When `source_repo_path` is absent, write no
provenance field: the module resolved to nothing the repository can name, and a
path you assembled yourself would be a guess.

**Do NOT build those paths out of `source_path`.** Your `source_path` is
`structure:` followed by a module path measured from the PROJECT directory,
while this field holds paths measured from the REPOSITORY root. The two are the
same string only when the project sits at the repository root. On a project at
`<repo>/sub/` the marker says `structure:src/auth` and the very same module is
`sub/src/auth` to git, to the requirement rung's own provenance, and to this
field. `source_repo_path` is that second spelling, put on your target so you
never have to derive it.

**Your target's `members` are NOT paths at this stage either.** They are the
need ids this element must account for, which is why they look like ids rather
than files. Writing them into the provenance field puts need ids in a field
declared to hold source paths.

When the key is ABSENT the project's ontology declares no such field. Write
none: an undeclared option is a diagnostic on the project's own build.

**`authoring` is the project's own directive for this stage.** It decides how
many elements you author, what they must cover and what shape they take. Follow
it. This skill decides how you work. The directive is written for forward
authoring, so it can name an input this run does not have, such as a use case
or a user story. Where it does, your target's module and the requirements
listed under it are that input. **It is also where a project asks for a
diagram**, and it is the only
place that ask is written down: neither this skill nor the forward one carries a
diagram in its output shape, so a directive asking for one is an instruction to
author one, not a suggestion. The key is absent when the stage declares no
directive, and this skill's own rules are then the whole answer.

**`diagram_format` is the syntax any diagram is authored in** (for example
`mermaid`), which the directive asking for the diagram does not state. Use the
RST directive it names (`.. <that value>::`). When the key is absent the project
configures no syntax, and a diagram is then better left out than authored in one
the project's docs build has no extension for. Whether the directive asks for a
diagram is a separate switch from whether the project's diagram GATE is on: if
the directive asks for one, author it even when the gate is off.

**`author_skill` names this project's forward-authoring skill for this stage,
and `author_skill_path` is where it is installed.** Read it for the output
shape only: it shows what an element of this stage looks like in this project,
so yours can look the same. Do not run it and do not follow it as instructions.
It is written for authoring from stated intent, it forbids reading source files
at all, and it waits for an approval nobody may be there to give. When the brief
names an `author_skill` and no `author_skill_path`, it is not installed, so
there is no file to read. Do not search for it.

## Check the project's id convention before you mint

**The brief's `produces` and `id_prefix` name the need type you author and the
prefix its ids start with.** Read them there. `id_prefix` is absent when that
type declares no prefix. Do not guess either value.

Only when you were handed no brief, or a brief that carries no `produces`, run
`ubc agent next --stage <STAGE_ID> -p <project path>` and read `produces` and
`route.id_prefix` from that payload.

Existing needs of that type show the rest of an id's shape. Mint ids in that
convention. Never invent a second convention beside one that already exists.

## The link runs FROM your element, and you edit no requirement

This is the opposite direction from the synthesis stage above, so read it
carefully. Your element carries the link. The requirements do not change at
all, and you must not open their files.

The link field is the one your briefing names for this stage, which `ubc agent
next --stage <STAGE_ID>` reports as `gate.link` with `gate.up_type`. Read it
there rather than assuming a name: a project is free to spell it otherwise.

**Every id in `members` must appear on at least one element you author.** A
requirement cited by no element fails the stage's own gate.

**An id MAY appear on several**, and sometimes has to. A requirement whose
behaviour genuinely spans two components is satisfied by both of them, and a
round-trip requirement is the standard case: "reconstruct the same tree from
what serializing it produced" is satisfied by the serializer and the
deserializer together, and citing only one of them would be false. Cite every
element the behaviour actually needs.

What is wrong is citing several because you could not decide which one owns it.
The test is whether you can say what each cited element contributes to that
requirement. If you cannot, the split is in the wrong place, not the citation.

## How many elements a module supports

**The project's own authoring directive decides this, whenever it states an
answer.** Follow it exactly. Where it asks for one element per distinct
responsibility, or for any other count or shape, that is the project speaking
about its own architecture, and it wins over everything else in this section.

**Only when the directive states no answer** does this skill's own default
apply, and it is recovery's own default, not a rule the project has stated:
usually ONE element per module. Author more than one only when the module
plainly holds several distinct responsibilities, and when it does, say so in
your report: a module that needs splitting at this stage is usually a module
worth splitting in the code, and that is worth a human seeing. Never split to
make the numbers look better, and never split a responsibility you cannot name.

Whichever count you land on, between them the elements you author for a module
must satisfy every id in `members`. That is the coverage rule, it holds
regardless of count, and it is what a directive asking for "enough that every
requirement is satisfied" is asking for.

## Grounded structure

1. Read the module. What does it take in, what does it hand back, what does it
   own that nothing else does?
2. Check that against the requirements in `members`. They were recovered from
   this same code, so an element that satisfies them and a description of what
   the module does should be the same sentence twice. Where they disagree, the
   code wins and the disagreement goes in your report.
3. Relate it to its neighbours ONLY through what the code shows: an import, a
   call, a shared type, a declared dependency. A layer you can see in a
   directory tree is a layer. A layer you can see only in your own head is not.
4. **Never fabricate.** No boundary, no dependency, no design intent and no
   pattern name that the module's own code does not support. When the intent
   behind a module genuinely is not recoverable, mark it with an explicit
   `[NEEDS CLARIFICATION: ...]` rather than inventing a rationale. That marker
   is a first-class gap the workflow tracks, so flagging costs nothing and
   guessing costs the reader's trust in every other element you wrote.

## Output shape

```rst
.. <type>:: <short_title>
   :id: <ID with the reported prefix>
   :status: <the briefing's `default_status`, or `draft` when it carries none>
   :<the briefing's `provenance_field`>: <the module's files, comma-separated>
   :<link_field>: <every member id this element satisfies>

   <What this module is responsible for, and how it relates to the modules
   around it, in terms the code supports. Plus whatever the project's
   `authoring` directive asks for, a diagram included.>
```

Drop the provenance line entirely when the briefing carries no
`provenance_field`.

It carries NO down-link to the code. The implementation arm links up to the
element, not the other way round, and the next section is how that link comes
to exist.

## Bind the code to your element

Your target may carry a `code_marker`. When it does, the project's lower arm is
marker-authored: a one-line codelinks marker in a source file MATERIALISES a
real need of `code_marker.produced_type`, carrying a link named
`code_marker.link_field` up to the element it realises. That link is what the
element's own lower gate counts. Without it a recovered element sits on top of
code the graph does not know about, and the gate below it stays open forever.

So after you author the element, and before you record, write ONE marker line
into each file listed in `code_marker.files`, in the shape `code_marker.example`
shows, with your element's id in the brackets. Those are the module's files the
codelinks project can actually parse, already filtered by language: write into
them and into nothing else, because a marker in a file outside that list is a
comment nothing reads. `code_marker.comment_prefix` is the comment lead for this
module's language, and the example already carries it. Put the marker at the top
of the file, but after any line the language requires to come first (a shebang
`#!`, a Python encoding declaration, and similar). Mint each marker's id with
`code_marker.id_prefix` and the project's id convention, one id per file, and do
not reuse an id across files.

Write into no file listed under `code_marker.already_marked`: that file carries
a marker for this rung already, and a second one mints a second need claiming
the same code, with nothing in the ledger able to tell them apart.

Then make sure a built `.rst` file names the codelinks project, or the markers
parse and materialise nothing:

```rst
.. src-trace::
   :project: <code_marker.src_trace_project>
```

When `code_marker.src_trace_documents` lists any document, the directive is
already there and you author none. When it is empty, author exactly one
directive for the whole run, in the first document you write, and never a
second one in another document of the same run: a second directive
materialises every marker of the project again, and every marker need is then
reported as a duplicate.

**When `code_marker` carries `unwritable`, write no marker and say so.** The
codelinks project parses one language and this module is not in it, or it
declares no `comment_type` so no comment lead resolves at all, or every file of
the module carries a marker already. The reason names which one it is and names
the fix. Report the module with that reason in your run report rather than
binding it with something dead.

**When the target carries no `code_marker` at all**, the project's lower arm is
not marker-authored, or the project turned markers off with
`[agent.reverse] write_code_markers`. Write nothing into source. That is not a
failure of this run, it is a property of the project, and the element you
authored is still correct without it.

This is the one place recovery writes into a source file, and it is bound by
the same rule as everything else here: propose it first. The outline you
present before authoring lists the files you will mark and the id each will
carry, and you write none of them until the user confirms. With no interactive
user, write them, and say in your report which files now carry a marker.

There is deliberately no diagram in the block above, and there is none in the
forward skill either. What a diagram must show is a per-project decision, so it
lives in the `authoring` directive rather than in a template here, and a
template would go stale against every project that asks for something else.

## Propose before you author

With an interactive user, report the elements you intend to author, the members
each would satisfy, and the target document, then wait. With none, decide, say
in your report that you decided and on what grounds, and carry the work
through.

## Record what you authored

After the document is written, record the run through
`record-recovery-ledger`. Pass your target's `source_path` through UNCHANGED,
prefix and all, and leave `members` behind: a structure target's members are
need ids, and `record` refuses a members list on a marker.

## Rules

1. The project's authoring directive decides how many elements a module
   gets. Absent one, this skill's own default is ONE per module unless the
   module plainly holds several responsibilities, and say so when it does.
2. Every member id appears on at least one element, and on several only when
   you can say what each of them contributes.
3. You edit no requirement, and you open no requirement's file.
4. Nothing about a module's boundaries, dependencies or intent that its own
   code does not support.
5. `[NEEDS CLARIFICATION: ...]` rather than a plausible rationale.
6. A field the project's own schema requires, that this evidence cannot
   ground, is not yours to invent. Leave it out of what you author, and say
   plainly in your report which field you left out and why the evidence
   could not ground it.
7. The recorded `source_path` is the briefing's, unchanged.
