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
#   tools/publish_demo_branch.sh [--dry-run] [BRANCH]
#
# Before it commits anything, it refreshes the two committed evidence snapshots
# (the JUnit test results and the gap report) and runs the same blocking checks as
# the graph-gates job. --dry-run stops right after those checks.
#
# It runs no reviews. A change expires the verdicts of the needs it touches and
# `ubc check` then fails, so the script stops and names those needs: review them in
# ubCode and run it again. Set UBC to use another ubc binary than the one on PATH.
set -euo pipefail

UBC="${UBC:-ubc}"
dry_run=false
if [[ "${1:-}" == "--dry-run" ]]; then
  dry_run=true
  shift
fi
branch="${1:-trailer-test-200a}"

# CI publishes trailer-test* names only, and a slash would nest the build too deep.
if [[ ! "$branch" =~ ^trailer-test[A-Za-z0-9._-]*$ ]]; then
  echo "error: '$branch' is not a trailer-test* name without slashes, so CI would not publish it" >&2
  exit 2
fi
cd "$(git rev-parse --show-toplevel)"
if git rev-parse --verify --quiet "refs/heads/$branch" >/dev/null ||
  git ls-remote --exit-code --heads origin "$branch" >/dev/null; then
  echo "error: branch '$branch' already exists, pass another name" >&2
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
  echo "$check_output" | tail -n 1 >&2
  python3 -I - docs/reports/gaps/gaps.json <<'EOF' >&2
import json, sys
stale = [g["id"] for g in json.load(open(sys.argv[1]))["gaps"] if g["category"] == "review"]
if stale:
    print("error: these needs lost their review; re-review them in ubCode, then run this again:")
    for need in stale:
        print(f"  {need}")
else:
    print("error: ubc check fails")
EOF
  exit 1
fi
if ! "$UBC" agent gaps -p docs 2>/dev/null | cmp -s - docs/reports/gaps/gaps.json; then
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
git switch -c "$branch"
git add -A -- docs src tests
git commit -q -F - <<EOF
feat: ${title,}

Carried out with ${ids[*]}. The test results and the gap snapshot are
regenerated, and ubc check, the gap snapshot and both import checks pass.
EOF
git push -u origin "$branch"
echo "CI now publishes ubTrace version '$branch'"
