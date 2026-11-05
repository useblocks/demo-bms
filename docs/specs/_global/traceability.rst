Traceability
============

Everything on this page is **derived**. Not one link, id or count below is
maintained by hand: the tables and the diagrams are queries over the same need
graph that ``ubc build needs`` compiles and that ``sphinx-build -b ubtrace``
publishes, so they cannot drift from the specs the way a hand-drawn matrix does.
Add a requirement, or a marker in the source, and it appears here on the next
build.

Read the diagrams as the V, seen from the top of each stream: the arrows point
*up* the way the needs declare them — a requirement ``traces_to`` its user
story, an architecture element ``satisfies`` a requirement, a software
requirement ``refines`` an element, and the two lower arms attach to the
software requirement, ``implements`` from the production source and ``verifies``
from the test source, with a ``testcase`` recording what the last run of that
test actually did.

**A red node is a gap.** ``ubc agent gaps`` runs the structural gate over the
whole graph, and :doc:`its findings are imported back into it </specs/_global/gaps>`
as ``gap`` needs — so a missing rung of the V is not something you have to run a
report to discover. It hangs off the need it is about, in red, in the diagram
below and in the ``gaps`` column of every level table.

The V, per stream
-----------------

Cell protection
~~~~~~~~~~~~~~~

.. needflow:: Cell protection — full chain
   :root_id: US_CELL_PROTECTION
   :root_direction: incoming
   :link_types: traces_to, satisfies, refines, implements, verifies, results_for, gap_for
   :direction: LR
   :show_link_names:
   :align: center

State estimation
~~~~~~~~~~~~~~~~

.. needflow:: State estimation — full chain
   :root_id: US_STATE_ESTIMATION
   :root_direction: incoming
   :link_types: traces_to, satisfies, refines, implements, verifies, results_for, gap_for
   :direction: LR
   :show_link_names:
   :align: center

Thermal management
~~~~~~~~~~~~~~~~~~

.. needflow:: Thermal management — full chain
   :root_id: US_THERMAL_MANAGEMENT
   :root_direction: incoming
   :link_types: traces_to, satisfies, refines, implements, verifies, results_for, gap_for
   :direction: LR
   :show_link_names:
   :align: center

Cell balancing
~~~~~~~~~~~~~~

The stream with the deliberate gap: its requirements have no architecture below
them yet, so the chain stops one level down. That is the point — the diagram
shows the hole rather than hiding it.

.. needflow:: Cell balancing — full chain
   :root_id: US_CELL_BALANCING
   :root_direction: incoming
   :link_types: traces_to, satisfies, refines, implements, verifies, results_for, gap_for
   :direction: LR
   :show_link_names:
   :align: center

Isolation monitoring
~~~~~~~~~~~~~~~~~~~~

The stream authored in Markdown (MyST) rather than reStructuredText. Same
ontology, same links, same diagram — the format of the source file is not a
property of the graph.

.. needflow:: Isolation monitoring — full chain
   :root_id: US_ISOLATION_MONITORING
   :root_direction: incoming
   :link_types: traces_to, satisfies, refines, implements, verifies, results_for, gap_for
   :direction: LR
   :show_link_names:
   :align: center

Level by level
--------------

The same graph as tables, one per level, each showing the links **out** of that
level and the links **in** from the level below. An empty incoming cell is a
coverage gap, and it is visible without running a report.

User stories
~~~~~~~~~~~~

.. needtable::
   :types: user_story
   :columns: id;title;traces_from;gaps
   :style: table

Requirements
~~~~~~~~~~~~

.. needtable::
   :types: req
   :columns: id;title;status;traces_to;satisfied_by;mitigated_by;gaps
   :style: table

Architecture
~~~~~~~~~~~~

.. needtable::
   :types: arch
   :columns: id;title;satisfies;refined_by;affected_by;gaps
   :style: table

Software requirements
~~~~~~~~~~~~~~~~~~~~~

Both lower arms hang off this level, so this is the table that says whether the
V closes: ``implements_back`` is the implementation arm, ``verifies_back`` the
verification arm.

.. needtable::
   :types: swreq
   :columns: id;title;refines;implements_back;verifies_back;gaps
   :style: table

Implementation arm
~~~~~~~~~~~~~~~~~~

.. needtable::
   :types: impl
   :columns: id;title;implements
   :style: table

Verification arm
~~~~~~~~~~~~~~~~

.. needtable::
   :types: test
   :columns: id;title;verifies;results
   :style: table

Recorded outcomes
~~~~~~~~~~~~~~~~~

``testcase`` needs are read from a committed JUnit snapshot on :doc:`test_run`,
so these are the outcomes of one real run, not of this build. Each links
``results_for`` to the test it ran.

.. needtable::
   :types: testcase
   :columns: id;title;result;time;results_for
   :style: table

Gaps
~~~~

The structural gate's own output, imported back into the graph by
``tools/import_gaps.py`` from a committed ``ubc agent gaps`` snapshot. This is the
same arrangement as ``testcase`` on the other arm of the V: a ``testcase``
records what *happened* when a test ran, a ``gap`` records what the *gate* found
when it last ran, and neither is authored by hand.

The point of importing them rather than reading the JSON is that a gap then
appears **where the reader already is** — on the need's own page, in the tables
above, and in red in the diagrams.

.. needtable::
   :types: gap
   :columns: id;gap_need_id;gap_need_type;gap_category;gap_link;gap_shortfall
   :style: table

Cross-cutting
~~~~~~~~~~~~~

Decisions constrain an architecture element; risks bear on a requirement.
Neither is exempt from the orphan gate, which is why both carry a link.

.. needtable::
   :types: decision
   :columns: id;title;affects
   :style: table

.. needtable::
   :types: risk
   :columns: id;title;mitigates
   :style: table
