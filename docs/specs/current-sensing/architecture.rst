Current Sensing — Architecture
==============================

Elements
--------

.. arch:: Pack Current Sensor
   :id: ARCH_PACK_CURRENT_SENSOR
   :status: draft
   :satisfies: REQ_CURRENT_ACCURACY, REQ_OVERCURRENT_DETECTION

   The Pack Current Sensor element turns the current in the negative main
   busbar into a calibrated, temperature-compensated value every 10 ms, and
   raises a separate hardware overcurrent line within 1 ms of the 800 A
   threshold. Whether it is a shunt with in-house measurement firmware or a
   bought current-sensor module is the open make-or-buy decision of this
   stream.

.. arch:: Charge Counter
   :id: ARCH_CHARGE_COUNTER
   :status: draft
   :satisfies: REQ_CURRENT_ACCURACY
   :sourcing: inhouse

   The Charge Counter element integrates the calibrated pack current over time
   into the charge moved since the last full charge, and hands it to the state
   estimation stream. It owns the integration, not the measurement.
