Current Sensing — User Stories
==============================

.. user_story:: Know the pack current precisely enough to count charge and protect the pack
   :id: US_CURRENT_SENSING
   :status: draft

   As a fleet operator, I want the battery management system to know how much
   current flows into and out of the pack at every moment, so that the remaining
   charge it reports stays trustworthy over a long shift and an overcurrent is
   cut off before it damages the cells or the busbars.

   The capability is observable from the vehicle. The reported state of charge
   does not drift away from the value measured at the next full charge, and a
   short circuit in the drive train opens the contactors instead of tripping
   the pack fuse.

   This stream is left at the make-or-buy decision on purpose: its architecture
   is drafted, and whether the current sensor is built in-house or bought as a
   supplier module is still open, so the workflow asks for the choice.
