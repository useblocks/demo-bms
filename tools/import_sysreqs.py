#!/usr/bin/env python3
"""Import the customer's DOORS system-requirement export into ``sys_req`` needs.

``docs/external/doors/needs.json`` is what ``ubconnect csv from-csv`` produces
from ``docs/external/doors/bms_sysreqs_v1.csv``, a committed snapshot of one OEM
DOORS baseline. This script turns it into the RST the graph is built from, so the
customer's requirements are needs like any other — visible in the level tables,
the ``needflow`` diagrams and the ubTrace export — rather than a JSON file
sitting next to the project.

Why an import step at all, rather than pointing ubCode at ``needs.json``: the
export is the customer's vocabulary, not this project's. Status values, need
types, field names and heading rows all have to be translated before they are
admissible here, and doing that in a script makes the translation reviewable
instead of implicit. The same arrangement as ``tools/import_test_results.py`` and
``tools/import_gaps.py`` on the other two imported types.

What the translation actually does:

* **Heading rows are dropped.** A DOORS module interleaves section headings with
  requirements in one flat list. A heading is document structure, not a
  requirement, and importing one would invent a need nobody can satisfy.
* **Statuses are mapped** onto this project's vocabulary. DOORS says
  ``Approved`` / ``Proposed`` / ``Rework``; ``[needs.fields.status]`` in
  ``docs/ubproject.toml`` admits only ``draft`` / ``review`` / ``approved``, and
  that enum is global.
* **Rationale becomes prose**, not a field. It is a paragraph of the customer's
  reasoning and belongs in the body where it is read.
* **ASIL, verification method and the DOORS identifiers become fields**, so they
  can be filtered and reported on.

The mapping tables below are the whole contract. An export value that is not in
them is a HARD ERROR rather than a silent default: a new DOORS status or a new
ASIL level means the customer changed something this project has not agreed to
yet, and quietly importing it as ``draft`` would hide exactly the change the
import exists to surface.

Usage::

    ubconnect-dev csv from-csv -c docs/external/doors/import.toml   # refresh the export
    python3 tools/import_sysreqs.py            # -> docs/specs/_external/system_requirements.rst
    python3 tools/import_sysreqs.py --check    # fail if the output is stale
"""

from __future__ import annotations

import argparse
import json
import sys
import textwrap
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_EXPORT = REPO_ROOT / "docs" / "external" / "doors" / "needs.json"
DEFAULT_OUTPUT = REPO_ROOT / "docs" / "specs" / "_external" / "system_requirements.rst"
DEFAULT_CSV = REPO_ROOT / "docs" / "external" / "doors" / "bms_sysreqs_v1.csv"

#: DOORS ``Object Type`` values that are document structure rather than
#: requirements. Dropped, and counted, so the run reports what it left out.
STRUCTURAL_TYPES = frozenset({"Heading", "Information", "Note"})

#: DOORS ``Status`` -> `[needs.fields.status]`. ``Proposed`` is not yet agreed,
#: so it lands as ``draft``; ``Rework`` is agreed-but-being-changed, which is
#: what ``review`` means here.
STATUS_MAP = {
    "Approved": "approved",
    "Proposed": "draft",
    "Rework": "review",
}

#: Accepted verbatim from the export -- the vocabulary is ISO 26262's, not ours,
#: and `[needs.fields.asil]` declares the same set. Listed here so an unexpected
#: value fails in this script, naming the requirement, rather than as a schema
#: violation several steps later.
ASIL_VALUES = frozenset({"QM", "ASIL A", "ASIL B", "ASIL C", "ASIL D"})
VERIFICATION_VALUES = frozenset({"Test", "Analysis", "Inspection", "Review"})


@dataclass(frozen=True)
class SysReq:
    """One imported system requirement, already translated."""

    id: str
    title: str
    text: str
    status: str
    asil: str
    verification_method: str
    doors_id: str
    doors_module: str
    rationale: str


def translate(needs: dict[str, dict[str, object]]) -> tuple[list[SysReq], list[str], list[str]]:
    """Translate exported needs into `SysReq`s.

    :returns: (requirements, ids of dropped structural rows, problem messages).
    """
    requirements: list[SysReq] = []
    dropped: list[str] = []
    problems: list[str] = []

    # Sorted by id so the output is deterministic: re-importing an unchanged
    # export must rewrite the file byte for byte, or `--check` is meaningless.
    for need_id in sorted(needs):
        raw = needs[need_id]
        object_type = str(raw.get("object_type", "") or "")

        if object_type in STRUCTURAL_TYPES:
            dropped.append(need_id)
            continue
        if object_type != "Requirement":
            problems.append(
                f"{need_id}: unknown Object Type {object_type!r} — neither a requirement "
                f"nor one of the structural types {sorted(STRUCTURAL_TYPES)}"
            )
            continue

        doors_status = str(raw.get("status", "") or "")
        if doors_status not in STATUS_MAP:
            problems.append(
                f"{need_id}: unknown DOORS status {doors_status!r} — "
                f"expected one of {sorted(STATUS_MAP)}"
            )
            continue

        asil = str(raw.get("asil", "") or "")
        if asil not in ASIL_VALUES:
            problems.append(
                f"{need_id}: unknown ASIL {asil!r} — expected one of {sorted(ASIL_VALUES)}"
            )
            continue

        method = str(raw.get("verification_method", "") or "")
        if method not in VERIFICATION_VALUES:
            problems.append(
                f"{need_id}: unknown verification method {method!r} — "
                f"expected one of {sorted(VERIFICATION_VALUES)}"
            )
            continue

        text = str(raw.get("content", "") or "").strip()
        if not text:
            problems.append(f"{need_id}: empty requirement text")
            continue

        requirements.append(
            SysReq(
                id=need_id,
                title=str(raw.get("title", "") or "").strip(),
                text=text,
                status=STATUS_MAP[doors_status],
                asil=asil,
                verification_method=method,
                doors_id=str(raw.get("object_identifier", "") or ""),
                doors_module=str(raw.get("module", "") or ""),
                rationale=str(raw.get("rationale", "") or "").strip(),
            )
        )

    return requirements, dropped, problems


def _display(path: Path) -> str:
    """Repo-relative when inside the repo, absolute otherwise."""
    try:
        return str(path.resolve().relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def _body(paragraph: str) -> list[str]:
    """One directive-body paragraph: wrapped to 88 columns, indented, blank line after."""
    return [f"   {line}" for line in textwrap.wrap(paragraph, 85)] + [""]


def render(requirements: list[SysReq], dropped: list[str], export: Path) -> str:
    """Render the generated RST. One `sys_req` directive per imported requirement."""
    rel_export = _display(export)
    rel_csv = _display(DEFAULT_CSV)
    title = "System Requirements (imported from DOORS)"
    lines = [
        title,
        "=" * (len(title.encode()) + 2),
        "",
        ".. warning::",
        "",
        "   **Generated file — do not edit by hand.** Written by",
        "   ``tools/import_sysreqs.py`` from ``%s``." % rel_export,
        "   Re-generate it with::",
        "",
        "      ubconnect csv from-csv -c %s/import.toml" % _display(export.parent),
        "      python3 tools/import_sysreqs.py",
        "",
        "   These are the **customer's** requirements, owned in their DOORS instance and",
        "   imported from a committed export of one baseline (``%s``)." % rel_csv,
        "   Nothing in this project may edit them: an edit here is overwritten by the next",
        "   import, and the customer would never see it. To map one onto this project, add",
        "   a ``covers`` link on the :need:`user story <US_CELL_PROTECTION>` that answers it.",
        "",
    ]

    if dropped:
        lines += [
            ".. note::",
            "",
            "   %d structural row(s) in the export (section headings) were dropped rather"
            % len(dropped),
            "   than imported. A heading is document structure, not a requirement, and no",
            "   user story could ever satisfy one.",
            "",
        ]

    lines += [
        "%d system requirement(s), each owing an incoming ``covers`` link from the user"
        % len(requirements),
        "story that answers it. One with no such link is the **mapping backlog** — a",
        "customer requirement this project has not yet claimed — and is reported by",
        "``ubc agent gaps`` against the ``user_stories`` stage. Ask the engine what to do",
        "about one with ``ubc agent next --id <SYS_ID>``.",
        "",
    ]

    for req in requirements:
        lines += [
            f".. sys_req:: {req.title}",
            f"   :id: {req.id}",
            f"   :status: {req.status}",
            f"   :doors_id: {req.doors_id}",
            f"   :doors_module: {req.doors_module}",
            f"   :asil: {req.asil}",
            f"   :verification_method: {req.verification_method}",
            "",
        ]
        lines += _body(req.text)
        if req.rationale:
            lines += _body(f"**Rationale (customer).** {req.rationale}")

    return "\n".join(lines).rstrip("\n") + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--export", type=Path, default=DEFAULT_EXPORT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--check",
        action="store_true",
        help="fail if the output is stale instead of writing it",
    )
    args = parser.parse_args()

    try:
        envelope = json.loads(args.export.read_text())
    except FileNotFoundError:
        print(f"error: {args.export} not found", file=sys.stderr)
        print(
            "hint: generate it with "
            f"`ubconnect csv from-csv -c {_display(args.export.parent)}/import.toml`",
            file=sys.stderr,
        )
        return 2
    except json.JSONDecodeError as exc:
        print(f"error: {args.export} is not valid JSON ({exc.msg})", file=sys.stderr)
        return 2

    # The ubconnect envelope names its own current version; do not assume "latest".
    versions = envelope.get("versions")
    if not isinstance(versions, dict) or not versions:
        print(f"error: {args.export} has no `versions` — is it a ubconnect export?", file=sys.stderr)
        return 2
    current = envelope.get("current_version")
    block = versions.get(current) if current in versions else next(iter(versions.values()))
    needs = (block or {}).get("needs")
    if not isinstance(needs, dict):
        print(f"error: {args.export} version block has no `needs` mapping", file=sys.stderr)
        return 2

    requirements, dropped, problems = translate(needs)

    if problems:
        print(
            f"error: {len(problems)} row(s) in {_display(args.export)} could not be imported:",
            file=sys.stderr,
        )
        for problem in problems:
            print(f"  {problem}", file=sys.stderr)
        print(
            "hint: the export uses a value this importer has no mapping for. Extend the "
            "tables at the top of tools/import_sysreqs.py once the value is agreed.",
            file=sys.stderr,
        )
        return 1

    if not requirements:
        print(f"error: {_display(args.export)} yielded no requirements", file=sys.stderr)
        return 1

    rendered = render(requirements, dropped, args.export)

    if args.check:
        current_text = args.output.read_text() if args.output.is_file() else ""
        if current_text != rendered:
            print(f"error: {args.output} is stale; re-run without --check", file=sys.stderr)
            return 1
        print(f"{args.output} is up to date ({len(requirements)} system requirements)")
        return 0

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(rendered)
    print(
        f"wrote {args.output} — {len(requirements)} system requirement(s) "
        f"from {_display(args.export)}, {len(dropped)} structural row(s) dropped"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
