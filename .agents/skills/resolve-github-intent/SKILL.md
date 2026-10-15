---
name: resolve-github-intent
description: "Resolve the GitHub issue and change-request references a recovery brief hands you, using the `gh` CLI, and report plainly when `gh` is missing, unauthenticated or unable to reach the host instead of guessing at what the references said."
provides:
  - { kind: issues, system: github }
  - { kind: change_requests, system: github }
---

# Resolve GitHub intent

This is the GitHub half of reverse recovery's evidence seam. The engine
extracts issue and change-request references out of commit messages and hands
them to a recovery run. It never fetches them: every forge authenticates
differently, and `gh` already owns GitHub's tokens, their rotation and their
expiry messages. Turning a reference into text is this skill's job.

Declaring `provides` in the frontmatter above is what makes `ubc agent reverse
sources` report `issues` and `change_requests` as available on a GitHub remote.
Installing this skill is the whole of that. Nothing else has to be configured.

This skill runs `gh` and never `ubc`, so it needs no binary path from the
harness. The recovery run that invoked it does, and carries its own rule.

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

Concretely here: a missing or unauthenticated `gh` is a line in your report and
then a recovery that continues without forge evidence. It is never a reason to
stop and ask whether to install or log in, and it is never a reason to install
anything yourself.

## Before anything else, check `gh`

Run `gh auth status`. Three outcomes, and each has its own answer:

- **`gh` is not on PATH.** Say so in your report, in one line, naming the
  install page (`https://cli.github.com`). Then continue the recovery WITHOUT
  forge evidence, using the commit messages and the code you already have.
- **`gh` is installed but not authenticated.** Say so, name `gh auth login`,
  and continue without forge evidence exactly as above.
- **`gh` answers with a logged-in account.** Resolve the references below.

Never guess what a reference said, and never treat a reference id as if it
were the text behind it. A recovery grounded in an invented issue body is
worse than one grounded in the code alone, because it reads as if it had a
source.

## Resolve the references you were handed

Your prompt carries the references the engine already extracted. Resolve only
the ones it says you may resolve, because their kind is selected for this run,
and do not go looking for more: re-deriving them from `git log` yourself drops
the cross-repository ones and the Jira allowlist you cannot see. A reference
your prompt lists as context only stays an identifier. Do not look it up.

Each reference carries an `id`, an `origin` naming the rule that matched it,
and, when the text named one, an `owner` and a `repo`. A reference WITHOUT an
owner belongs to this repository. A reference WITH one belongs to a different
repository and must be resolved against it, or you fetch a real but unrelated
issue that happens to share the number. A reference whose origin is
`jira-key` is not a GitHub issue and is never passed to `gh`. A Jira key is
resolved only with a skill that covers Jira, and this skill does not, so report
it as unresolved.

```
gh issue view <id> --json number,title,state,body,labels
gh pr    view <id> --json number,title,state,body,labels
gh issue view <id> --repo <owner>/<repo> --json number,title,state,body
```

**A bare `#N` does not say whether it is an issue or a change request.** GitHub
shares one number space between them, which is why the engine leaves `kind`
absent rather than guessing. When `kind` is absent, try `gh issue view` first
and fall back to `gh pr view` on a not-found, and use what you find only if the
kind it turns out to be is selected for this run. When `kind` is present, use
it.

A reference that 404s, or that a token cannot see, is a reference you report as
unresolved. It is not a reference you fill in from the surrounding commit.

## What to do with what you resolved

Feed the resolved titles and bodies into the recovery you were already running,
as INTENT: what the change was for. The code stays the grounding source for
what the software does. Where the two disagree, the code wins and the
disagreement is worth a line in your report.

Report, at the end, how many references you resolved and how many you could
not, with the reason for each failure. A recovery that silently resolved two
of eleven references looks identical to one that resolved all eleven.
