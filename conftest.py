"""Pytest root marker, and the bridge from a JUnit report back to the `test` needs.

Its presence puts the repository root on ``sys.path``, so the test modules can
import the production packages as ``src.<stream>.<module>``.

It also stamps every test case with the id of the ``test`` need it runs. Each test
function carries a one-line codelinks marker directly above it::

    # @<title>, <TEST_ID>, [<SWREQ_ID>]
    def test_something() -> None:

and the hook below copies ``<TEST_ID>`` into the case's ``results_for`` user
property, which pytest writes into the JUnit XML as
``<property name="results_for" value="TEST_..."/>``. ``[test_reports]
property_link_types`` in docs/ubproject.toml turns that property into the
``results_for`` link of the imported ``test_result`` need, so the report links
itself to the graph with nothing generated in between. A test with no marker gets
no property, and the ``trace-test_result-results_for`` rule in docs/schemas.json
reports its result as unattributed.
"""

from __future__ import annotations

import inspect
import re

import pytest

#: The marker grammar declared in `[codelinks.projects.tests]`; only the id is read.
MARKER = re.compile(r"^\s*#\s*@[^,]+,\s*(?P<id>TEST_[A-Z][A-Z0-9_]*),")


def _marker_id(function: object) -> str | None:
    """Return the `test` need id of the marker directly above *function*, if any.

    Blank lines between the marker and the function (or its first decorator) are
    skipped; any other line ends the search, so a marker never binds to a test it
    is not written above.
    """
    try:
        lines = inspect.findsource(function)[0]
        start = inspect.getsourcelines(function)[1] - 1  # 0-based first line
    except (OSError, TypeError):
        return None
    for line in reversed(lines[:start]):
        if not line.strip():
            continue
        match = MARKER.match(line)
        return match.group("id") if match else None
    return None


def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    for item in items:
        need_id = _marker_id(getattr(item, "function", None))
        if need_id is not None:
            item.user_properties.append(("results_for", need_id))
