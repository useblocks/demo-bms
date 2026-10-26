"""Pytest root configuration.

Its presence puts the repository root on ``sys.path``, so the test modules can
import the production packages as ``src.<stream>.<module>``.

It also writes the two JUnit properties that ``[test_reports]`` in
``docs/ubproject.toml`` reads: ``results_for`` on every test case (the ``test``
need its codelinks marker declares, which becomes the case's link) and
``test_run_label`` on the suite.
"""

import re
from datetime import datetime
from functools import cache
from pathlib import Path

import pytest

#: The two marker forms of the `tests` codelinks project: the one-line
#: `# @<title>, <TEST_ID>, [...]` and the `:id:` line of a `# @need` block.
ONELINE_ID = re.compile(r"^\s*#\s*@[^,]+,\s*(?P<id>TEST_[A-Z][A-Z0-9_]*)\s*,")
BLOCK_ID = re.compile(r"^\s*#\s*:id:\s*(?P<id>TEST_[A-Z][A-Z0-9_]*)\s*$")
DEF_LINE = re.compile(r"^\s*def\s+(?P<name>test_\w+)\s*\(")


@cache
def _test_ids(path: Path) -> dict[str, str]:
    """Map each test function in a module to the id of the marker above it.

    A marker binds to the first ``def test_*`` beneath it, as codelinks binds it.
    """
    ids: dict[str, str] = {}
    pending: str | None = None
    for line in path.read_text().splitlines():
        if marker := ONELINE_ID.match(line) or BLOCK_ID.match(line):
            pending = marker.group("id")
        elif (definition := DEF_LINE.match(line)) and pending:
            ids[definition.group("name")] = pending
            pending = None
    return ids


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    unmapped = []
    for item in items:
        need_id = _test_ids(item.path).get(getattr(item, "originalname", item.name))
        if need_id:
            item.user_properties.append(("results_for", need_id))
        else:
            unmapped.append(item.nodeid)
    # Only a recorded report needs the link: an outcome that names no test is evidence for nothing.
    if unmapped and config.option.xmlpath:
        raise pytest.UsageError("no `test` marker above: " + ", ".join(unmapped))


@pytest.fixture(scope="session", autouse=True)
def _test_run_label(record_testsuite_property) -> None:
    # Date SPACE time: an ISO `T` would make ubTrace's Elasticsearch map the field as a date.
    record_testsuite_property("test_run_label", datetime.now().astimezone().isoformat(" ", "seconds"))
