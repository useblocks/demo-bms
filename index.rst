BMS — Battery Management System
===============================

Everything-as-code across a minimized V-model: four streams, each decomposed
from user stories down to software requirements, with the implementation and
verification arms hanging off the software requirements as real needs
materialised from one-line markers in the source.

This page is the toctree for the Sphinx / ubTrace export only — ``ubc`` indexes
the same ``specs/**`` sources directly and needs no entry point. The stages are
listed in V-model order per stream, so the export reads top-down the way the
project was authored.

.. toctree::
   :maxdepth: 1
   :caption: The graph

   traceability

.. toctree::
   :maxdepth: 2
   :caption: Cell protection

   specs/cell-protection/user_stories
   specs/cell-protection/requirements
   specs/cell-protection/architecture
   specs/cell-protection/software_requirements

.. toctree::
   :maxdepth: 2
   :caption: State estimation

   specs/state-estimation/user_stories
   specs/state-estimation/requirements
   specs/state-estimation/architecture
   specs/state-estimation/software_requirements

.. toctree::
   :maxdepth: 2
   :caption: Thermal management

   specs/thermal-management/user_stories
   specs/thermal-management/requirements
   specs/thermal-management/architecture
   specs/thermal-management/software_requirements

.. toctree::
   :maxdepth: 2
   :caption: Cell balancing

   specs/cell-balancing/user_stories
   specs/cell-balancing/requirements

.. toctree::
   :maxdepth: 2
   :caption: Isolation monitoring (Markdown)

   specs/isolation-monitoring/user_stories
   specs/isolation-monitoring/requirements
   specs/isolation-monitoring/architecture
   specs/isolation-monitoring/software_requirements

.. toctree::
   :maxdepth: 2
   :caption: Implementation and verification arms

   src/code_trace
   tests/code_trace

.. toctree::
   :maxdepth: 2
   :caption: Cross-cutting

   specs/_global/decisions
   specs/_global/risks
   specs/_global/test_results
   specs/_global/gaps
