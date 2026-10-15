#!/usr/bin/env bash
# Upload the ubTrace artefact of this project to team.useblocks.com.
#
# Usage:
#   uv run --extra ubtrace sphinx-build -b ubtrace -W --keep-going . _build/ubtrace
#   UBTRACE_INGEST_TOKEN=<token> bash upload_ubtrace.sh
#
# The token needs "Ingest" permission for the target project on
# team.useblocks.com.
#
# WHERE the artefact is published is NOT configured here. `ubt_sphinx` writes
# its output into the ingest layout
#   _build/ubtrace/<ubtrace_organization>/<ubtrace_project>/<ubtrace_version>/
# and this script DISCOVERS that path, so conf.py is the single source for the
# organisation, the project and the version. An earlier revision hard-coded a
# second copy of the three values here, and the first real publish failed on
# exactly that: conf.py said `useblocks`, this script said `useblocks-rollout`,
# and the build the job had just produced was nowhere the script looked.
#
# Set UBTRACE_VERSION to publish one specific version when the build tree holds
# several (CI sets it to the tag name on tag pushes, and passes the same value
# to sphinx-build as `-D ubtrace_version=`). Set UBTRACE_ORG and UBTRACE_PROJECT
# only to re-target an already-built artefact at a different project.
#
# Set UBTRACE_GIT_BRANCH, UBTRACE_GIT_COMMIT and UBTRACE_GIT_PULL_REQUEST to
# record which source state produced the build. ubTrace stores them as metadata
# beside the version (NOT part of the version id) and exposes them through
#   GET /v1/artifacts/organizations/<org>/projects/<project>/versions-with-dimensions
# as a `git` object per version. All three are optional; CI fills them from the
# GitHub context, a local run that sets none records nothing.
#
# For a self-hosted instance, point UBTRACE_URL at its API instead:
#   export UBTRACE_URL=http://ubtrace-api.local/api

set -euo pipefail

BUILD_ROOT="${BUILD_ROOT:-_build/ubtrace}"
export UBTRACE_URL="${UBTRACE_URL:-https://api.team.useblocks.com/api}"
: "${UBTRACE_INGEST_TOKEN:?UBTRACE_INGEST_TOKEN is not set (create a token with Ingest permissions on team.useblocks.com and export it first)}"

# The version directories are exactly the depth-3 directories under the build
# root: <org>/<project>/<version>. Collected with a read loop rather than
# `mapfile` so this still runs under the bash 3.2 that ships with macOS.
VERSION_DIRS=()
while IFS= read -r _dir; do
  # Honour a pinned version, so a build tree holding both `main` and a tag
  # publishes the one the caller asked for instead of refusing as ambiguous.
  if [[ -z "${UBTRACE_VERSION:-}" || "$(basename "${_dir}")" == "${UBTRACE_VERSION}" ]]; then
    VERSION_DIRS+=("${_dir}")
  fi
done < <(find "${BUILD_ROOT}" -mindepth 3 -maxdepth 3 -type d 2>/dev/null | sort)

if [[ ${#VERSION_DIRS[@]} -eq 0 ]]; then
  echo "ERROR: no built version directory under ${BUILD_ROOT}${UBTRACE_VERSION:+ for version '${UBTRACE_VERSION}'}" >&2
  echo "Run the ubtrace build first:" >&2
  echo "  uv run --extra ubtrace sphinx-build -b ubtrace -W --keep-going docs _build/ubtrace" >&2
  exit 1
fi
if [[ ${#VERSION_DIRS[@]} -gt 1 ]]; then
  echo "ERROR: ${BUILD_ROOT} holds more than one built version:" >&2
  printf '  %s\n' "${VERSION_DIRS[@]}" >&2
  echo "Set UBTRACE_VERSION to pick one, or rebuild into a clean directory." >&2
  exit 1
fi

BUILD_DIR="${VERSION_DIRS[0]}"
export UBTRACE_VERSION="$(basename "${BUILD_DIR}")"
export UBTRACE_PROJECT="$(basename "$(dirname "${BUILD_DIR}")")"
export UBTRACE_ORG="$(basename "$(dirname "$(dirname "${BUILD_DIR}")")")"

# Reject an empty build directory: tar on an empty directory produces a legal
# ~45-byte archive, and uploading that with ?overwrite=true would silently
# replace the live version with nothing.
if [[ -z "$(ls -A "${BUILD_DIR}")" ]]; then
  echo "ERROR: build directory ${BUILD_DIR} is empty" >&2
  exit 1
fi

# --- Git provenance (optional) ------------------------------------------------
# Which source state produced this build. `ubt_sphinx` cannot know it -- a Sphinx
# build has no idea which branch or commit it came from -- so the CALLER states
# it and it rides to the ingest endpoint as query parameters (#2052). Every value
# is OPTIONAL, and each is OMITTED rather than sent empty when its variable is
# unset: ubTrace reads an empty parameter as "not supplied" either way, so
# omitting it says the same thing more plainly and keeps the logged URL honest
# about what was recorded.
#
# The values are percent-encoded because a branch name may legally contain `&`,
# `#`, `=` or `+`, any of which would otherwise split, truncate or mis-decode the
# query string. Commit hashes and pull-request numbers cannot, but encoding them
# costs nothing and keeps one rule for all three.
urlencode() {
  # Percent-encode every byte outside RFC 3986's unreserved set. `LC_ALL=C` makes
  # bash index the string one BYTE at a time, so a multi-byte branch name encodes
  # correctly instead of being read as one wide character.
  local LC_ALL=C
  local string="$1" encoded="" i char
  for (( i = 0; i < ${#string}; i++ )); do
    char="${string:i:1}"
    case "${char}" in
      [a-zA-Z0-9.~_-]) encoded+="${char}" ;;
      *) encoded+="$(printf '%%%02X' "'${char}")" ;;
    esac
  done
  printf '%s' "${encoded}"
}

INGEST_QUERY="overwrite=true"
if [[ -n "${UBTRACE_GIT_BRANCH:-}" ]]; then
  INGEST_QUERY+="&gitBranch=$(urlencode "${UBTRACE_GIT_BRANCH}")"
fi
if [[ -n "${UBTRACE_GIT_COMMIT:-}" ]]; then
  INGEST_QUERY+="&gitCommit=$(urlencode "${UBTRACE_GIT_COMMIT}")"
fi
if [[ -n "${UBTRACE_GIT_PULL_REQUEST:-}" ]]; then
  INGEST_QUERY+="&gitPullRequest=$(urlencode "${UBTRACE_GIT_PULL_REQUEST}")"
fi
INGEST_URL="${UBTRACE_URL}/v1/ingest/${UBTRACE_ORG}/${UBTRACE_PROJECT}/${UBTRACE_VERSION}?${INGEST_QUERY}"

echo "Publishing ${BUILD_DIR}"
echo "  -> ${INGEST_URL}"

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
  "${INGEST_URL}") \
  || curl_exit=$?

echo "ubTrace HTTP ${http_code}"
cat "${RESPONSE_BODY}"
echo

exit "${curl_exit}"
