#!/usr/bin/env bash
# Publish the result of a demo change request as its own branch and ubTrace version.
#
# The demo starts from a clean trailer-test checkout, the 250 A baseline. The
# change request runs in ubCode: the anchor edit, assess, approve, execute and
# close all leave their edits uncommitted in the working tree. This script turns
# that working tree into a new branch, trailer-test-200a unless named otherwise,
# and pushes it. .github/workflows/ubtrace.yml publishes every trailer-test*
# branch under its own name, so the result sits in ubTrace beside the version it
# started from instead of overwriting it.
#
# Usage, from anywhere inside the checkout:
#   tools/publish_demo_branch.sh [--dry-run] [--force] [BRANCH]
#
# Before it commits anything, it refreshes the two committed evidence snapshots
# (the JUnit test results and the gap report) and runs the same blocking checks as
# the graph-gates job. --dry-run stops right after those checks.
#
# A BRANCH that already exists is refused unless --force is given, which rebuilds
# it from this checkout and force-pushes it. CI's upload always asks ubTrace to
# overwrite, so the version of that name is replaced too, and a test run can reuse
# its name.
#
# Review verdicts are not part of the demo. A change expires the verdicts of the
# needs it touches, and tools/import_gaps.py leaves those review gaps out of the
# generated gap needs, so they do not block the publish. Set UBC to use another ubc
# binary than the one on PATH.
set -euo pipefail

UBC="${UBC:-ubc}"
dry_run=false
force=false
while [[ "${1:-}" == --* ]]; do
  case "$1" in
    --dry-run) dry_run=true ;;
    --force) force=true ;;
    *)
      echo "error: unknown option $1" >&2
      exit 2
      ;;
  esac
  shift
done
branch="${1:-trailer-test-200a}"

# CI publishes trailer-test* names only, and a slash would nest the build too deep.
if [[ ! "$branch" =~ ^trailer-test[A-Za-z0-9._-]*$ ]]; then
  echo "error: '$branch' is not a trailer-test* name without slashes, so CI would not publish it" >&2
  exit 2
fi
cd "$(git rev-parse --show-toplevel)"
if ! $force && { git rev-parse --verify --quiet "refs/heads/$branch" >/dev/null ||
  git ls-remote --exit-code --heads origin "$branch" >/dev/null; }; then
  echo "error: branch '$branch' already exists; pass another name, or --force to replace it" >&2
  exit 2
fi

echo "== change requests"
# Every change request whose record is uncommitted here must already be closed.
ids=()
titles=()
while IFS=$'\t' read -r id state path title; do
  [[ -n "$(git status --porcelain --untracked-files=all -- "$path")" ]] || continue
  echo "  $id: $state"
  if [[ "$state" != "closed" ]]; then
    echo "error: $id is '$state'; close it in ubCode first" >&2
    exit 1
  fi
  ids+=("$id")
  titles+=("$title")
done < <("$UBC" agent change list -p docs | python3 -I -c '
import json, sys
for cr in json.load(sys.stdin)["change_requests"]:
    print(cr["id"], cr["state"], cr["path"], cr["title"], sep="\t")
')
if (( ${#ids[@]} == 0 )); then
  echo "error: no uncommitted change request in this working tree" >&2
  exit 1
fi

echo "== test results"
status=0
uv run pytest -q --junitxml=docs/reports/junit/testresults.xml >/dev/null || status=$?
# Exit 1 only means some tests failed, which the results record (two fail on
# purpose); anything higher means the run itself broke.
if (( status > 1 )); then
  echo "error: pytest did not complete (exit $status)" >&2
  exit 1
fi
uv run python tools/import_test_results.py

echo "== gap snapshot"
# Two passes: importing the gaps adds GAP needs, which changes the totals the next
# report states, and CI wants the snapshot byte-identical to a fresh report.
for _ in 1 2; do
  "$UBC" agent gaps -p docs >docs/reports/gaps/gaps.json 2>/dev/null || true
  python3 -I -c 'import json, sys; json.load(open(sys.argv[1]))' docs/reports/gaps/gaps.json
  uv run python tools/import_gaps.py >/dev/null
done

echo "== gates"
if ! check_output="$("$UBC" check docs 2>&1)"; then
  echo "$check_output" | tail -n 20 >&2
  echo "error: ubc check fails" >&2
  exit 1
fi
# `ubc agent gaps` exits non-zero whenever it finds a gap, and this project keeps
# one on purpose, so its exit code is ignored and only the report is compared.
fresh_report="$(mktemp)"
trap 'rm -f "$fresh_report"' EXIT
"$UBC" agent gaps -p docs >"$fresh_report" 2>/dev/null || true
if ! cmp -s "$fresh_report" docs/reports/gaps/gaps.json; then
  echo "error: the gap snapshot does not match a fresh ubc agent gaps report" >&2
  exit 1
fi
uv run python tools/import_gaps.py --check >/dev/null
uv run python tools/import_test_results.py --check >/dev/null
echo "  ubc check, the gap snapshot and both import checks pass"

if $dry_run; then
  echo "dry run: would commit to '$branch' and push it"
  exit 0
fi

echo "== publish"
title="${titles[0]}"
# The commit subject lower-cases the title's first letter. Spelled out with tr
# rather than `${title,}`, which needs bash 4: macOS still ships bash 3.2.
first="$(printf '%s' "${title:0:1}" | tr '[:upper:]' '[:lower:]')"
# -C rather than -c: with --force an existing local branch is reset to this checkout.
git switch -C "$branch"
git add -A -- docs src tests
git commit -q -F - <<EOF
feat: ${first}${title:1}

Carried out with ${ids[*]}. The test results and the gap snapshot are
regenerated, and ubc check, the gap snapshot and both import checks pass.
EOF
if $force; then
  git push --force -u origin "$branch"
else
  git push -u origin "$branch"
fi
echo "CI now publishes ubTrace version '$branch'"
