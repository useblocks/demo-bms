Cell Balancing — User Stories
=================================

.. user_story:: Even out the charge across the cells so the pack keeps its usable capacity
   :id: US_CELL_BALANCING
   :status: draft

   As a fleet operator, I want the battery pack to even out the charge between
   its cells on its own, so that the usable capacity of the pack is not dragged
   down by whichever single cell drifted furthest from the rest.

   The capability is observable from the vehicle. After a charge session the
   pack reports a cell voltage spread that has shrunk rather than grown. Over
   months, the usable capacity of the pack tracks the average cell rather than
   the weakest one, which the fleet report shows as a slower loss of range. A
   workshop reading the per-cell voltages after a standing period sees them
   converged into a narrow band instead of fanned out.

   Out of scope for this story: protecting cells from damage, reporting
   remaining charge, and regulating pack temperature. Those are separate
   capabilities with their own stories.
