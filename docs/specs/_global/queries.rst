Queries
=======

Three questions asked of the graph three ways: a **filter string** — the tables
below are that filter, rendered by this build — the same string through
``ubc query filter``, and **Cypher** through ``ubc query cypher`` or the
``query_cypher`` tool of ``ubc serve mcp``.

``trace_up`` is the derived link type that makes the Cypher short: the union of
the six chain links (``traces_to``, ``satisfies``, ``refines``, ``implements``,
``verifies``, ``results_for``), declared once in ``ubproject.toml``. No author
writes it. "Up the V" is one relationship type, so a variable-length path follows
it to any depth, and ``trace_up_back`` is the view down from a need.

Safety requirements with no verifying test
------------------------------------------

An ASIL C or D requirement that no test reaches is the safety case's first hole.
The tests hang three levels down (``test -> swreq -> arch -> req``), so this is a
question about a path, not about one need.

Filter string — exact, because the path is already a field: ``test_count`` is
derived on every rung (a swreq counts the tests that verify it, an arch sums its
swreqs, a req its archs), so the three-level question reads one value. ``ubc query
filter`` answers the same string.

.. code-block:: text

   type == 'req' and asil in ['C', 'D'] and test_count == 0

.. needtable::
   :filter: type == 'req' and asil in ['C', 'D'] and test_count == 0
   :columns: id;title;asil;test_count
   :style: table

Cypher — the whole path, over the union:

.. code-block:: cypher

   MATCH (r:req)
   WHERE r.asil IN ['C', 'D']
     AND NOT EXISTS { MATCH (r)<-[:trace_up*]-(:test) }
   RETURN r.id AS req, r.asil AS asil

Both answer **none**: every ASIL C and D requirement has two to ten tests below it.
Drop the ASIL condition and the answer is ``REQ_CELL_BALANCING_WINDOW`` (QM), the
deliberate gap.

Every need of the cell-protection stream, by type
-------------------------------------------------

A stream is a directory, ``specs/cell-protection/``, and nothing on a need says
which stream it belongs to. The authored needs carry it in their document name;
the ``impl``, ``test`` and ``testcase`` needs of the stream live in ``src/``,
``tests/`` and ``specs/_global/``, and belong to it only through the chain.

Filter string — the authored needs alone:

.. code-block:: text

   docname.startswith('specs/cell-protection/')

.. needtable::
   :filter: docname.startswith('specs/cell-protection/')
   :columns: id;type;title
   :sort: type
   :style: table

Cypher — the whole stream, everything that traces up to its story:

.. code-block:: cypher

   MATCH (n)-[:trace_up*0..]->(:user_story {id: 'US_CELL_PROTECTION'})
   RETURN n.type AS type, count(DISTINCT n) AS needs
   ORDER BY type

The filter finds 21 needs; the path finds 61, the 40 more being the stream's code,
tests and results. What it costs today: a document-name prefix for the authored
needs plus a graph walk for the derived ones. A namespace on every need would make
it one comparison.

Failed test results and the requirements they are evidence for
---------------------------------------------------------------

Filter string — the tests whose recorded result did not pass, with that result
(``results``) and the requirements each one's chain reaches (``chain_reqs``), both
derived from the links:

.. code-block:: text

   type == 'test' and not all_passed

.. needtable::
   :filter: type == 'test' and not all_passed
   :columns: id;results;chain_reqs
   :style: table

Cypher — the same chain walked in the query, up from the recorded test case:

.. code-block:: cypher

   MATCH (tc:testcase)-[:trace_up*]->(r:req)
   WHERE tc.result = 'failed'
   RETURN tc.id AS result, collect(DISTINCT r.id) AS reqs
   ORDER BY result

Two failures reach four requirements: the failing case of
``TEST_IMBALANCE_WARNING`` reaches three through one architecture element.

One level down, the same verdict is a field of the software requirement:
``all_tests_passed`` (every test verifying it passed its last run), derived from
``all_passed`` on each test, and ``test_count``. Unverified or failing, in one
filter:

.. code-block:: text

   type == 'swreq' and (test_count == 0 or not all_tests_passed)

.. needtable::
   :filter: type == 'swreq' and (test_count == 0 or not all_tests_passed)
   :columns: id;title;test_count;impl_count;all_tests_passed
   :style: table

.. needflow:: One failure, followed up the V
   :root_id: TF_RUN_0EA_BC926
   :root_direction: outgoing
   :link_types: trace_up
   :direction: LR
   :align: center

Requirements of the active chemistry
------------------------------------

The project is a 150 % specification: the pack chemistry comes from the variant
data (``[variants]`` in ``ubproject.toml``), and a requirement written for one
chemistry carries it in its ``chemistry`` field. Which requirements belong to the
chemistry this build is for?

Filter string — the same through ``ubc query filter``:

.. code-block:: text

   type == 'req' and chemistry == var.pack.chemistry

.. needtable::
   :filter: type == 'req' and chemistry == var.pack.chemistry
   :columns: id;title;chemistry
   :style: table

Cypher — ubCode reaches the variant data through the reserved ``$var`` parameter:

.. code-block:: text

   MATCH (r:req) WHERE r.chemistry = $var.pack.chemistry
   RETURN r.id, r.title

The NMC build answers ``REQ_CELL_VOLTAGE_LIMITS``; the LFP build adds
``REQ_LFP_CHARGE_TAPER``, which exists in that build only.
