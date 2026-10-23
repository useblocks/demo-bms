Test run, read from the JUnit report
====================================

This page reads the same committed pytest run the importer reads,
``reports/junit/testresults.xml``, with a ``test-file`` directive: one need for
the file, one for its suite and one per test case, beside the ``test_result``
needs on :doc:`test_results`. Replacing the importer with it is the next commit.

.. test-file:: Committed pytest run
   :file: reports/junit/testresults.xml
   :id: TF_RUN
   :auto_suites:
   :auto_cases:
