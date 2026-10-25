Cell Balancing — User Stories
=================================

.. user_story:: Even out the charge across the cells so the pack keeps its usable capacity
   :id: US_CELL_BALANCING
   :status: draft

   As a fleet operator, I want the battery pack to even out the charge between
   its cells on its own, so that the usable capacity of the pack is not dragged
   down by whichever single cell drifted furthest from the rest.

   The capability is observable from the vehicle. A workshop measuring the cell
   voltages of a resting pack within a stated time after a charge session ends
   finds them converged into a stated narrow band instead of fanned out.

   Out of scope for this story: protecting cells from damage, reporting
   remaining charge, and regulating pack temperature. Those are separate
   capabilities with their own stories.
