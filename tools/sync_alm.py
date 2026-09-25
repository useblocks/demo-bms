#!/usr/bin/env python3
"""Acquire the system-requirement level from Jama Connect.

Jama is the MASTER of the system requirements in this project. They are authored,
reviewed and baselined there; this repository holds a copy so the architecture,
software requirements, code and tests below them can link up to something the
graph can resolve.

Delete every requirement in this repository and run this script: they come back,
byte for byte, from Jama. That is the whole point — the local copy is disposable,
the ALM is not.

    ubc script sync-jama              acquire, keeping the mode the tree is in
    ubc script sync-jama:rst          acquire as RST   (round-trip)  and switch
    ubc script sync-jama:external     acquire as JSON  (read-only)   and switch

`sync-jama` and `sync-jama:rst` do the same thing WHILE the tree is already in
rst mode. They differ only when it is not: the bare form keeps the current mode,
the suffixed forms force one.

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

ONE MODE, ONE ARTEFACT
======================

    ubconnect jama from-jama    Jama project 59 -> docs/_build/alm/needs.json
    harden (in this script)     make that raw export buildable
    render (in this script)     -> EXACTLY ONE of:
                                     docs/specs/_global/alm_requirements.rst
                                     docs/alm/external.json
    then                        delete the raw export and the other artefact

The raw export is a throw-away under `_build/` (gitignored). It used to be
committed as `docs/alm/needs.json`, which meant a sync left THREE copies of the
same 20 requirements in the tree — the raw export, the external source and the
RST page — of which at most one was ever live. There is now one.

Because the raw export is gone, there is no offline path: acquiring means
acquiring, and switching modes needs Jama reachable.

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
# `from-jama` drops its raw export here (`[ubconnect.from_jama] outdir`). It is
# under _build/, so it is gitignored and thrown away after hardening.
RAW = REPO / "docs" / "_build" / "alm" / "needs.json"
EXTERNAL = REPO / "docs" / "alm" / "external.json"
CROSSWALK = REPO / "docs" / "alm" / "crosswalk.json"
# Where the Jama credentials are looked for, in order. `docs/` is first because
# it is the ubc project root — it holds `ubproject.toml`, and it is the working
# directory `ubc script` runs a script in, so that is where someone naturally
# puts the file. Both are gitignored. `ALM_ENV_FILE` overrides the search
# entirely, e.g. to share one file across several repositories.
ENV_CANDIDATES = [REPO / "docs" / ".env", REPO / ".env"]


def env_file() -> Path:
    """The `.env` that will be read — the first that exists, else the preferred one."""
    override = os.environ.get("ALM_ENV_FILE")
    if override:
        return Path(override)
    return next((p for p in ENV_CANDIDATES if p.is_file()), ENV_CANDIDATES[0])
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


def load_dotenv(path: Path) -> list[str]:
    """Read KEY=VALUE lines from `path` into os.environ, returning the keys set.

    Neither ubConnect nor `ubc script` reads a `.env` file, so without this the
    file would have no effect at all and every sync would need
    `set -a && . ./.env && set +a` in front of it. Loading it here works because
    ubConnect is started as a CHILD process and inherits this environment — and
    it saves needing `source` on Linux and its non-existent equivalent on Windows.

    Deliberately minimal: no interpolation, no multi-line values, no escapes.
    Everything after the first `=` is the value, so a `#` inside a secret is kept
    rather than silently truncating it as an inline comment. Surrounding quotes
    are stripped, which is how a value gets leading or trailing spaces.

    A variable already in the real environment WINS over the file, so an explicit
    `export` or a CI secret is never clobbered by a stale local `.env`.
    """
    if not path.is_file():
        return []

    loaded: list[str] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):  # tolerate a shell-style file
            line = line[len("export ") :].lstrip()
        key, separator, value = line.partition("=")
        key = key.strip()
        if not separator or not key:
            continue
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        if key in os.environ:  # the real environment wins
            continue
        os.environ[key] = value
        loaded.append(key)
    return loaded


def die(message: str) -> NoReturn:
    print(f"error: {message}", file=sys.stderr)
    raise SystemExit(1)


def load_config() -> dict:
    return tomllib.loads(CONFIG.read_text(encoding="utf-8"))


def current_mode() -> str:
    """Which mode the working tree is in, read off the artefacts themselves.

    No marker file and no ambiguity: exactly one data artefact exists at a time,
    so its presence IS the mode.
    """
    return "external" if EXTERNAL.exists() else "rst"


MARK_BEGIN = "# sync-jama:begin"
MARK_END = "# sync-jama:end"

EXTERNAL_BLOCK = """[[needs.external_needs]]
json_path = "alm/external.json"
base_url = "https://useblocks-partner.jamacloud.com"
target_url = "perspective.req#/containers/{{need['jama_id']}}/details?projectId=59"
css_class = "alm-external"
"""


def write_mode_config(mode: str) -> None:
    """Put (or remove) the `[[needs.external_needs]]` entry for the active mode.

    The two modes are two sources for the same need ids, so exactly one of them
    may be configured at a time — and a configured source whose file is missing
    is a warning this project treats as fatal. Neither condition can be expressed
    in static TOML, so the sync owns a marked region and rewrites it.
    """
    text = CONFIG.read_text(encoding="utf-8")
    start = text.index(MARK_BEGIN) + len(MARK_BEGIN)
    end = text.index(MARK_END)
    body = f"\n{EXTERNAL_BLOCK}\n" if mode == "external" else "\n"
    updated = text[:start] + body + text[end:]
    if updated != text:
        CONFIG.write_text(updated, encoding="utf-8")


def pull(config: dict) -> None:
    """Run `ubconnect jama from-jama` into the snapshot path."""
    exe = shutil.which("ubconnect")
    if exe is None:
        die("ubconnect is not on PATH — it is a standalone binary, not a pip package")

    env = env_file()
    loaded = load_dotenv(env)
    if loaded:
        print(f"read {', '.join(loaded)} from {env.relative_to(REPO)}")

    missing = [v for v in ("JAMA_USERNAME", "JAMA_PASSWORD") if not os.environ.get(v)]
    if missing:
        looked = " or ".join(str(p.relative_to(REPO)) for p in ENV_CANDIDATES)
        die(
            f"{' and '.join(missing)} not set, and no .env supplied "
            f"{'them' if len(missing) > 1 else 'it'} (looked in {looked}).\n"
            "       cp docs/.env.example docs/.env and fill in the Jama OAuth "
            "client id and secret."
        )

    project = config["ubconnect"]["from_jama"]["project_id"]
    print(f"acquiring the system level from Jama project {project}")
    subprocess.run(
        [exe, "jama", "from-jama", "--config", str(CONFIG)],
        cwd=CONFIG.parent,
        check=True,
    )


def normalise_snapshot() -> None:
    """Rewrite the pulled snapshot so an unchanged Jama gives an EMPTY git diff.

    `from-jama` stamps a fresh `created` timestamp on every run and does not
    order its schema keys, so a sync that changed nothing still produced a
    14-line diff. That noise is not cosmetic: the whole point of committing the
    snapshot is that `git diff docs/alm/` IS the change notification Jama never
    sent, and a notification that fires every time says nothing.

    Dropping `created` is safe — nothing reads it, and the commit already carries
    a better timestamp than the one the exporter invents.
    """
    snapshot = json.loads(RAW.read_text(encoding="utf-8"))
    snapshot.pop("created", None)
    for version in (snapshot.get("versions") or {}).values():
        version.pop("created", None)
    RAW.write_text(
        json.dumps(snapshot, indent=1, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
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


def render_external(needs: list[dict]) -> str:
    """The `[[needs.external_needs]]` source. Only written in external mode."""
    payload = {n["id"]: {k: v for k, v in n.items() if k != "_sort"} for n in needs}
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
    args = parser.parse_args()
    mode = args.mode or current_mode()
    config = load_config()

    pull(config)
    normalise_snapshot()
    if not CROSSWALK.exists():
        die(f"{CROSSWALK} does not exist")

    needs = harden(
        needs_of(json.loads(RAW.read_text(encoding="utf-8"))),
        config,
        json.loads(CROSSWALK.read_text(encoding="utf-8")),
    )
    if not needs:
        die("no needs survived hardening — check docs/alm/crosswalk.json")

    # ONE data artefact. The other is removed, so the working tree can never
    # show two answers to "where do the requirements live".
    PAGE.parent.mkdir(parents=True, exist_ok=True)
    PAGE.write_text(render_page(needs, mode), encoding="utf-8")
    if mode == "external":
        EXTERNAL.write_text(render_external(needs), encoding="utf-8")
    else:
        EXTERNAL.unlink(missing_ok=True)
    write_mode_config(mode)

    # The raw export has done its job. Keeping it would put a third copy of the
    # same 20 requirements in the tree.
    RAW.unlink(missing_ok=True)

    if mode == "external":
        print(
            f"mode external: {len(needs)} requirement(s) in "
            f"{EXTERNAL.relative_to(REPO)} (read-only), no RST blocks"
        )
    else:
        print(
            f"mode rst: {len(needs)} requirement(s) in "
            f"{PAGE.relative_to(REPO)}, no external.json"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
