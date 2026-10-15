State Estimation — Requirements
===================================

.. req:: The battery management system shall report a state of charge whose absolute error stays within 3 % of rated capacity between 10 % and 90 % state of charge
   :id: REQ_SOC_ACCURACY
   :status: draft
   :asil: QM
   :traces_to: US_STATE_ESTIMATION

   The battery management system shall report a state of charge (the share of
   rated capacity still available) whose absolute deviation from the
   reference value measured on a pack conditioned to 25 °C stays within 3 % of
   rated capacity, for every reported value in the 10 % to 90 % band. The
   reference value is the charge counted out of a fully charged pack by a
   calibrated bench.

.. req:: The battery management system shall publish an updated state of charge value every 100 ms
   :id: REQ_SOC_UPDATE_PERIOD
   :status: draft
   :asil: QM
   :traces_to: US_STATE_ESTIMATION

   The battery management system shall publish a state of charge value on the
   vehicle interface with a period of 100 ms and a tolerance of 10 ms, for as
   long as the system is awake. A missing publication within 110 ms of the
   previous one is a violation of this requirement.

.. req:: The battery management system shall correct the state of charge from the open-circuit voltage after the pack has rested for at least 30 minutes
   :id: REQ_SOC_REST_CORRECTION
   :status: draft
   :asil: QM
   :traces_to: US_STATE_ESTIMATION

   The battery management system shall replace the counted state of charge with
   the value derived from the measured open-circuit voltage once the absolute
   pack current has stayed below 1 A continuously for at least 30 minutes. This
   bounds the accumulated counting drift each time the vehicle stands still long
   enough for the cell voltages to settle.

.. req:: The battery management system shall restore the state of charge after a power cycle within 2 % of the value reported before shutdown
   :id: REQ_SOC_PERSISTENCE
   :status: draft
   :asil: QM
   :traces_to: US_STATE_ESTIMATION

   The battery management system shall report, on the first publication after a
   power cycle in which no charge left or entered the pack, a state of charge
   within 2 % of rated capacity of the last value it published before shutdown.
   This is what keeps the displayed charge level from jumping when the vehicle is
   switched off and on again.

.. req:: The battery management system shall report a remaining capacity that never increases over the life of the pack
   :id: REQ_SOH_CAPACITY_REPORT
   :status: draft
   :asil: QM
   :traces_to: US_STATE_ESTIMATION

   The battery management system shall report a remaining capacity, expressed as
   a percentage of rated capacity, whose successive reported values never
   increase. A newly measured capacity above the currently reported one is
   discarded, so an optimistic single measurement cannot make a worn pack look
   healthier than it was.

.. req:: The battery management system shall flag the state of charge as unreliable when pack current measurements have been unavailable for more than 5 seconds
   :id: REQ_SOC_INVALID_FLAG
   :status: draft
   :asil: A
   :traces_to: US_STATE_ESTIMATION

   The battery management system shall set an unreliable flag alongside the
   published state of charge whenever no valid pack current measurement has been
   received for more than 5 seconds, and shall clear the flag only after the
   next open-circuit-voltage correction. The flag is what lets the vehicle stop
   presenting a range prediction it cannot support.
