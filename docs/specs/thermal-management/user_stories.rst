Thermal Management — User Stories
=====================================

.. user_story:: Keep the pack in its usable temperature band while driving and charging
   :id: US_THERMAL_MANAGEMENT
   :status: draft
   :covers: SYS_1031, SYS_1032, SYS_1033

   As a driver, I want the battery pack to warm itself when it is cold and cool
   itself when it is hot, so that I get the charging speed I was promised and
   the pack does not age faster than the warranty assumes.

   The capability is observable from the vehicle. On a cold morning the
   available charging power rises within a stated time instead of staying low
   for the whole session. On a hot day the pack keeps delivering drive power at
   a reduced but predictable level instead of cutting out. The workshop can read
   back the cooling and heating requests the pack made together with the
   temperatures that caused them. The temperature spread between the warmest and
   the coldest cell stays inside a stated band, so no part of the pack ages
   ahead of the rest.

   Out of scope for this story: disconnecting the pack on a safety fault, and
   reporting remaining charge. Those are separate capabilities with their own
   stories.
