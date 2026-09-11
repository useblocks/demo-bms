Verification Arm — Source Trace
===================================

Every ``test`` need of this project is authored as a one-line codelinks marker in
the test source under ``tests/``. This directive is what materialises those
markers into real needs; without it the markers parse but no need is created and
the verification gate never closes.

.. src-trace::
   :project: tests
