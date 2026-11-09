Cell Voltage Acquisition — User Stories
=======================================

.. user_story:: Measure every cell voltage reliably with a part the industry already qualified
   :id: US_CELL_VOLTAGE_ACQUISITION
   :status: draft
   :sourcing: supplier

   As a fleet operator, I want every cell voltage in the pack to be measured
   reliably and continuously, so that protection, balancing and state
   estimation all work from the same trustworthy picture of the cells.

   The capability is observable from the workshop. A diagnostic read-out shows
   every cell voltage, and a broken sense wire is reported as a fault instead
   of as a plausible-looking voltage.

   This capability is bought, not built: the cell voltages are measured by a
   supplier's battery-monitoring front end, so the stream follows the supplier
   arm of the workflow (supplier specifications, then acceptance tests) instead
   of the in-house software arm.
