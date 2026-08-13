Cell Protection — Software Requirements
===========================================

.. swreq:: The acquisition component shall publish one complete set of cell voltage and cell temperature samples every 10 ms
   :id: SWREQ_CELL_SAMPLE_CYCLE
   :status: draft
   :refines: ARCH_CELL_MEASUREMENT_ACQ

   The acquisition component shall publish, every 10 ms with a tolerance of 1 ms,
   one sample set containing exactly one voltage value in millivolts and one
   temperature value in tenths of a degree Celsius for every configured cell and
   sensor, together with the cycle timestamp in milliseconds. A sample set in
   which any configured channel is absent is not a complete set.

.. swreq:: The acquisition component shall mark a cell voltage sample invalid when it deviates from its module median by more than 250 mV
   :id: SWREQ_MODULE_MEDIAN_VALIDITY
   :status: draft
   :refines: ARCH_CELL_MEASUREMENT_ACQ

   The acquisition component shall compute, per module and per cycle, the median
   of that module's cell voltage samples, and shall set the invalid flag on every
   sample of that module whose absolute difference from the median exceeds
   250 mV. All other samples of the module carry a cleared invalid flag.

.. swreq:: The current monitor component shall report an overcurrent condition only after the pack current has stayed above 350 A for 100 ms
   :id: SWREQ_OVERCURRENT_DEBOUNCE
   :status: draft
   :refines: ARCH_CURRENT_PATH_MONITOR

   The current monitor component shall report an overcurrent condition on its
   output once its internal above-threshold timer, incremented by the 1 ms sample
   period on every sample above 350 A in the discharge direction and reset to
   zero on any sample at or below 350 A, has reached 100 ms. Until then the
   output reports no overcurrent condition.

.. swreq:: The supervisor component shall evaluate every valid sample against the static limit table once per 10 ms cycle
   :id: SWREQ_LIMIT_EVALUATION
   :status: draft
   :refines: ARCH_SAFETY_SUPERVISOR

   The supervisor component shall compare, once per 10 ms cycle, every sample of
   the received sample set that carries a cleared invalid flag against the four
   entries of the static limit table — undervoltage at 2.50 V, overvoltage at
   4.25 V, overtemperature at 60 °C, and the debounced overcurrent condition —
   and shall emit a limit-violation event naming the first entry that is
   violated.

.. swreq:: The supervisor component shall exclude every sample carrying a set invalid flag from limit evaluation
   :id: SWREQ_IGNORE_INVALID_SAMPLES
   :status: draft
   :refines: ARCH_SAFETY_SUPERVISOR

   The supervisor component shall skip any sample whose invalid flag is set when
   comparing samples against the limit table, so that such a sample can never
   produce a limit-violation event. A cycle in which every sample of the set is
   invalid produces no event at all.

.. swreq:: The supervisor component shall leave the FAULT_LATCHED state only on receipt of a diagnostic service reset
   :id: SWREQ_LATCH_STATE_MACHINE
   :status: draft
   :refines: ARCH_SAFETY_SUPERVISOR

   The supervisor component shall enter the ``FAULT_LATCHED`` state on the first
   limit-violation event and shall transition back to ``RUN`` only on receipt of
   a diagnostic service reset request. While in ``FAULT_LATCHED`` it keeps
   asserting the open command regardless of the values in subsequent sample sets.

.. swreq:: The contactor component shall de-energise both coil channels within 10 ms of receiving the open command
   :id: SWREQ_CONTACTOR_DEENERGISE
   :status: draft
   :refines: ARCH_CONTACTOR_ACTUATOR

   The contactor component shall drive both coil channel outputs to their
   de-energised level no later than 10 ms after the open command is asserted on
   its input, measured from the timestamp of the asserting call to the timestamp
   at which both outputs read de-energised.

.. swreq:: The fault memory component shall write a fault record within 20 ms of receiving a limit-violation event
   :id: SWREQ_FAULT_RECORD_WRITE
   :status: draft
   :refines: ARCH_FAULT_MEMORY

   The fault memory component shall append, no later than 20 ms after receiving a
   limit-violation event, one 16-byte record to the 64-entry ring carrying the
   channel identifier, the limit identifier, the measured value and the cycle
   timestamp of that event. When the ring is full the oldest record is
   overwritten.
