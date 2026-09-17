Workflow Gaps
===============

.. warning::

   **Generated file — do not edit by hand.** Written by
   ``tools/import_gaps.py`` from ``docs/reports/gaps/gaps.json``.
   Re-generate it with::

      ubc agent gaps > docs/reports/gaps/gaps.json
      python3 tools/import_gaps.py

   The report is a **committed snapshot**: the structural gate is not re-run
   on every build, so these needs record what ``ubc agent gaps`` found when it
   last ran, not what it would find now.

13 open gap(s) — 4 review, 8 trace_backward, 1 trace_forward.

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

.. gap:: SYS_1041 — nothing links back to it with covers
   :id: GAP_SYS_1041_NO_COVERS_BACK
   :gap_for: SYS_1041
   :gap_category: trace_backward
   :gap_link: covers
   :gap_shortfall: 0 of 1
   :gap_need_id: SYS_1041
   :gap_need_type: sys_req
   :style: red_bar

   ``SYS_1041`` (sys_req) fails the ``trace_backward`` gate: nothing links back to it
   with covers.

   It carries **0 of 1** of the ``covers`` links that gate requires.

   Resolve it with ``ubc agent next --id SYS_1041``, which names the stage that owes the
   missing artefact, then refresh this page from a new ``ubc agent gaps`` snapshot.

.. gap:: SYS_1042 — nothing links back to it with covers
   :id: GAP_SYS_1042_NO_COVERS_BACK
   :gap_for: SYS_1042
   :gap_category: trace_backward
   :gap_link: covers
   :gap_shortfall: 0 of 1
   :gap_need_id: SYS_1042
   :gap_need_type: sys_req
   :style: red_bar

   ``SYS_1042`` (sys_req) fails the ``trace_backward`` gate: nothing links back to it
   with covers.

   It carries **0 of 1** of the ``covers`` links that gate requires.

   Resolve it with ``ubc agent next --id SYS_1042``, which names the stage that owes the
   missing artefact, then refresh this page from a new ``ubc agent gaps`` snapshot.

.. gap:: SYS_1061 — nothing links back to it with covers
   :id: GAP_SYS_1061_NO_COVERS_BACK
   :gap_for: SYS_1061
   :gap_category: trace_backward
   :gap_link: covers
   :gap_shortfall: 0 of 1
   :gap_need_id: SYS_1061
   :gap_need_type: sys_req
   :style: red_bar

   ``SYS_1061`` (sys_req) fails the ``trace_backward`` gate: nothing links back to it
   with covers.

   It carries **0 of 1** of the ``covers`` links that gate requires.

   Resolve it with ``ubc agent next --id SYS_1061``, which names the stage that owes the
   missing artefact, then refresh this page from a new ``ubc agent gaps`` snapshot.

.. gap:: SYS_1062 — nothing links back to it with covers
   :id: GAP_SYS_1062_NO_COVERS_BACK
   :gap_for: SYS_1062
   :gap_category: trace_backward
   :gap_link: covers
   :gap_shortfall: 0 of 1
   :gap_need_id: SYS_1062
   :gap_need_type: sys_req
   :style: red_bar

   ``SYS_1062`` (sys_req) fails the ``trace_backward`` gate: nothing links back to it
   with covers.

   It carries **0 of 1** of the ``covers`` links that gate requires.

   Resolve it with ``ubc agent next --id SYS_1062``, which names the stage that owes the
   missing artefact, then refresh this page from a new ``ubc agent gaps`` snapshot.

.. gap:: SYS_1063 — nothing links back to it with covers
   :id: GAP_SYS_1063_NO_COVERS_BACK
   :gap_for: SYS_1063
   :gap_category: trace_backward
   :gap_link: covers
   :gap_shortfall: 0 of 1
   :gap_need_id: SYS_1063
   :gap_need_type: sys_req
   :style: red_bar

   ``SYS_1063`` (sys_req) fails the ``trace_backward`` gate: nothing links back to it
   with covers.

   It carries **0 of 1** of the ``covers`` links that gate requires.

   Resolve it with ``ubc agent next --id SYS_1063``, which names the stage that owes the
   missing artefact, then refresh this page from a new ``ubc agent gaps`` snapshot.

.. gap:: SYS_1064 — nothing links back to it with covers
   :id: GAP_SYS_1064_NO_COVERS_BACK
   :gap_for: SYS_1064
   :gap_category: trace_backward
   :gap_link: covers
   :gap_shortfall: 0 of 1
   :gap_need_id: SYS_1064
   :gap_need_type: sys_req
   :style: red_bar

   ``SYS_1064`` (sys_req) fails the ``trace_backward`` gate: nothing links back to it
   with covers.

   It carries **0 of 1** of the ``covers`` links that gate requires.

   Resolve it with ``ubc agent next --id SYS_1064``, which names the stage that owes the
   missing artefact, then refresh this page from a new ``ubc agent gaps`` snapshot.

.. gap:: SYS_1065 — nothing links back to it with covers
   :id: GAP_SYS_1065_NO_COVERS_BACK
   :gap_for: SYS_1065
   :gap_category: trace_backward
   :gap_link: covers
   :gap_shortfall: 0 of 1
   :gap_need_id: SYS_1065
   :gap_need_type: sys_req
   :style: red_bar

   ``SYS_1065`` (sys_req) fails the ``trace_backward`` gate: nothing links back to it
   with covers.

   It carries **0 of 1** of the ``covers`` links that gate requires.

   Resolve it with ``ubc agent next --id SYS_1065``, which names the stage that owes the
   missing artefact, then refresh this page from a new ``ubc agent gaps`` snapshot.

.. gap:: US_CELL_BALANCING — it carries no covers link upwards
   :id: GAP_US_CELL_BALANCING_NO_COVERS
   :gap_for: US_CELL_BALANCING
   :gap_category: trace_forward
   :gap_link: covers
   :gap_shortfall: 0 of 1
   :gap_need_id: US_CELL_BALANCING
   :gap_need_type: user_story
   :style: red_bar

   ``US_CELL_BALANCING`` (user_story) fails the ``trace_forward`` gate: it carries no
   covers link upwards.

   It carries **0 of 1** of the ``covers`` links that gate requires.

   Resolve it with ``ubc agent next --id US_CELL_BALANCING``, which names the stage that
   owes the missing artefact, then refresh this page from a new ``ubc agent gaps``
   snapshot.

.. gap:: US_CELL_PROTECTION — its review verdict does not cover the need as it now reads
   :id: GAP_US_CELL_PROTECTION_REVIEW
   :gap_for: US_CELL_PROTECTION
   :gap_category: review
   :gap_link: review
   :gap_shortfall: 0 of 1
   :gap_need_id: US_CELL_PROTECTION
   :gap_need_type: user_story
   :style: red_bar

   ``US_CELL_PROTECTION`` (user_story) fails the ``review`` gate: its review verdict
   does not cover the need as it now reads.

   It has **0 of 1** of the current review verdicts that gate requires.

   Resolve it with ``ubc agent next --id US_CELL_PROTECTION``, which names the stage
   that owes the missing artefact, then refresh this page from a new ``ubc agent gaps``
   snapshot.

.. gap:: US_ISOLATION_MONITORING — its review verdict does not cover the need as it now reads
   :id: GAP_US_ISOLATION_MONITORING_REVIEW
   :gap_for: US_ISOLATION_MONITORING
   :gap_category: review
   :gap_link: review
   :gap_shortfall: 0 of 1
   :gap_need_id: US_ISOLATION_MONITORING
   :gap_need_type: user_story
   :style: red_bar

   ``US_ISOLATION_MONITORING`` (user_story) fails the ``review`` gate: its review
   verdict does not cover the need as it now reads.

   It has **0 of 1** of the current review verdicts that gate requires.

   Resolve it with ``ubc agent next --id US_ISOLATION_MONITORING``, which names the
   stage that owes the missing artefact, then refresh this page from a new ``ubc agent
   gaps`` snapshot.

.. gap:: US_STATE_ESTIMATION — its review verdict does not cover the need as it now reads
   :id: GAP_US_STATE_ESTIMATION_REVIEW
   :gap_for: US_STATE_ESTIMATION
   :gap_category: review
   :gap_link: review
   :gap_shortfall: 0 of 1
   :gap_need_id: US_STATE_ESTIMATION
   :gap_need_type: user_story
   :style: red_bar

   ``US_STATE_ESTIMATION`` (user_story) fails the ``review`` gate: its review verdict
   does not cover the need as it now reads.

   It has **0 of 1** of the current review verdicts that gate requires.

   Resolve it with ``ubc agent next --id US_STATE_ESTIMATION``, which names the stage
   that owes the missing artefact, then refresh this page from a new ``ubc agent gaps``
   snapshot.

.. gap:: US_THERMAL_MANAGEMENT — its review verdict does not cover the need as it now reads
   :id: GAP_US_THERMAL_MANAGEMENT_REVIEW
   :gap_for: US_THERMAL_MANAGEMENT
   :gap_category: review
   :gap_link: review
   :gap_shortfall: 0 of 1
   :gap_need_id: US_THERMAL_MANAGEMENT
   :gap_need_type: user_story
   :style: red_bar

   ``US_THERMAL_MANAGEMENT`` (user_story) fails the ``review`` gate: its review verdict
   does not cover the need as it now reads.

   It has **0 of 1** of the current review verdicts that gate requires.

   Resolve it with ``ubc agent next --id US_THERMAL_MANAGEMENT``, which names the stage
   that owes the missing artefact, then refresh this page from a new ``ubc agent gaps``
   snapshot.
