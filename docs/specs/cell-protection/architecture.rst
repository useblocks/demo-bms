Cell Protection — Architecture
==================================

Component overview
------------------

.. mermaid::

   flowchart LR
       AFE[["Cell AFE chain<br/>(hardware)"]]
       SHUNT[["Pack current shunt<br/>(hardware)"]]
       CTR[["HV contactors<br/>(hardware)"]]
       DIAG[["Diagnostic tester<br/>(external)"]]

       ACQ["ARCH_CELL_MEASUREMENT_ACQ<br/>Cell Measurement Acquisition"]
       CUR["ARCH_CURRENT_PATH_MONITOR<br/>Pack Current Path Monitor"]
       SUP["ARCH_SAFETY_SUPERVISOR<br/>Cell Protection Safety Supervisor"]
       ACT["ARCH_CONTACTOR_ACTUATOR<br/>HV Contactor Actuator"]
       MEM["ARCH_FAULT_MEMORY<br/>Cell Protection Fault Memory"]

       AFE --> ACQ
       SHUNT --> CUR
       ACQ -- "validated cell U/T samples" --> SUP
       CUR -- "filtered pack current" --> SUP
       SUP -- "open command + latch state" --> ACT
       SUP -- "fault record" --> MEM
       ACT --> CTR
       MEM <-- "read / service reset" --> DIAG
       DIAG -- "service reset" --> SUP

Elements
--------

.. arch:: Cell Measurement Acquisition
   :id: ARCH_CELL_MEASUREMENT_ACQ
   :status: draft
   :satisfies: JAMA_Rollout_Demo-SYSRQ-3[fingerprint=="2e04648b"], JAMA_Rollout_Demo-SYSRQ-5[fingerprint=="3b70e418"], JAMA_Rollout_Demo-SYSRQ-7[fingerprint=="ba6b7f45"]

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
   :satisfies: JAMA_Rollout_Demo-SYSRQ-4

   The Pack Current Path Monitor element owns the acquisition of the pack current
   from the shunt amplifier, sampled at 1 ms and reported with a signed sign
   convention in which discharge is positive. It holds the 100 ms persistence
   window as a monotonic timer that starts on the first sample above 350 A and
   resets on the first sample at or below it, so the supervisor receives an
   already-debounced overcurrent condition rather than a raw sample.

.. arch:: Cell Protection Safety Supervisor
   :id: ARCH_SAFETY_SUPERVISOR
   :status: draft
   :satisfies: JAMA_Rollout_Demo-SYSRQ-3[fingerprint=="2e04648b"], JAMA_Rollout_Demo-SYSRQ-4[fingerprint=="0824db15"], JAMA_Rollout_Demo-SYSRQ-5[fingerprint=="3b70e418"], JAMA_Rollout_Demo-SYSRQ-8[fingerprint=="ebe64430"]

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
   :satisfies: JAMA_Rollout_Demo-SYSRQ-6[fingerprint=="2814bece"], JAMA_Rollout_Demo-SYSRQ-8[fingerprint=="ebe64430"]

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
   :satisfies: JAMA_Rollout_Demo-SYSRQ-9[fingerprint=="aac71062"]

   The Cell Protection Fault Memory element owns a fixed-size ring of 64 fault
   records in non-volatile memory. Each record is a fixed 16-byte layout carrying
   the sensor or cell identifier, the limit identifier, the measured value and
   the cycle timestamp. It serves those records over the diagnostic interface and
   is the element that consumes the service reset request, forwarding it to the
   supervisor once the record of the active fault has been written.
