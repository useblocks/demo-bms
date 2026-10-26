Test Results
==============

.. warning::

   **Generated file — do not edit by hand.** Written by
   ``tools/import_test_results.py`` from ``docs/reports/junit/testresults.xml``.
   Re-generate it with::

      python3 -m pytest -q --junitxml=docs/reports/junit/testresults.xml
      python3 tools/import_test_results.py

   The report is a **committed snapshot**: the suite is not re-run on every
   build, so these needs record what happened in the run named below, not
   what would happen now.

Run ``2026-10-26 12:45:34 +01:00`` — 53 test cases, 2 failed, 51 passed, 0.050 s total.

Every need below carries ``results_for`` up to the ``test`` need whose execution it records, so a query can walk requirement → software requirement → test → recorded outcome without leaving the graph.

.. test_result:: An acknowledgement carrying a different id does not stop the timer — passed
   :id: TRES_ACTUATOR_ACK_ID_MATCH
   :results_for: TEST_ACTUATOR_ACK_ID_MATCH
   :outcome: passed
   :runtime_s: 0.000
   :test_run_label: 2026-10-26 12:45:34 +01:00
   :chain_reqs: REQ_COOLING_REQUEST, REQ_HEATING_REQUEST, REQ_THERMAL_ACTUATOR_FAILSAFE

   ``tests/thermal_management/test_actuator_if.py::test_only_a_matching_request_id_confirms`` recorded ``passed`` in 0.000 s.

.. test_result:: A new request restarts the acknowledgement timer cleanly — passed
   :id: TRES_ACTUATOR_ACK_RESTART
   :results_for: TEST_ACTUATOR_ACK_RESTART
   :outcome: passed
   :runtime_s: 0.000
   :test_run_label: 2026-10-26 12:45:34 +01:00
   :chain_reqs: REQ_COOLING_REQUEST, REQ_HEATING_REQUEST, REQ_THERMAL_ACTUATOR_FAILSAFE

   ``tests/thermal_management/test_actuator_if.py::test_a_new_request_clears_the_previous_verdict`` recorded ``passed`` in 0.000 s.

.. test_result:: A request goes unconfirmed after 2 s without a matching acknowledgement — passed
   :id: TRES_ACTUATOR_ACK_TIMER
   :results_for: TEST_ACTUATOR_ACK_TIMER
   :outcome: passed
   :runtime_s: 0.000
   :test_run_label: 2026-10-26 12:45:34 +01:00
   :chain_reqs: REQ_COOLING_REQUEST, REQ_HEATING_REQUEST, REQ_THERMAL_ACTUATOR_FAILSAFE

   ``tests/thermal_management/test_actuator_if.py::test_missing_acknowledgement_becomes_unconfirmed_at_two_seconds`` recorded ``passed`` in 0.000 s.

.. test_result:: Anchors closer than 40 percent SOC yield no capacity candidate — passed
   :id: TRES_CAPACITY_ANCHOR_SPREAD
   :results_for: TEST_CAPACITY_ANCHOR_SPREAD
   :outcome: passed
   :runtime_s: 0.000
   :test_run_label: 2026-10-26 12:45:34 +01:00
   :chain_reqs: REQ_SOH_CAPACITY_REPORT

   ``tests/state_estimation/test_soh_tracker.py::test_narrow_anchor_spread_is_refused`` recorded ``passed`` in 0.000 s.

.. test_result:: A capacity candidate above the reported value is discarded — failed
   :id: TRES_CAPACITY_MONOTONIC_CLAMP
   :results_for: TEST_CAPACITY_MONOTONIC_CLAMP
   :outcome: failed
   :runtime_s: 0.000
   :test_run_label: 2026-10-26 12:45:34 +01:00
   :chain_reqs: REQ_SOH_CAPACITY_REPORT

   ``tests/state_estimation/test_soh_tracker.py::test_reported_capacity_never_increases`` recorded ``failed`` in 0.000 s.

   Reported message: assert 1 == 2 + where 1 = <src.state_estimation.soh_tracker.SohTracker object at 0x7f05b7be0440>.rejected

.. test_result:: A long run of candidates forms a non increasing sequence — passed
   :id: TRES_CAPACITY_MONOTONIC_SEQUENCE
   :results_for: TEST_CAPACITY_MONOTONIC_SEQUENCE
   :outcome: passed
   :runtime_s: 0.000
   :test_run_label: 2026-10-26 12:45:34 +01:00
   :chain_reqs: REQ_SOH_CAPACITY_REPORT

   ``tests/state_estimation/test_soh_tracker.py::test_reported_sequence_is_monotonic_under_noise`` recorded ``passed`` in 0.000 s.

.. test_result:: Acquisition publishes one complete sample set per 10 ms cycle — passed
   :id: TRES_CELL_SAMPLE_CYCLE
   :results_for: TEST_CELL_SAMPLE_CYCLE
   :outcome: passed
   :runtime_s: 0.000
   :test_run_label: 2026-10-26 12:45:34 +01:00
   :chain_reqs: REQ_CELL_OVERTEMPERATURE, REQ_CELL_VOLTAGE_LIMITS, REQ_MEASUREMENT_PLAUSIBILITY

   ``tests/cell_protection/test_acquisition.py::test_complete_sample_set_every_cycle`` recorded ``passed`` in 0.000 s.

.. test_result:: Acquisition cycle is due only after the 10 ms period elapsed — passed
   :id: TRES_CELL_SAMPLE_CYCLE_PERIOD
   :results_for: TEST_CELL_SAMPLE_CYCLE_PERIOD
   :outcome: passed
   :runtime_s: 0.000
   :test_run_label: 2026-10-26 12:45:34 +01:00
   :chain_reqs: REQ_CELL_OVERTEMPERATURE, REQ_CELL_VOLTAGE_LIMITS, REQ_MEASUREMENT_PLAUSIBILITY

   ``tests/cell_protection/test_acquisition.py::test_cycle_is_due_only_after_ten_milliseconds`` recorded ``passed`` in 0.000 s.

.. test_result:: Charge is integrated trapezoidally on every 10 ms tick — passed
   :id: TRES_CHARGE_INTEGRATION
   :results_for: TEST_CHARGE_INTEGRATION
   :outcome: passed
   :runtime_s: 0.000
   :test_run_label: 2026-10-26 12:45:34 +01:00
   :chain_reqs: REQ_SOC_ACCURACY

   ``tests/state_estimation/test_coulomb_counter.py::test_trapezoidal_integration_over_three_ticks`` recorded ``passed`` in 0.000 s.

.. test_result:: A ramping current integrates to the exact trapezoid area — passed
   :id: TRES_CHARGE_INTEGRATION_RAMP
   :results_for: TEST_CHARGE_INTEGRATION_RAMP
   :outcome: passed
   :runtime_s: 0.000
   :test_run_label: 2026-10-26 12:45:34 +01:00
   :chain_reqs: REQ_SOC_ACCURACY

   ``tests/state_estimation/test_coulomb_counter.py::test_linear_ramp_matches_the_analytic_area`` recorded ``passed`` in 0.000 s.

.. test_result:: Throughput accumulates the absolute charge in both directions — passed
   :id: TRES_CHARGE_THROUGHPUT
   :results_for: TEST_CHARGE_THROUGHPUT
   :outcome: passed
   :runtime_s: 0.000
   :test_run_label: 2026-10-26 12:45:34 +01:00
   :chain_reqs: REQ_SOC_ACCURACY

   ``tests/state_estimation/test_coulomb_counter.py::test_throughput_counts_charge_and_discharge_alike`` recorded ``passed`` in 0.000 s.

.. test_result:: Both coil channels de-energise within the 10 ms budget — passed
   :id: TRES_CONTACTOR_DEENERGISE
   :results_for: TEST_CONTACTOR_DEENERGISE
   :outcome: passed
   :runtime_s: 0.000
   :test_run_label: 2026-10-26 12:45:34 +01:00
   :chain_reqs: REQ_FAULT_LATCH, REQ_FAULT_REACTION_TIME

   ``tests/cell_protection/test_contactor.py::test_open_deenergises_both_channels_within_budget`` recorded ``passed`` in 0.000 s.

.. test_result:: A latched supervisor state blocks any close request — passed
   :id: TRES_CONTACTOR_LATCH_BLOCK
   :results_for: TEST_CONTACTOR_LATCH_BLOCK
   :outcome: passed
   :runtime_s: 0.000
   :test_run_label: 2026-10-26 12:45:34 +01:00
   :chain_reqs: REQ_FAULT_LATCH, REQ_FAULT_REACTION_TIME

   ``tests/cell_protection/test_contactor.py::test_close_is_refused_while_latched`` recorded ``passed`` in 0.000 s.

.. test_result:: The cooling request follows the 35 over 30 C hysteresis band — passed
   :id: TRES_COOLING_HYSTERESIS
   :results_for: TEST_COOLING_HYSTERESIS
   :outcome: passed
   :runtime_s: 0.000
   :test_run_label: 2026-10-26 12:45:34 +01:00
   :chain_reqs: REQ_CELL_TEMP_SPREAD, REQ_COOLING_REQUEST, REQ_HEATING_REQUEST

   ``tests/thermal_management/test_evaluator.py::test_cooling_request_holds_inside_the_band`` recorded ``passed`` in 0.000 s.

.. test_result:: Only a completed OCV correction clears the unreliable verdict — passed
   :id: TRES_CURRENT_STALENESS_LATCH
   :results_for: TEST_CURRENT_STALENESS_LATCH
   :outcome: passed
   :runtime_s: 0.000
   :test_run_label: 2026-10-26 12:45:34 +01:00
   :chain_reqs: REQ_SOC_INVALID_FLAG

   ``tests/state_estimation/test_validity_monitor.py::test_returning_samples_do_not_clear_the_verdict`` recorded ``passed`` in 0.000 s.

.. test_result:: A valid sample resets the staleness timer before the limit — passed
   :id: TRES_CURRENT_STALENESS_RESET
   :results_for: TEST_CURRENT_STALENESS_RESET
   :outcome: passed
   :runtime_s: 0.000
   :test_run_label: 2026-10-26 12:45:34 +01:00
   :chain_reqs: REQ_SOC_INVALID_FLAG

   ``tests/state_estimation/test_validity_monitor.py::test_a_valid_sample_resets_the_timer`` recorded ``passed`` in 0.000 s.

.. test_result:: The unreliable verdict is raised after 5 s without a valid current sample — passed
   :id: TRES_CURRENT_STALENESS_TIMER
   :results_for: TEST_CURRENT_STALENESS_TIMER
   :outcome: passed
   :runtime_s: 0.000
   :test_run_label: 2026-10-26 12:45:34 +01:00
   :chain_reqs: REQ_SOC_INVALID_FLAG

   ``tests/state_estimation/test_validity_monitor.py::test_verdict_is_raised_only_past_five_seconds`` recorded ``passed`` in 0.000 s.

.. test_result:: The 64 entry ring overwrites its oldest record when full — passed
   :id: TRES_FAULT_RECORD_RING
   :results_for: TEST_FAULT_RECORD_RING
   :outcome: passed
   :runtime_s: 0.000
   :test_run_label: 2026-10-26 12:45:34 +01:00
   :chain_reqs: REQ_FAULT_RECORD

   ``tests/cell_protection/test_fault_memory.py::test_ring_overwrites_the_oldest_record`` recorded ``passed`` in 0.000 s.

.. test_result:: A fault record is written inside 20 ms carrying channel limit and value — passed
   :id: TRES_FAULT_RECORD_WRITE
   :results_for: TEST_FAULT_RECORD_WRITE
   :outcome: passed
   :runtime_s: 0.000
   :test_run_label: 2026-10-26 12:45:34 +01:00
   :chain_reqs: REQ_FAULT_RECORD

   ``tests/cell_protection/test_fault_memory.py::test_record_carries_the_required_fields_and_fixed_size`` recorded ``passed`` in 0.000 s.

.. test_result:: The heating request follows the 5 under 10 C hysteresis band — passed
   :id: TRES_HEATING_HYSTERESIS
   :results_for: TEST_HEATING_HYSTERESIS
   :outcome: passed
   :runtime_s: 0.000
   :test_run_label: 2026-10-26 12:45:34 +01:00
   :chain_reqs: REQ_CELL_TEMP_SPREAD, REQ_COOLING_REQUEST, REQ_HEATING_REQUEST

   ``tests/thermal_management/test_evaluator.py::test_heating_request_holds_inside_the_band`` recorded ``passed`` in 0.000 s.

.. test_result:: A cycle of only invalid samples produces no event at all — passed
   :id: TRES_IGNORE_INVALID_ALL
   :results_for: TEST_IGNORE_INVALID_ALL
   :outcome: passed
   :runtime_s: 0.000
   :test_run_label: 2026-10-26 12:45:34 +01:00
   :chain_reqs: REQ_CELL_OVERTEMPERATURE, REQ_CELL_VOLTAGE_LIMITS, REQ_FAULT_LATCH, REQ_PACK_OVERCURRENT

   ``tests/cell_protection/test_supervisor.py::test_fully_invalid_cycle_is_silent`` recorded ``passed`` in 0.000 s.

.. test_result:: An invalid sample can never command the contactors open — passed
   :id: TRES_IGNORE_INVALID_SAMPLES
   :results_for: TEST_IGNORE_INVALID_SAMPLES
   :outcome: passed
   :runtime_s: 0.000
   :test_run_label: 2026-10-26 12:45:34 +01:00
   :chain_reqs: REQ_CELL_OVERTEMPERATURE, REQ_CELL_VOLTAGE_LIMITS, REQ_FAULT_LATCH, REQ_PACK_OVERCURRENT

   ``tests/cell_protection/test_supervisor.py::test_invalid_samples_are_excluded_from_evaluation`` recorded ``passed`` in 0.000 s.

.. test_result:: The imbalance warning tracks the spread above 8 K — failed
   :id: TRES_IMBALANCE_WARNING
   :results_for: TEST_IMBALANCE_WARNING
   :outcome: failed
   :runtime_s: 0.000
   :test_run_label: 2026-10-26 12:45:34 +01:00
   :chain_reqs: REQ_CELL_TEMP_SPREAD, REQ_COOLING_REQUEST, REQ_HEATING_REQUEST

   ``tests/thermal_management/test_evaluator.py::test_imbalance_warning_tracks_the_spread_directly`` recorded ``failed`` in 0.000 s.

   Reported message: assert True is False + where True = update_imbalance(80) + where update_imbalance = <src.thermal_management.evaluator.ThermalStateEvaluator object at 0x7f05b7b895b0>.update_imbalance

.. test_result:: The isolation fault is set strictly below 500 ohm per volt and only on a valid ratio — passed
   :id: TRES_ISOLATION_FAULT_FLAG
   :results_for: TEST_ISOLATION_FAULT_FLAG
   :outcome: passed
   :runtime_s: 0.000
   :test_run_label: 2026-10-26 12:45:34 +01:00
   :chain_reqs: REQ_ISOLATION_FAULT

   ``tests/isolation_monitoring/test_monitor.py::test_fault_is_set_strictly_below_the_limit_on_valid_ratios_only`` recorded ``passed`` in 0.000 s.

.. test_result:: The isolation ratio is resistance over pack voltage and invalid below 50 V — passed
   :id: TRES_ISOLATION_RATIO
   :results_for: TEST_ISOLATION_RATIO
   :outcome: passed
   :runtime_s: 0.000
   :test_run_label: 2026-10-26 12:45:34 +01:00
   :chain_reqs: REQ_ISOLATION_FAULT

   ``tests/isolation_monitoring/test_monitor.py::test_ratio_is_resistance_over_voltage_and_invalid_below_fifty_volts`` recorded ``passed`` in 0.000 s.

.. test_result:: The latched violation keeps the first cause not the latest — passed
   :id: TRES_LATCH_FIRST_CAUSE
   :results_for: TEST_LATCH_FIRST_CAUSE
   :outcome: passed
   :runtime_s: 0.000
   :test_run_label: 2026-10-26 12:45:34 +01:00
   :chain_reqs: REQ_CELL_OVERTEMPERATURE, REQ_CELL_VOLTAGE_LIMITS, REQ_FAULT_LATCH, REQ_PACK_OVERCURRENT

   ``tests/cell_protection/test_supervisor.py::test_latch_retains_the_first_violation`` recorded ``passed`` in 0.000 s.

.. test_result:: FAULT_LATCHED is left only on a diagnostic service reset — passed
   :id: TRES_LATCH_STATE_MACHINE
   :results_for: TEST_LATCH_STATE_MACHINE
   :outcome: passed
   :runtime_s: 0.000
   :test_run_label: 2026-10-26 12:45:34 +01:00
   :chain_reqs: REQ_CELL_OVERTEMPERATURE, REQ_CELL_VOLTAGE_LIMITS, REQ_FAULT_LATCH, REQ_PACK_OVERCURRENT

   ``tests/cell_protection/test_supervisor.py::test_latch_survives_healthy_samples_and_clears_only_on_reset`` recorded ``passed`` in 0.000 s.

.. test_result:: The actuator fallback share is flat at 30 percent while unconfirmed — passed
   :id: TRES_LIMIT_ACTUATOR_SHARE
   :results_for: TEST_LIMIT_ACTUATOR_SHARE
   :outcome: passed
   :runtime_s: 0.000
   :test_run_label: 2026-10-26 12:45:34 +01:00
   :chain_reqs: REQ_POWER_DERATING, REQ_SUSTAINED_DISCHARGE_LIMIT, REQ_THERMAL_ACTUATOR_FAILSAFE

   ``tests/thermal_management/test_power_limit.py::test_actuator_share_is_flat_and_conditional`` recorded ``passed`` in 0.000 s.

.. test_result:: Supervisor evaluates each valid sample against the four limit table entries — passed
   :id: TRES_LIMIT_EVALUATION
   :results_for: TEST_LIMIT_EVALUATION
   :outcome: passed
   :runtime_s: 0.000
   :test_run_label: 2026-10-26 12:45:34 +01:00
   :chain_reqs: REQ_CELL_OVERTEMPERATURE, REQ_CELL_VOLTAGE_LIMITS, REQ_FAULT_LATCH, REQ_PACK_OVERCURRENT

   ``tests/cell_protection/test_supervisor.py::test_each_limit_table_entry_is_evaluated`` recorded ``passed`` in 0.000 s.

.. test_result:: A sample inside every limit produces no violation — passed
   :id: TRES_LIMIT_EVALUATION_NOMINAL
   :results_for: TEST_LIMIT_EVALUATION_NOMINAL
   :outcome: passed
   :runtime_s: 0.000
   :test_run_label: 2026-10-26 12:45:34 +01:00
   :chain_reqs: REQ_CELL_OVERTEMPERATURE, REQ_CELL_VOLTAGE_LIMITS, REQ_FAULT_LATCH, REQ_PACK_OVERCURRENT

   ``tests/cell_protection/test_supervisor.py::test_nominal_sample_produces_no_violation`` recorded ``passed`` in 0.000 s.

.. test_result:: The published limit is the minimum of all three derating causes — passed
   :id: TRES_LIMIT_MINIMUM
   :results_for: TEST_LIMIT_MINIMUM
   :outcome: passed
   :runtime_s: 0.000
   :test_run_label: 2026-10-26 12:45:34 +01:00
   :chain_reqs: REQ_POWER_DERATING, REQ_SUSTAINED_DISCHARGE_LIMIT, REQ_THERMAL_ACTUATOR_FAILSAFE

   ``tests/thermal_management/test_power_limit.py::test_published_limit_takes_the_minimum`` recorded ``passed`` in 0.000 s.

.. test_result:: The plausibility median is taken per module not per pack — passed
   :id: TRES_MODULE_MEDIAN_SCOPE
   :results_for: TEST_MODULE_MEDIAN_SCOPE
   :outcome: passed
   :runtime_s: 0.000
   :test_run_label: 2026-10-26 12:45:34 +01:00
   :chain_reqs: REQ_CELL_OVERTEMPERATURE, REQ_CELL_VOLTAGE_LIMITS, REQ_MEASUREMENT_PLAUSIBILITY

   ``tests/cell_protection/test_acquisition.py::test_median_is_scoped_to_the_module`` recorded ``passed`` in 0.000 s.

.. test_result:: Cell voltage beyond 250 mV from the module median is flagged invalid — passed
   :id: TRES_MODULE_MEDIAN_VALIDITY
   :results_for: TEST_MODULE_MEDIAN_VALIDITY
   :outcome: passed
   :runtime_s: 0.000
   :test_run_label: 2026-10-26 12:45:34 +01:00
   :chain_reqs: REQ_CELL_OVERTEMPERATURE, REQ_CELL_VOLTAGE_LIMITS, REQ_MEASUREMENT_PLAUSIBILITY

   ``tests/cell_protection/test_acquisition.py::test_module_median_deviation_marks_sample_invalid`` recorded ``passed`` in 0.000 s.

.. test_result:: A completed correction replaces the anchor of the fused estimate — passed
   :id: TRES_OCV_CORRECTION_ANCHOR
   :results_for: TEST_OCV_CORRECTION_ANCHOR
   :outcome: passed
   :runtime_s: 0.000
   :test_run_label: 2026-10-26 12:45:34 +01:00
   :chain_reqs: REQ_SOC_ACCURACY, REQ_SOC_REST_CORRECTION

   ``tests/state_estimation/test_ocv_corrector.py::test_correction_moves_the_fused_estimate_anchor`` recorded ``passed`` in 0.000 s.

.. test_result:: Voltages outside the OCV table clamp to its ends — passed
   :id: TRES_OCV_TABLE_CLAMP
   :results_for: TEST_OCV_TABLE_CLAMP
   :outcome: passed
   :runtime_s: 0.000
   :test_run_label: 2026-10-26 12:45:34 +01:00
   :chain_reqs: REQ_SOC_ACCURACY, REQ_SOC_REST_CORRECTION

   ``tests/state_estimation/test_ocv_corrector.py::test_out_of_table_voltages_clamp_instead_of_extrapolating`` recorded ``passed`` in 0.000 s.

.. test_result:: The SOC is interpolated linearly between two OCV table points — passed
   :id: TRES_OCV_TABLE_LOOKUP
   :results_for: TEST_OCV_TABLE_LOOKUP
   :outcome: passed
   :runtime_s: 0.000
   :test_run_label: 2026-10-26 12:45:34 +01:00
   :chain_reqs: REQ_SOC_ACCURACY, REQ_SOC_REST_CORRECTION

   ``tests/state_estimation/test_ocv_corrector.py::test_linear_interpolation_between_table_points`` recorded ``passed`` in 0.000 s.

.. test_result:: Overcurrent is reported only after 100 ms continuously above 350 A — passed
   :id: TRES_OVERCURRENT_DEBOUNCE
   :results_for: TEST_OVERCURRENT_DEBOUNCE
   :outcome: passed
   :runtime_s: 0.000
   :test_run_label: 2026-10-26 12:45:34 +01:00
   :chain_reqs: REQ_PACK_OVERCURRENT

   ``tests/cell_protection/test_current_monitor.py::test_overcurrent_needs_the_full_persistence_window`` recorded ``passed`` in 0.000 s.

.. test_result:: An inrush falling back inside 100 ms resets the overcurrent timer — passed
   :id: TRES_OVERCURRENT_INRUSH_RESET
   :results_for: TEST_OVERCURRENT_INRUSH_RESET
   :outcome: passed
   :runtime_s: 0.000
   :test_run_label: 2026-10-26 12:45:34 +01:00
   :chain_reqs: REQ_PACK_OVERCURRENT

   ``tests/cell_protection/test_current_monitor.py::test_short_inrush_does_not_trip`` recorded ``passed`` in 0.000 s.

.. test_result:: A rest condition needs 30 continuous minutes below 1 A — passed
   :id: TRES_REST_DETECTION
   :results_for: TEST_REST_DETECTION
   :outcome: passed
   :runtime_s: 0.000
   :test_run_label: 2026-10-26 12:45:34 +01:00
   :chain_reqs: REQ_SOC_ACCURACY, REQ_SOC_REST_CORRECTION

   ``tests/state_estimation/test_ocv_corrector.py::test_rest_requires_the_full_thirty_minutes`` recorded ``passed`` in 0.000 s.

.. test_result:: A load in the middle of the rest window restarts the timer — passed
   :id: TRES_REST_DETECTION_RESET
   :results_for: TEST_REST_DETECTION_RESET
   :outcome: passed
   :runtime_s: 0.000
   :test_run_label: 2026-10-26 12:45:34 +01:00
   :chain_reqs: REQ_SOC_ACCURACY, REQ_SOC_REST_CORRECTION

   ``tests/state_estimation/test_ocv_corrector.py::test_load_during_rest_resets_the_timer`` recorded ``passed`` in 0.000 s.

.. test_result:: Each write targets the slot holding the lower write counter — passed
   :id: TRES_SOC_PERSIST_ALTERNATION
   :results_for: TEST_SOC_PERSIST_ALTERNATION
   :outcome: passed
   :runtime_s: 0.000
   :test_run_label: 2026-10-26 12:45:34 +01:00
   :chain_reqs: REQ_SOC_PERSISTENCE

   ``tests/state_estimation/test_soc_store.py::test_writes_alternate_between_the_two_slots`` recorded ``passed`` in 0.000 s.

.. test_result:: The SOC record is written on shutdown and every 60 seconds — passed
   :id: TRES_SOC_PERSIST_WRITE
   :results_for: TEST_SOC_PERSIST_WRITE
   :outcome: passed
   :runtime_s: 0.000
   :test_run_label: 2026-10-26 12:45:34 +01:00
   :chain_reqs: REQ_SOC_PERSISTENCE

   ``tests/state_estimation/test_soc_store.py::test_writes_happen_on_shutdown_and_on_the_periodic_interval`` recorded ``passed`` in 0.000 s.

.. test_result:: Restore reports no stored value when neither slot is valid — passed
   :id: TRES_SOC_RESTORE_NO_VALID_SLOT
   :results_for: TEST_SOC_RESTORE_NO_VALID_SLOT
   :outcome: passed
   :runtime_s: 0.000
   :test_run_label: 2026-10-26 12:45:34 +01:00
   :chain_reqs: REQ_SOC_PERSISTENCE

   ``tests/state_estimation/test_soc_store.py::test_restore_reports_absence_rather_than_a_default`` recorded ``passed`` in 0.000 s.

.. test_result:: Restore returns the checksum valid slot with the higher counter — passed
   :id: TRES_SOC_RESTORE_SLOT
   :results_for: TEST_SOC_RESTORE_SLOT
   :outcome: passed
   :runtime_s: 0.000
   :test_run_label: 2026-10-26 12:45:34 +01:00
   :chain_reqs: REQ_SOC_PERSISTENCE

   ``tests/state_estimation/test_soc_store.py::test_restore_prefers_the_newest_valid_slot`` recorded ``passed`` in 0.000 s.

.. test_result:: A frame carries the latest SOC capacity and validity values — passed
   :id: TRES_STATE_FRAME_CONTENT
   :results_for: TEST_STATE_FRAME_CONTENT
   :outcome: passed
   :runtime_s: 0.000
   :test_run_label: 2026-10-26 12:45:34 +01:00
   :chain_reqs: REQ_SOC_INVALID_FLAG, REQ_SOC_UPDATE_PERIOD

   ``tests/state_estimation/test_publisher.py::test_frame_carries_the_latest_values`` recorded ``passed`` in 0.000 s.

.. test_result:: The battery state frame is sent every 100 ms — passed
   :id: TRES_STATE_FRAME_PERIOD
   :results_for: TEST_STATE_FRAME_PERIOD
   :outcome: passed
   :runtime_s: 0.000
   :test_run_label: 2026-10-26 12:45:34 +01:00
   :chain_reqs: REQ_SOC_INVALID_FLAG, REQ_SOC_UPDATE_PERIOD

   ``tests/state_estimation/test_publisher.py::test_frame_is_sent_once_per_period`` recorded ``passed`` in 0.000 s.

.. test_result:: A producer that did not update does not suppress the frame — passed
   :id: TRES_STATE_FRAME_REPEATS_LAST
   :results_for: TEST_STATE_FRAME_REPEATS_LAST
   :outcome: passed
   :runtime_s: 0.000
   :test_run_label: 2026-10-26 12:45:34 +01:00
   :chain_reqs: REQ_SOC_INVALID_FLAG, REQ_SOC_UPDATE_PERIOD

   ``tests/state_estimation/test_publisher.py::test_stale_producer_values_are_repeated_not_skipped`` recorded ``passed`` in 0.000 s.

.. test_result:: The sustained-load share draws 250 A while the 10 s average current is at or above 250 A — passed
   :id: TRES_SUSTAINED_LOAD_LIMIT
   :results_for: TEST_SUSTAINED_LOAD_LIMIT
   :outcome: passed
   :runtime_s: 0.002
   :test_run_label: 2026-10-26 12:45:34 +01:00
   :chain_reqs: REQ_POWER_DERATING, REQ_SUSTAINED_DISCHARGE_LIMIT, REQ_THERMAL_ACTUATOR_FAILSAFE

   ``tests/thermal_management/test_power_limit.py::test_sustained_load_share_holds_the_current_at_the_limit`` recorded ``passed`` in 0.002 s.

.. test_result:: The ramp decreases monotonically across the derating band — passed
   :id: TRES_TEMP_DERATE_MONOTONIC
   :results_for: TEST_TEMP_DERATE_MONOTONIC
   :outcome: passed
   :runtime_s: 0.000
   :test_run_label: 2026-10-26 12:45:34 +01:00
   :chain_reqs: REQ_POWER_DERATING, REQ_SUSTAINED_DISCHARGE_LIMIT, REQ_THERMAL_ACTUATOR_FAILSAFE

   ``tests/thermal_management/test_power_limit.py::test_ramp_is_monotonically_decreasing`` recorded ``passed`` in 0.000 s.

.. test_result:: The temperature power share ramps linearly from 55 C to 60 C — passed
   :id: TRES_TEMP_DERATE_RAMP
   :results_for: TEST_TEMP_DERATE_RAMP
   :outcome: passed
   :runtime_s: 0.000
   :test_run_label: 2026-10-26 12:45:34 +01:00
   :chain_reqs: REQ_POWER_DERATING, REQ_SUSTAINED_DISCHARGE_LIMIT, REQ_THERMAL_ACTUATOR_FAILSAFE

   ``tests/thermal_management/test_power_limit.py::test_derating_ramp_endpoints_and_midpoint`` recorded ``passed`` in 0.000 s.

.. test_result:: The thermal picture is reduced from the valid cell temperatures only — passed
   :id: TRES_TEMP_EXTREMA
   :results_for: TEST_TEMP_EXTREMA
   :outcome: passed
   :runtime_s: 0.000
   :test_run_label: 2026-10-26 12:45:34 +01:00
   :chain_reqs: REQ_CELL_TEMP_SPREAD, REQ_COOLING_REQUEST, REQ_HEATING_REQUEST

   ``tests/thermal_management/test_evaluator.py::test_extrema_and_spread_ignore_invalid_samples`` recorded ``passed`` in 0.000 s.

.. test_result:: A cycle without any valid temperature publishes no thermal picture — passed
   :id: TRES_TEMP_EXTREMA_UNAVAILABLE
   :results_for: TEST_TEMP_EXTREMA_UNAVAILABLE
   :outcome: passed
   :runtime_s: 0.000
   :test_run_label: 2026-10-26 12:45:34 +01:00
   :chain_reqs: REQ_CELL_TEMP_SPREAD, REQ_COOLING_REQUEST, REQ_HEATING_REQUEST

   ``tests/thermal_management/test_evaluator.py::test_fully_invalid_cycle_reports_unavailable`` recorded ``passed`` in 0.000 s.

.. test_result:: A full cycle derives both requests and the warning together — passed
   :id: TRES_THERMAL_CYCLE
   :results_for: TEST_THERMAL_CYCLE
   :outcome: passed
   :runtime_s: 0.000
   :test_run_label: 2026-10-26 12:45:34 +01:00
   :chain_reqs: REQ_CELL_TEMP_SPREAD, REQ_COOLING_REQUEST, REQ_HEATING_REQUEST

   ``tests/thermal_management/test_evaluator.py::test_cycle_drives_every_output`` recorded ``passed`` in 0.000 s.
