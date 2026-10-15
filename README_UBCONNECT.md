# ubConnect showcase: the system requirements live in Jama

This branch is `main` plus one idea: **the top of the V lives somewhere else.**

The 20 system requirements (`req`) are no longer written in this repo. They live
in Jama, in the project
[Rollout_Demo](https://useblocks-partner.jamacloud.com/perspective.req#/projects/59/).
ubConnect pulls them in. Everything below them (architecture, software
requirements, code, tests) is still written here, and links up to them.

## What changed compared to `main`

| What | Where |
|---|---|
| The ids are now Jama's: `JAMA_Rollout_Demo-SYSRQ-<n>`. The old id is kept as `:legacy_id:` | every `req` |
| The Jama connection (URL, project, field mapping, status labels) | [docs/ubconnect.toml](docs/ubconnect.toml) |
| The pulled-in requirements | [docs/specs/_global/alm_requirements.rst](docs/specs/_global/alm_requirements.rst) |
| What Jama cannot store (stream, link to the user story) | [docs/alm/crosswalk.json](docs/alm/crosswalk.json): do not delete it |
| The sync script and the reset script | [tools/sync_alm.py](tools/sync_alm.py), [tools/reset_demo.py](tools/reset_demo.py) |

## Setup

You need 3 things:

1. **`ubconnect` on your `PATH`.** It is a standalone program, not a pip package.
   Check it with `which ubconnect`.
2. **Your Jama login in `docs/.env`.** It is gitignored. Copy the template and
   fill in the OAuth client id and secret:
   ```bash
   cp docs/.env.example docs/.env
   ```
3. **The Jama instance in `docs/ubconnect.toml`.** This is already set up for
   `useblocks-partner.jamacloud.com`, project 59. Only change it if you use
   another instance.

Test the login:

```bash
cd docs && set -a && . ./.env && set +a && ubconnect jama check --config ubconnect.toml
```

A normal build does **not** need any of this. The pulled-in requirements are
committed, so the build works without Jama.

## Use it

```bash
ubc script sync-jama --path docs            # pull from Jama, keep the current mode
ubc script sync-jama:rst --path docs        # pull as RST (editable)
ubc script sync-jama:external --path docs   # pull as JSON (read-only)
ubc script reset:dry --path docs            # show what reset would do
ubc script reset --path docs                # back to the start (asks first, DISCARDS uncommitted work)
```

Sync and reset are also in VS Code, under `Tasks: Run Task`.

## The demo

```bash
ubc script reset --path docs       # delete the requirements
ubc check docs                     # lots of errors: every link up is broken
ubc script sync-jama --path docs   # get them back from Jama
ubc check docs                     # No errors found
```

The point: **the copy in the repo can be thrown away. Jama is the master.**

If nothing changed in Jama, the sync gives an empty `git diff`. So a diff means
something really changed in Jama.

## The two modes

| | `rst` | `external` |
|---|---|---|
| File | `docs/specs/_global/alm_requirements.rst` | `docs/alm/external.json` |
| Can you edit it here? | yes | no |
| A link to it opens | the page here | the item in Jama |

Only one exists at a time. The sync also rewrites the `sync-jama` block in
`docs/ubproject.toml` for you.

## Good to know

- **It only flows down.** Jama → repo. There is no way back, on purpose.
- **A change in Jama marks reviews as stale.** Change a requirement in Jama, sync,
  then run `ubc agent gaps -p docs`. The requirement and the architecture under it
  now need a new review.
