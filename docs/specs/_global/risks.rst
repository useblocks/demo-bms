Risks
=====

.. risk:: A single overheating cell propagates into a pack-wide thermal runaway
   :id: RISK_THERMAL_RUNAWAY_PROPAGATION
   :status: draft
   :mitigates: JAMA_Rollout_Demo-SYSRQ-5, JAMA_Rollout_Demo-SYSRQ-6

   **Cause**: an internal short in one cell raises its temperature far faster
   than the surrounding cells, and the energy it releases heats its neighbours
   past their own runaway onset.

   **Effect**: a pack-wide fire that no software reaction can stop once it has
   started. Severity is the highest the project recognises; the vehicle and its
   occupants are at risk.

   **Mitigation**: the 60 °C per-sensor limit and the 50 ms reaction budget are
   both set so that the pack is disconnected while the event is still confined to
   one cell. The limit is deliberately per sensor rather than per pack average,
   because an average hides exactly the single-cell case this risk is about.

   **Residual**: a short that develops between two temperature sensors is
   detected later than one directly at a sensor. Sensor placement density is a
   hardware measure outside this project's scope.

.. risk:: A welded or stuck contactor leaves the pack connected after a protection fault
   :id: RISK_STUCK_CONTACTOR
   :status: draft
   :mitigates: JAMA_Rollout_Demo-SYSRQ-8

   **Cause**: repeated interruption of high current welds a contactor's contacts,
   or a coil driver output fails in the energised state.

   **Effect**: the protection reaction is commanded and reported as executed, but
   the high-voltage circuit stays live. Every other element continues to report
   healthy, so the failure is silent.

   **Mitigation**: the latch keeps the open command asserted indefinitely rather
   than retrying and giving up, and the dual-channel driver means one failed
   output does not keep the circuit closed. The latch also forces a service
   action, which is where the welded contact is found.

   **Residual**: a mechanically welded contactor cannot be opened by software at
   all. Detecting it requires a high-voltage measurement across the contactor,
   which this project does not own.

.. risk:: A slowly drifting cell sensor stays inside the plausibility band
   :id: RISK_SENSOR_DRIFT_UNDETECTED
   :status: draft
   :mitigates: JAMA_Rollout_Demo-SYSRQ-7

   **Cause**: an ageing analogue front-end channel drifts by less than the 250 mV
   plausibility window, so every individual reading looks plausible against its
   module median.

   **Effect**: a protection limit is evaluated against a wrong value. A drift
   towards the middle of the range is the dangerous direction: the real cell can
   sit outside its window while the reported value does not.

   **Mitigation**: the plausibility check is against the module median rather than
   a fixed band, so a drifting channel is compared against its neighbours as they
   age with it. The 250 mV window is set well below the margin between the
   protection limits and the cell's true damage thresholds.

   **Residual**: a drift smaller than 250 mV remains undetected by design. Closing
   it needs a periodic absolute reference measurement, which is a candidate for a
   later software release.

.. risk:: An overestimated state of charge strands the vehicle
   :id: RISK_SOC_OVERESTIMATE_STRANDING
   :status: draft
   :mitigates: JAMA_Rollout_Demo-SYSRQ-11, JAMA_Rollout_Demo-SYSRQ-16

   **Cause**: accumulated counting drift with no rest period long enough to take
   an open-circuit-voltage anchor, or a lost current signal during a long drive.

   **Effect**: the driver is shown a range the pack cannot deliver and stops
   without warning. For a fleet the cost is a recovery, not a safety event, but
   trust in the reported figure is lost permanently.

   **Mitigation**: the accuracy requirement bounds the error inside the band that
   matters, the rest correction bounds the drift whenever the duty cycle allows
   it, and the unreliable flag is what lets the vehicle stop presenting a
   prediction it cannot support instead of presenting a wrong one.

   **Residual**: a vehicle that is driven continuously and never rests keeps
   accumulating drift until the staleness limit raises the flag. The flag is the
   accepted fallback, not a fix.

.. risk:: Loss of coolant flow is invisible to the battery management system
   :id: RISK_COOLANT_LOSS
   :status: draft
   :mitigates: JAMA_Rollout_Demo-SYSRQ-21

   **Cause**: a failed pump, an air lock, or a leak means a raised cooling
   request moves no heat, while the request itself is acknowledged normally.

   **Effect**: the pack heats up under load with no thermal authority left. Left
   unhandled it walks into the cell-protection overtemperature limit and
   disconnects the pack mid-drive.

   **Mitigation**: the acknowledgement timeout turns an unanswered request into an
   explicit unconfirmed verdict, and the 30 % fallback limit caps the power the
   pack is allowed to deliver so the temperature rise slows instead of continuing
   at full load.

   **Residual**: an actuator that acknowledges normally while moving no coolant is
   not detected by this measure. Detecting it needs a coolant flow or
   differential-temperature signal, which is a hardware measure outside this
   project's scope.
