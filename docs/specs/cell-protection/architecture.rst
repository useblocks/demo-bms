Cell Protection — Architecture
==================================

Component overview
------------------

.. needuml::

   left to right direction
   hide stereotype
   skinparam rectangle<<external>> {
     BackgroundColor #F3F4F6
     BorderStyle dashed
   }

   rectangle "Cell AFE chain\n(hardware)" as AFE <<external>>
   rectangle "Pack current shunt\n(hardware)" as SHUNT <<external>>
   rectangle "HV contactors\n(hardware)" as CTR <<external>>
   rectangle "Diagnostic tester\n(external)" as DIAG <<external>>

   {{flow("ARCH_CELL_MEASUREMENT_ACQ")}}
   {{flow("ARCH_CURRENT_PATH_MONITOR")}}
   {{flow("ARCH_SAFETY_SUPERVISOR")}}
   {{flow("ARCH_CONTACTOR_ACTUATOR")}}
   {{flow("ARCH_FAULT_MEMORY")}}

   AFE --> ARCH_CELL_MEASUREMENT_ACQ
   SHUNT --> ARCH_CURRENT_PATH_MONITOR
   ARCH_CELL_MEASUREMENT_ACQ --> ARCH_SAFETY_SUPERVISOR : validated cell U/T samples
   ARCH_CURRENT_PATH_MONITOR --> ARCH_SAFETY_SUPERVISOR : filtered pack current
   ARCH_SAFETY_SUPERVISOR --> ARCH_CONTACTOR_ACTUATOR : open command + latch state
   ARCH_SAFETY_SUPERVISOR --> ARCH_FAULT_MEMORY : fault record
   ARCH_CONTACTOR_ACTUATOR --> CTR
   ARCH_FAULT_MEMORY <--> DIAG : read / service reset
   DIAG --> ARCH_SAFETY_SUPERVISOR : service reset

Elements
--------

.. arch:: Cell Measurement Acquisition
   :id: ARCH_CELL_MEASUREMENT_ACQ
   :status: draft
   :satisfies: REQ_CELL_VOLTAGE_LIMITS, REQ_CELL_OVERTEMPERATURE, REQ_MEASUREMENT_PLAUSIBILITY

   The Cell Measurement Acquisition element owns the cyclic readout of all cell
   voltages and cell temperatures from the daisy-chained analogue front-end
   devices, on a fixed 10 ms cycle. It converts each raw reading into millivolts
   and tenths of a degree Celsius, and stamps it with the cycle timestamp the
   downstream reaction-time budget is measured from. It is also the owner of the
   plausibility decision: for each module it computes the median of that module's
   cell voltages and marks any cell deviating from it by more than 250 mV as
   invalid, so an invalid reading is already tagged before any limit is
   evaluated.

.. arch:: Pack Current Path Monitor
   :id: ARCH_CURRENT_PATH_MONITOR
   :status: draft
   :satisfies: REQ_PACK_OVERCURRENT

   The Pack Current Path Monitor element owns the acquisition of the pack current
   from the shunt amplifier, sampled at 1 ms and reported with a signed sign
   convention in which discharge is positive. It holds the 100 ms persistence
   window as a monotonic timer that starts on the first sample above 350 A and
   resets on the first sample at or below it, so the supervisor receives an
   already-debounced overcurrent condition rather than a raw sample.

.. arch:: Cell Protection Safety Supervisor
   :id: ARCH_SAFETY_SUPERVISOR
   :status: draft
   :satisfies: REQ_CELL_VOLTAGE_LIMITS, REQ_PACK_OVERCURRENT, REQ_CELL_OVERTEMPERATURE, REQ_FAULT_LATCH

   The Cell Protection Safety Supervisor element is the single decision point of
   this stream. It evaluates every validated measurement against a static limit
   table (undervoltage, overvoltage, overtemperature, overcurrent) once per 10 ms
   cycle, and holds the latched safety state as a two-state machine, ``RUN`` and
   ``FAULT_LATCHED``, whose only exit from ``FAULT_LATCHED`` is a diagnostic
   service reset. It ignores measurements tagged invalid, and on the first
   violation it emits both the open command towards the contactor actuator and
   the fault record towards the fault memory.

.. arch:: High-Voltage Contactor Actuator
   :id: ARCH_CONTACTOR_ACTUATOR
   :status: draft
   :satisfies: REQ_FAULT_REACTION_TIME, REQ_FAULT_LATCH

   The High-Voltage Contactor Actuator element owns the two contactor coil
   drivers and drives them as a dual-channel low-side pair, so that de-energising
   either channel opens the circuit. It translates the supervisor's open command
   into a coil de-energise within one 10 ms cycle, which leaves the remaining
   40 ms of the 50 ms budget to acquisition and evaluation. While the supervisor
   reports ``FAULT_LATCHED`` it drives both channels off unconditionally and
   ignores any close request.

.. arch:: Cell Protection Fault Memory
   :id: ARCH_FAULT_MEMORY
   :status: draft
   :satisfies: REQ_FAULT_RECORD

   The Cell Protection Fault Memory element owns a fixed-size ring of 64 fault
   records in non-volatile memory. Each record is a fixed 16-byte layout carrying
   the sensor or cell identifier, the limit identifier, the measured value and
   the cycle timestamp. It serves those records over the diagnostic interface and
   is the element that consumes the service reset request, forwarding it to the
   supervisor once the record of the active fault has been written.
