Design Decisions
================

.. decision:: Fuse coulomb counting with an open-circuit-voltage anchor rather than run a Kalman filter
   :id: DEC_COULOMB_PLUS_OCV
   :status: draft
   :affects: ARCH_COULOMB_COUNTER, ARCH_OCV_CORRECTOR

   **Context**

   The reported state of charge has to stay within 3 % of rated capacity across
   the 10–90 % band, on a microcontroller whose remaining budget for the whole
   estimation stream is roughly 5 % of one core and 8 kB of RAM. Coulomb counting
   alone drifts without bound; a cell voltage reading alone is unusable under
   load because the internal resistance drop swamps the open-circuit voltage.

   **Alternatives**

   An extended Kalman filter over an equivalent-circuit cell model was rejected:
   it meets the accuracy target comfortably but needs a per-cell-chemistry
   parameter set, a matrix library, and roughly ten times the compute budget we
   have, and its tuning is not reviewable by the safety team. Pure coulomb
   counting with a periodic full-charge reset was rejected because a vehicle that
   is never charged to 100 % never resets, which is exactly the fleet duty cycle
   we are designing for. A voltage-only lookup on every cycle was rejected
   because it is wrong by tens of percent under load.

   **Consequences**

   Absolute accuracy now depends on the vehicle standing still for 30 minutes
   often enough to take an anchor, which we accept as a duty-cycle assumption
   that has to be stated and monitored rather than designed away — hence the
   separate validity monitor and the unreliable flag. It also splits the
   estimator into two elements with a narrow interface, which keeps each one
   individually reviewable, and it defers any model-based estimation to a
   possible later variant.

   **Rationale**

   The fused counter-plus-anchor design is the only one of the three that hits
   the accuracy target inside the compute budget while staying simple enough for
   the safety team to review by reading it.

.. decision:: Drive the high-voltage contactors as a dual-channel low-side pair
   :id: DEC_DUAL_CHANNEL_CONTACTOR
   :status: draft
   :affects: ARCH_CONTACTOR_ACTUATOR

   **Context**

   Opening the high-voltage circuit is the only reaction the cell-protection
   stream has, so a single stuck driver output would remove the whole protection
   effect while every other element still reports healthy. The reaction also has
   to complete inside a 50 ms system budget.

   **Alternatives**

   A single coil driver with a read-back diagnostic was rejected: the read-back
   detects the stuck output but cannot open the circuit once it is stuck, so the
   protection effect still depends on one part. A high-side plus low-side pair on
   the same coil was rejected because both switches sit in the same current path,
   so a welded contactor defeats both.

   **Consequences**

   Either channel de-energising is sufficient to open the circuit, so no single
   driver failure removes the protection. The cost is a second driver stage, a
   second diagnostic path, and roughly 15 % more board area in the driver
   section. It also means the actuator can never confirm "closed" from one
   channel alone, which the close path has to account for.

   **Rationale**

   Two independent channels turn a single-point failure into a detected,
   non-critical one, which is what the reaction being the only available
   protection measure requires.

.. decision:: Keep the cell-protection limits in a static table rather than a calibratable parameter set
   :id: DEC_SUPERVISOR_LIMIT_TABLE
   :status: draft
   :affects: ARCH_SAFETY_SUPERVISOR

   **Context**

   The four protection limits decide when the pack disconnects. They are also
   exactly the values an application engineer would most like to tune on a test
   bench, and exactly the values that must not be tunable in a shipped vehicle.

   **Alternatives**

   Holding the limits in the calibratable parameter area was rejected: it makes
   bench work convenient but puts the safety limits behind the same
   write-protection as ordinary calibration data, so any tool that can flash
   calibration can move them. Reading them from the diagnostic interface at
   start-up was rejected for the same reason plus a start-up dependency on a bus
   that may be silent.

   **Consequences**

   The limits are compiled in, so changing one is a software release with the
   full review and test chain behind it, and bench experiments need a dedicated
   engineering build. In exchange the shipped limits cannot be moved by any field
   tool, and the supervisor has no start-up dependency on external data.

   **Rationale**

   A limit that decides whether the pack disconnects belongs in the artefact that
   goes through the safety review chain, not in the one that is designed to be
   rewritten in the field.

.. decision:: Persist the state of charge in two alternating slots instead of one journalled record
   :id: DEC_TWO_SLOT_PERSISTENCE
   :status: draft
   :affects: ARCH_SOC_STORE

   **Context**

   The stored state of charge must survive an unannounced power loss, including
   one that lands in the middle of the write itself, and the available
   non-volatile area is a few hundred bytes with a limited erase-cycle budget.

   **Alternatives**

   A single record with a checksum was rejected: a power loss during its write
   leaves no valid copy at all, which is the case we are trying to survive. A
   full journal with a replayable log was rejected as disproportionate — it
   costs more area and erase cycles than the whole store is allowed, to protect
   one float.

   **Consequences**

   An interrupted write can only ever corrupt the older of the two records, so
   one valid copy always remains, and the reader picks a winner by write counter.
   The cost is double the storage area and a restore path that has to handle "no
   valid slot" explicitly rather than assuming a value is always there.

   **Rationale**

   Two slots are the smallest structure that makes an interrupted write
   survivable, which a single checksummed record is not, at a fraction of a
   journal's cost.

.. decision:: Separate the cooling and heating hysteresis bands from the power derating ramp
   :id: DEC_HYSTERESIS_BANDS
   :status: draft
   :affects: ARCH_THERMAL_STATE_EVALUATOR, ARCH_POWER_LIMIT_CALCULATOR

   **Context**

   Both the actuator requests and the permitted discharge power are driven by the
   same highest-cell-temperature figure, but they need opposite behaviour at the
   threshold: an actuator request must not chatter, and a power limit must not
   step.

   **Alternatives**

   One shared hysteresis band feeding both outputs was rejected: it stops the
   chatter but makes the power limit jump at the switching point, which the
   driver feels as the pack cutting in and out. One shared linear ramp feeding
   both was rejected: it smooths the power but leaves the pump switching on and
   off around the threshold.

   **Consequences**

   The evaluator owns two Schmitt-trigger bands and the limit calculator owns a
   linear ramp, so each output gets the shape it needs and the two can be tuned
   independently. The cost is that the same temperature figure is interpreted in
   two places, so a future change to the sensor set has to be reflected in both
   elements.

   **Rationale**

   The two outputs have genuinely different failure modes at the threshold, so
   giving each its own transfer function is cheaper than accepting either the
   chatter or the power step.
