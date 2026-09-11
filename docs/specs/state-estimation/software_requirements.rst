State Estimation — Software Requirements
============================================

.. swreq:: The coulomb counter component shall update the accumulated charge by trapezoidal integration on every 10 ms tick
   :id: SWREQ_CHARGE_INTEGRATION
   :status: draft
   :refines: ARCH_COULOMB_COUNTER

   The coulomb counter component shall add, on every 10 ms tick, the mean of the
   current sample of this tick and the current sample of the previous tick
   multiplied by 0.01 seconds to its ampere-second accumulator. The first tick
   after initialisation contributes nothing, because no previous sample exists to
   average against.

.. swreq:: The corrector component shall report a rest condition after the absolute pack current has stayed below 1 A for 30 minutes
   :id: SWREQ_REST_DETECTION
   :status: draft
   :refines: ARCH_OCV_CORRECTOR

   The corrector component shall report a rest condition once its internal rest
   timer, incremented by the tick period on every tick whose absolute current
   sample is below 1 A and reset to zero on any tick at or above 1 A, has reached
   1800 seconds. The reported condition clears on the next reset of that timer.

.. swreq:: The corrector component shall derive the state of charge from the mean cell voltage by linear interpolation in the 21-point open-circuit-voltage table
   :id: SWREQ_OCV_TABLE_LOOKUP
   :status: draft
   :refines: ARCH_OCV_CORRECTOR

   The corrector component shall map a mean cell voltage to a state of charge by
   locating the two adjacent table points that bracket the voltage and
   interpolating linearly between their state-of-charge values. A voltage below
   the first point yields 0 %, and a voltage above the last point yields 100 %.

.. swreq:: The store component shall write the two-slot state-of-charge record on every shutdown request and every 60 seconds while awake
   :id: SWREQ_SOC_PERSIST_WRITE
   :status: draft
   :refines: ARCH_SOC_STORE

   The store component shall write one record — state of charge, write counter
   incremented by one, and checksum over both — into the slot not used by the
   previous write, on every shutdown request and additionally whenever 60 seconds
   have passed since its last write. The slot it overwrites is always the one
   carrying the lower write counter.

.. swreq:: The store component shall restore the state of charge from the valid slot carrying the higher write counter
   :id: SWREQ_SOC_RESTORE_SLOT
   :status: draft
   :refines: ARCH_SOC_STORE

   The store component shall, on initialisation, verify the checksum of both
   slots and return the state of charge of whichever checksum-valid slot carries
   the higher write counter. When neither slot is checksum-valid it reports that
   no stored value is available.

.. swreq:: The capacity tracker component shall discard every capacity candidate that is above the currently reported capacity
   :id: SWREQ_CAPACITY_MONOTONIC_CLAMP
   :status: draft
   :refines: ARCH_SOH_TRACKER

   The capacity tracker component shall accept a new capacity candidate as the
   reported capacity only when the candidate is strictly below the currently
   reported capacity, and shall leave the reported capacity unchanged otherwise.
   The reported capacity therefore forms a non-increasing sequence over the life
   of the component.

.. swreq:: The validity monitor component shall raise the unreliable verdict after 5 seconds without a valid pack current sample
   :id: SWREQ_CURRENT_STALENESS_TIMER
   :status: draft
   :refines: ARCH_ESTIMATION_VALIDITY_MONITOR

   The validity monitor component shall raise the unreliable verdict once its
   staleness timer, reset to zero by every valid pack current sample and
   incremented by the elapsed time otherwise, has exceeded 5 seconds. The verdict
   clears only on notification of a completed open-circuit-voltage correction.

.. swreq:: The publisher component shall send the battery state frame every 100 ms
   :id: SWREQ_STATE_FRAME_PERIOD
   :status: draft
   :refines: ARCH_STATE_PUBLISHER

   The publisher component shall send one battery state frame, carrying the last
   values it holds for state of charge, remaining capacity and the validity
   verdict, every 100 ms with a tolerance of 10 ms while the system is awake. A
   producer that has not updated its value since the previous frame does not
   delay or suppress the frame.
