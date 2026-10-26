# Spec: read the test evidence through sphinx-test-reports

Status: **implemented** on `feat/test-reports` (2026-10-26), stacked on #15. The
decisions taken while building are in §7, and what the build turned up is in §8.
Checked against ubc 0.38.0 and sphinx-needs 9.1.0 + sphinx-test-reports 3.0.1.

## 1. Goal

Replace the hand-rolled test-evidence importer with ubCode's native test-report
support (`[test_reports]`, beta since ubCode 0.37.0; current release 0.38.0) and
sphinx-test-reports on the Sphinx side:

- the committed JUnit snapshot is read **directly** by a `test-file` directive.
  There is no generator and no generated RST, so there is nothing to keep in sync;
- each `<testcase>` becomes a `testcase` need that links `results_for` to the
  `test` need whose run it records, exactly as `test_result` does today;
- `tools/import_test_results.py`, `specs/_global/test_results.rst` and the
  `test_result` type are deleted.

What must not change: the demo story. The run is still a committed snapshot,
two tests are still red on purpose, the same four requirements still come back
with failing evidence, and an unmapped test case is still a hard error.

## 2. Existing work

| Branch / PR | State | Relation |
|---|---|---|
| `feat/test-reports` | this work | implements this spec on top of #15 |
| #15 `chrisjsewell:per-type-model-pr` (draft) | open | **partial overlap.** Adds an empty `[test_reports]`, `specs/_global/test_run.rst` (one `test-file` with `:auto_suites:` / `:auto_cases:` over the committed XML), `sphinx-test-reports>=3.0.1`, `sphinx_test_reports` in `conf.py`. The new needs sit **beside** the importer's, and nothing links them. Its description lists "switching the test results to test-reports" as open work and names the blocker: no key joins a case to its `test` need. |

No other branch or PR touches this. This spec is the follow-up to #15: it
supplies the join key and does the replacement.

## 3. What exists today

| Piece | Where | Role |
|---|---|---|
| Snapshot | `docs/reports/junit/testresults.xml` | one pytest run, 52 cases, 2 failed / 50 passed |
| Importer | `tools/import_test_results.py` (378 lines) | joins `(classname, name)` to the codelinks marker above each `def test_*`, resolves `chain_reqs` by regex over the spec sources, writes RST |
| Generated page | `docs/specs/_global/test_results.rst` (52 `test_result` needs) | `TRES_<X>` → `results_for` → `TEST_<X>` |
| Type and fields | `docs/ubproject.toml` | `test_result` type; `outcome`, `runtime_s`, `test_run_label` (ES-safe pattern), `chain_reqs`; `results_for` link; `test_results` stage (`produces = "test_result"`, outgoing trace edge) |
| Rules | `docs/schemas.json` | `id-prefix-test_result`, `trace-test_result-results_for`, `field-test_result-run-evidence` |
| Reports | `docs/reports/queries/{verif_results,verif_siblings,safety_evidence,health_failing,health_reqs}.cypher`, `program_health.html.j2`, `traceability_coverage.html.j2` | read `test_result`, `outcome`, `runtime_s`, `test_run_label`, `chain_reqs` |
| Pages | `docs/specs/_global/traceability.rst`, `docs/index.rst` | needtable over `test_result`; toctree entry |
| CI | `.github/workflows/ubtrace.yml` | `import_test_results.py --check` in "Generated specs match snapshots" |
| Prose | `README.md`, `docs/conf.py`, `tools/import_gaps.py`, `.claude/plans/release-please.md` | describe the importer, its ES workaround and its ids |

## 4. Target design

### 4.1 The join key: pytest writes it, `property_link_types` reads it

pytest writes one `<property name="results_for" value="TEST_…"/>` per
`<testcase>`, and the config maps that property onto the link:

```toml
[test_reports]
property_link_types = { results_for = "results_for" }
extra_options = ["test_run_label"]   # §4.3
```

The test id comes from the codelinks marker above the test function: the same
rule the importer applies today, moved to the place that records the evidence.
A root `conftest.py` hook (`pytest_collection_modifyitems`) reads the marker
(the one-line form and, after #15, the multi-line `# @need[md] test:` block) and
appends `("results_for", <id>)` to `item.user_properties`. Using
`user_properties` directly avoids the `record_property` fixture's xunit2 warning.

**Recording a report with an unmarked test fails** (`pytest.UsageError`, only
under `--junitxml`, so ordinary runs are unaffected). That keeps the importer's
guarantee ("an unmapped outcome is evidence pointing at nothing") and moves it
earlier: no snapshot can be recorded with an unmapped case.

Alternatives considered and rejected:

- *A case-name field in the marker grammar*: 52 marker edits, and the function
  name is written twice.
- *`@pytest.mark` with the test id*: the id is written twice, and the two copies drift.
- *Hand-written `test-case` directives*: 52 directives to maintain, or a
  generator again.
- *The `test-reports build needs` converter + needimport*: a third tool, and a
  generated file again.

### 4.2 The snapshot is recorded once more

- `[tool.pytest.ini_options] junit_family = "xunit1"`. The legacy family also
  writes `file` and `line` on each `<testcase>`, so `case_file` / `case_line` are
  filled. #15 notes they are `""` on all 52 cases with pytest's default xunit2.
  Properties are written under either family.
- Re-record with the documented command
  (`uv run pytest -q --junitxml=docs/reports/junit/testresults.xml`). The new
  snapshot carries 52 `results_for` properties, `file`/`line`, and a new
  timestamp. The two planted defects still fail, so the outcomes are unchanged.

### 4.3 The run label moves to the suite need

An autouse session fixture writes
`record_testsuite_property("test_run_label", <start time as "YYYY-MM-DD HH:MM:SS+HH:MM">)`,
and `extra_options = ["test_run_label"]` turns it into a field of the
`testsuite` need. The project declares `[needs.fields.test_run_label]` for every
type, with its ES-safe pattern: a field the project declares "is kept as
declared", and the `testsuite` type cannot carry it alone (sphinx-needs#2371).
The guard against Elasticsearch date detection stays in force.

### 4.4 The page

`specs/_global/test_run.rst` (from #15) becomes the `test_results` stage's route:

```rst
.. test-file:: Committed pytest run
   :file: reports/junit/testresults.xml
   :id: TF_RUN
   :auto_suites:
   :auto_cases:
```

Optionally add `.. test-results:: reports/junit/testresults.xml` underneath: a
per-suite pass/fail table, styled by ubCode out of the box. It creates no needs.

### 4.5 Ontology changes (`docs/ubproject.toml`)

| Today | After |
|---|---|
| `test_result` type, prefix `TRES_` | removed; `testcase` (plus `testfile`, `testsuite`) come from `[test_reports]` |
| `outcome` (`passed\|failed\|error\|skipped`) | `result` (adds `disabled`) |
| `runtime_s` (string, verbatim) | `time` (string; declare `[needs.fields.time] schema = { type = "number" }` if numeric comparisons are wanted) |
| `test_run_label` on every result | `test_run_label` on the `testsuite` need (§4.3) |
| `chain_reqs` (stamped) | removed; reports walk the graph instead (§4.7) |
| title `<marker title> — <outcome>` | the test function name |
| body: `path::function` + one-line message | the card shows the case fields, then the failure message and text and captured output; `case_file` / `case_line` |
| `results_for` link | unchanged |
| stage `test_results`: `produces = "test_result"`, path `test_results.rst` | `produces = "testcase"`, path `specs/_global/test_run.rst`; trace edge unchanged |
| `gap_need_type` enum lists `test_result` | lists `testcase` instead (moot if #15 has made it derived) |

The `test_result` type, the stage switch and #15's derived `all_passed` must
change in one commit. While both kinds of result link to a `test`, `all_passed`
reads the wrong field on half of them.

### 4.6 Ids

Default (recommended): the hashed ids sphinx-test-reports generates under the
file's `:id:`, e.g. `TF_RUN_0EA_BC926`. They are upper-case, short, identical in
ubc and Sphinx (checked), and stable as long as a test's class and name do not
change. Nothing authored links **to** a case, so a renamed test changing its
case id is harmless.

Alternative: `deterministic_case_ids = true`, e.g.
`testcase__test_evaluator__test_imbalance_warning_tracks_the_spread_directly_xxxxx`.
These ids are readable but long and lower-case. They can also collide with
section anchors (`needs.test_report_id_shadows_section`).

The README's `TRES_IMBALANCE_WARNING` reference has to change either way.

### 4.7 Reports and pages

- **Cypher queries** (`verif_results`, `verif_siblings`, `safety_evidence`,
  `health_failing`, `health_reqs`): change `test_result` to `testcase`, `.outcome`
  to `.result`, and `.runtime_s` to `.time`. **Keep the column aliases**
  (`AS outcome`, `AS runtime`) so `safety_case` and `verification_cockpit`
  templates need no change.
- **`program_health.html.j2`**: change the rung `test_result` to `testcase`, and
  read the run label from the `testsuite` need.
- **`traceability_coverage.html.j2`** (a plain template that reads `chain_reqs`):
  it stays a plain template, because the README uses it to contrast plain
  templates with insights. It iterates `test` needs and reads #15's derived
  `chain_reqs` / `all_passed`, plus a new derived `result_count` (`count` over
  `results_for_back`), which tells "passed" from "never ran". A derived field on
  `testcase` itself is **not** possible yet: a project cannot declare a type the
  extension adds (sphinx-needs#2371).
- **`traceability.rst`**: change the "Recorded outcomes" needtable to
  `:types: testcase`, `:columns: id;result;time;results_for`.
- **#15's derived fields**: `chain_reqs` on `test_result` goes away.
  `all_passed` on `test` becomes `test = "result == 'passed'"` over
  `results_for_back`. Both tools derive the same values: the two failing tests
  are `false`, and `all_tests_passed` / `test_count` above them are unchanged.

### 4.8 Gates

- **New `schemas.json` rule `trace-testcase-results_for`**: the current
  `trace-test_result-results_for` rule with `select` on `testcase`, requiring
  exactly one `results_for` that targets a `test`. This rule is
  **required, not optional**. `ubc agent gaps` does **not** catch a case without
  `results_for`, because the auto-expansion links every case to its suite and
  file through `links`, so it is never an orphan (checked). Remove
  `id-prefix-test_result`, `trace-test_result-results_for` and
  `field-test_result-run-evidence`.
- **CI**: drop `import_test_results.py --check`. The snapshot → RST link it
  guarded no longer exists. Keep `import_gaps.py --check`.
- **Reality → snapshot** stays unguarded, as today. The obvious check (run
  pytest, compare `(classname, name, result, results_for)` with the committed
  file, ignore timestamps) belongs to the release-please plan's `qa.yml`, not to
  this migration.

### 4.9 Sphinx and ubTrace

- Dependencies and `conf.py` come from #15: `sphinx-needs>=9.1,<10`,
  `sphinx-test-reports>=3.0.1`, and `sphinx_test_reports` in `extensions`.
- The 18 test-report fields are global (sphinx-needs#2372), so every other need
  carries them as `null`. Elasticsearch date detection is safe: no field holds a
  date-like value, and `test_run_label` keeps its pattern.
- **Not yet verified**: the ubTrace upload with these types, and whether
  ubt-coverage still counts `results_for` edges from `testcase` (the per-need
  `_back` discovery documented in `conf.py`). Publish to a throwaway
  `ubtrace_version` before merging.

### 4.10 Prose

- `README.md`:
  - the test-results section (commands, mapping, "the importer joins …");
  - the Cypher examples (`test_result`, `outcome`);
  - the `TRES_` id;
  - the `test_result` / `gap` mirror table: test evidence is now read natively,
    gaps are still imported;
  - the `ubc agent audit` quirk: re-check whether it still applies;
  - the coverage-report paragraph on `chain_reqs`.
- `docs/conf.py`: the ES and ubt-coverage comments that cite
  `import_test_results.py` and "50 test_results".
- `docs/ubproject.toml`: the comments on the four fields, the type and the stage.
- `tools/import_gaps.py` docstring, and `.claude/plans/release-please.md` (its
  `import_test_results.py --check` row).

## 5. Plan, as built

Three commits on top of #15, each leaving `ubc check docs`, `ubc agent gaps`
(one known gap) and `sphinx-build -W --keep-going` (html and both ubtrace
variants) green:

1. **Record the join key.** The conftest hook, the run-label fixture and
   `junit_family = "xunit1"`, then a re-recorded snapshot. The importer still ran
   at this point, unaffected by the new properties.
2. **Switch.** `[test_reports]` keys, the run-label field, the schema rule, the
   stage, #15's derived fields, the queries, templates and pages. The importer,
   `test_results.rst` and the `test_result` type are deleted, `gaps.json` is
   refreshed, and CI drops the `--check`. This has to be one commit (§4.5).
3. **Prose.** The README, the `conf.py` and `import_gaps.py` notes, the
   release-please plan, and this spec.

## 6. Acceptance criteria

- [x] 52 `testcase` needs, each with exactly one `results_for` to a `test`, with
      the same ids in `ubc` and the Sphinx `needs.json`. Every derived and
      test-report field has the same value in both.
- [x] `ubc agent status`: the `test_results` stage covers 52/52 `test` parents.
      `ubc agent gaps` equals the baseline apart from `summary.total_needs`
      (259 -> 207).
- [ ] `ubc agent config-validate` / `doctor` clean. **Not met**: both report
      `testcase` as undeclared (useblocks/ubcode#4107, §8).
- [x] The README's failing-evidence query, adapted, returns the same four
      requirements from the same two failures: `REQ_COOLING_REQUEST`,
      `REQ_HEATING_REQUEST`, `REQ_CELL_TEMP_SPREAD`, `REQ_SOH_CAPACITY_REPORT`.
- [x] The coverage report still reads 19/20 with a chain, 15 verified vs 4
      failing, 52 results at 96.2 %. The three insights render the same numbers;
      only ids, the run label and `0.0` vs `0.000` runtimes differ.
- [x] Removing a test's marker makes pytest refuse to record a report (exit 4).
      Removing a `results_for` property is a schema violation in
      `ubc schema validate` and fails the Sphinx `-W` build.
- [x] No `test_result`, `TRES_`, `import_test_results` or `runtime_s` left
      outside history.
- [x] `sphinx-build -b html` and `-b ubtrace` (NMC, LFP) with `-W --keep-going`:
      0 warnings.
- [ ] A dry-run upload shows the cases and their coverage in ubTrace. Not done.

## 7. Decisions

1. **Stacked on #15.** It brings the dependencies, `conf.py`, the
   `[test_reports]` table, `test_run.rst`, the multi-line markers and the derived
   fields this work re-points. This branch merges after #15, or #15 lands through
   it.
2. **#15's verdict roll-up works over `testcase`**: `all_passed` reads `result`
   over `results_for_back`, the same in both tools.
3. **Case ids: the hashed default** (`TF_RUN_0EA_BC926`). The queries page roots
   its needflow at one, and a renamed test fails that build loudly.
4. **`test-results` table on `test_run.rst`: yes.**
5. **The stage keeps `produces = "testcase"`** despite §8's `config-validate`
   error. The alternative, deleting the stage, would drop a correct workflow
   declaration to work around a validator bug.

## 8. Risks and observations

- **`ubc agent config-validate` and `doctor` exit 1** on `produces = "testcase"`:
  they check stages against `[[needs.types]]` and miss the types `[test_reports]`
  adds. This is useblocks/ubcode#4107, open. `status`, `gaps` and `next` read the
  stage correctly. Neither command is in CI; the `pharaoh-onboard` skill expects
  `doctor` to be `ok`. The spec's original spike missed this because it read only
  the tail of the output.
- **`ubc agent gaps` does not see an unlinked case**: the auto-expansion links
  every case to its suite and file, so none is an orphan. The schema rule is the
  gate.
- **Beta.** ubCode marks test reports beta. The diagnostics are thorough
  (`needs.test_report_*`), but a behaviour change in a minor release is possible.
- **`result_text` is empty** for pytest failures in both tools. The failure
  message reaches the case's card, not a field. No report reads it.
- **xunit1** is pytest's legacy family. Still supported in pytest 9.1.1; if it is
  dropped, only `case_file` / `case_line` are lost.
- **Global fields.** The test-report fields, and now `test_run_label`, are `null`
  on every other need until sphinx-needs#2371 / #2372 are fixed.
- **ubTrace upload untested**, as in #15: publish to a throwaway
  `ubtrace_version` before relying on it.
