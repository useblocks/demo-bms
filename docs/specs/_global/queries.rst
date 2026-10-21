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
the ``impl``, ``test`` and ``test_result`` needs of the stream live in ``src/``,
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

Filter string — the results, with the requirements each one's chain reaches
(``chain_reqs``, derived from the links):

.. code-block:: text

   type == 'test_result' and outcome == 'failed'

.. needtable::
   :filter: type == 'test_result' and outcome == 'failed'
   :columns: id;outcome;results_for;chain_reqs
   :style: table

Cypher — the same chain walked in the query rather than read from a stamped field:

.. code-block:: cypher

   MATCH (tr:test_result)-[:trace_up*]->(r:req)
   WHERE tr.outcome = 'failed'
   RETURN tr.id AS result, collect(DISTINCT r.id) AS reqs
   ORDER BY result

Two failures reach four requirements: ``TRES_IMBALANCE_WARNING`` reaches three
through one architecture element.

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
   :root_id: TRES_IMBALANCE_WARNING
   :root_direction: outgoing
   :link_types: trace_up
   :direction: LR
   :align: center
