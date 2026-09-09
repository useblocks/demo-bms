#!/usr/bin/env python3
"""Render the graph gates' results as a GitHub Actions job summary.

The `graph-gates` job in `.github/workflows/ubtrace.yml` does not block the
publish (see the comment at the top of that file), so its whole value is what a
reader can see afterwards. A red X on a commit says *something* is off; this
turns the run page into the actual answer — which gate failed, which needs are
implicated, and how far the trace matrix is from closed.

Markdown on stdout, meant to be redirected into ``$GITHUB_STEP_SUMMARY``.

NOTHING HERE MAY RAISE. A summary step runs with `if: always()`, precisely so it
still reports when a gate has failed — and a gate failing is exactly when an
input file is missing, truncated or not the shape this script expects. A summary
that crashes would replace a useful report with a second, unrelated failure, so
every input is read defensively and a section that cannot be rendered says so
instead of exploding. The gates themselves are what fail the job; this script
only ever describes them.

Usage::

    python3 tools/gate_summary.py \\
        --ubc-version 0.34.0 \\
        --result "Sources parse=success" \\
        --result "Gap snapshot current=failure" \\
        --gaps "$RUNNER_TEMP/gaps.json" \\
        --trace "$RUNNER_TEMP/trace.json" \\
        --verdicts "$RUNNER_TEMP/verdicts.json" >> "$GITHUB_STEP_SUMMARY"

Every ``--result`` is a ``<label>=<outcome>`` pair, the outcome being a step's
``outcome`` value from the workflow (``success`` / ``failure`` / ``skipped`` /
``cancelled``). Every file argument is optional and may point at something that
does not exist.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

#: GitHub renders these inline, and each is paired with a word in the table so the
#: summary still reads correctly to a screen reader and in a plain-text copy.
GLYPH = {
    "success": "✅",
    "failure": "❌",
    "skipped": "⏭️",
    "cancelled": "⏹️",
}


def load(path: Path | None) -> Any:
    """Read one JSON input, or return None for anything unreadable.

    Deliberately total: a missing file, an empty file, a truncated write from a
    killed process and a JSON document of the wrong shape all collapse to the same
    "no data" answer, which the caller renders as a note.
    """
    if path is None or not path.is_file():
        return None
    try:
        return json.loads(path.read_text())
    except (json.JSONDecodeError, OSError, UnicodeDecodeError):
        return None


def esc(value: object) -> str:
    """Escape a value for a markdown table cell.

    Only the pipe matters: it would otherwise open a new column. Need ids and link
    names cannot contain one today, but this text comes from a tool's JSON output,
    not from this repository, so it is not this script's place to assume.
    """
    return str(value).replace("|", "\\|")


def gates_section(results: list[tuple[str, str]]) -> list[str]:
    """The headline table: one row per blocking gate, worst news first to read."""
    if not results:
        return []
    lines = ["| Gate | Result |", "|---|---|"]
    for label, outcome in results:
        glyph = GLYPH.get(outcome, "❔")
        lines.append(f"| {esc(label)} | {glyph} {esc(outcome)} |")
    return lines + [""]


def gaps_section(data: Any) -> list[str]:
    """The structural gaps, as the gate reported them."""
    if not isinstance(data, dict) or not isinstance(data.get("gaps"), list):
        return ["> Gap report unavailable — the snapshot gate did not produce one.", ""]

    gaps = data["gaps"]
    if not gaps:
        return ["**No structural gaps.** Every declared trace obligation is met.", ""]

    lines = [
        f"**{len(gaps)} open gap(s).**",
        "",
        "| Need | Type | Gate | Link | Present |",
        "|---|---|---|---|---|",
    ]
    for gap in gaps:
        if not isinstance(gap, dict):
            continue
        have, want = gap.get("have"), gap.get("need")
        present = f"{have} of {want}" if isinstance(have, int) and isinstance(want, int) else ""
        lines.append(
            f"| `{esc(gap.get('id', '?'))}` | {esc(gap.get('type', ''))} "
            f"| {esc(gap.get('category', ''))} | `{esc(gap.get('link', ''))}` | {present} |"
        )
    return lines + [""]


def trace_section(data: Any) -> list[str]:
    """The bidirectional trace matrix, one row per declared edge.

    The per-direction gap ids are listed rather than just counted: on a demo graph
    with one hole, naming it is the whole point, and on a broken one it is the
    shortest path from "the matrix is red" to "this need is why".
    """
    if not isinstance(data, dict) or not isinstance(data.get("edges"), list):
        return ["> Trace matrix unavailable.", ""]

    lines = [
        "| Edge | Forward | Backward | Uncovered |",
        "|---|---|---|---|",
    ]
    for edge in data["edges"]:
        if not isinstance(edge, dict):
            continue
        fwd, bwd = edge.get("forward") or {}, edge.get("backward") or {}
        missing = [*(fwd.get("gaps") or []), *(bwd.get("gaps") or [])]
        mark = "" if edge.get("ok") else "❌ "
        lines.append(
            f"| {mark}`{esc(edge.get('edge', '?'))}` "
            f"| {esc(fwd.get('covered', '?'))} / {esc(fwd.get('total', '?'))} "
            f"| {esc(bwd.get('covered', '?'))} / {esc(bwd.get('total', '?'))} "
            f"| {', '.join(f'`{esc(m)}`' for m in missing)} |"
        )
    return lines + [""]


def verdicts_section(data: Any) -> list[str]:
    """The AI-review substance gate, as a one-line verdict plus any problem ids.

    `malformed` is a COUNT in the engine's output while its siblings are LISTS, so
    both shapes are handled rather than assumed.
    """
    if not isinstance(data, dict):
        return ["> Verdict check unavailable.", ""]

    categories = ["missing", "failing", "malformed", "outdated", "unverifiable", "stale"]
    problems: list[str] = []
    for name in categories:
        value = data.get(name)
        count = len(value) if isinstance(value, list) else (value if isinstance(value, int) else 0)
        if count:
            ids = ", ".join(f"`{esc(v)}`" for v in value) if isinstance(value, list) else ""
            problems.append(f"- **{name}**: {count}{f' — {ids}' if ids else ''}")

    if not problems:
        return ["**Every review verdict is fresh and passing.**", ""]
    return [f"{'✅' if data.get('ok') else '❌'} substance gate", "", *problems, ""]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ubc-version", default="")
    parser.add_argument(
        "--result",
        action="append",
        default=[],
        metavar="LABEL=OUTCOME",
        help="a gate step's label and its workflow `outcome`; repeatable",
    )
    parser.add_argument("--gaps", type=Path)
    parser.add_argument("--trace", type=Path)
    parser.add_argument("--verdicts", type=Path)
    args = parser.parse_args()

    results: list[tuple[str, str]] = []
    for item in args.result:
        label, _, outcome = item.partition("=")
        results.append((label.strip(), outcome.strip() or "unknown"))

    heading = "Graph gates"
    if args.ubc_version:
        heading += f" — ubc {args.ubc_version}"

    failed = [label for label, outcome in results if outcome == "failure"]
    if not results:
        # No `--result` reached us at all. Saying "all gates passed" here would be a
        # green light nobody earned, so report the absence instead.
        verdict = "❔ **No gate results were reported.** The sections below, if any, are all there is."
    elif failed:
        # `publish` declares `needs: graph-gates`, so a failed gate SKIPS the publish
        # rather than shipping a stale artefact. If that dependency is ever dropped,
        # this sentence is the thing that has to change with it.
        verdict = (
            f"❌ **{len(failed)} gate(s) failed.** The publish job is skipped, so "
            "ubTrace still holds the artefact from the last green run."
        )
    else:
        verdict = "✅ **All gates passed.** The committed snapshots match the graph."

    lines = [
        f"## {heading}",
        "",
        verdict,
        "",
        *gates_section(results),
        "### Structural gaps",
        "",
        *gaps_section(load(args.gaps)),
        "### Trace coverage",
        "",
        *trace_section(load(args.trace)),
        "### Review verdicts",
        "",
        *verdicts_section(load(args.verdicts)),
    ]
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
