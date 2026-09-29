#!/usr/bin/env python3
"""Bridge the system models into the needs graph: SysML v2 and AUTOSAR.

The models are NOT authored in this repository. Their masters are the modelling
tools — an MBSE tool for the SysML v2 system architecture, an AUTOSAR authoring
tool for the software components — and `docs/models/` holds their exports:

    docs/models/bms.sysml    SysML v2 textual notation
    docs/models/bms.arxml    AUTOSAR classic R4.x ARXML

This script reads both and writes one read-only external-needs source per model:

    docs/models/sysml.json   one `sysml_part` need per part definition
    docs/models/autosar.json one `swc` need per software component,
                             one `port_if` need per port interface

Both sources are loaded through `[[needs.external_needs]]`, so nothing here can
be edited locally, and every reference to a model element opens the model file
at the line that defines it. The links come FROM the model, because the model
owns them:

    sysml_part --satisfies-->  req    a SysML v2 `satisfy` relationship; the
                                      requirement is mirrored in the model with
                                      its Jama id as the SysML short name
    sysml_part --part_of-->    sysml_part   part usages of the system
    swc        --realizes-->   arch   an AUTOSAR special data group,
                                      <SDG GID="useblocks.Traceability">
    swc        --provides-->   port_if   a P-PORT-PROTOTYPE
    swc        --requires-->   port_if   an R-PORT-PROTOTYPE

With these in place one query walks the whole chain — a Jama requirement, the
SysML v2 part that satisfies it, the architecture in Git, the AUTOSAR component
that realizes it, the code and the test:

    ubc script trace

THE READERS ARE DEMO READERS
============================

The ARXML reader is complete for what it reads (XML, AUTOSAR R4 namespace).
The SysML v2 reader is NOT a SysML v2 parser: it reads the subset of the textual
notation this model uses — `package`, `part def`, `part <name> : <Type>;`,
`requirement <'<short name>'> <name>;`, `satisfy <requirement> by <part>;` and
`doc /* ... */` — and says so when it meets anything else it cannot place. A
production bridge reads the model through the standard Systems Modeling API
(SysML v2 API & Services) or a real parser, and emits the same JSON.

Neither ubConnect nor Sphinx-Needs has a SysML v2 or an AUTOSAR connector today.
The point of this script is the SHAPE: any model that can be exported as
structured text becomes needs through ~100 lines, and from then on it takes part
in everything the graph does — traceability, suspect links, ubTrace.

    ubc script import-models      re-read both models (no network)
"""

from __future__ import annotations

import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
MODELS = REPO / "docs" / "models"
SYSML = MODELS / "bms.sysml"
ARXML = MODELS / "bms.arxml"
NS = {"ar": "http://autosar.org/schema/r4.0"}


def snake(name: str) -> str:
    """CellMeasurementAcq -> CELL_MEASUREMENT_ACQ (this project's id grammar)."""
    return re.sub(r"(?<=[a-z0-9])(?=[A-Z])", "_", name).upper()


def words(name: str) -> str:
    """CellMeasurementAcq -> Cell Measurement Acq."""
    return re.sub(r"(?<=[a-z0-9])(?=[A-Z])", " ", name)


def envelope(project: str, needs: dict) -> str:
    return (
        json.dumps(
            {
                "project": project,
                "current_version": "model",
                "versions": {"model": {"needs_amount": len(needs), "needs": needs}},
            },
            indent=1,
            ensure_ascii=False,
            sort_keys=True,
        )
        + "\n"
    )


# --- SysML v2 --------------------------------------------------------------------

DOC = re.compile(r"doc\s*/\*(?P<body>.*?)\*/", re.DOTALL)
PACKAGE = re.compile(r"^\s*package\s+(?P<name>\w+)\s*\{")
REQUIREMENT = re.compile(r"^\s*requirement\s+<'(?P<short>[^']+)'>\s+(?P<name>\w+)\s*;")
PART_DEF = re.compile(r"^\s*part\s+def\s+(?P<name>\w+)\s*\{")
PART_USAGE = re.compile(r"^\s*part\s+(?P<name>\w+)\s*:\s*(?P<type>\w+)\s*;")
SATISFY = re.compile(r"^\s*satisfy\s+(?P<req>\w+)\s+by\s+(?P<part>\w+)\s*;")


def clean_doc(body: str) -> str:
    lines = [re.sub(r"^\s*\*\s?", "", line).rstrip() for line in body.strip().splitlines()]
    return " ".join(" ".join(lines).split())


def read_sysml(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()

    # Docs belong to the part def whose body they open; find each by position.
    docs_at = {text.count("\n", 0, m.start()) + 1: clean_doc(m["body"]) for m in DOC.finditer(text)}

    requirements: dict[str, str] = {}  # usage name -> short name (the Jama id)
    part_defs: dict[str, dict] = {}  # def name -> {line, doc}
    usages: dict[tuple[str, str], str] = {}  # (owner def, usage) -> type
    satisfies: list[tuple[str, str, str, int]] = []  # (owner def, req, part usage, line)
    unplaced: list[int] = []

    owner: str | None = None
    depth_at_owner = 0
    depth = 0
    in_doc = False
    for number, raw in enumerate(lines, start=1):
        line = raw.split("//", 1)[0] if not in_doc else raw
        if in_doc:
            if "*/" in line:
                in_doc = False
            continue
        if "doc" in line and "/*" in line and "*/" not in line:
            in_doc = True
            continue

        if (m := PART_DEF.match(line)):
            owner, depth_at_owner = m["name"], depth
            part_defs[owner] = {"line": number, "doc": ""}
        elif (m := REQUIREMENT.match(line)):
            requirements[m["name"]] = m["short"]
        elif (m := PART_USAGE.match(line)) and owner:
            usages[(owner, m["name"])] = m["type"]
        elif (m := SATISFY.match(line)) and owner:
            satisfies.append((owner, m["req"], m["part"], number))
        elif line.strip() and not PACKAGE.match(line) and line.strip() not in {"{", "}"}:
            if not line.strip().startswith(("doc", "*", "/*")):
                unplaced.append(number)

        depth += line.count("{") - line.count("}")
        if owner and depth <= depth_at_owner:
            owner = None

    if unplaced:
        print(
            f"note: {path.name}: {len(unplaced)} line(s) outside the supported subset, "
            f"ignored: {', '.join(map(str, unplaced[:8]))}",
            file=sys.stderr,
        )

    # A part def's doc is the first `doc /* */` between its own line and the next
    # part def — so a doc further down can never be attributed to the wrong def.
    order = sorted(part_defs, key=lambda n: part_defs[n]["line"])
    doc_lines = sorted(docs_at)
    for i, name in enumerate(order):
        start = part_defs[name]["line"]
        stop = part_defs[order[i + 1]]["line"] if i + 1 < len(order) else 10**9
        inside = [d for d in doc_lines if start < d < stop]
        part_defs[name]["doc"] = docs_at[inside[0]] if inside else ""

    needs: dict[str, dict] = {}
    for name in order:
        need_id = f"SYSML_{snake(name)}"
        needs[need_id] = {
            "id": need_id,
            "type": "sysml_part",
            "title": words(name),
            "content": part_defs[name]["doc"],
            "model_file": path.name,
            "model_line": str(part_defs[name]["line"]),
            "model_kind": "SysML v2 part def",
            "satisfies": [],
            "part_of": [],
        }

    for (owner_def, _usage), part_type in usages.items():
        child = f"SYSML_{snake(part_type)}"
        parent = f"SYSML_{snake(owner_def)}"
        if child in needs and parent not in needs[child]["part_of"]:
            needs[child]["part_of"].append(parent)

    for owner_def, req_usage, part_usage, number in satisfies:
        part_type = usages.get((owner_def, part_usage))
        short = requirements.get(req_usage)
        if not part_type or not short:
            print(f"note: {path.name}:{number}: cannot resolve `satisfy {req_usage} by "
                  f"{part_usage}`, skipped", file=sys.stderr)
            continue
        target = needs[f"SYSML_{snake(part_type)}"]
        if short not in target["satisfies"]:
            target["satisfies"].append(short)

    for need in needs.values():
        need["satisfies"].sort(key=_natural)
    return needs


# --- AUTOSAR ARXML -----------------------------------------------------------------


def _text(element: ET.Element | None, path: str) -> str:
    found = element.find(path, NS) if element is not None else None
    return " ".join((found.text or "").split()) if found is not None else ""


def _line_of(lines: list[str], short_name: str) -> int:
    needle = f"<SHORT-NAME>{short_name}</SHORT-NAME>"
    for number, line in enumerate(lines, start=1):
        if needle in line:
            return number
    return 1


def read_arxml(path: Path) -> dict:
    lines = path.read_text(encoding="utf-8").splitlines()
    root = ET.parse(path).getroot()
    needs: dict[str, dict] = {}

    for interface in root.iterfind(".//ar:SENDER-RECEIVER-INTERFACE", NS):
        name = _text(interface, "ar:SHORT-NAME")
        elements = [_text(e, "ar:SHORT-NAME") for e in interface.iterfind(".//ar:VARIABLE-DATA-PROTOTYPE", NS)]
        need_id = f"AR_IF_{snake(name.removesuffix('_I'))}"
        needs[need_id] = {
            "id": need_id,
            "type": "port_if",
            "title": name,
            "content": _text(interface, "ar:DESC/ar:L-2")
            + (f" Data elements: {', '.join(elements)}." if elements else ""),
            "model_file": path.name,
            "model_line": str(_line_of(lines, name)),
            "model_kind": "AUTOSAR SENDER-RECEIVER-INTERFACE",
        }

    for component in root.iterfind(".//ar:APPLICATION-SW-COMPONENT-TYPE", NS):
        name = _text(component, "ar:SHORT-NAME")
        realizes = [
            (sd.text or "").strip()
            for sdg in component.iterfind(".//ar:SDG", NS)
            if sdg.get("GID") == "useblocks.Traceability"
            for sd in sdg.iterfind("ar:SD", NS)
            if sd.get("GID") == "realizes" and (sd.text or "").strip()
        ]

        def ports(tag: str, ref: str) -> list[str]:
            out = []
            for port in component.iterfind(f".//ar:{tag}", NS):
                target = _text(port, f"ar:{ref}")
                if target:
                    out.append(f"AR_IF_{snake(target.rsplit('/', 1)[-1].removesuffix('_I'))}")
            return sorted(out)

        need_id = f"AR_SWC_{snake(name)}"
        needs[need_id] = {
            "id": need_id,
            "type": "swc",
            "title": words(name),
            "content": _text(component, "ar:DESC/ar:L-2"),
            "model_file": path.name,
            "model_line": str(_line_of(lines, name)),
            "model_kind": "AUTOSAR APPLICATION-SW-COMPONENT-TYPE",
            "realizes": realizes,
            "provides": ports("P-PORT-PROTOTYPE", "PROVIDED-INTERFACE-TREF"),
            "requires": ports("R-PORT-PROTOTYPE", "REQUIRED-INTERFACE-TREF"),
        }
    return needs


def _natural(value: str) -> tuple:
    return tuple(int(t) if t.isdigit() else t for t in re.split(r"(\d+)", value))


def main() -> int:
    sysml = read_sysml(SYSML)
    arxml = read_arxml(ARXML)
    (MODELS / "sysml.json").write_text(envelope("BMS system model (SysML v2)", sysml), encoding="utf-8")
    (MODELS / "autosar.json").write_text(envelope("BMS software components (AUTOSAR)", arxml), encoding="utf-8")

    parts = sum(1 for n in sysml.values() if n["type"] == "sysml_part")
    sat = sum(len(n["satisfies"]) for n in sysml.values())
    swcs = [n for n in arxml.values() if n["type"] == "swc"]
    ifs = sum(1 for n in arxml.values() if n["type"] == "port_if")
    print(f"SysML v2  {SYSML.name}: {parts} part defs, {sat} satisfy links -> docs/models/sysml.json")
    print(
        f"AUTOSAR   {ARXML.name}: {len(swcs)} software components, {ifs} port interfaces, "
        f"{sum(len(n['realizes']) for n in swcs)} realizes links -> docs/models/autosar.json"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
