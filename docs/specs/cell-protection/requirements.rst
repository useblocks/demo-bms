Cell Protection — Requirements
==================================

This page is a **150 % specification**. The cell voltage limits below are not
literals: they are resolved from the pack chemistry in the active variant data
(``variants/nmc.json`` unless overridden), which currently selects
:variant:`pack.chemistry` and keeps every cell between
:variant:`pack.cell_v_min` V and :variant:`pack.cell_v_max` V. Build the LFP
profile with ``ubc script variant-diff`` to see exactly which requirement
changes. The implementation and verification arms in this repository are the
NMC build.

.. if:: var.pack.chemistry == 'LFP'

   .. note::

      LFP profile. The flat open-circuit-voltage plateau of lithium iron
      phosphate leaves little headroom between "full" and the upper limit, so
      cell balancing is what keeps a full pack clear of this reaction.

.. note::

   **The requirements of this stream live in Jama Connect, not in this file.**
   They are pulled down by ``tools/sync_alm.py`` and rendered on
   :doc:`/specs/_global/alm_requirements`. Edit them in Jama; the architecture
   below them is authored here and links up into the imported set.

.. needtable::
   :filter: type == "req" and alm_stream == "cell-protection"
   :columns: id;title;status;legacy_id;satisfied_by;gaps
   :style: table
