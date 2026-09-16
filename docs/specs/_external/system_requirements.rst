System Requirements (imported from DOORS)
===========================================

The customer's system requirements, owned in their IBM DOORS instance. They are
the top of this project's V: every :need:`user story <US_CELL_PROTECTION>` traces
up into this layer with a ``covers`` link, so no stream exists without a customer
requirement justifying it.

.. note::

   **These needs are not authored in this repository and cannot be edited here.**
   They are loaded directly from ``external/doors/needs.json`` by
   ``[[needs.external_needs]]`` in ``ubproject.toml``, which projects them from
   the export unchanged — there is no generated file to edit and no glue code in
   between. Refresh the layer from a new DOORS baseline with::

      ubconnect csv from-csv -c external/doors/import.toml

   A requirement that is wrong, ambiguous or unimplementable is a conversation
   with the customer, not a commit here.

The imported fields are the customer's own: ``object_identifier`` is the DOORS object
identifier a customer engineer searches for in their tool, ``asil`` is the safety
integrity level allocated by the vehicle hazard analysis, and ``doors_status``
is *their* lifecycle state — deliberately not this project's ``status``, which no
imported need carries.

All system requirements
-----------------------

.. needtable::
   :types: sys_req
   :columns: id;object_identifier;title;doors_status;asil;verification_method;covered_by
   :style: table

The mapping backlog
-------------------

A requirement with an empty ``covered_by`` above is one **no user story has
claimed**. That is a real backlog, not a defect to paper over: it is expected to
be non-empty for as long as the customer specifies more than this project builds.

Each one is reported by ``ubc agent gaps`` as a ``trace_backward`` gap against the
``user_stories`` stage, and carried as accepted debt in the ``release-check``
baseline until the project takes it on. Ask the engine what to do about one with::

   ubc agent next --id <SYS_ID> -p docs

The authoritative list is the gate's, not this page's — read it from
:doc:`/specs/_global/gaps`, or straight from the engine::

   ubc agent gaps -p docs

There is deliberately no second table filtered to the uncovered requirements here.
``covered_by`` is an incoming-link field and simply does not exist on a need that
has none, so ``not covered_by`` raises ``name 'covered_by' is not defined`` during
the build rather than matching them — which under ``-W`` fails the build outright.
