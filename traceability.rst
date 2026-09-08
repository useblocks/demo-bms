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
from the test source, with a ``test_result`` recording what the last run of that
test actually did.

The V, per stream
-----------------

Cell protection
~~~~~~~~~~~~~~~

.. needflow:: Cell protection — full chain
   :root_id: US_CELL_PROTECTION
   :root_direction: incoming
   :link_types: traces_to, satisfies, refines, implements, verifies, results_for
   :direction: LR
   :show_link_names:
   :align: center

State estimation
~~~~~~~~~~~~~~~~

.. needflow:: State estimation — full chain
   :root_id: US_STATE_ESTIMATION
   :root_direction: incoming
   :link_types: traces_to, satisfies, refines, implements, verifies, results_for
   :direction: LR
   :show_link_names:
   :align: center

Thermal management
~~~~~~~~~~~~~~~~~~

.. needflow:: Thermal management — full chain
   :root_id: US_THERMAL_MANAGEMENT
   :root_direction: incoming
   :link_types: traces_to, satisfies, refines, implements, verifies, results_for
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
   :link_types: traces_to, satisfies, refines, implements, verifies, results_for
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
   :columns: id;title;traces_from
   :style: table

Requirements
~~~~~~~~~~~~

.. needtable::
   :types: req
   :columns: id;title;status;traces_to;satisfied_by;mitigated_by
   :style: table

Architecture
~~~~~~~~~~~~

.. needtable::
   :types: arch
   :columns: id;title;satisfies;refined_by;affected_by
   :style: table

Software requirements
~~~~~~~~~~~~~~~~~~~~~

Both lower arms hang off this level, so this is the table that says whether the
V closes: ``implements_back`` is the implementation arm, ``verifies_back`` the
verification arm.

.. needtable::
   :types: swreq
   :columns: id;title;refines;implements_back;verifies_back
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

``test_result`` needs are imported from a committed JUnit snapshot, so these are
the outcomes of one real run, not of this build. ``chain_reqs`` is the resolved
``test -> swreq -> arch -> req`` roll-up each one carries as a field.

.. needtable::
   :types: test_result
   :columns: id;outcome;runtime_s;results_for;chain_reqs
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
