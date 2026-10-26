# Demo helpers for the trailer-test branch.
#
# The demo starts from a clean trailer-test checkout and runs the change request in
# ubCode. `make publish` then commits the result to its own branch and pushes it,
# and CI publishes every trailer-test* branch as an ubTrace version of the same
# name. A test run uses a name of its own and is removed again with `make clean-run`.
#
#   make setup
#   make publish-check BRANCH=trailer-test-e2e
#   make publish BRANCH=trailer-test-e2e
#   make publish BRANCH=trailer-test-e2e FORCE=1   # rerun under the same name
#   make clean-run BRANCH=trailer-test-e2e
#
# Needs git, uv, ubc 0.38.0 on PATH (or UBC=/path/to/ubc) and, for clean-run, an
# authenticated gh.

BRANCH ?= trailer-test-200a
REPO ?= useblocks/demo-bms
# FORCE=1 reuses an existing BRANCH: it is rebuilt from this checkout and
# force-pushed, and CI overwrites the ubTrace version of the same name.
FORCE ?=
PUBLISH_FLAGS := $(if $(FORCE),--force)

.DEFAULT_GOAL := help
.PHONY: help setup publish-check publish clean-run

help: ## List the targets
	@grep -E '^[a-z-]+:.*## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*## "}; {printf "  %-14s %s\n", $$1, $$2}'

setup: ## Install the Python environment the tests run in
	uv sync

publish-check: ## Refresh the evidence and run the gates for BRANCH, push nothing
	tools/publish_demo_branch.sh --dry-run $(PUBLISH_FLAGS) $(BRANCH)

publish: ## Commit the change to BRANCH and push it, so CI publishes the ubTrace version
	tools/publish_demo_branch.sh $(PUBLISH_FLAGS) $(BRANCH)

# Only ever with an explicit BRANCH, so a bare `make clean-run` cannot fall back to
# the default and remove the recorded demo's branch.
clean-run: ## Remove a test run: BRANCH locally and on origin, and its CI runs
	@if [ "$(origin BRANCH)" != "command line" ]; then \
	  echo "error: name the branch to remove, e.g. make clean-run BRANCH=trailer-test-e2e" >&2; exit 2; \
	fi
	@case "$(BRANCH)" in \
	  trailer-test) echo "error: refusing to remove the trailer-test baseline" >&2; exit 2 ;; \
	  trailer-test?*) ;; \
	  *) echo "error: '$(BRANCH)' is not a trailer-test* branch" >&2; exit 2 ;; \
	esac
	@if [ "$$(git branch --show-current)" = "$(BRANCH)" ]; then git switch trailer-test; fi
	-git branch -D $(BRANCH)
	-git push origin --delete $(BRANCH)
	gh run list --repo $(REPO) --branch $(BRANCH) --limit 50 --json databaseId --jq '.[].databaseId' \
	  | while read -r run; do gh run delete --repo $(REPO) "$$run"; done
	@echo "Still by hand: delete ubTrace version '$(BRANCH)' on team.useblocks.com, and close the issue from act 3."
