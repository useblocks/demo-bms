State Estimation — User Stories
===================================

.. user_story:: Report a trustworthy remaining charge and remaining capacity for the pack
   :id: US_STATE_ESTIMATION
   :status: draft

   As a fleet operator, I want the battery pack to report how much charge it has
   left and how much of its original capacity it has lost, so that I can trust
   the predicted range of a vehicle and plan when a pack needs replacing.

   The capability is observable from the vehicle and on the workshop bench. The
   charge level the vehicle shows does not jump when the vehicle is switched off
   and on again. The fleet report shows a remaining-capacity figure that never
   rises over the life of the pack. A workshop that discharges a fully charged
   pack on a calibrated bench finds every charge level the pack reported over
   the everyday middle of its range, away from the nearly full and nearly empty
   ends, within a stated tolerance of the charge that actually came out.

   Out of scope for this story: protecting the cells from damage, and regulating
   pack temperature. Those are separate capabilities with their own stories.
