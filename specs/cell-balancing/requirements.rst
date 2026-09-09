Cell Balancing — Requirements
=================================

.. note::

   This stream was deliberately left **undecomposed** while the gap view needed a
   real, non-artificial gap to show. It is now decomposed the whole way down —
   :doc:`architecture <architecture>`, :doc:`software requirements
   <software_requirements>`, implementation markers under ``src/cell_balancing/``
   and test markers under ``tests/cell_balancing/`` — so the chain below this
   requirement is complete.

.. req:: The battery management system shall reduce the cell voltage spread to 20 mV or less within 8 hours of a charge session ending
   :id: REQ_CELL_BALANCING_WINDOW
   :status: draft
   :traces_to: US_CELL_BALANCING

   The battery management system shall bring the difference between the highest
   and the lowest cell voltage of the pack to 20 mV or less within 8 hours of
   the end of a charge session, measured while the pack is at rest and every
   cell temperature is between 15 °C and 45 °C. The spread is evaluated on
   settled cell voltages, so the 8 hour window includes the time the cells need
   to relax after charging.
