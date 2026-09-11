---
name: recover-requirement-from-code
description: "Recover requirements from the observable behavior of the source files one recovery target names when a project has code but no spec graph yet, grounded strictly in what those files do, each emitted for a human to confirm or correct."
---

# Recover a requirement from code

This is the bottom stage of reverse recovery: a project has real code but no
requirement above it yet. You read the source files ONE recovery target names
and emit one or more requirements (of the type named in your briefing)
describing the behavior those files observably provide. This is extraction, not
drafting: every requirement must be grounded in what the files actually do,
never in what they plausibly should do.

Pass `-p <project path>` on every `ubc agent` command. `<project path>` is the
directory that holds the target `ubproject.toml` (the project the recovered
need belongs to). A repository can contain several `ubproject.toml` files, so
without `-p` the command runs against the current directory and can target
the wrong project. Resolve `<project path>` once from the briefing you were
handed and reuse it on every call.

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

Your briefing carries one target from `ubc agent reverse plan`'s output (a
`source_path`, its `last_commit`, its `members`, its `kinds`, its
`member_kinds` and its `recovered_into`), plus the brief's own `route_path`,
`known_streams`, `default_status`, `provenance_field`, `authoring` and
`author_skill`.

**The target you were handed IS the work order. Use it, and do not re-run
`ubc agent reverse plan` to rebuild it.** A second run sees a different ledger
and a different working tree, so it can group the same files differently. The
engine keys the ledger on what it offered you, so recording against a work
order you re-derived splits one recovery across two ledger keys: `ubc agent
reverse status` then reports the same files twice, and the next `plan` run
offers files that are already recovered.

**`source_path` names either one FILE or a DIRECTORY.** A directory is a
multi-file recovery unit: several files that belong together, recovered in one
act. When it is a directory, `members` lists exactly which files the act covers,
and those are the files to read. Read every one of them, and read only those:
`members` is not a listing of the directory, and the engine deliberately left
out the files an earlier pass already recovered. When `source_path` names a
file, `members` comes back EMPTY (`[]`, not missing: the engine always
serializes the key) and that one file is the whole target. Test for an empty
list, never for an absent key.

**`kinds` and `member_kinds` say HOW to read, and they answer at different
levels.** A kind is a lens: `code` states what the system DOES, `tests` states
what behavior is EXPECTED of it, `docs` states what was PROMISED, `adrs` states
WHY a choice was made. `kinds` is every lens present anywhere in the target, so
on a multi-file unit it tells you the unit holds tests without telling you
which file is one. `member_kinds` gives each member its own, and that is the one
to read that file by. Read each member under its own lens, not under the
target's union: a unit holding eleven source files and one test is eleven files
stating what the system does and one stating what is expected of it, and
treating all twelve as either would misread eleven of them.

A lens is a hint, never a filter. Every member is read, whatever its kind, and
a member with no kind at all (the classifier declined to label it) is still
read.

Emit ONE set of requirements for the whole target, covering every member, and
record it once. Do not split a unit back into one recovery per file: that is the
grouping the engine already made, and undoing it writes several shards where
the engine expects one.

**You choose the target document. The engine does not.** `route_path` is the
stage's configured route with its `{stream}` placeholder left in, for example
`specs/{stream}/requirements.rst`. A stream is a coordinate in the needs graph,
not a folder, and this recovery is what CREATES it, so there is nothing for the
engine to look up: deciding which stream a piece of code belongs to is a
judgment about what that code is FOR, and it is yours. `known_streams` lists
the slugs this project already uses. Reuse one when the code belongs to it,
rather than authoring a synonym beside it. A new stream is the right answer
when none of them covers this code, and an empty `known_streams` means you are
naming the first one.

Put your slug in place of `{stream}` and author at the path that gives. That
concrete path is the `target_rst` you hand back for recording, and
`ubc agent reverse record` refuses one that still carries `{stream}`.

**Unless the target carries a `recovered_into`, in which case that is the
document.** A non-null `recovered_into` means this exact target has been
recovered before, and it is the path the earlier pass authored its needs into,
read from the ledger rather than guessed. Author this pass there too, whatever
stream you would otherwise have chosen, and hand that same path back as
`target_rst`. Choosing differently does not give you a second document: the
ledger records ONE destination per source and takes the newer one, so the needs
the earlier pass authored would be recorded as living in your new document
while their text stays where it is. `ubc agent reverse record` warns when a
re-record does that and names the needs it just re-homed. `recovered_into` is
`null` for a source recovered for the first time, which is the ordinary case
and leaves the choice entirely yours. It is `null` in one other case, and the
action is the same: the earlier pass recorded a destination that cannot be
authored into (it escapes the project, or it still carries `{stream}`), so the
engine drops it rather than send you at it, and the brief says so under
`unusable_targets`. Test for `null`, never for an absent key: the engine always
serializes it.

**`source_path` and `target_rst` are measured from different places, so do not
resolve them the same way.** `source_path` is relative to the REPOSITORY root
(the directory holding `.git`), because it doubles as a git pathspec.
`target_rst` is relative to the PROJECT directory (the one holding
`ubproject.toml`), because that is where the stage's configured route writes.
The two are the same directory only when the project sits at the repository
root, so a project at `<repo>/sub/` gives you `sub/src/auth/token.rs` alongside
`specs/auth/requirements.rst`. Pass `source_path` back exactly as you received
it, never trimmed to look like `target_rst`.

If, and only if, you were handed NO target at all, run
`ubc agent reverse plan <scope> --stage <STAGE_ID> -p <project path>` yourself
and take one entry of `targets` whole, plus the brief's `route_path`,
`known_streams`, `default_status`, `provenance_field`, `authoring` and
`author_skill`. Take that
entry as it comes, `members` and `recovered_into`
included. This is the
fallback for a missing briefing, never a second opinion on one you already
have.
For the type this stage produces and its id prefix, run
`ubc agent next --stage <STAGE_ID> -p <project path>` and read `produces` and
`route.id_prefix`. Do not guess either.

**Read `produces` and `route.id_prefix` from that payload and nothing else.**
`ubc agent next` answers for FORWARD authoring, so the same payload also
carries a `skill` naming the stage's forward authoring skill rather than this
one, and a `gate` demanding the very upward trace link this stage must not
author. Two keys of that payload are the stage's ontology, which is what you
came for. Everything else you need about this stage is already on your
briefing, so read it there.

Do NOT re-discover the project with `find`, `grep`, or `cat` beyond reading the
source files your target names and the config reads this skill names below.

## The project decides the shape, not this skill

Four keys of your briefing carry what varies from one project to the next.
None of them is written into this skill, and none of them is yours to guess.

**`default_status` is the status every need you author opens in.** Write
`:status: <that value>`. When the key is ABSENT the project declares no
lifecycle states, and the value is `draft`, which is what a forward authoring
run is given on such a project. A recovered need opens exactly where a
hand-authored one opens, because both go through review before anything trusts
them. What marks a need as machine-recovered is the ledger entry `record`
writes afterwards, never a word in the status field, so do not invent a status
of your own to mark it and do not carry one over from an example.

**`provenance_field` names the field that records where a need came from.**
When the key is present, write that field on every need you author, with the
repository-relative path of each source file you actually read, comma-separated,
exactly as `source_path` and `members` gave them to you. One file for a
single-file target, every member for a unit. Do not shorten a path, do not turn
it into a URL, and do not add a file you did not read.

When the key is ABSENT the project's ontology declares no such field. Write
none, and do not invent one: an undeclared option is a diagnostic on the
project's own build. The engine reads the declaration off the project config,
so the answer is already made by the time you see it.

**`authoring` is the project's own directive for this stage**, and it is where
"how many" and "what shape" are answered. Follow it. It is written for forward
authoring, so it can name an input you do not have, such as a use case or a
stated intent. The shape and the coverage it asks for still hold, and the code
is your input in place of that stated intent. The key is absent when the
stage declares no directive, and this skill's own rules are then the whole
answer.

**`author_skill` names the skill a forward run at this stage would use.** It is
a POINTER, not something to run. Do not load it and do not follow it: it is
written for authoring from stated intent, it forbids reading source files, it
orders the upward trace link this stage must not author, and it waits for an
approval nobody may be there to give. It is on your briefing so that a person
comparing what you recovered against what this project authors by hand knows
which document to open.

## Check the project's id convention before you mint

`route.id_prefix` is only the fixed lead of a valid id, not the full
pattern a minted id must satisfy. The project's own `id_regex` governs
what may follow that lead, and none of the `reverse plan`, `next`, or
`audit` verbs reject an id that violates it: audit even echoes an invalid
id back to you as though it were fine. Before you mint any id, read the
project's `id_regex` (`ubc config <project path>`, under `needs.id_regex`,
or the `[needs]` table in `ubproject.toml` directly, both of which this
skill sanctions despite the no-re-discovery rule above) and check every id
you are about to mint against it. Build each id as the reported prefix
followed by a descriptive word, never followed by a number: a digit right
after the prefix is exactly what an `id_regex` requiring a letter there
(for example `^[A-Z]+_[A-Z][A-Z0-9_]*$`) rejects. If a recovered need
still seems to have been silently dropped after you author it, run
`ubc build index <project path> --show-warnings` to see the id and other
validation diagnostics that none of the `ubc agent` commands above
surface.

## Shall-clause rules

1. **Subject is the component, or an external actor it responds to.** Never
   a function, class, private method, or file name. "The CSV Importer shall
   reject a malformed row" is a requirement. "`_parse_row` shall raise
   `ValueError`" is code narration, not a requirement.
2. **No internal implementation details in the body, and no line numbers,
   ever.** No private function names, no leading-underscore methods, no file
   paths, no "around line N". A clean behavioral shall with zero backticks
   beats a code-narration shall with ten.
3. **One shall clause per requirement, no compound obligations.** Zero
   intra-clause conjunctions joining modal-verb phrases ("shall X and shall
   Y", "shall X, or Y"). Split a compound behavior into separate
   requirements instead of bundling it.
4. **Enumerate every distinct observable behavior, file by file**, not one
   bundled requirement for the whole target: every error condition that
   escapes a file's public surface, every published config key or flag it
   reads, every public function or entry point it exposes. Work through the
   members one at a time and apply this to each. A typical 200-500 line file
   yields somewhere between 1 and 5 requirements. Fewer than 1 for a file only
   if that file has no observable behavior at all. Where your briefing's
   `authoring` directive says something different about how many or about what
   must be covered, the directive wins: this rule is the default for a project
   that says nothing.
5. **Backticks are for code and protocol tokens only**, never for format
   acronyms, ordinary nouns, or emphasis. A tester would copy-paste a
   backticked string into test code or configuration.

## Output shape (one directive per requirement)

```rst
.. <type>:: <one-sentence shall-clause title>
   :id: <ID with the reported prefix>
   :status: <the briefing's `default_status`, or `draft` when it carries none>
   :<the briefing's `provenance_field`>: <the source paths you read, comma-separated>

   <Requirement body>. Exactly one shall-clause, grounded in observable
   behavior, with no compound "and/or".
```

Drop the provenance line entirely when the briefing carries no
`provenance_field`.

Do not emit any upward trace link here. Extraction is the bottom stage:
a recovered requirement has no parent yet, and gets one only later, when
`recover-need-from-cluster` climbs a stage and authors the up-link onto
it.

Do not add an ad-hoc field for the source file. The briefing's
`provenance_field` is the one channel for that, and its presence or absence is
the project's answer, already read off the project's own ontology. Inventing a
second field beside it puts an undeclared option on the need, and a name of your
own choosing on a fact the project already knows how to spell.

The rest of the provenance is not a field at all: which agent and model ran,
when, and what the source's content was at the time are recorded in the
project's ledger afterwards by `record-recovery-ledger`.

## Propose before you author

**With an interactive user**, do NOT write any RST yet. Present a short,
scannable outline first: the id (with the reported prefix) and one-line
shall-clause title of each requirement you will emit, and the observable
behavior each one traces to. Wait for them to approve or adjust, and do not
author until they confirm.

**With no interactive user**, make the same outline and approve it yourself.
Check it against the members' own behavior, then author. Do not stop here and
do not ask.

On approval (yours or the user's), author exactly what you agreed at the path
you substituted into `route_path`.

### The subject check, on every body, before you author

Rules 1 and 2 above are the standard. This is how you verify you met it, and it
is not optional: **read the grammatical subject of every body you drafted.**

If that subject is a function, method, class or file, the requirement is code
narration and has to be rewritten before it is authored. The test is mechanical.
A body that opens "The `some_name` method ...", "The `some_name` function ...",
or "`some_name` shall ..." fails it. So does one whose subject is a file name.

Rewrite by asking what the CALLER gets, not what the code is called:

```text
FAILS:  The `node_insert_as_child` method adds a new node as a child of an
        existing parent node, returning the new child's index.
PASSES: The tree shall insert a new node holding the given data as the last
        child of an existing parent node and return the new node's index.
```

Both sentences describe the same behaviour. The second one survives the method
being renamed, split or inlined, which is the whole reason a requirement is
written down separately from the code. The first is a second copy of the code,
and it goes stale the first time anyone touches it.

Count the bodies that fail the check and state the number in your report, `0`
included. Counting is what makes the check happen.

## Rules

- **If a file's behavior is too ambiguous to state faithfully as a
  requirement, do NOT guess or fabricate.** Write
  `[NEEDS CLARIFICATION: <exactly what you need to know>]` in the body and
  move on to the next behavior.
- Write `shall`, not `should` or `must`, for the normative clause.
- Keep the body free of design detail. That belongs to a later stage.
- **A field the project's own schema requires, that this evidence cannot
  ground, is not yours to invent.** Leave it out of what you author, and say
  plainly in your report which field you left out and why the evidence could
  not ground it.
- This skill never invokes `ubc agent reverse record`. Hand your emitted
  requirements to `record-recovery-ledger` once you are done.
