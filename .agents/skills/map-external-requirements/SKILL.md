---
name: map-external-requirements
description: Map imported external system requirements onto the project's user stories, adding a covers link to the story that already answers each one and authoring a new story only where none does.
---

# Map external requirements onto user stories

The artefact of this stage is usually **a link, not a need**. The imported
`sys_req` layer is the customer's specification; your job is to say which of this
project's user stories answers each requirement, and to author a new story only
where nothing does.

Pass `-p <project path>` on every `ubc agent` command. `<project path>` is the
directory that holds the target `ubproject.toml` (the project the need you are
authoring belongs to). A repository can contain several `ubproject.toml`
files, so without `-p` the command runs against the current directory and can
target the wrong project. Resolve `<project path>` once from the briefing you
were handed and reuse it on every call.

When these instructions say `ubc`, run the exact version-matched `ubc` the
harness named in the task, not a bare `ubc` from your PATH, and never one
you install yourself. With no path given, use the `ubc` on your PATH.

## NEVER edit the imported requirements

The `sys_req` needs are **generated** into `specs/_external/` from the customer's
DOORS export by `tools/import_sysreqs.py`. They are not yours to change:

- An edit there is silently overwritten by the next import, and the customer
  never sees it.
- The `covers` link is authored on the **user story** side, pointing up. Never
  add a link field to a `sys_req`.
- A requirement that is wrong, ambiguous or unimplementable is **not** fixed by
  editing it. Say so (see *When nothing fits* below); changing it is a
  conversation with the customer, not a commit.

## Use the briefing and the tools — do NOT spelunk the filesystem

The briefing in your prompt ALREADY contains the anchor need, the upstream needs
you must cover, and the resolved route. Do NOT re-discover the project: no `find`,
`grep`, `cat`, or reading `.rst` files to rebuild context. When you genuinely need
one specific need's full detail, run `ubc agent audit --id <ID> -p <project path>`;
for a need's context briefing run `ubc agent context --id <ID> --no-code -p <project path>`.

Two commands matter most here:

- `ubc agent gaps -p <project path>` — every `sys_req` with a `trace_backward`
  gap on `covers` is an unclaimed requirement. That list IS the backlog.
- `ubc agent audit --id <SYS_ID> -p <project path>` — the requirement's full text,
  ASIL and verification method, which is what you judge a story against.

## Mind the route when the anchor is a `sys_req`

The stage route is per-stream, so it is resolved from the **anchor's** location.
Anchored on a `sys_req` the engine reports `specs/_external/user_stories.rst` —
which is the generated directory and is **never** a place to author. Treat that
as "route not resolved":

- **Adding a `covers` link** to an existing story: edit that story where it already
  lives, `specs/<its stream>/user_stories.rst`, regardless of the reported route.
- **Authoring a new story**: put it in the stream it belongs to. Re-anchor with
  `ubc agent next --id <US_ID> -p <project path>` to get the real route, or create
  `specs/<new-stream>/user_stories.rst` for a genuinely new capability.

## Prefer a link over a new story

Most requirements are already answered. Author a new `user_story` only when no
existing story covers the capability at all. One story per coherent capability,
**never** one per requirement — a story that maps one-to-one onto a single
customer requirement is almost always a requirement wearing a story's clothes.

A new story is justified when the requirements it would cover describe a
capability with its own user, its own observable outcome, and its own stream. If
they are variations of something an existing story already promises, extend that
story's `covers` list instead.

## Propose before you author

Do NOT edit anything yet. First present a short, scannable table of the mapping
you propose and ask the user to approve or adjust it:

| Requirement | Proposed home | Why |
|---|---|---|
| `SYS_1041` | `US_CELL_BALANCING` (existing) | already promises charge equalisation |
| `SYS_1061` | new story, `ota-update` stream | no existing story covers field updates |

Call out explicitly:

- every requirement you propose to leave **unmapped**, and why,
- every **new** story, with the stream it would live in,
- any requirement you are **unsure** about, rather than quietly assigning it.

Keep it scannable, not the full RST. Wait for the user to approve or adjust, and
do not author until they confirm. On approval, make exactly the changes you
agreed, then leave the independent review to the separate review step.

## Output shape

Adding a link to an existing story — the `covers` field is a comma-separated list,
kept in ascending id order:

```rst
.. user_story:: <unchanged title>
   :id: <unchanged id>
   :status: <unchanged status>
   :covers: SYS_1041, SYS_1042
```

Authoring a new story: the shape of the `user_stories` stage for this project,
carrying `covers` up to every requirement it claims.

## When nothing fits

A requirement this project genuinely does not build is a legitimate outcome, not
a failure to map. Leave it unmapped and say so in your proposal — an honest
backlog is the point of the import. Do NOT:

- invent a user story to make a gap go green,
- attach a requirement to a loosely-related story to clear the gate,
- edit the `sys_req`.

The uncovered requirement stays a `trace_backward` gap and is carried as accepted
debt in the `release-check` baseline until the project takes it on.

## Rules

- **If you cannot decide or lack the context to map this faithfully, do NOT guess
  or fabricate.** Say which requirement you cannot place and exactly what you need
  to know. For a new story you must author but cannot ground, write
  `[NEEDS CLARIFICATION: <exactly what you need to know>]` in the body and stop —
  the gate fails closed on any need whose body still carries the marker.
- Never edit anything under `specs/_external/`.
- Never add a link field to a `sys_req`.
- A story may cover many requirements; a requirement may be covered by more than
  one story, but prefer a single clear home.
- Preserve the existing title, id, status and body of any story you only relink.
