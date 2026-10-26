Cell Protection — LFP Charging
==============================

This page is a **variant document**: it is part of the LFP build only
(``[[source.variant_sources]]`` in ``ubproject.toml``). In every other build it
is not read at all — no page, no need.

.. req:: The battery management system shall taper the charge current once any LFP cell reaches 3.65 V
   :id: REQ_LFP_CHARGE_TAPER
   :status: approved
   :asil: B
   :traces_to: US_CELL_PROTECTION
   :chemistry: <{ var.pack.chemistry }>

   On a lithium iron phosphate pack the battery management system shall reduce
   the requested charge current as soon as any cell reaches
   :variant:`pack.cell_v_max` V, and hold that cell at or below it until the
   current has fallen to the end-of-charge threshold. The flat LFP voltage
   plateau leaves no other early signal of a full cell.
