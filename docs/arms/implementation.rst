Implementation Arm — Source Trace
=====================================

Every ``impl`` need of this project is authored as a one-line codelinks marker in
the production source under ``src/``. This directive is what materialises those
markers into real needs; without it the markers parse but no need is created and
the implementation gate never closes.

.. src-trace::
   :project: code
