:orphan:

Change to REQ_SUSTAINED_DISCHARGE_LIMIT: The battery management system shall limit the pack discharge current to 200 A once its 10 s average reaches 200 A
==========================================================================================================================================================

.. change_request:: Lower the sustained discharge limit from 250 A to 200 A
   :id: CR_SUSTAINED_DISCHARGE_LIMIT
   :cr_anchor: REQ_SUSTAINED_DISCHARGE_LIMIT
   :cr_computed_impact: ARCH_POWER_LIMIT_CALCULATOR, DEC_HYSTERESIS_BANDS, IMPL_LIMIT_MINIMUM, IMPL_SUSTAINED_LOAD_LIMIT, IMPL_TEMP_DERATE_RAMP, SWREQ_LIMIT_MINIMUM, SWREQ_SUSTAINED_LOAD_LIMIT, SWREQ_TEMP_DERATE_RAMP, TEST_LIMIT_ACTUATOR_SHARE, TEST_LIMIT_MINIMUM, TEST_SUSTAINED_LOAD_LIMIT, TEST_TEMP_DERATE_MONOTONIC, TEST_TEMP_DERATE_RAMP, TRES_LIMIT_ACTUATOR_SHARE, TRES_LIMIT_MINIMUM, TRES_SUSTAINED_LOAD_LIMIT, TRES_TEMP_DERATE_MONOTONIC, TRES_TEMP_DERATE_RAMP, US_THERMAL_MANAGEMENT
   :cr_potentially_affected: ARCH_THERMAL_STATE_EVALUATOR, REQ_POWER_DERATING, REQ_THERMAL_ACTUATOR_FAILSAFE
   :cr_impact_modify: SWREQ_SUSTAINED_LOAD_LIMIT, IMPL_SUSTAINED_LOAD_LIMIT, TEST_SUSTAINED_LOAD_LIMIT, TRES_SUSTAINED_LOAD_LIMIT
   :cr_impact_excluded: ARCH_POWER_LIMIT_CALCULATOR, DEC_HYSTERESIS_BANDS, IMPL_LIMIT_MINIMUM, IMPL_TEMP_DERATE_RAMP, SWREQ_LIMIT_MINIMUM, SWREQ_TEMP_DERATE_RAMP, TEST_LIMIT_ACTUATOR_SHARE, TEST_LIMIT_MINIMUM, TEST_TEMP_DERATE_MONOTONIC, TEST_TEMP_DERATE_RAMP, TRES_LIMIT_ACTUATOR_SHARE, TRES_LIMIT_MINIMUM, TRES_TEMP_DERATE_MONOTONIC, TRES_TEMP_DERATE_RAMP, US_THERMAL_MANAGEMENT
   :cr_approval_decision: approved
   :cr_approval_by: Marco Heinemann <marco.heinemann@useblocks.com>
   :cr_approval_at: 2026-10-26T12:59:25Z
   :cr_status:
      approved | 2026-10-26T12:59:25Z | Marco Heinemann <marco.heinemann@useblocks.com> | LGTM
      executed | 2026-10-26T13:01:48Z | Marco Heinemann <marco.heinemann@useblocks.com> | recorded with --done, without running the cascade
      closed | 2026-10-26T13:18:09Z | Marco Heinemann <marco.heinemann@useblocks.com> | closed by Marco Heinemann <marco.heinemann@useblocks.com>

   **Purpose**

   A bench run that towed a trailer up a mountain pass at the 250 A sustained limit heated the pack to 58 °C, and the drive power was cut (issue #…). REQ_SUSTAINED_DISCHARGE_LIMIT now holds the sustained current to 200 A. Carry that through the software requirement, the code and the tests.

   **Planned changes**

   - SWREQ_SUSTAINED_LOAD_LIMIT: title and statement move the threshold and the held current from 250 A to 200 A; the capped share becomes 200 A divided by the 320 A full permitted power draws (62.5 %) while the trailing 10 s average is at or above 200 A, and 100 % below 200 A.
   - IMPL_SUSTAINED_LOAD_LIMIT: ``CONTINUOUS_DISCHARGE_LIMIT_A`` in ``src/thermal_management/power_limit.py`` moves from 250.0 to 200.0, and the codelinks marker title on ``sustained_load_share_pct`` changes from 250 A to 200 A. The logic is unchanged.
   - TEST_SUSTAINED_LOAD_LIMIT: in ``test_sustained_load_share_holds_the_current_at_the_limit`` the marker title and docstring move to 200 A; the "below the limit" sample (currently 200 A, which is now AT the limit) drops below 200 A, e.g. 150 A; the expected capped share becomes 62.5 instead of 78.125; the sustained full-power demand must settle at 200.0 A instead of 250.0 A; the comments naming 250 A follow.
   - TRES_SUSTAINED_LOAD_LIMIT: re-imported from a fresh test run after the test above is updated, so its title carries 200 A and its outcome reflects the new expectation. Not hand-edited.

   **Exclusion rationale**

   - ARCH_POWER_LIMIT_CALCULATOR: describes the sustained-load limit only as "computed from the pack discharge current" with no current value, and its ``:satisfies:`` already includes the anchor; nothing in it is made wrong by 200 A.
   - DEC_HYSTERESIS_BANDS: concerns the separation of the temperature hysteresis bands from the temperature ramp; it says nothing about discharge current.
   - SWREQ_TEMP_DERATE_RAMP: the 55–60 °C temperature ramp is independent of the current threshold.
   - IMPL_TEMP_DERATE_RAMP: implements the temperature ramp only; no current constant is involved.
   - TEST_TEMP_DERATE_RAMP: asserts temperature-ramp endpoints only; unaffected by the current threshold.
   - TEST_TEMP_DERATE_MONOTONIC: asserts monotonicity of the temperature ramp only; unaffected.
   - SWREQ_LIMIT_MINIMUM: specifies taking the minimum of the three shares; it names no current value, so lowering the threshold leaves it correct.
   - IMPL_LIMIT_MINIMUM: ``publish`` receives the sustained-load share as a parameter and takes the minimum; it does not read the current constant.
   - TEST_LIMIT_MINIMUM: passes explicit ``sustained_load_pct`` values (40, 80, 70) and never derives them from 250 A, so its expectations hold at 200 A.
   - TEST_LIMIT_ACTUATOR_SHARE: asserts the flat 30 % actuator share only; unaffected.
   - TRES_TEMP_DERATE_RAMP, TRES_TEMP_DERATE_MONOTONIC, TRES_LIMIT_MINIMUM, TRES_LIMIT_ACTUATOR_SHARE: their tests are not changed by this CR, so their recorded outcome, title and ``:chain_reqs:`` stay valid; a re-import for TRES_SUSTAINED_LOAD_LIMIT may refresh their run stamp, but no content of theirs changes because of this CR.
   - US_THERMAL_MANAGEMENT: phrases the sustained-load behaviour as "never draws more current than its cells are rated to deliver continuously" without a number; the trailer scenario already motivates the lower limit, so the story stays accurate.

   Tier 2 (ARCH_THERMAL_STATE_EVALUATOR, REQ_POWER_DERATING, REQ_THERMAL_ACTUATOR_FAILSAFE) is not pulled into scope: none of them states a discharge current value. The anchor REQ_SUSTAINED_DISCHARGE_LIMIT is left out of the impact links because it was already edited to 200 A as the start of this change. No new obligation (need) is created: the existing test covers the new value once updated.
