# Plan: release-please + Pharaoh release gate + ubTrace release-candidate dashboard

Status: **shelved** (drafted 2026-09-09, decisions confirmed, nothing implemented)

> **Two premises have since changed (2026-09-10).** `ubc` now runs in CI via
> [useblocks/ubc-action](https://github.com/useblocks/ubc-action), and
> `.github/workflows/ubtrace.yml` now REFRESHES the imported artefacts and commits
> the result instead of gating on their staleness. Both affect the decisions below;
> the corrected statements are marked inline.

## Goal

1. Commits follow conventional commits.
2. release-please collects changes into a release PR.
3. The latest release candidate is always reported in ubTrace, as a dashboard that
   proves the next version is ready to release.
4. The release PR is gated on all the analysis and QA Pharaoh can do being in sync
   with the actual code.
5. Merging the release candidate triggers the release.
6. Release notes have a home.

## Confirmed decisions

| Question | Decision |
|---|---|
| How the Pharaoh gates run in CI, given `ubc` has no public distribution | **Full gate, non-blocking for now** — wire every `ubc` step in with `continue-on-error` and a loud step-summary note, so the workflow is complete and flips to blocking the moment the CLI is available in CI. <br>**Superseded:** the CLI *is* available in CI now (`ubc-action`, version resolved from the marketplace), so `ubc check` already blocks in `ubtrace.yml` while `trace`/`verdict-check` stay advisory by choice, not by necessity. |
| Treatment of the deliberate test defects and the deliberate structural gap | **Gap baselined, failing tests block** — `REQ_CELL_BALANCING_WINDOW` goes into the accepted-gap baseline; the two planted defects make the candidate RED, and the dashboard goes green only once they are fixed. |
| How the release candidate appears in ubTrace | **Fixed `rc` slot, overwritten** on every push to the release branch. Nothing accumulates, no version deletion ever needed; the real semver is shown inside the artefact. |
| Where release notes live | **`CHANGELOG.md` + `myst-parser`** — release-please owns the changelog, and it ships inside the ubTrace artefact via the toctree. |

## What is already in place (works in our favour)

- Commits already follow conventional commits (`feat:`, `fix(ci):`, `chore:`) — nothing to retrofit.
- `.github/workflows/ubtrace.yml` already publishes `main` on push and `v<X.Y.Z>` on
  tag push, with a version allow-list guard, and deliberately never publishes from a PR.
- `ubc agent release-check --baseline <file> --with-verdicts` is exactly the release
  gate wanted: it ratchets structural gaps against accepted debt and folds the
  verdict (substance) gate into the same pass.
- The repo idiom for "is the analysis in sync with the code" is established, though
  it has moved on from `--check`: the committed artefacts are the generated PAGES
  (`specs/_global/gaps.rst`, `specs/_global/test_results.rst`), and the pipeline
  captures `ubc agent gaps`, re-runs both importers and pushes whatever changed.
  `reports/gaps/gaps.json` is gitignored (re-derivable); only
  `reports/junit/testresults.xml` is still a committed snapshot, because a test run
  cannot be re-derived from the sources.
- No git tags exist yet, so the release-please bootstrap is clean.

## Files to create

| File | Purpose |
|---|---|
| `release-please-config.json` | release-type `python`, `bump-minor-pre-major`, `extra-files` entry for `ubproject.toml`'s `[project] version` |
| `.release-please-manifest.json` | bootstrap `{".": "0.1.0"}` -> first release lands as **0.2.0** (there are unreleased `feat:` commits) |
| `.github/workflows/release-please.yml` | push to `main` -> maintain the release PR; on merge -> tag `v<X.Y.Z>` + GitHub Release |
| `.github/workflows/qa.yml` | reusable (`workflow_call`) release-readiness gate |
| `.github/workflows/release-candidate.yml` | push to `release-please--branches--main` -> run `qa.yml`, then publish the artefact to the `rc` slot |
| `.github/workflows/commitlint.yml` | conventional-commit check on PR commits + semantic PR title |
| `commitlint.config.js` | conventional config |
| `reports/release/gap-baseline.json` | accepted-debt baseline, generated locally by `ubc agent release-check --baseline ... --update-baseline`, so `REQ_CELL_BALANCING_WINDOW` is recorded debt and any *new* gap fails |
| `CHANGELOG.md` | seeded stub; release-please owns it from then on |

## Files to modify

- `.github/workflows/ubtrace.yml` — extend the version allow-list to admit `rc`;
  call `qa.yml` on PRs instead of duplicating the build gate.
- `pyproject.toml` — add `myst-parser` to the `ubtrace` extra.
- `conf.py` — enable `myst_parser`; add a `release_candidate` toggle so an `rc`
  build titles itself with the real semver.
- `index.rst` — `CHANGELOG.md` into the toctree.
- `README.md` — a release section documenting the flow.

## The gate (`qa.yml`), in order of what each step proves

| Check | Proves | Blocking day one? |
|---|---|---|
| `ubc agent config-validate` / `doctor` | the process config still matches the ontology | no (advisory) |
| `pytest --junitxml` | the code does what the specs say | **yes** |
| ~~`tools/import_test_results.py --check`~~ | **Superseded** — `ubtrace.yml` re-runs the importer and pushes the result, so a second workflow gating on staleness would fail on something already being fixed. `--check` survives for asking, not gating. | no |
| `ubc agent gaps` | the structural gap list | no (advisory) |
| ~~`tools/import_gaps.py --check`~~ | **Superseded**, same reason. | no |
| `ubc agent trace` | both directions of every trace edge are covered | no (advisory) |
| `ubc agent release-check --baseline reports/release/gap-baseline.json --with-verdicts` | no *new* structural gaps, and no missing/failing/**outdated** verdicts — an outdated verdict is precisely "a need changed and nobody re-reviewed it" | no (advisory) |
| `sphinx-build -b ubtrace -W --keep-going` | the artefact still builds warning-free | **yes** |

- Every `ubc`-dependent step: `continue-on-error` plus a loud step-summary line
  saying the gate is advisory until the CLI is available in CI. A single
  `UBC_GATE_BLOCKING` flag flips them all to blocking later.
- Results also written to the GitHub step summary, so the release PR carries the
  verdict inline.
- CI keeps the baseline **read-only** (no `--update-baseline`): baseline changes are
  made locally and committed, so accepted debt is always a reviewed diff.

## ubTrace release-candidate dashboard

- Publish the release PR's artefact into a single fixed version slot named `rc`,
  overwritten on every push to the release branch (`upload_ubtrace.sh` already
  sends `?overwrite=true`).
- On merge, the tag push publishes the permanent `v<X.Y.Z>` through the existing job.
- The candidate's real semver appears *inside* the artefact (release-notes page +
  `html_title`), so `rc` is never ambiguous about which version it is.
- Trigger on `push` to `release-please--branches--main` rather than `pull_request`,
  so secrets are available without any fork exposure.

Open question that this design makes moot: it could not be confirmed whether the
ubTrace API supports **deleting** a version — the ingest script only ever POSTs.
The fixed-slot approach means no deletion is ever needed.

## Known consequence to accept

Since failing tests block, the release PR is red today: the two planted boundary
defects (`IMPL_IMBALANCE_WARNING` in `src/thermal_management/evaluator.py`,
`IMPL_CAPACITY_MONOTONIC_CLAMP` in `src/state_estimation/soh_tracker.py`) fail the
gate, so no release can be cut until they are fixed. That is the intended demo
("prove the new version is ready"), but it means the merge -> release arm cannot be
shown end-to-end until then.

Escape hatch to build in: a `release-override` PR label that downgrades the test
gate to advisory and stamps the reason into the step summary and the artefact, so
the merge -> tag -> publish arm can be demoed without deleting the defects.

## Blocker: the `ubc` CLI is not distributed publicly

Probed and not found: PyPI, the private `pypi.useblocks.com` index, npm, GitHub
releases. On this machine it exists only inside the ubCode VS Code extension at
`/Users/ruby/.vscode/extensions/useblocks.ubcode-<version>-darwin-arm64/server/cli/ubc`
(see the `local-ubc-cli-path` memory). This is why the Pharaoh gates start advisory.

To make them blocking, CI needs: a fetch source for the binary, and a
`UBCODE_LICENSE_KEY` secret (`ubc` also accepts `--license-key` / `UBCODE_LICENSE_STAGE`).

## Manual steps (cannot be done from here)

1. Create a PAT or GitHub App token and add it as secret `RELEASE_PLEASE_TOKEN`.
   **Both requirements depend on this**: a PR opened by `GITHUB_TOKEN` does not
   trigger `pull_request` workflows (so the gate would never run on the release PR),
   and a tag pushed by `GITHUB_TOKEN` does not trigger the tag-push ubTrace publish
   (so the release would not publish).
2. Set the repo to squash-merge only (release-please reads the squash title).
3. Add branch protection on `main` requiring the `qa` check.
4. When the full gate should block: supply the `ubc` fetch source and add
   `UBCODE_LICENSE_KEY`.

## When picking this back up

- Nothing was implemented; no files created or modified, nothing committed or pushed.
- Existing secret in use: `UBTRACE_INGEST_TOKEN` (Ingest permission on the
  `useblocks-rollout` / `rollout-demo-bms` project at team.useblocks.com).
- `conf.py` is the single source for org / project / version; `upload_ubtrace.sh`
  discovers the built path rather than re-declaring it. Keep it that way.
