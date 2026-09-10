Workflow Gaps
===============

.. warning::

   **Generated file — do not edit by hand.** Written by
   ``tools/import_gaps.py`` from ``reports/gaps/gaps.json``.
   Re-generate it with::

      ubc agent gaps > reports/gaps/gaps.json
      python3 tools/import_gaps.py

   The report is a **committed snapshot**: the structural gate is not re-run
   on every build, so these needs record what ``ubc agent gaps`` found when it
   last ran, not what it would find now.

3 open gap(s) — 1 review, 1 trace_backward, 1 trace_forward.

Each need below carries ``gap_for`` down to the need the gate attributed it
to, so the gap shows up as a red node beside that need in every ``needflow``
diagram and as a non-empty ``gaps`` cell in every level table on
:doc:`/traceability`. Ask the engine what to do about one with
``ubc agent next --id <NEED_ID>``.

.. gap:: REQ_CELL_BALANCING_WINDOW — nothing links back to it with satisfies
   :id: GAP_REQ_CELL_BALANCING_WINDOW_NO_SATISFIES_BACK
   :gap_for: REQ_CELL_BALANCING_WINDOW
   :gap_category: trace_backward
   :gap_link: satisfies
   :gap_shortfall: 0 of 1
   :gap_need_id: REQ_CELL_BALANCING_WINDOW
   :gap_need_type: req
   :style: red_bar

   ``REQ_CELL_BALANCING_WINDOW`` (req) fails the ``trace_backward`` gate: nothing links
   back to it with satisfies.

   It carries **0 of 1** of the ``satisfies`` links that gate requires.

   Resolve it with ``ubc agent next --id REQ_CELL_BALANCING_WINDOW``, which names the
   stage that owes the missing artefact, then refresh this page from a new ``ubc agent
   gaps`` snapshot.

.. gap:: REQ_CELL_VOLTAGE_LIMITS — the review gate is not satisfied
   :id: GAP_REQ_CELL_VOLTAGE_LIMITS_REVIEW
   :gap_for: REQ_CELL_VOLTAGE_LIMITS
   :gap_category: review
   :gap_link: review
   :gap_shortfall: 0 of 1
   :gap_need_id: REQ_CELL_VOLTAGE_LIMITS
   :gap_need_type: req
   :style: red_bar

   ``REQ_CELL_VOLTAGE_LIMITS`` (req) fails the ``review`` gate. This importer carries no
   description for that gate — it postdates the engine version ``tools/import_gaps.py``
   was written against. Read the raw record in the snapshot for the detail.

   It carries **0 of 1** of the ``review`` links that gate requires.

   Resolve it with ``ubc agent next --id REQ_CELL_VOLTAGE_LIMITS``, which names the
   stage that owes the missing artefact, then refresh this page from a new ``ubc agent
   gaps`` snapshot.

.. gap:: REQ_CELL_VOLTAGE_LIMITS — it carries no traces_to link upwards
   :id: GAP_REQ_CELL_VOLTAGE_LIMITS_NO_TRACES_TO
   :gap_for: REQ_CELL_VOLTAGE_LIMITS
   :gap_category: trace_forward
   :gap_link: traces_to
   :gap_shortfall: 0 of 1
   :gap_need_id: REQ_CELL_VOLTAGE_LIMITS
   :gap_need_type: req
   :style: red_bar

   ``REQ_CELL_VOLTAGE_LIMITS`` (req) fails the ``trace_forward`` gate: it carries no
   traces_to link upwards.

   It carries **0 of 1** of the ``traces_to`` links that gate requires.

   Resolve it with ``ubc agent next --id REQ_CELL_VOLTAGE_LIMITS``, which names the
   stage that owes the missing artefact, then refresh this page from a new ``ubc agent
   gaps`` snapshot.
