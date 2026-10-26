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
   :cr_approval_at: 2026-10-26T16:19:33Z
   :cr_status:
      approved | 2026-10-26T16:19:33Z | David Schmitt <david.schmitt@useblocks.com> | approved by David Schmitt <david.schmitt@useblocks.com>
      executed | 2026-10-26T16:21:06Z | David Schmitt <david.schmitt@useblocks.com> | recorded with --done, without running the cascade
      closed | 2026-10-26T16:28:04Z | David Schmitt <david.schmitt@useblocks.com> | closed by David Schmitt <david.schmitt@useblocks.com>

   **Purpose**

   A bench run that towed a trailer up a mountain pass at the 250 A sustained limit heated the pack to 58 °C, and the drive power was cut (issue #…). REQ_SUSTAINED_DISCHARGE_LIMIT now holds the sustained current to 200 A. Carry that through the software requirement, the code and the tests.

   **Planned changes**

   - SWREQ_SUSTAINED_LOAD_LIMIT: title and statement move from 250 A to 200 A, both as the 10 s average threshold and as the held current; the sustained-load share becomes 200 A / 320 A (62.5 %) instead of 250 A / 320 A (78.125 %). The 10 s window and the 320 A full-power reference are unchanged.
   - IMPL_SUSTAINED_LOAD_LIMIT: ``CONTINUOUS_DISCHARGE_LIMIT_A`` in ``src/thermal_management/power_limit.py`` moves from 250.0 to 200.0, and the codelinks marker title on ``sustained_load_share_pct`` is rewritten to say 200 A.
   - TEST_SUSTAINED_LOAD_LIMIT: the marker title and docstring say 200 A; the expected capped share becomes 62.5; the "below the limit" sample (currently exactly 200 A, which would now sit AT the limit) moves below 200 A, e.g. 150 A; the sustained full-power check expects the current to settle at 200.0 A instead of 250.0 A.
   - TRES_SUSTAINED_LOAD_LIMIT: its title carries the 250 A figure from the test; it is re-recorded by re-running the modified test, not edited by hand, so the title reads 200 A and the outcome reflects the new limit.

   **Exclusion rationale**

   - ARCH_POWER_LIMIT_CALCULATOR: describes a sustained-load limit computed from the pack discharge current without naming a value; its responsibilities, inputs and the min-of-three structure are unchanged.
   - DEC_HYSTERESIS_BANDS: concerns the separation of the cooling/heating hysteresis bands from the temperature derating ramp; the sustained-current limit plays no part in it.
   - SWREQ_TEMP_DERATE_RAMP: the 55–60 °C temperature ramp is independent of the current limit.
   - IMPL_TEMP_DERATE_RAMP: implements the unchanged temperature ramp; no reference to the current limit.
   - TEST_TEMP_DERATE_RAMP: verifies the unchanged ramp endpoints and midpoint.
   - TEST_TEMP_DERATE_MONOTONIC: verifies the unchanged ramp's monotonicity.
   - SWREQ_LIMIT_MINIMUM: requires publishing the minimum of the three shares; it names no current threshold, so it holds as written with a 200 A sustained-load share.
   - IMPL_LIMIT_MINIMUM: ``publish`` takes the sustained-load share as a parameter and takes the minimum; no value moves.
   - TEST_LIMIT_MINIMUM: feeds arbitrary sustained-load shares (40 %, 80 %, 70 %) directly into ``publish``; none is derived from 250 A, so the assertions stay valid.
   - TEST_LIMIT_ACTUATOR_SHARE: verifies the 30 % actuator fallback, unrelated to the current limit.
   - TRES_TEMP_DERATE_RAMP, TRES_TEMP_DERATE_MONOTONIC, TRES_LIMIT_MINIMUM, TRES_LIMIT_ACTUATOR_SHARE: results of tests this change does not touch; their titles carry no 250 A figure. They will be re-recorded by the next test run as usual, with no content change caused by this request.
   - US_THERMAL_MANAGEMENT: says the pack never draws more than its cells' continuous rating under sustained load, without naming a value; the 200 A figure refines how that intent is met, not the intent itself.
