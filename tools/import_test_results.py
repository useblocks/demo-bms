#!/usr/bin/env python3
"""Import a JUnit XML test report into `test_result` needs.

The test suite is NOT re-run on every build. ``reports/junit/testresults.xml`` is
a committed snapshot of one real pytest run, and this script turns it into needs
so the recorded outcomes are part of the graph rather than an untraceable file
next to it.

The mapping is deterministic, not heuristic. Every test case in this project
carries a one-line codelinks marker directly above its function::

    # @<title>, <TEST_ID>, test, [<SWREQ_ID>]
    def test_something() -> None:

so the pair (test module, function name) identifies exactly one ``test`` need.
This script rebuilds that pairing from the test sources and joins it against the
report's ``classname`` / ``name`` attributes. A test case the join cannot resolve
is reported as an error rather than silently dropped: an unmapped outcome is
evidence pointing at nothing.

Usage::

    python3 tools/import_test_results.py            # default paths
    python3 tools/import_test_results.py --check     # fail if the output is stale
"""

from __future__ import annotations

import argparse
import re
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_REPORT = REPO_ROOT / "reports" / "junit" / "testresults.xml"
DEFAULT_TESTS_DIR = REPO_ROOT / "tests"
DEFAULT_SPECS_DIR = REPO_ROOT / "specs"
DEFAULT_OUTPUT = REPO_ROOT / "specs" / "_global" / "test_results.rst"

#: Directive id line and the two upward link fields the roll-up walks, as they
#: appear in the spec sources. Parsed from source rather than from `needs.json` so
#: the import never depends on a build having already run. Two directive
#: spellings: the RST `.. swreq::` and the MyST fence ```{swreq} used by the
#: Markdown-authored `specs/isolation-monitoring/` stream; the field lines are
#: the same in both, indented in RST and at column 0 in Markdown.
RST_DIRECTIVE = re.compile(r"^\.\.\s+(?P<type>[a-z_]+)::")
MD_DIRECTIVE = re.compile(r"^\s*(?:`{3,}|:{3,})\{(?P<type>[a-z_]+)\}")
RST_FIELD = re.compile(r"^\s*:(?P<name>id|refines|satisfies):\s*(?P<value>.+?)\s*$")

#: The one-line codelinks marker grammar declared in `[codelinks.projects.tests]`.
MARKER = re.compile(
    r"^\s*#\s*@(?P<title>[^,]+),\s*(?P<id>TEST_[A-Z][A-Z0-9_]*),\s*test\s*,\s*"
    r"\[(?P<verifies>[^\]]*)\]\s*$"
)
DEF_LINE = re.compile(r"^\s*def\s+(?P<name>test_[A-Za-z0-9_]+)\s*\(")

#: JUnit child element -> the outcome word recorded on the need. JUnit spells the
#: failure element `failure`; the field says `failed`, which is what a reader
#: filtering `outcome != "passed"` expects to see.
OUTCOME_BY_TAG = {"failure": "failed", "error": "error", "skipped": "skipped"}


@dataclass(frozen=True)
class TestNeed:
    """One `test` need, as recovered from its marker in the test source."""

    need_id: str
    title: str
    verifies: str
    module: str
    function: str
    path: str


@dataclass(frozen=True)
class Outcome:
    """One `<testcase>` element of the report, joined to its `test` need."""

    need: TestNeed
    outcome: str
    runtime_s: str
    message: str
    chain_reqs: tuple[str, ...] = ()


def collect_spec_links(specs_dir: Path) -> dict[str, list[str]]:
    """Read `:refines:` / `:satisfies:` off the spec directives.

    Returns one flat ``need id -> parent ids`` map. Both fields are upward links
    and no id is ever both a swreq and an arch, so one map is enough to walk
    ``swreq -> arch -> req`` without tracking which rung a hop is on.
    """
    parents: dict[str, list[str]] = {}
    for source in sorted([*specs_dir.rglob("*.rst"), *specs_dir.rglob("*.md")]):
        current_id: str | None = None
        pending: list[str] = []
        for line in source.read_text().splitlines():
            if RST_DIRECTIVE.match(line) or MD_DIRECTIVE.match(line):
                current_id, pending = None, []
                continue
            field = RST_FIELD.match(line)
            if field is None:
                continue
            name, value = field.group("name"), field.group("value")
            if name == "id":
                current_id = value
                if pending:
                    parents.setdefault(current_id, []).extend(pending)
                    pending = []
            else:
                targets = [t.strip() for t in value.split(",") if t.strip()]
                if current_id is None:
                    pending.extend(targets)  # link listed above the :id: line
                else:
                    parents.setdefault(current_id, []).extend(targets)
    return parents


def resolve_chain_reqs(swreq_ids: list[str], parents: dict[str, list[str]]) -> tuple[str, ...]:
    """Walk `swreq -> arch -> req` and return the requirement ids reached.

    Only ids with the `REQ_` prefix are returned: the walk is bounded by the
    project's id convention rather than by a hop count, so an extra rung inserted
    between arch and req would still resolve.
    """
    reached: set[str] = set()
    seen: set[str] = set()
    frontier = list(swreq_ids)
    while frontier:
        current = frontier.pop()
        if current in seen:
            continue
        seen.add(current)
        if current.startswith("REQ_"):
            reached.add(current)
            continue
        frontier.extend(parents.get(current, []))
    return tuple(sorted(reached))


def collect_test_needs(tests_dir: Path) -> dict[tuple[str, str], TestNeed]:
    """Rebuild the (module, function) -> `test` need map from the test sources.

    A marker binds to the FIRST ``def test_*`` line beneath it, which is exactly
    the rule the codelinks parser applies, so the two never disagree.
    """
    found: dict[tuple[str, str], TestNeed] = {}
    for source in sorted(tests_dir.rglob("test_*.py")):
        rel = source.relative_to(REPO_ROOT)
        module = ".".join(rel.with_suffix("").parts)
        pending: re.Match[str] | None = None
        for line in source.read_text().splitlines():
            marker = MARKER.match(line)
            if marker is not None:
                pending = marker
                continue
            definition = DEF_LINE.match(line)
            if definition is not None and pending is not None:
                function = definition.group("name")
                found[(module, function)] = TestNeed(
                    need_id=pending.group("id"),
                    title=pending.group("title").strip(),
                    verifies=pending.group("verifies").strip(),
                    module=module,
                    function=function,
                    path=str(rel),
                )
                pending = None
    return found


def read_report(report: Path) -> tuple[dict[str, str], list[ET.Element]]:
    """Return the suite attributes and every `<testcase>` element of the report."""
    root = ET.parse(report).getroot()
    suite = root if root.tag == "testsuite" else root.find("testsuite")
    if suite is None:
        raise SystemExit(f"{report}: no <testsuite> element found")
    return dict(suite.attrib), list(suite.iter("testcase"))


def classify(case: ET.Element) -> tuple[str, str]:
    """Reduce a `<testcase>` to one outcome word plus the reported message.

    A case with none of the failure/error/skipped children passed; that absence
    is how JUnit encodes success, so it is read as `passed` rather than guessed.
    """
    for tag, outcome in OUTCOME_BY_TAG.items():
        child = case.find(tag)
        if child is not None:
            message = (child.get("message") or child.text or "").strip()
            return outcome, " ".join(message.split())[:300]
    return "passed", ""


def join(
    cases: list[ET.Element],
    needs: dict[tuple[str, str], TestNeed],
    parents: dict[str, list[str]],
) -> tuple[list[Outcome], list[str]]:
    """Join report cases onto `test` needs, collecting the unresolvable ones."""
    joined: list[Outcome] = []
    unmapped: list[str] = []
    for case in cases:
        key = (case.get("classname", ""), case.get("name", ""))
        need = needs.get(key)
        if need is None:
            unmapped.append(f"{key[0]}::{key[1]}")
            continue
        outcome, message = classify(case)
        swreq_ids = [t.strip() for t in need.verifies.split(",") if t.strip()]
        joined.append(
            Outcome(
                need=need,
                outcome=outcome,
                runtime_s=case.get("time", "0.000"),
                message=message,
                chain_reqs=resolve_chain_reqs(swreq_ids, parents),
            )
        )
    return joined, unmapped


def _run_label(timestamp: str) -> str:
    """Format the run identifier so it is NOT a parseable ISO-8601 datetime.

    `test_run_label` is stamped on every `test_result`, and because extra options
    are global it is also written as "" on every OTHER need. ubTrace indexes needs
    into Elasticsearch with dynamic mapping and date detection on, so a value
    like `2026-08-13T15:35:36.742977+02:00` types the field as `date` for the
    whole index — and then every need carrying "" is rejected with "cannot
    parse empty datetime", silently dropping it from the index and from every
    Elasticsearch-backed view.

    Swapping the ISO `T` for a space is enough: neither
    `strict_date_optional_time` nor `yyyy/MM/dd HH:mm:ss Z` matches, so the
    field maps as text and the empty values are accepted. Verified against
    Elasticsearch 9.3: the `T` form maps to `date` and rejects "" with HTTP
    400; this form maps to `text` and accepts it.

    Do NOT "restore" the ISO format here. An Elasticsearch mapping cannot be
    changed in place, so re-poisoning the field would require deleting the
    project index on the server to recover.
    """
    if timestamp == "unknown":
        return timestamp
    # 2026-08-13T15:35:36.742977+02:00 -> 2026-08-13 15:35:36 +02:00
    date_part, _, time_part = timestamp.partition("T")
    if not time_part:
        return timestamp
    clock, sep, offset = time_part.partition("+")
    clock = clock.split(".")[0]
    if sep:
        return f"{date_part} {clock} +{offset}"
    return f"{date_part} {clock}"


def render(suite: dict[str, str], joined: list[Outcome], report: Path) -> str:
    """Render the generated RST. One `test_result` directive per joined case."""
    run_id = _run_label(suite.get("timestamp", "unknown"))
    rel_report = report.relative_to(REPO_ROOT)
    counts: dict[str, int] = {}
    for item in joined:
        counts[item.outcome] = counts.get(item.outcome, 0) + 1
    tally = ", ".join(f"{n} {name}" for name, n in sorted(counts.items()))

    title = "Test Results"
    lines = [
        title,
        "=" * (len(title.encode()) + 2),
        "",
        ".. warning::",
        "",
        "   **Generated file — do not edit by hand.** Written by",
        "   ``tools/import_test_results.py`` from ``%s``." % rel_report,
        "   Re-generate it with::",
        "",
        "      python3 -m pytest -q --junitxml=%s" % rel_report,
        "      python3 tools/import_test_results.py",
        "",
        "   The report is a **committed snapshot**: the suite is not re-run on every",
        "   build, so these needs record what happened in the run named below, not",
        "   what would happen now.",
        "",
        f"Run ``{run_id}`` — {suite.get('tests', '?')} test cases, {tally}, "
        f"{suite.get('time', '?')} s total.",
        "",
        f"Every need below carries ``results_for`` up to the ``test`` need whose "
        f"execution it records, so a query can walk requirement → software "
        f"requirement → test → recorded outcome without leaving the graph.",
        "",
    ]

    for item in sorted(joined, key=lambda o: o.need.need_id):
        need = item.need
        result_id = "TRES_" + need.need_id[len("TEST_") :]
        lines += [
            f".. test_result:: {need.title} — {item.outcome}",
            f"   :id: {result_id}",
            f"   :results_for: {need.need_id}",
            f"   :outcome: {item.outcome}",
            f"   :runtime_s: {item.runtime_s}",
            f"   :test_run_label: {run_id}",
            f"   :chain_reqs: {', '.join(item.chain_reqs)}",
            "",
            f"   ``{need.path}::{need.function}`` recorded ``{item.outcome}`` in "
            f"{item.runtime_s} s.",
            "",
        ]
        if item.message:
            lines += [f"   Reported message: {item.message}", ""]

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--tests-dir", type=Path, default=DEFAULT_TESTS_DIR)
    parser.add_argument("--specs-dir", type=Path, default=DEFAULT_SPECS_DIR)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--check",
        action="store_true",
        help="do not write; exit non-zero if the output is missing or stale",
    )
    args = parser.parse_args()

    if not args.report.is_file():
        print(f"error: report not found: {args.report}", file=sys.stderr)
        return 2

    needs = collect_test_needs(args.tests_dir)
    parents = collect_spec_links(args.specs_dir)
    suite, cases = read_report(args.report)
    joined, unmapped = join(cases, needs, parents)

    if unmapped:
        print(
            f"error: {len(unmapped)} reported test case(s) map to no `test` need:",
            file=sys.stderr,
        )
        for name in unmapped:
            print(f"  {name}", file=sys.stderr)
        print(
            "hint: every test function needs a one-line marker above it.",
            file=sys.stderr,
        )
        return 1

    rendered = render(suite, joined, args.report)

    if args.check:
        current = args.output.read_text() if args.output.is_file() else ""
        if current != rendered:
            print(f"error: {args.output} is stale; re-run without --check", file=sys.stderr)
            return 1
        print(f"{args.output} is up to date ({len(joined)} results)")
        return 0

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(rendered)
    unreported = sorted(
        n.need_id for k, n in needs.items() if k not in {(o.need.module, o.need.function) for o in joined}
    )
    print(f"wrote {args.output} — {len(joined)} results from run {suite.get('timestamp')}")
    if unreported:
        print(f"note: {len(unreported)} `test` need(s) have no recorded outcome:")
        for need_id in unreported:
            print(f"  {need_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
