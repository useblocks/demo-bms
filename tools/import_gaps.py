#!/usr/bin/env python3
"""Import a `ubc agent gaps` JSON report into `gap` needs.

The structural gate is NOT re-run on every build. ``docs/reports/gaps/gaps.json`` is a
committed snapshot of one real ``ubc agent gaps`` run, and this script turns it
into needs so the gate's findings are part of the graph rather than an
untraceable file next to it — the same arrangement as the JUnit snapshot on the
other side of the V (see ``tools/import_test_results.py``).

Why put the gate's output back INTO the graph at all: because a gap is only
useful where the reader already is. A JSON file says
``REQ_CELL_BALANCING_WINDOW`` has no incoming ``satisfies``; a ``gap`` need says
it on the requirement's own page, in the level tables, in the per-stream
``needflow`` diagram, and in the ubTrace export — in red, next to the need it is
about.

The mapping is deterministic, not heuristic. One record of the report becomes
exactly one ``gap`` need, whose id is derived from the need the gap is attributed
to plus the gate that reported it, so re-importing an unchanged report rewrites
the same file byte for byte and a fixed gap disappears rather than lingering
under a fresh id.

A record naming a need that is in no source is a hard error, not a silent drop:
that means the snapshot is stale, and a stale gap would author a dangling
``gap_for`` link that fails the Sphinx build under ``-W``. "Source" is every way
a need reaches the graph — the directives under ``specs/``, the codelinks markers
under ``src/`` and ``tests/``, and the external JSON exports that
``[[needs.external_needs]]`` projects in, which is how the customer's ``sys_req``
layer arrives.

Usage::

    ubc agent gaps > docs/reports/gaps/gaps.json   # refresh the snapshot (exits 1 on gaps)
    python3 tools/import_gaps.py              # default paths -> docs/specs/_global/gaps.rst
    python3 tools/import_gaps.py --check      # fail if the output is stale
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import textwrap
import tomllib
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_REPORT = REPO_ROOT / "docs" / "reports" / "gaps" / "gaps.json"
DEFAULT_SPECS_DIR = REPO_ROOT / "docs" / "specs"
#: The two codelinks projects: the tree each scans, and the need type its marker
#: grammar defaults to. Mirrors `[codelinks.projects.*]` in docs/ubproject.toml,
#: where `type` is the LAST field with a default so no marker has to spell it.
DEFAULT_CODE_DIRS = ((REPO_ROOT / "src", "impl"), (REPO_ROOT / "tests", "test"))
DEFAULT_OUTPUT = REPO_ROOT / "docs" / "specs" / "_global" / "gaps.rst"
#: The ubc project config. Read for its `[[needs.external_needs]]` sources, which
#: name the only needs that exist in no file this script would otherwise open.
DEFAULT_UBPROJECT = REPO_ROOT / "docs" / "ubproject.toml"

#: Directive line and `:id:` field as they appear in the spec sources. Parsed
#: from source rather than from `needs.json` so the import never depends on a
#: build having already run — `needs.json` is gitignored and may not exist. Two
#: directive spellings: the RST `.. req::` and the MyST fence ```{req} used by
#: the Markdown-authored `specs/isolation-monitoring/` stream; the `:id:` line
#: is the same in both, indented in RST and at column 0 in Markdown.
RST_DIRECTIVE = re.compile(r"^\.\.\s+(?P<type>[a-z_]+)::")
MD_DIRECTIVE = re.compile(r"^\s*(?:`{3,}|:{3,})\{(?P<type>[a-z_]+)\}")
RST_ID = re.compile(r"^\s*:id:\s*(?P<id>[A-Z][A-Z0-9_]*)\s*$")

#: The one-line codelinks marker grammar shared by both `[codelinks.projects]`
#: blocks: `# @<title>, <ID>, [<PARENT_ID>, ...]`, optionally followed by an explicit
#: `, <type>`. The type is the grammar's LAST field and defaults per project (`impl`
#: under src/, `test` under tests/), so the markers leave it out; a marker that does
#: spell it wins over the default. `impl` and `test` needs exist only as these
#: markers, so a gap attributed to one resolves through here.
MARKER = re.compile(
    r"^\s*#\s*@(?P<title>[^,]+),\s*(?P<id>[A-Z][A-Z0-9_]*),\s*"
    r"\[(?P<links>[^\]]*)\](?:\s*,\s*(?P<type>[a-z_]+))?\s*$"
)

#: `category` -> the phrase that completes "<NEED_ID> — ...", and the id suffix
#: that keeps two gaps on the same need apart. `{link}` is substituted where the
#: gate names a link; the two trace categories are the only ones that do.
#:
#: The categories are the ones the 0.35 engine emits (`trace_forward`,
#: `trace_backward`, `orphan`, `status_disallowed`, `status_undeclared`,
#: `needs_clarification`, `code_trace`, `review`). `ubc agent` is alpha and says
#: so — its JSON shapes may still change — so an UNKNOWN category is rendered generically
#: rather than rejected: a gate finding must never be dropped because this table
#: has not caught up with the engine.
#:
#: The phrases carry NO inline markup on purpose. Each one is used twice — as the
#: directive's TITLE and inside its body — and a title is not a place for roles:
#: single backticks would resolve as the default role, and the title is also what
#: graphviz wraps into a node label on the needflow diagrams.
CATEGORIES: dict[str, tuple[str, str]] = {
    "trace_backward": ("nothing links back to it with {link}", "NO_{LINK}_BACK"),
    "trace_forward": ("it carries no {link} link upwards", "NO_{LINK}"),
    "orphan": ("it is an orphan, with no trace link in either direction", "ORPHAN"),
    "status_disallowed": ("its status is disallowed for release", "STATUS_DISALLOWED"),
    "status_undeclared": ("its status is not declared in the lifecycle", "STATUS_UNDECLARED"),
    "needs_clarification": ("it still carries a NEEDS CLARIFICATION marker", "NEEDS_CLARIFICATION"),
    "code_trace": ("it has no code trace", "CODE_TRACE"),
    # The substance gate, not a trace gate: it reports a need whose review verdict
    # under `.pharaoh/verdicts/` is missing, failing, or fingerprinted against an
    # earlier wording. The record still carries a `link` — the gate names ITSELF
    # there, "review", which is why `[needs.fields.gap_link]` admits a word that is
    # no link option.
    "review": ("its review verdict does not cover the need as it now reads", "REVIEW"),
}
FALLBACK = ("the {category} gate is not satisfied", "{CATEGORY}")

#: How the `have`/`need` counts are read aloud, where "links" is wrong. Only the
#: substance gate counts something other than links; everything else falls through
#: to the default.
SHORTFALLS: dict[str, str] = {
    "review": "It has **{shortfall}** of the current review verdicts that gate requires.",
}
DEFAULT_SHORTFALL = "It carries **{shortfall}** of the ``{link}`` links that gate requires."


@dataclass(frozen=True)
class Gap:
    """One record of the report, joined to the need it is attributed to."""

    need_id: str
    need_type: str
    category: str
    link: str
    have: int | None
    want: int | None
    gap_id: str
    phrase: str
    #: False when the engine reported a category this importer has no description
    #: for. The gap is still rendered — dropping a gate finding would be worse than
    #: describing it thinly — but the body says so instead of restating the phrase.
    known: bool

    @property
    def shortfall(self) -> str:
        """The counts as ONE text label, e.g. `0 of 1`.

        Deliberately not two numeric fields. Extra options are global in ubCode,
        so whatever shape this takes is also written as "" on the ~190 needs that
        are not gaps, and the `test_run_label` comment in ubproject.toml records
        what a type-detected empty field costs in the Elasticsearch index behind
        ubTrace. A string that can never be read as a number or a date is the
        cheap way to stay out of that failure mode.
        """
        if self.have is None or self.want is None:
            return ""
        return f"{self.have} of {self.want}"


def collect_need_types(
    specs_dir: Path, code_dirs: tuple[tuple[Path, str], ...]
) -> dict[str, str]:
    """Return `need id -> type` for every need authored in the sources.

    Every authoring form is read: the RST directives and the MyST fences under
    ``specs/``, and the one-line codelinks markers under ``src/`` and ``tests/``
    that materialise the ``impl`` and ``test`` needs. A gap can be attributed to
    any of them.
    """
    types: dict[str, str] = {}

    for source in sorted([*specs_dir.rglob("*.rst"), *specs_dir.rglob("*.md")]):
        current_type: str | None = None
        for line in source.read_text().splitlines():
            directive = RST_DIRECTIVE.match(line) or MD_DIRECTIVE.match(line)
            if directive is not None:
                current_type = directive.group("type")
                continue
            found = RST_ID.match(line)
            if found is not None and current_type is not None:
                types[found.group("id")] = current_type

    for code_dir, default_type in code_dirs:
        if not code_dir.is_dir():
            continue
        for source in sorted(code_dir.rglob("*.py")):
            for line in source.read_text().splitlines():
                marker = MARKER.match(line)
                if marker is not None:
                    types[marker.group("id")] = marker.group("type") or default_type

    return types


def collect_external_need_types(ubproject: Path) -> dict[str, str]:
    """Return `need id -> type` for every need projected in from an external export.

    The customer's ``sys_req`` layer is owned in their DOORS instance and reaches
    the graph through ``[[needs.external_needs]]`` in the ubc project config, not
    through a directive under ``specs/``, so a gap attributed to one resolves
    only here. The config is read for the export paths rather than the paths
    being hardcoded, so adding a second external source needs no change here.

    The export itself is read exactly as ``ubconnect`` writes it: a version map
    keyed by ``current_version``, with a flat ``needs`` map as the older, single-
    version fallback.
    """
    if not ubproject.is_file():
        # Not an error: `--specs-dir` may point at a tree with no project config
        # beside it, and a project with no external layer is the normal case.
        return {}

    config = tomllib.loads(ubproject.read_text())
    types: dict[str, str] = {}

    for source in config.get("needs", {}).get("external_needs", []) or []:
        json_path = source.get("json_path")
        if not json_path:
            # A `json_url` source is fetched during the build and cannot be read
            # here. Skip it silently; a gap naming one of its needs still fails
            # below, which is the honest outcome.
            continue
        export = Path(json_path)
        if not export.is_absolute():
            # `json_path` is relative to the config, which is `docs/`, not the repo root.
            export = ubproject.parent / export
        if not export.is_file():
            print(f"warning: external needs export not found: {_display(export)}", file=sys.stderr)
            continue
        document = json.loads(export.read_text())
        versions = document.get("versions") or {}
        version = document.get("current_version") or ""
        needs = (versions.get(version) or {}).get("needs") or document.get("needs") or {}
        for need_id, need in needs.items():
            types[str(need_id)] = str(need.get("type", "") or "")

    return types


def _gap_id(need_id: str, category: str, link: str, taken: set[str]) -> str:
    """Derive a stable, unique `GAP_` id for one gate finding.

    Stable so that re-importing an unchanged report is a no-op and a FIXED gap
    disappears instead of reappearing under a new id; unique because one need can
    hold several findings at once (a missing forward link and a missing backward
    link on different link types, say).
    """
    _, suffix_template = CATEGORIES.get(category, FALLBACK)
    suffix = suffix_template.format(LINK=link.upper(), CATEGORY=category.upper())
    candidate = f"GAP_{need_id}_{suffix}"
    # Defensive only: the (need, category, link) triple is already unique in every
    # report shape seen so far, but a duplicate id would fail the build far from
    # its cause, so disambiguate rather than emit one.
    disambiguated, n = candidate, 1
    while disambiguated in taken:
        n += 1
        disambiguated = f"{candidate}_{n}"
    taken.add(disambiguated)
    return disambiguated


def join(records: list[dict[str, object]], types: dict[str, str]) -> tuple[list[Gap], list[str]]:
    """Turn report records into `Gap`s, collecting the ones naming an absent need."""
    gaps: list[Gap] = []
    unmapped: list[str] = []
    taken: set[str] = set()

    ordered = sorted(
        records,
        key=lambda r: (str(r.get("id", "")), str(r.get("category", "")), str(r.get("link", ""))),
    )
    for record in ordered:
        need_id = str(record.get("id", ""))
        if need_id not in types:
            unmapped.append(need_id or "<record with no id>")
            continue
        category = str(record.get("category", "unknown"))
        link = str(record.get("link", "") or "")
        phrase_template, _ = CATEGORIES.get(category, FALLBACK)
        gaps.append(
            Gap(
                need_id=need_id,
                # The report carries the need's type itself; the sources are the
                # fallback, and agree with it in every case seen.
                need_type=str(record.get("type", "") or types[need_id]),
                category=category,
                link=link,
                have=record.get("have") if isinstance(record.get("have"), int) else None,
                want=record.get("need") if isinstance(record.get("need"), int) else None,
                gap_id=_gap_id(need_id, category, link, taken),
                phrase=phrase_template.format(link=link, category=category),
                known=category in CATEGORIES,
            )
        )
    return gaps, unmapped


def _display(path: Path) -> str:
    """Path as written into the generated page and the messages.

    Repo-relative when it is inside the repo — that is the committed default and
    the form a reader can copy into a command — and absolute otherwise, because
    `--report` accepts any path and `Path.relative_to` raises rather than falling
    back on one it cannot make relative.
    """
    try:
        return str(path.resolve().relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def _body(paragraph: str) -> list[str]:
    """One directive-body paragraph: wrapped to 88 columns, indented, blank line after."""
    return [f"   {line}" for line in textwrap.wrap(paragraph, 85)] + [""]


def render(gaps: list[Gap], by_category: dict[str, int], report: Path) -> str:
    """Render the generated RST. One `gap` directive per gate finding."""
    rel_report = _display(report)
    title = "Workflow Gaps"
    lines = [
        title,
        "=" * (len(title.encode()) + 2),
        "",
        ".. warning::",
        "",
        "   **Generated file — do not edit by hand.** Written by",
        "   ``tools/import_gaps.py`` from ``%s``." % rel_report,
        "   Re-generate it with::",
        "",
        "      ubc agent gaps > %s" % rel_report,
        "      python3 tools/import_gaps.py",
        "",
        "   The report is a **committed snapshot**: the structural gate is not re-run",
        "   on every build, so these needs record what ``ubc agent gaps`` found when it",
        "   last ran, not what it would find now.",
        "",
    ]

    # NOTE the deliberate omission of the report's `summary.total_needs`. It counts
    # the gap needs this script wrote on the PREVIOUS run, so quoting it would make
    # the generated page depend on its own output and drift by one on every second
    # import. Only the gap list and its per-category tally are self-consistent, so
    # only those are rendered.
    if gaps:
        tally = ", ".join(f"{n} {name}" for name, n in sorted(by_category.items()))
        lines += [
            f"{len(gaps)} open gap(s) — {tally}.",
            "",
            "Each need below carries ``gap_for`` down to the need the gate attributed it",
            "to, so the gap shows up as a red node beside that need in every ``needflow``",
            "diagram and as a non-empty ``gaps`` cell in every level table on",
            ":doc:`/traceability`. Ask the engine what to do about one with",
            "``ubc agent next --id <NEED_ID>``.",
            "",
        ]
    else:
        lines += [
            "**No gaps.** The last ``ubc agent gaps`` run found the graph structurally",
            "complete, so this page holds no needs at all — which is exactly what a clean",
            "gate should look like from the outside.",
            "",
        ]

    for gap in gaps:
        lines += [
            f".. gap:: {gap.need_id} — {gap.phrase}",
            f"   :id: {gap.gap_id}",
            f"   :gap_for: {gap.need_id}",
            f"   :gap_category: {gap.category}",
        ]
        # A record that carries no link (an `orphan`, say) writes no `:gap_link:` at
        # all rather than an empty one: extra options default to "" anyway, and a
        # field line with nothing after the colon is noise on the rendered page.
        if gap.link:
            lines.append(f"   :gap_link: {gap.link}")
        if gap.shortfall:
            lines.append(f"   :gap_shortfall: {gap.shortfall}")
        lines += [
            f"   :gap_need_id: {gap.need_id}",
            f"   :gap_need_type: {gap.need_type}",
            # sphinx-needs CSS class, NOT the graphviz shape (that is `style` on the
            # type in ubproject.toml). It paints the need's own rendered block red.
            "   :style: red_bar",
            "",
        ]
        if gap.known:
            lines += _body(
                f"``{gap.need_id}`` ({gap.need_type}) fails the ``{gap.category}`` "
                f"gate: {gap.phrase}."
            )
        else:
            lines += _body(
                f"``{gap.need_id}`` ({gap.need_type}) fails the ``{gap.category}`` gate. "
                "This importer carries no description for that gate — it postdates the "
                "engine version ``tools/import_gaps.py`` was written against. Read the "
                "raw record in the snapshot for the detail."
            )
        if gap.shortfall:
            lines += _body(
                SHORTFALLS.get(gap.category, DEFAULT_SHORTFALL).format(
                    shortfall=gap.shortfall, link=gap.link
                )
            )
        lines += _body(
            f"Resolve it with ``ubc agent next --id {gap.need_id}``, which names the stage "
            "that owes the missing artefact, then refresh this page from a new "
            "``ubc agent gaps`` snapshot."
        )

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--specs-dir", type=Path, default=DEFAULT_SPECS_DIR)
    parser.add_argument(
        "--code-dir",
        action="append",
        dest="code_dirs",
        metavar="TYPE=PATH",
        help="a codelinks tree and the need type its markers default to, e.g. impl=src",
    )
    parser.add_argument(
        "--ubproject",
        type=Path,
        default=DEFAULT_UBPROJECT,
        help="the ubc project config, read for its `[[needs.external_needs]]` exports",
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--check",
        action="store_true",
        help="do not write; exit non-zero if the output is missing or stale",
    )
    args = parser.parse_args()

    if not args.report.is_file():
        print(f"error: gap report not found: {args.report}", file=sys.stderr)
        print("hint: ubc agent gaps > docs/reports/gaps/gaps.json", file=sys.stderr)
        return 2

    try:
        report = json.loads(args.report.read_text())
    except json.JSONDecodeError as exc:
        print(f"error: {args.report} is not valid JSON: {exc}", file=sys.stderr)
        return 2
    if not isinstance(report, dict) or not isinstance(report.get("gaps"), list):
        print(
            f"error: {args.report} has no `gaps` list — is it the output of `ubc agent gaps`?",
            file=sys.stderr,
        )
        return 2

    if args.code_dirs:
        code_dirs = tuple(
            (Path(path), need_type) for need_type, _, path in (spec.partition("=") for spec in args.code_dirs)
        )
    else:
        code_dirs = DEFAULT_CODE_DIRS
    # External first: a need authored in this repository is the source of truth
    # for its own type, so the authored sources overwrite rather than the reverse.
    types = collect_external_need_types(args.ubproject)
    types.update(collect_need_types(args.specs_dir, code_dirs))
    gaps, unmapped = join(report["gaps"], types)

    if unmapped:
        print(
            f"error: {len(unmapped)} reported gap(s) name a need that is not in the sources:",
            file=sys.stderr,
        )
        for need_id in unmapped:
            print(f"  {need_id}", file=sys.stderr)
        print(
            f"hint: either the snapshot is stale — re-run "
            f"`ubc agent gaps -p docs > {_display(args.report)}` and retry — or the need "
            f"is an external one and {_display(args.ubproject)} does not project its "
            "export in with `[[needs.external_needs]]`.",
            file=sys.stderr,
        )
        return 1

    rendered = render(
        gaps,
        {str(k): int(v) for k, v in (report.get("by_category") or {}).items()},
        args.report,
    )

    if args.check:
        current = args.output.read_text() if args.output.is_file() else ""
        if current != rendered:
            print(f"error: {args.output} is stale; re-run without --check", file=sys.stderr)
            return 1
        print(f"{args.output} is up to date ({len(gaps)} gaps)")
        return 0

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(rendered)
    print(f"wrote {args.output} — {len(gaps)} gap(s) from {_display(args.report)}")
    for gap in gaps:
        print(f"  {gap.gap_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
