System Models (SysML v2, AUTOSAR)
===================================

The system models of this project are **not authored here**. Their masters are
the modelling tools — an MBSE tool for the SysML v2 system architecture, an
AUTOSAR authoring tool for the software components. ``docs/models/`` holds their
exports, and ``tools/import_models.py`` turns them into read-only needs::

   ubc script import-models     # re-read both models, no network
   ubc script trace             # one Jama requirement, through every tool

Every element on this page is an **external need**: there is no local text to
edit, and each reference opens the model file at the line that defines the
element. The links come from the models, because the models own them.

.. list-table::
   :header-rows: 1
   :widths: 22 28 50

   * - Model
     - Export
     - Linked into the graph by
   * - SysML v2 system architecture
     - ``models/bms.sysml`` (textual notation)
     - ``satisfy`` relationships to the requirements, which the model mirrors by
       their Jama id as SysML short name
   * - AUTOSAR software components
     - ``models/bms.arxml`` (classic platform R4.x)
     - a special data group on each component,
       ``<SDG GID="useblocks.Traceability">``, naming the architecture element
       it realizes

.. note::

   Neither ubConnect nor Sphinx-Needs has a SysML v2 or an AUTOSAR connector
   today. The importer is the pattern, not a product feature: any model that
   can be exported as structured text becomes needs, and from then on it takes
   part in everything the graph does — traceability, suspect links, ubTrace. The
   SysML v2 reader handles the subset of the notation this model uses; a
   production bridge reads the model through the SysML v2 API.

One requirement, every tool
---------------------------

``JAMA_Rollout_Demo-SYSRQ-4`` — the pack overcurrent requirement — as the
system model, the architecture and the software components see it.

.. needflow:: Pack overcurrent — Jama, SysML v2, Git and AUTOSAR
   :filter: id in ["JAMA_Rollout_Demo-SYSRQ-4", "SYSML_CELL_PROTECTION", "ARCH_CURRENT_PATH_MONITOR", "ARCH_SAFETY_SUPERVISOR", "AR_SWC_CURRENT_PATH_MONITOR", "AR_SWC_SAFETY_SUPERVISOR", "SWREQ_OVERCURRENT_DEBOUNCE", "SWREQ_LIMIT_EVALUATION"]
   :link_types: satisfies, realizes, refines
   :direction: LR
   :show_link_names:
   :align: center

SysML v2 parts
--------------

.. needtable::
   :types: sysml_part
   :columns: id;title;satisfies;part_of;model_line
   :style: table

AUTOSAR software components
---------------------------

.. needtable::
   :types: swc
   :columns: id;title;realizes;provides;requires;model_line
   :style: table

AUTOSAR port interfaces
-----------------------

.. needtable::
   :types: port_if
   :columns: id;title;provided_by;required_by;model_line
   :style: table
