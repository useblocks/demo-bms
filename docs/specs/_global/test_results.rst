Test Results
============

The recorded outcomes of the last committed test run, read straight from the
JUnit report ``reports/junit/testresults.xml``. The directive below turns the
report into one need per suite and one ``test_result`` need per test case; nothing
is generated, so a new report is all it takes to update this page::

   uv run pytest -q --junitxml=docs/reports/junit/testresults.xml

The report is a **committed snapshot**: the suite is not re-run on every build, so
these needs record what happened in that run, not what would happen now.

Every ``test_result`` carries ``results_for`` up to the ``test`` need whose
execution it records, taken from the ``results_for`` property the root
``conftest.py`` writes into each test case. So a query can walk requirement →
software requirement → test → recorded outcome without leaving the graph.

.. test-file:: BMS unit test run
   :id: TRES_RUN
   :file: reports/junit/testresults.xml
   :auto_suites:
   :auto_cases:
