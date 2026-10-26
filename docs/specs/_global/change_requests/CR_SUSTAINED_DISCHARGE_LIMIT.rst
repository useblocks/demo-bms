:orphan:

Change to REQ_SUSTAINED_DISCHARGE_LIMIT: The battery management system shall limit the pack discharge current to 200 A once its 10 s average reaches 200 A
==========================================================================================================================================================

.. change_request:: Change to REQ_SUSTAINED_DISCHARGE_LIMIT: The battery management system shall limit the pack discharge current to 200 A once its 10 s average reaches 200 A
   :id: CR_SUSTAINED_DISCHARGE_LIMIT
   :cr_anchor: REQ_SUSTAINED_DISCHARGE_LIMIT
   :cr_computed_impact: ARCH_POWER_LIMIT_CALCULATOR, DEC_HYSTERESIS_BANDS, IMPL_LIMIT_MINIMUM, IMPL_SUSTAINED_LOAD_LIMIT, IMPL_TEMP_DERATE_RAMP, SWREQ_LIMIT_MINIMUM, SWREQ_SUSTAINED_LOAD_LIMIT, SWREQ_TEMP_DERATE_RAMP, TEST_LIMIT_ACTUATOR_SHARE, TEST_LIMIT_MINIMUM, TEST_SUSTAINED_LOAD_LIMIT, TEST_TEMP_DERATE_MONOTONIC, TEST_TEMP_DERATE_RAMP, TRES_LIMIT_ACTUATOR_SHARE, TRES_LIMIT_MINIMUM, TRES_SUSTAINED_LOAD_LIMIT, TRES_TEMP_DERATE_MONOTONIC, TRES_TEMP_DERATE_RAMP, US_THERMAL_MANAGEMENT
   :cr_potentially_affected: ARCH_THERMAL_STATE_EVALUATOR, REQ_POWER_DERATING, REQ_THERMAL_ACTUATOR_FAILSAFE
   :cr_impact_modify: SWREQ_SUSTAINED_LOAD_LIMIT, IMPL_SUSTAINED_LOAD_LIMIT, TEST_SUSTAINED_LOAD_LIMIT, TRES_SUSTAINED_LOAD_LIMIT
   :cr_impact_excluded: ARCH_POWER_LIMIT_CALCULATOR, DEC_HYSTERESIS_BANDS, IMPL_LIMIT_MINIMUM, IMPL_TEMP_DERATE_RAMP, SWREQ_LIMIT_MINIMUM, SWREQ_TEMP_DERATE_RAMP, TEST_LIMIT_ACTUATOR_SHARE, TEST_LIMIT_MINIMUM, TEST_TEMP_DERATE_MONOTONIC, TEST_TEMP_DERATE_RAMP, TRES_LIMIT_ACTUATOR_SHARE, TRES_LIMIT_MINIMUM, TRES_TEMP_DERATE_MONOTONIC, TRES_TEMP_DERATE_RAMP, US_THERMAL_MANAGEMENT
   :cr_approval_decision: approved
   :cr_approval_by: David Schmitt <david.schmitt@useblocks.com>
   :cr_approval_at: 2026-10-26T21:42:29Z
   :cr_status:
      approved | 2026-10-26T21:42:29Z | David Schmitt <david.schmitt@useblocks.com> | approved by David Schmitt <david.schmitt@useblocks.com>
      executed | 2026-10-26T21:44:06Z | David Schmitt <david.schmitt@useblocks.com> | recorded with --done, without running the cascade
      closed | 2026-10-26T21:45:12Z | David Schmitt <david.schmitt@useblocks.com> | closed by David Schmitt <david.schmitt@useblocks.com>

   **Purpose**

   A bench run that towed a trailer up a mountain pass at the 250 A sustained limit heated the pack to 58 °C, and the drive power was cut. REQ_SUSTAINED_DISCHARGE_LIMIT now holds the sustained current to 200 A. Carry that through the software requirement, the code and the tests.

   **Planned changes**

   - SWREQ_SUSTAINED_LOAD_LIMIT: move the sustained-load threshold and cap from 250 A to 200 A in the title and body; the capped share becomes 200 A divided by the 320 A full-power draw (62.5 %, was 78.125 %), applied while the trailing 10 s average is at or above 200 A and released below 200 A.
   - IMPL_SUSTAINED_LOAD_LIMIT: change the threshold and cap constant in the code from 250 A to 200 A so the share computed is 200/320, and update the codelinks marker title from 250 A to 200 A.
   - TEST_SUSTAINED_LOAD_LIMIT: move the test's stimulus and expected values to the 200 A threshold (average just below 200 A gives 100 %; at or above 200 A gives the share that draws 200 A), and update the marker title from 250 A to 200 A.
   - TRES_SUSTAINED_LOAD_LIMIT: the recorded result belongs to the 250 A version of the test. Re-run the test and record it again under the 200 A title.

   **Exclusion rationale**

   - ARCH_POWER_LIMIT_CALCULATOR: describes the sustained-load limit only as "computed from the pack discharge current" and does not state a value, so its allocation and its minimum-of-three structure still hold at 200 A.
   - DEC_HYSTERESIS_BANDS: concerns the temperature hysteresis bands and the temperature ramp only, and the sustained-current threshold is not part of that decision.
   - SWREQ_LIMIT_MINIMUM: takes the minimum of the three shares regardless of how the sustained-load share is computed, so nothing in its statement depends on the current threshold.
   - IMPL_LIMIT_MINIMUM: implements the minimum selection, which stays the same.
   - TEST_LIMIT_MINIMUM: checks that the smallest share is the one selected, not the value of the sustained-load threshold.
   - TRES_LIMIT_MINIMUM: TEST_LIMIT_MINIMUM is unchanged, so its recorded result is still valid.
   - TEST_LIMIT_ACTUATOR_SHARE: checks the 30 % actuator fallback share, which this change does not touch.
   - TRES_LIMIT_ACTUATOR_SHARE: TEST_LIMIT_ACTUATOR_SHARE is unchanged, so its recorded result is still valid.
   - SWREQ_TEMP_DERATE_RAMP: the 55 °C to 60 °C temperature ramp does not depend on the discharge current.
   - IMPL_TEMP_DERATE_RAMP: implements the temperature ramp, which stays the same.
   - TEST_TEMP_DERATE_RAMP: checks the temperature ramp end points and midpoint, which stay the same.
   - TEST_TEMP_DERATE_MONOTONIC: checks that the temperature ramp decreases monotonically, which stays the same.
   - TRES_TEMP_DERATE_RAMP: TEST_TEMP_DERATE_RAMP is unchanged, so its recorded result is still valid.
   - TRES_TEMP_DERATE_MONOTONIC: TEST_TEMP_DERATE_MONOTONIC is unchanged, so its recorded result is still valid.
   - US_THERMAL_MANAGEMENT: the story promises only that the pack "never draws more current than its cells are rated to deliver continuously". It names no ampere value. A 200 A limit is lower than the former 250 A, which the anchor described as the continuous rating, so that promise still holds.
