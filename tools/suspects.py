#!/usr/bin/env python3
"""Suspect-link analysis for the requirements acquired from Jama.

Every architecture element pins the fingerprint of each requirement it was
reviewed against, inside the link itself:

    :satisfies: JAMA_Rollout_Demo-SYSRQ-4[fingerprint=="3f9a01bc"]

`tools/sync_alm.py` stamps a fresh fingerprint on each requirement it acquires.
When a requirement changes in Jama, the next sync moves its fingerprint, and
every link still pinned to the old value becomes SUSPECT: sphinx-needs reports
`needs.link_condition_failed` in the editor, in `ubc check` and in
`sphinx-build -W`. This script is the readable view of the same fact, plus the
one command that clears it after review.

    ubc script suspects          list suspect links and what they reach
    ubc script suspects:accept   re-baseline every link after review

Four states per link, only the first is green:

    confirmed   pinned fingerprint == the requirement's fingerprint now
    suspect     pinned fingerprint != now — the requirement changed since review
    unpinned    no fingerprint at all — the link was never baselined
    dangling    the requirement is not in the graph (not acquired, or removed
                in Jama)

Only links THIS repository owns are pinned: `satisfies` on the architecture.
Links owned elsewhere — a SysML v2 part that satisfies a requirement, an AUTOSAR
component that realizes an architecture element — belong to their model and are
read-only here, so they are reported as reached by the change, never rewritten.

`suspects:accept` is the review record. It rewrites the pinned values in the
sources and nothing else, so its git diff says exactly which links a human
confirmed against which version of which requirement. It never touches the
review verdicts in `.pharaoh/verdicts/`: those carry their own one-hop
fingerprint, go `outdated` by themselves when an upstream requirement changes
(`ubc agent verdict-check`), and are cleared by a fresh review, not by this.

Exits 1 while any link is suspect, unpinned or dangling, so CI can gate on it.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DOCS = REPO / "docs"
PAGE = DOCS / "specs" / "_global" / "alm_requirements.rst"
EXTERNAL = DOCS / "alm" / "external.json"

# The authored sources that may carry a managed link. The generated requirement
# page is excluded: it is the TARGET of the links, and it is rewritten by the sync.
SOURCES = sorted(
    p
    for p in (DOCS / "specs").rglob("*")
    if p.suffix in {".rst", ".md"} and p != PAGE
)

MANAGED_LINK = "satisfies"
ALM_PREFIX = "JAMA_"

OPTION = re.compile(rf"^(?P<indent>\s*):{MANAGED_LINK}:(?P<value>.*)$")
TARGET = re.compile(r"^\s*(?P<id>[A-Za-z0-9_\-]+)\s*(?:\[(?P<cond>.*)\])?\s*$")
PINNED = re.compile(r'^\s*fingerprint\s*==\s*"(?P<fp>[0-9a-f]+)"\s*$')
DIRECTIVE = re.compile(r"^(?:\.\. [\w-]+::|```\{[\w-]+\}|:::\{[\w-]+\})")
NEED_ID = re.compile(r"^\s*:id:\s*(?P<id>\S+)\s*$")

# What the blast radius lists, and in which order. The requirement itself, its
# user story and the risks it mitigates are upstream of the change, not reached.
REACH_ORDER = ["arch", "swreq", "impl", "test", "swc", "sysml_part"]
REACH_NAMES = {
    "arch": "architecture",
    "swreq": "software requirements",
    "impl": "implementations",
    "test": "tests",
    "swc": "AUTOSAR components",
    "sysml_part": "SysML v2 parts",
}


@dataclass
class Link:
    owner: str
    target: str
    pinned: str | None
    other_condition: str | None
    path: Path
    line: int  # 1-based

    def state(self, current: dict[str, dict]) -> str:
        if self.target not in current:
            return "dangling"
        if self.pinned is None:
            return "unpinned"
        return "confirmed" if self.pinned == current[self.target]["fingerprint"] else "suspect"


def current_requirements() -> dict[str, dict]:
    """id -> {fingerprint, title} for every requirement acquired from Jama, now."""
    if EXTERNAL.exists():
        snap = json.loads(EXTERNAL.read_text(encoding="utf-8"))
        versions = snap.get("versions") or {}
        needs = next(iter(versions.values()), {}).get("needs", {})
        return {
            k: {"fingerprint": v.get("fingerprint", ""), "title": v.get("title", "")}
            for k, v in needs.items()
        }
    if not PAGE.exists():
        return {}

    found: dict[str, dict] = {}
    title = ""
    current: str | None = None
    for raw in PAGE.read_text(encoding="utf-8").splitlines():
        if raw.startswith(".. req::"):
            title, current = raw[len(".. req::") :].strip(), None
            continue
        match = NEED_ID.match(raw)
        if match:
            current = match["id"]
            found[current] = {"fingerprint": "", "title": title}
            continue
        if current and raw.strip().startswith(":fingerprint:"):
            found[current]["fingerprint"] = raw.split(":fingerprint:", 1)[1].strip()
    return found


def split_targets(value: str) -> list[str]:
    """Split a link option on the commas that are NOT inside a [condition]."""
    parts, depth, buf = [], 0, []
    for char in value:
        if char == "[":
            depth += 1
        elif char == "]":
            depth -= 1
        if char == "," and depth == 0:
            parts.append("".join(buf))
            buf = []
            continue
        buf.append(char)
    parts.append("".join(buf))
    return [p.strip() for p in parts if p.strip()]


def scan() -> list[Link]:
    links: list[Link] = []
    for path in SOURCES:
        owner: str | None = None
        pending: list[tuple[int, str]] = []
        lines = path.read_text(encoding="utf-8").splitlines()

        def flush() -> None:
            for lineno, value in pending:
                for raw_target in split_targets(value):
                    match = TARGET.match(raw_target)
                    if not match or not match["id"].startswith(ALM_PREFIX):
                        continue
                    cond = match["cond"]
                    pinned = PINNED.match(cond) if cond else None
                    links.append(
                        Link(
                            owner=owner or "<no id>",
                            target=match["id"],
                            pinned=pinned["fp"] if pinned else None,
                            other_condition=cond if cond and not pinned else None,
                            path=path,
                            line=lineno,
                        )
                    )
            pending.clear()

        for index, raw in enumerate(lines, start=1):
            if DIRECTIVE.match(raw.lstrip()) and not raw.startswith(" "):
                flush()
                owner = None
                continue
            match = NEED_ID.match(raw)
            if match and owner is None:
                owner = match["id"]
                continue
            option = OPTION.match(raw)
            if option:
                pending.append((index, option["value"]))
        flush()
    return links


# Down the V from one requirement: the architecture that satisfies it, the
# software requirements that refine that architecture, the code and tests on
# those, the AUTOSAR components that realize the architecture, and the SysML v2
# parts that satisfy the requirement directly. `ubc agent impact` is not used:
# its closure walks up AND down, so from a requirement it wanders through the
# shared user story into sibling requirements, and it never descends past `arch`.
REACH_QUERY = " UNION ".join(
    [
        "MATCH (a:arch)-[:satisfies]->(:req {{id:'{id}'}}) RETURN 'arch' AS kind, a.id AS id",
        "MATCH (w:swreq)-[:refines]->(:arch)-[:satisfies]->(:req {{id:'{id}'}}) "
        "RETURN 'swreq' AS kind, w.id AS id",
        "MATCH (x)-[:implements|verifies]->(:swreq)-[:refines]->(:arch)"
        "-[:satisfies]->(:req {{id:'{id}'}}) RETURN x.type AS kind, x.id AS id",
    ]
)
MODEL_REACH = [
    "MATCH (s:swc)-[:realizes]->(:arch)-[:satisfies]->(:req {{id:'{id}'}}) "
    "RETURN 'swc' AS kind, s.id AS id",
    "MATCH (m:sysml_part)-[:satisfies]->(:req {{id:'{id}'}}) RETURN 'sysml_part' AS kind, m.id AS id",
]


def _cypher(exe: str, query: str) -> list[dict] | None:
    result = subprocess.run(
        [exe, "query", "cypher", "-f", "json", "-p", str(DOCS), query],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return None
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return None


def blast_radius(req_id: str) -> dict[str, list[str]]:
    """Everything a change to `req_id` reaches down the V, grouped by need type."""
    exe = shutil.which("ubc")
    if exe is None:
        return {}
    rows = _cypher(exe, " UNION ".join([REACH_QUERY] + MODEL_REACH).format(id=req_id))
    if rows is None:  # a project without the model bridge has no swc/sysml_part
        rows = _cypher(exe, REACH_QUERY.format(id=req_id)) or []
    grouped: dict[str, list[str]] = {}
    for row in rows:
        if row.get("kind") in REACH_NAMES and row.get("id"):
            bucket = grouped.setdefault(row["kind"], [])
            if row["id"] not in bucket:
                bucket.append(row["id"])
    for bucket in grouped.values():
        bucket.sort(key=_natural)
    return grouped


def rel(path: Path) -> str:
    return str(path.relative_to(DOCS))


def report(links: list[Link], current: dict[str, dict]) -> int:
    states = {"confirmed": [], "suspect": [], "unpinned": [], "dangling": []}
    for link in links:
        states[link.state(current)].append(link)

    total = len(links)
    if not current:
        print("no requirements acquired from Jama — run `ubc script sync-jama` first")
        return 1

    if not (states["suspect"] or states["unpinned"] or states["dangling"]):
        print(f"all {total} links confirmed against the requirements Jama holds now")
        return 0

    suspect_reqs = sorted({l.target for l in states["suspect"]}, key=_natural)
    if states["suspect"]:
        noun = "requirement" if len(suspect_reqs) == 1 else "requirements"
        print(
            f"{len(states['suspect'])} suspect link(s) — {len(suspect_reqs)} {noun} "
            f"changed in Jama since they were reviewed\n"
        )
    for req_id in suspect_reqs:
        req = current[req_id]
        print(f"{req_id}   fingerprint now {req['fingerprint']}")
        print(f"  \"{_shorten(req['title'], 96)}\"")
        for link in [l for l in states["suspect"] if l.target == req_id]:
            print(
                f"  SUSPECT  {link.owner:<34} reviewed against {link.pinned}   "
                f"{rel(link.path)}:{link.line}"
            )
        reach = blast_radius(req_id)
        if reach:
            summary = ", ".join(
                f"{len(reach[t])} {_noun(t, len(reach[t]))}" for t in REACH_ORDER if t in reach
            )
            print(f"  reaches  {summary}")
            for need_type in REACH_ORDER:
                if need_type in reach:
                    shown = ", ".join(reach[need_type][:4])
                    more = f" +{len(reach[need_type]) - 4}" if len(reach[need_type]) > 4 else ""
                    print(f"           {REACH_NAMES[need_type]:<22} {shown}{more}")
        print()

    for link in states["unpinned"]:
        print(
            f"UNPINNED {link.owner} -> {link.target}   never baselined   "
            f"{rel(link.path)}:{link.line}"
        )
    for link in states["dangling"]:
        print(
            f"DANGLING {link.owner} -> {link.target}   not in the graph — "
            f"acquired? removed in Jama?   {rel(link.path)}:{link.line}"
        )
    if states["unpinned"] or states["dangling"]:
        print()

    print(f"{len(states['confirmed'])} of {total} links confirmed.")
    if states["suspect"] or states["unpinned"]:
        print("Review the architecture above, then:  ubc script suspects:accept")
    return 1


def accept(links: list[Link], current: dict[str, dict]) -> int:
    """Rewrite every managed link to the fingerprint its requirement has now."""
    if not current:
        print("no requirements acquired from Jama — run `ubc script sync-jama` first")
        return 1

    changed = 0
    dangling = 0
    for path in SOURCES:
        text = path.read_text(encoding="utf-8")
        out_lines = []
        for raw in text.splitlines(keepends=True):
            option = OPTION.match(raw.rstrip("\n"))
            if not option:
                out_lines.append(raw)
                continue
            targets = []
            for raw_target in split_targets(option["value"]):
                match = TARGET.match(raw_target)
                if not match or not match["id"].startswith(ALM_PREFIX):
                    targets.append(raw_target)
                    continue
                req_id, cond = match["id"], match["cond"]
                if cond and not PINNED.match(cond):
                    targets.append(raw_target)  # someone else's condition: leave it
                    continue
                if req_id not in current:
                    dangling += 1
                    targets.append(raw_target)
                    continue
                now = current[req_id]["fingerprint"]
                was = PINNED.match(cond)["fp"] if cond else None
                if was != now:
                    changed += 1
                    print(f"  {req_id:<28} {was or 'unpinned':>8} -> {now}   {rel(path)}")
                targets.append(f'{req_id}[fingerprint=="{now}"]')
            newline = "\n" if raw.endswith("\n") else ""
            out_lines.append(f"{option['indent']}:{MANAGED_LINK}: {', '.join(targets)}{newline}")
        new_text = "".join(out_lines)
        if new_text != text:
            path.write_text(new_text, encoding="utf-8")

    if changed:
        print(f"\nre-baselined {changed} link(s). `git diff docs/specs` is the review record.")
    else:
        print("nothing to re-baseline — every link already matches Jama")
    if dangling:
        print(f"{dangling} link(s) point at requirements not in the graph and were left as they are")
    return 0


def _noun(need_type: str, count: int) -> str:
    plural = REACH_NAMES[need_type]
    if count != 1 or not plural.endswith("s"):
        return plural
    return plural[:-1]  # "1 test", "1 SysML v2 part"


def _natural(value: str) -> tuple:
    return tuple(int(t) if t.isdigit() else t for t in re.split(r"(\d+)", value))


def _shorten(text: str, width: int) -> str:
    return text if len(text) <= width else text[: width - 1].rstrip() + "…"


def main() -> int:
    parser = argparse.ArgumentParser(description="Suspect-link analysis for Jama requirements.")
    parser.add_argument(
        "--accept",
        action="store_true",
        help="re-baseline every link to the fingerprint the requirement has now",
    )
    args = parser.parse_args()

    current = current_requirements()
    links = scan()
    return accept(links, current) if args.accept else report(links, current)


if __name__ == "__main__":
    raise SystemExit(main())
