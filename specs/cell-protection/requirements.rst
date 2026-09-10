Cell Protection — Requirements
==================================

.. req:: The battery management system shall open the high-voltage contactors when any cell voltage leaves the range 2.50 V to 4.25 V
   :id: REQ_CELL_VOLTAGE_LIMITS
   :status: draft
   :traces_to:

   The battery management system shall command the high-voltage contactors open
   whenever a valid cell voltage measurement is below 2.50 V or above 4.25 V.
   The limits apply to every cell of the pack individually, so a single cell
   outside the range is sufficient to trigger the reaction, regardless of the
   pack voltage.

.. req:: The battery management system shall open the high-voltage contactors when the pack discharge current exceeds 350 A for more than 100 ms
   :id: REQ_PACK_OVERCURRENT
   :status: draft
   :traces_to: US_CELL_PROTECTION

   The battery management system shall command the high-voltage contactors open
   whenever the measured pack current in the discharge direction stays above
   350 A continuously for more than 100 ms. Currents above the limit that fall
   back below it within 100 ms do not trigger the reaction, so a normal
   acceleration inrush is not treated as a fault.

.. req:: The battery management system shall open the high-voltage contactors when any cell temperature exceeds 60 °C
   :id: REQ_CELL_OVERTEMPERATURE
   :status: draft
   :traces_to: US_CELL_PROTECTION

   The battery management system shall command the high-voltage contactors open
   whenever a valid cell temperature measurement is above 60 °C. The limit
   applies to every temperature sensor of the pack individually, so one sensor
   above the limit is sufficient to trigger the reaction.

.. req:: The battery management system shall issue the contactor-open command within 50 ms of detecting a cell-protection limit violation
   :id: REQ_FAULT_REACTION_TIME
   :status: draft
   :traces_to: US_CELL_PROTECTION

   The battery management system shall issue the contactor-open command no later
   than 50 ms after the measurement sample that first violated a cell-protection
   limit. The interval is measured from the timestamp of that sample to the
   timestamp of the command on the contactor interface.

.. req:: The battery management system shall classify a cell voltage measurement as invalid when it deviates from its module median by more than 250 mV
   :id: REQ_MEASUREMENT_PLAUSIBILITY
   :status: draft
   :traces_to: US_CELL_PROTECTION

   The battery management system shall mark a cell voltage measurement invalid
   whenever its absolute difference from the median of the cell voltages of the
   same module exceeds 250 mV. An invalid measurement is not used to evaluate a
   cell-protection limit, so a single failed sensor cannot by itself command the
   contactors open.

.. req:: The battery management system shall keep the high-voltage contactors open after a cell-protection fault until a diagnostic service reset is received
   :id: REQ_FAULT_LATCH
   :status: draft
   :traces_to: US_CELL_PROTECTION

   The battery management system shall hold the contactor-open command after a
   cell-protection fault, and shall release it only after receiving a diagnostic
   service reset request. Measurements returning inside their limits do not
   release the hold, so an intermittent condition cannot re-close the
   high-voltage circuit without a service action.

.. req:: The battery management system shall store a fault record naming the cell identifier, the violated limit and the measured value for every cell-protection fault
   :id: REQ_FAULT_RECORD
   :status: draft
   :traces_to: US_CELL_PROTECTION

   The battery management system shall write one fault record per cell-protection
   fault into non-volatile memory, and each record shall carry the identifier of
   the cell or sensor concerned, the identifier of the limit that was violated,
   and the measured value at the violating sample. The record remains readable
   over the diagnostic interface after a power cycle.
