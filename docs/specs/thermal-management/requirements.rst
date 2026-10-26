Thermal Management — Requirements
=====================================

.. req:: The battery management system shall request coolant flow when the highest cell temperature exceeds 35 °C
   :id: REQ_COOLING_REQUEST
   :status: draft
   :asil: A
   :traces_to: US_THERMAL_MANAGEMENT

   The battery management system shall raise a cooling request on the thermal
   interface whenever the highest valid cell temperature is above 35 °C, and
   shall withdraw it once that temperature has fallen to 30 °C or below. The 5 K
   difference between the two thresholds keeps the request from oscillating while
   the pack sits at the limit.

.. req:: The battery management system shall request pack heating when the lowest cell temperature is below 5 °C
   :id: REQ_HEATING_REQUEST
   :status: draft
   :asil: QM
   :traces_to: US_THERMAL_MANAGEMENT

   The battery management system shall raise a heating request on the thermal
   interface whenever the lowest valid cell temperature is below 5 °C, and shall
   withdraw it once that temperature has risen to 10 °C or above. This is what
   restores the promised charging power on a cold morning instead of leaving it
   low for the whole session.

.. req:: The battery management system shall reduce the permitted discharge power linearly to zero between 55 °C and 60 °C highest cell temperature
   :id: REQ_POWER_DERATING
   :status: draft
   :asil: B
   :traces_to: US_THERMAL_MANAGEMENT

   The battery management system shall publish a permitted discharge power that
   falls linearly from the full permitted value at 55 °C to zero at 60 °C
   highest valid cell temperature. The vehicle therefore loses power
   predictably as the pack heats up, instead of being cut off at a single
   threshold.

.. req:: The battery management system shall limit the pack discharge current to 250 A once its 10 s average reaches 250 A
   :id: REQ_SUSTAINED_DISCHARGE_LIMIT
   :status: draft
   :asil: B
   :traces_to: US_THERMAL_MANAGEMENT

   The battery management system shall limit the permitted discharge power it
   publishes so that the pack discharge current cannot exceed 250 A, the
   continuous discharge rating of the cells, from the moment its average over
   the trailing 10 s reaches 250 A until that average falls below 250 A again.
   Below that average the full discharge power stays available for a short
   peak, while a sustained load such as towing a trailer up a mountain pass is
   held to 250 A, so the pack does not heat up into the range where its drive
   power has to be cut back.

.. req:: The battery management system shall report a thermal imbalance warning when the spread between highest and lowest cell temperature exceeds 8 K
   :id: REQ_CELL_TEMP_SPREAD
   :status: draft
   :asil: QM
   :traces_to: US_THERMAL_MANAGEMENT

   The battery management system shall set a thermal imbalance warning on the
   diagnostic interface whenever the difference between the highest and the
   lowest valid cell temperature exceeds 8 K. The warning is what makes uneven
   ageing visible in the workshop before it shows up as lost capacity.

.. req:: The battery management system shall apply the thermal fallback power limit when the coolant actuator does not confirm a request within 2 seconds
   :id: REQ_THERMAL_ACTUATOR_FAILSAFE
   :status: draft
   :asil: B
   :traces_to: US_THERMAL_MANAGEMENT

   The battery management system shall publish the thermal fallback power limit,
   defined as 30 % of the full permitted discharge power, whenever a raised
   cooling or heating request has not been confirmed by the coolant actuator
   within 2 seconds. An unconfirmed request means the pack temperature can no
   longer be influenced, so the power the pack is allowed to deliver is capped
   instead.
