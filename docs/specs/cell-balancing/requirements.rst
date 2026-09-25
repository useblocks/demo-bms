Cell Balancing — Requirements
=================================

.. note::

   This stream is deliberately left **undecomposed**: the requirement below has
   no architecture, no software requirements, no implementation and no tests
   beneath it. It exists so that the gap view has a real, non-artificial gap to
   show, and so the agent workflow can be driven live from a requirement whose
   downstream artefacts genuinely do not exist yet.

.. note::

   **The requirements of this stream live in Jama Connect, not in this file.**
   They are pulled down by ``tools/sync_alm.py`` and rendered on
   :doc:`/specs/_global/alm_requirements`. Edit them in Jama; the architecture
   below them is authored here and links up into the imported set.

.. needtable::
   :filter: type == "req" and alm_stream == "cell-balancing"
   :columns: id;title;status;legacy_id;satisfied_by;gaps
   :style: table
