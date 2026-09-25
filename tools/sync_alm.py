#!/usr/bin/env python3
"""Acquire the system-requirement level from Jama Connect.

Jama is the MASTER of the system requirements in this project. They are authored,
reviewed and baselined there; this repository holds a copy so the architecture,
software requirements, code and tests below them can link up to something the
graph can resolve.

Delete every requirement in this repository and run this script: they come back,
byte for byte, from Jama. That is the whole point — the local copy is disposable,
the ALM is not.

    ubc script sync-jama              acquire, in whichever mode is active
    ubc script sync-jama:rst          acquire as RST      (round-trip)
    ubc script sync-jama:external     acquire as JSON     (read-only)
    ubc script sync-jama:offline      re-render, no network

TWO MODES, ONE SOURCE
=====================

Both modes read the same Jama project and produce the same 20 needs. They differ
in what lands in the repository and in what the graph will let you do with it.

  rst        `docs/specs/_global/alm_requirements.rst` holds a real `.. req::`
             block per requirement. They are ordinary local needs: ubCode
             resolves them, `ubc diff` sees them, and the file is a normal RST
             source you could edit and push back — the COMPLETE ROUND TRIP. The
             file says "generated, do not edit" because Jama is the master, but
             nothing at the tool level stops you.

  external   The requirements never become source files at all. They are loaded
             straight out of `docs/alm/external.json` through
             `[[needs.external_needs]]`, which is READ-ONLY by construction:
             there is no text to edit, and every reference to one of them opens
             the item in Jama instead of a local page. Nothing can drift, because
             there is nothing local to drift from.

The switch is the mode flag and nothing else. `[[needs.external_needs]]` stays
wired in `ubproject.toml` permanently and simply carries no needs while `rst` is
active, so flipping modes never edits configuration — it only rewrites the two
artefacts this script owns.

THE PIPELINE
============

    ubconnect jama from-jama    Jama project 59  ->  docs/alm/needs.json
    harden (in this script)     make that snapshot buildable
    render (in this script)     ->  docs/alm/external.json   (external mode)
                                ->  docs/specs/_global/alm_requirements.rst

Requirements flow DOWN only. There is deliberately no `[ubconnect.to_jama]` block
in `docs/ubproject.toml`, so a back-flow from here is not merely discouraged, it
is unconfigured. The one-time migration that seeded the Jama project ran from a
throw-away config outside this repository.

Hardening exists for the reason it exists in every ALM pipeline: what the ALM
returns is not what a needs build accepts.

  * Jama sends picklists as numeric option ids, so `status` arrives as `292`
    rather than `Draft`. `[jama_status_labels]` in `docs/ubproject.toml` resolves
    it into the vocabulary `[needs.fields.status]` enum-validates.
  * Jama knows nothing about this repository's streams or user stories, so the
    `traces_to` link up to the user story and the `alm_stream` grouping are
    re-attached from `docs/alm/crosswalk.json` — keyed on Jama's `globalId`,
    which is stable across project copies and re-imports.

`docs/alm/needs.json` is COMMITTED, so a normal build never needs Jama to be
reachable. Only the sync runs the online path, and its diff is the change
notification Jama never sent. Run it nightly or on merge requests, never per
build: the Jama REST API degrades under continuous sync load.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import textwrap
from pathlib import Path
from typing import NoReturn

try:
    import tomllib
except ModuleNotFoundError:  # Python < 3.11
    import tomli as tomllib  # type: ignore[no-redef]

REPO = Path(__file__).resolve().parent.parent
CONFIG = REPO / "docs" / "ubproject.toml"
SNAPSHOT = REPO / "docs" / "alm" / "needs.json"
EXTERNAL = REPO / "docs" / "alm" / "external.json"
CROSSWALK = REPO / "docs" / "alm" / "crosswalk.json"
PAGE = REPO / "docs" / "specs" / "_global" / "alm_requirements.rst"

JAMA_PROJECT_URL = "https://useblocks-partner.jamacloud.com/perspective.req#/projects/59/"

STREAM_TITLES = {
    "cell-protection": "Cell protection",
    "state-estimation": "State estimation",
    "thermal-management": "Thermal management",
    "cell-balancing": "Cell balancing",
    "isolation-monitoring": "Isolation monitoring",
}

# Written onto every need in both modes. Kept in one place so the RST blocks and
# the external JSON cannot drift apart in which fields they carry.
CARRIED_FIELDS = (
    "status",
    "traces_to",
    "alm_stream",
    "legacy_id",
    "jama_id",
    "jama_document_key",
    "jama_url",
    "global_id",
)


def die(message: str) -> NoReturn:
    print(f"error: {message}", file=sys.stderr)
    raise SystemExit(1)


def load_config() -> dict:
    return tomllib.loads(CONFIG.read_text(encoding="utf-8"))


def current_mode() -> str:
    """Which mode the working tree is in, read off the artefacts themselves.

    No marker file: the mode IS whether the external source carries needs.
    """
    if not EXTERNAL.exists():
        return "rst"
    try:
        return "external" if needs_of(json.loads(EXTERNAL.read_text())) else "rst"
    except (json.JSONDecodeError, SystemExit):
        return "rst"


def pull(config: dict) -> None:
    """Run `ubconnect jama from-jama` into the snapshot path."""
    exe = shutil.which("ubconnect")
    if exe is None:
        die("ubconnect is not on PATH — it is a standalone binary, not a pip package")
    missing = [v for v in ("JAMA_USERNAME", "JAMA_PASSWORD") if not os.environ.get(v)]
    if missing:
        die(
            f"{' and '.join(missing)} not set. Export the Jama OAuth client id and "
            "secret, or run with --offline to re-render the committed snapshot."
        )

    project = config["ubconnect"]["from_jama"]["project_id"]
    print(f"acquiring the system level from Jama project {project}")
    subprocess.run(
        [exe, "jama", "from-jama", "--config", str(CONFIG)],
        cwd=CONFIG.parent,
        check=True,
    )


def needs_of(snapshot: dict) -> dict:
    versions = snapshot.get("versions") or {}
    key = snapshot.get("current_version") or next(iter(versions), None)
    if key is None:
        die("snapshot holds no version")
    return versions[key].get("needs") or {}


def harden(needs: dict, config: dict, crosswalk: dict) -> list[dict]:
    """Turn raw from-jama output into needs this project can build."""
    labels = {str(k): v for k, v in config.get("jama_status_labels", {}).items()}
    unknown_status: set[str] = set()
    orphans: list[str] = []
    out: list[dict] = []

    for need in needs.values():
        gid = need.get("global_id") or need.get("jama_global_id")
        entry = crosswalk.get(gid)
        if entry is None:
            orphans.append(need.get("id", "<no id>"))
            continue

        raw_status = str(need.get("status", "")).strip()
        if raw_status and raw_status not in labels:
            unknown_status.add(raw_status)

        out.append(
            {
                "id": need["id"],
                "type": "req",
                "title": need["title"],
                "content": (need.get("content") or "").strip(),
                "status": labels.get(raw_status, raw_status.lower()),
                "traces_to": entry.get("traces_to") or [],
                "alm_stream": entry["stream"],
                "legacy_id": entry["legacy_id"],
                "jama_id": str(need.get("jama_id", "")),
                "jama_document_key": need.get("jama_document_key", ""),
                "jama_url": need.get("jama_url", ""),
                "global_id": gid,
                "_sort": int(need.get("jama_id") or 0),
            }
        )

    if orphans:
        shown = ", ".join(orphans[:5]) + (" ..." if len(orphans) > 5 else "")
        print(f"note: {len(orphans)} Jama item(s) not in the crosswalk, skipped: {shown}")
        print("      add them to docs/alm/crosswalk.json to pull them into the graph")
    if unknown_status:
        print(
            "note: unmapped Jama status option id(s): "
            + ", ".join(sorted(unknown_status))
            + " — add them to [jama_status_labels] in docs/ubproject.toml"
        )

    out.sort(key=lambda n: (n["alm_stream"], n["_sort"]))
    return out


# --- rendering ----------------------------------------------------------------


def rst_block(need: dict) -> str:
    lines = [f".. req:: {need['title']}", f"   :id: {need['id']}"]
    for field in CARRIED_FIELDS:
        value = need[field]
        if isinstance(value, list):
            if not value:
                continue
            value = ", ".join(value)
        lines.append(f"   :{field}: {value}")
    block = "\n".join(lines)
    if not need["content"]:
        return block
    # RST needs a blank line between a directive's option block and its content.
    return block + "\n\n" + textwrap.indent(need["content"], "   ")


HEAD = """\
System Requirements (source: Jama)
====================================

.. warning::

   **Generated — do not edit by hand.** Every requirement below is owned by the
   Jama project `Rollout_Demo <{project_url}>`__. Edit it there, then re-acquire::

      ubc script sync-jama            # in whichever mode is active
      ubc script sync-jama:rst        # as RST, round-trip
      ubc script sync-jama:external   # as read-only JSON

Delete this page and run the sync: the requirements come back from Jama. The
local copy is disposable; the ALM is not.

Nothing here is ever written back to Jama. Requirements flow down only; the
evidence that flows back up (test cases, test runs) is a separate push and a
separate configuration. Each requirement keeps ``:legacy_id:``, the identifier it
carried while it was still authored in this repository, so the migration stays
auditable.
"""

MODE_RST = """
.. note::

   **Mode: RST — the complete round trip.** Each requirement below is a real
   ``.. req::`` block in this file: an ordinary local need that ubCode resolves,
   ``ubc diff`` sees, and you could in principle edit and push back.
   ``[[needs.external_needs]]`` is wired but carries nothing while this mode is
   active. Switch with ``ubc script sync-jama:external``.
"""

MODE_EXTERNAL = """
.. note::

   **Mode: external — read-only by construction.** The requirements are NOT
   source files. They are loaded out of ``docs/alm/external.json`` through
   ``[[needs.external_needs]]``, so there is no local text to edit and nothing
   that can drift; every reference to one of them opens the item in Jama rather
   than a page here. Switch with ``ubc script sync-jama:rst`` to get editable RST
   blocks instead.

.. needtable::
   :filter: type == "req"
   :columns: id;title;status;alm_stream;legacy_id;satisfied_by
   :style: table
"""


def render_page(needs: list[dict], mode: str) -> str:
    head = HEAD.format(project_url=JAMA_PROJECT_URL)
    if mode == "external":
        return head + MODE_EXTERNAL

    chunks = [head + MODE_RST]
    for stream in sorted({n["alm_stream"] for n in needs}):
        title = STREAM_TITLES.get(stream, stream)
        chunks.append(f"\n{title}\n{'-' * max(len(title), 3)}\n")
        for need in [n for n in needs if n["alm_stream"] == stream]:
            chunks.append(rst_block(need) + "\n")
    return "\n".join(chunks)


def render_external(needs: list[dict], mode: str) -> str:
    """The `[[needs.external_needs]]` source. Empty unless external mode is on."""
    payload = {}
    if mode == "external":
        payload = {
            n["id"]: {k: v for k, v in n.items() if k != "_sort"} for n in needs
        }
    return json.dumps(
        {
            "project": "BMS system requirements (Jama)",
            "current_version": "jama",
            "versions": {"jama": {"needs_amount": len(payload), "needs": payload}},
        },
        indent=1,
        ensure_ascii=False,
    ) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Acquire the system-requirement level from Jama Connect.",
    )
    parser.add_argument(
        "--mode",
        choices=("rst", "external"),
        help="rst: generated RST blocks (round-trip). external: read-only JSON. "
        "Omitted keeps the mode the working tree is already in.",
    )
    parser.add_argument(
        "--offline",
        action="store_true",
        help="skip the Jama call and re-render the committed snapshot",
    )
    args = parser.parse_args()

    # `ubc script` forwards no extra arguments, so the offline switch has to be
    # reachable from the environment too: `ALM_OFFLINE=1 ubc script sync-jama:rst`
    # flips modes on a laptop with no Jama reachable.
    offline = args.offline or os.environ.get("ALM_OFFLINE") == "1"
    mode = args.mode or current_mode()
    config = load_config()

    if not offline:
        pull(config)
    if not SNAPSHOT.exists():
        die(f"{SNAPSHOT} does not exist — run once without --offline")
    if not CROSSWALK.exists():
        die(f"{CROSSWALK} does not exist")

    needs = harden(
        needs_of(json.loads(SNAPSHOT.read_text(encoding="utf-8"))),
        config,
        json.loads(CROSSWALK.read_text(encoding="utf-8")),
    )
    if not needs:
        die("no needs survived hardening — check docs/alm/crosswalk.json")

    PAGE.parent.mkdir(parents=True, exist_ok=True)
    PAGE.write_text(render_page(needs, mode), encoding="utf-8")
    EXTERNAL.write_text(render_external(needs, mode), encoding="utf-8")

    where = "external.json (read-only)" if mode == "external" else "alm_requirements.rst"
    print(f"mode {mode}: {len(needs)} requirement(s) acquired into {where}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
