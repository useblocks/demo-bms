Test run
========

The recorded outcomes of one real pytest run, read straight from the committed
JUnit report ``reports/junit/testresults.xml``. The suite is not re-run on every
build, so these are the outcomes of the run named on the suite below, not of
this build.

Each test case links ``results_for`` to the ``test`` need whose run it records:
the root ``conftest.py`` writes that id into the report from the marker above
the test function.

.. test-results:: reports/junit/testresults.xml

.. test-file:: Committed pytest run
   :file: reports/junit/testresults.xml
   :id: TF_RUN
   :auto_suites:
   :auto_cases:
