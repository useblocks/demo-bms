State Estimation — User Stories
===================================

.. user_story:: Report a trustworthy remaining charge and remaining capacity for the pack
   :id: US_STATE_ESTIMATION
   :status: draft

   As a fleet operator, I want the battery pack to report how much energy it has
   left and how much of its original capacity it has lost, so that I can trust
   the predicted range of a vehicle and plan when a pack needs replacing.

   The capability is observable from the vehicle. The dashboard shows a charge
   level that stays within a stated tolerance of the energy the vehicle actually
   delivers before it stops. The level does not jump when the vehicle is
   switched off and on again. The fleet report shows a remaining-capacity figure
   that only decreases over the life of the pack. A workshop that fully
   discharges and fully recharges a pack can confirm both figures against the
   energy that physically went in and out.

   Out of scope for this story: protecting the cells from damage, and regulating
   pack temperature. Those are separate capabilities with their own stories.
