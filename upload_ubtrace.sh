#!/usr/bin/env bash
# Upload the ubTrace artefact of this project to team.useblocks.com.
#
# Usage:
#   uv run --extra ubtrace sphinx-build -b ubtrace -W --keep-going . _build/ubtrace
#   UBTRACE_INGEST_TOKEN=<token> bash upload_ubtrace.sh
#
# The token needs "Ingest" permission for the target project on
# team.useblocks.com. UBTRACE_VERSION may be overridden from the environment
# (CI sets it to the tag name on tag pushes); it defaults to "main", which is
# what a plain local run publishes.
#
# For a self-hosted instance, point UBTRACE_URL at its API instead:
#   export UBTRACE_URL=http://ubtrace-api.local/api

set -euo pipefail

export UBTRACE_URL="${UBTRACE_URL:-https://api.team.useblocks.com/api}"
: "${UBTRACE_INGEST_TOKEN:?UBTRACE_INGEST_TOKEN is not set (create a token with Ingest permissions on team.useblocks.com and export it first)}"
export UBTRACE_ORG=useblocks-rollout
export UBTRACE_PROJECT=rollout-demo-bms
export UBTRACE_VERSION="${UBTRACE_VERSION:-main}"

# ubt_sphinx writes its output into the ingest layout
#   _build/ubtrace/<ubtrace_organization>/<ubtrace_project>/<ubtrace_version>/
# so the three values above MUST match conf.py (or the `-D ubtrace_version=...`
# override passed to sphinx-build at build time). Package the VERSION directory
# — the one that directly contains docs/ubtrace/needs.json.
BUILD_DIR="_build/ubtrace/${UBTRACE_ORG}/${UBTRACE_PROJECT}/${UBTRACE_VERSION}"

# Reject a missing OR empty build directory: tar on an empty directory produces
# a legal ~45-byte archive, and uploading that with ?overwrite=true would
# silently replace the live version with nothing.
if [[ ! -d "${BUILD_DIR}" || -z "$(ls -A "${BUILD_DIR}")" ]]; then
  echo "ERROR: build directory ${BUILD_DIR} is missing or empty" >&2
  echo "Run the ubtrace build first:" >&2
  echo "  uv run --extra ubtrace sphinx-build -b ubtrace -W --keep-going . _build/ubtrace" >&2
  exit 1
fi

ARCHIVE="$(mktemp -t ubtrace-build-XXXXXX.tar.gz)"
trap 'rm -f "${ARCHIVE}"' EXIT
tar -czf "${ARCHIVE}" -C "${BUILD_DIR}" .

# Log the HTTP status and the response body (ingest id, accepted byte count) so
# a publish is auditable from the run log alone. --fail-with-body still makes
# curl exit non-zero on HTTP >= 400; capture that exit code so the response is
# always printed first, then propagate it.
RESPONSE_BODY="$(mktemp -t ubtrace-response-XXXXXX)"
trap 'rm -f "${ARCHIVE}" "${RESPONSE_BODY}"' EXIT
curl_exit=0
http_code=$(curl --fail-with-body --show-error \
  -w '%{http_code}' -o "${RESPONSE_BODY}" \
  -H "Authorization: Bearer ${UBTRACE_INGEST_TOKEN}" \
  -F "file=@${ARCHIVE}" \
  "${UBTRACE_URL}/v1/ingest/${UBTRACE_ORG}/${UBTRACE_PROJECT}/${UBTRACE_VERSION}?overwrite=true") \
  || curl_exit=$?

echo "ubTrace HTTP ${http_code}"
cat "${RESPONSE_BODY}"
echo

exit "${curl_exit}"
