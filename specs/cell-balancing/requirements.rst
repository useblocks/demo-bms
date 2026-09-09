Cell Balancing — Requirements
=================================

.. note::

   This stream is deliberately left **undecomposed**: the requirement below has
   no architecture, no software requirements, no implementation and no tests
   beneath it. It exists so that the gap view has a real, non-artificial gap to
   show, and so the agent workflow can be driven live from a requirement whose
   downstream artefacts genuinely do not exist yet.

.. req:: The battery management system shall reduce the cell voltage spread to 20 mV or less within 8 hours of a charge session ending
   :id: REQ_CELL_BALANCING_WINDOW
   :status: draft
   :traces_to: US_CELL_BALANCING

   The battery management system shall bring the difference between the highest
   and the lowest cell voltage of the pack to 20 mV or less within 8 hours of
   the end of a charge session, measured while the pack is at rest and every
   cell temperature is between 15 °C and 45 °C. The spread is evaluated on
   settled cell voltages, so the 8 hour window includes the time the cells need
   to relax after charging. Change this requirement to see if the gates catch the change.
