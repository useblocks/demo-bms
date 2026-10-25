Thermal Management — User Stories
=====================================

.. user_story:: Keep the pack in its usable temperature band while driving and charging
   :id: US_THERMAL_MANAGEMENT
   :status: draft

   As a driver, I want the battery pack to warm itself when it is cold and cool
   itself when it is hot, so that I get the charging speed I was promised and
   the pack does not age faster than the warranty assumes.

   The capability is observable from the vehicle. On a cold morning the pack
   calls for heating while its coldest cell is too cold to charge quickly, and
   stops once that cell has warmed up. On a hot day it calls for cooling while
   its warmest cell runs hot, and stops once that cell has cooled down again.
   As the pack nears its upper temperature limit, the drive power it allows
   falls off gradually and predictably instead of cutting out at a single
   threshold. Even under sustained full load, such as towing a trailer up a
   mountain pass, the pack never draws more current than its cells are rated to
   deliver continuously, so it does not heat up into the range where its drive
   power has to be cut back. If the cooling and heating system stops responding,
   the pack falls back to a reduced drive power, because it can no longer keep
   its own temperature in check. When the spread between the warmest and the
   coldest cell grows too wide, the workshop is warned, so uneven ageing is
   caught before it costs capacity.

   Out of scope for this story: disconnecting the pack on a safety fault, and
   reporting remaining charge. Those are separate capabilities with their own
   stories.
