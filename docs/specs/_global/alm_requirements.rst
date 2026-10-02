System Requirements (source: Jama)
====================================

.. warning::

   **Generated — do not edit by hand.** Every requirement below is owned by the
   Jama project `Rollout_Demo <https://useblocks-partner.jamacloud.com/perspective.req#/projects/59/>`__. Edit it there, then re-acquire::

      ubc script sync-jama            # in whichever mode is active
      ubc script sync-jama:rst        # as RST, round-trip
      ubc script sync-jama:external   # as read-only JSON

Delete this page and run the sync: the requirements come back from Jama. The
local copy is disposable; the ALM is not.

Nothing here is ever written back to Jama. Requirements flow down only; the
evidence that flows back up (test cases, test runs) is a separate push and a
separate configuration. Each requirement keeps ``:legacy_id:``, the identifier it
carried while it was still authored in this repository, so the migration stays
auditable.

.. note::

   **Mode: RST — the complete round trip.** Each requirement below is a real
   ``.. req::`` block in this file: an ordinary local need that ubCode resolves,
   ``ubc diff`` sees, and you could in principle edit and push back.
   ``[[needs.external_needs]]`` is wired but carries nothing while this mode is
   active. Switch with ``ubc script sync-jama:external``.


Cell balancing
--------------

.. req:: The battery management system shall reduce the cell voltage spread to 20 mV or less within 8 hours of a charge session ending
   :id: JAMA_Rollout_Demo-SYSRQ-2
   :status: draft
   :traces_to: US_CELL_BALANCING
   :alm_stream: cell-balancing
   :legacy_id: REQ_CELL_BALANCING_WINDOW
   :jama_id: 12730
   :jama_document_key: Rollout_Demo-SYSRQ-2
   :jama_url: https://useblocks-partner.jamacloud.com/perspective.req#/containers/12730/details?projectId=59
   :global_id: GID-57924

   The battery management system shall bring the difference between the highest
   and the lowest cell voltage of the pack to 20 mV or less within 8 hours of
   the end of a charge session, measured while the pack is at rest and every
   cell temperature is between 15 °C and 45 °C. The spread is evaluated on
   settled cell voltages, so the 8 hour window includes the time the cells need
   to relax after charging.


Cell protection
---------------

.. req:: The battery management system shall open the high-voltage contactors when any cell voltage leaves the safe window of the pack chemistry
   :id: JAMA_Rollout_Demo-SYSRQ-3
   :status: draft
   :traces_to: US_CELL_PROTECTION
   :alm_stream: cell-protection
   :legacy_id: REQ_CELL_VOLTAGE_LIMITS
   :jama_id: 12731
   :jama_document_key: Rollout_Demo-SYSRQ-3
   :jama_url: https://useblocks-partner.jamacloud.com/perspective.req#/containers/12731/details?projectId=59
   :global_id: GID-57925

   The battery management system shall command the high-voltage contactors open
   whenever a valid cell voltage measurement is below :variant:`pack.cell_v_min` V
   or above :variant:`pack.cell_v_max` V. The limits apply to every cell of the
   pack individually, so a single cell outside the range is sufficient to trigger
   the reaction, regardless of the pack voltage.

.. req:: The battery management system shall open the high-voltage contactors when the pack discharge current exceeds 350 A for more than 100 ms
   :id: JAMA_Rollout_Demo-SYSRQ-4
   :status: draft
   :traces_to: US_CELL_PROTECTION
   :alm_stream: cell-protection
   :legacy_id: REQ_PACK_OVERCURRENT
   :jama_id: 12732
   :jama_document_key: Rollout_Demo-SYSRQ-4
   :jama_url: https://useblocks-partner.jamacloud.com/perspective.req#/containers/12732/details?projectId=59
   :global_id: GID-57926

   The battery management system shall command the high-voltage contactors open
   whenever the measured pack current in the discharge direction stays above
   350 A continuously for more than 100 ms. Currents above the limit that fall
   back below it within 100 ms do not trigger the reaction, so a normal
   acceleration inrush is not treated as a fault.

.. req:: The battery management system shall open the high-voltage contactors when any cell temperature exceeds 60 °C
   :id: JAMA_Rollout_Demo-SYSRQ-5
   :status: draft
   :traces_to: US_CELL_PROTECTION
   :alm_stream: cell-protection
   :legacy_id: REQ_CELL_OVERTEMPERATURE
   :jama_id: 12733
   :jama_document_key: Rollout_Demo-SYSRQ-5
   :jama_url: https://useblocks-partner.jamacloud.com/perspective.req#/containers/12733/details?projectId=59
   :global_id: GID-57927

   The battery management system shall command the high-voltage contactors open
   whenever a valid cell temperature measurement is above 60 °C. The limit
   applies to every temperature sensor of the pack individually, so one sensor
   above the limit is sufficient to trigger the reaction.

.. req:: The battery management system shall issue the contactor-open command within 50 ms of detecting a cell-protection limit violation
   :id: JAMA_Rollout_Demo-SYSRQ-6
   :status: draft
   :traces_to: US_CELL_PROTECTION
   :alm_stream: cell-protection
   :legacy_id: REQ_FAULT_REACTION_TIME
   :jama_id: 12734
   :jama_document_key: Rollout_Demo-SYSRQ-6
   :jama_url: https://useblocks-partner.jamacloud.com/perspective.req#/containers/12734/details?projectId=59
   :global_id: GID-57928

   The battery management system shall issue the contactor-open command no later
   than 50 ms after the measurement sample that first violated a cell-protection
   limit. The interval is measured from the timestamp of that sample to the
   timestamp of the command on the contactor interface.

.. req:: The battery management system shall classify a cell voltage measurement as invalid when it deviates from its module median by more than 250 mV
   :id: JAMA_Rollout_Demo-SYSRQ-7
   :status: draft
   :traces_to: US_CELL_PROTECTION
   :alm_stream: cell-protection
   :legacy_id: REQ_MEASUREMENT_PLAUSIBILITY
   :jama_id: 12735
   :jama_document_key: Rollout_Demo-SYSRQ-7
   :jama_url: https://useblocks-partner.jamacloud.com/perspective.req#/containers/12735/details?projectId=59
   :global_id: GID-57929

   The battery management system shall mark a cell voltage measurement invalid
   whenever its absolute difference from the median of the cell voltages of the
   same module exceeds 250 mV. An invalid measurement is not used to evaluate a
   cell-protection limit, so a single failed sensor cannot by itself command the
   contactors open.

.. req:: The battery management system shall keep the high-voltage contactors open after a cell-protection fault until a diagnostic service reset is received
   :id: JAMA_Rollout_Demo-SYSRQ-8
   :status: draft
   :traces_to: US_CELL_PROTECTION
   :alm_stream: cell-protection
   :legacy_id: REQ_FAULT_LATCH
   :jama_id: 12736
   :jama_document_key: Rollout_Demo-SYSRQ-8
   :jama_url: https://useblocks-partner.jamacloud.com/perspective.req#/containers/12736/details?projectId=59
   :global_id: GID-57930

   The battery management system shall hold the contactor-open command after a
   cell-protection fault, and shall release it only after receiving a diagnostic
   service reset request. Measurements returning inside their limits do not
   release the hold, so an intermittent condition cannot re-close the
   high-voltage circuit without a service action.

.. req:: The battery management system shall store a fault record naming the cell identifier, the violated limit and the measured value for every cell-protection fault
   :id: JAMA_Rollout_Demo-SYSRQ-9
   :status: draft
   :traces_to: US_CELL_PROTECTION
   :alm_stream: cell-protection
   :legacy_id: REQ_FAULT_RECORD
   :jama_id: 12737
   :jama_document_key: Rollout_Demo-SYSRQ-9
   :jama_url: https://useblocks-partner.jamacloud.com/perspective.req#/containers/12737/details?projectId=59
   :global_id: GID-57931

   The battery management system shall write one fault record per cell-protection
   fault into non-volatile memory, and each record shall carry the identifier of
   the cell or sensor concerned, the identifier of the limit that was violated,
   and the measured value at the violating sample. The record remains readable
   over the diagnostic interface after a power cycle.


Isolation monitoring
--------------------

.. req:: The battery management system shall report an isolation fault when the isolation resistance falls below 500 Ω per volt of pack voltage
   :id: JAMA_Rollout_Demo-SYSRQ-10
   :status: draft
   :traces_to: US_ISOLATION_MONITORING
   :alm_stream: isolation-monitoring
   :legacy_id: REQ_ISOLATION_FAULT
   :jama_id: 12738
   :jama_document_key: Rollout_Demo-SYSRQ-10
   :jama_url: https://useblocks-partner.jamacloud.com/perspective.req#/containers/12738/details?projectId=59
   :global_id: GID-57932

   The battery management system shall set the isolation fault whenever the
   measured isolation resistance between the high-voltage bus and the vehicle
   chassis, divided by the measured pack voltage, is below 500 Ω/V — the minimum
   ISO 6469-1 requires of a DC high-voltage system. The ratio, not the absolute
   resistance, is what is compared, so the same barrier is judged more strictly
   on a higher-voltage pack.


State estimation
----------------

.. req:: The battery management system shall report a state of charge whose absolute error stays within 3 % of rated capacity between 10 % and 90 % state of charge
   :id: JAMA_Rollout_Demo-SYSRQ-11
   :status: draft
   :traces_to: US_STATE_ESTIMATION
   :alm_stream: state-estimation
   :legacy_id: REQ_SOC_ACCURACY
   :jama_id: 12739
   :jama_document_key: Rollout_Demo-SYSRQ-11
   :jama_url: https://useblocks-partner.jamacloud.com/perspective.req#/containers/12739/details?projectId=59
   :global_id: GID-57933

   The battery management system shall report a state of charge (the share of
   rated capacity still available) whose absolute deviation from the
   reference value measured on a pack conditioned to 25 °C stays within 3 % of
   rated capacity, for every reported value in the 10 % to 90 % band. The
   reference value is the charge counted out of a fully charged pack by a
   calibrated bench.

.. req:: The battery management system shall publish an updated state of charge value every 100 ms
   :id: JAMA_Rollout_Demo-SYSRQ-12
   :status: draft
   :traces_to: US_STATE_ESTIMATION
   :alm_stream: state-estimation
   :legacy_id: REQ_SOC_UPDATE_PERIOD
   :jama_id: 12740
   :jama_document_key: Rollout_Demo-SYSRQ-12
   :jama_url: https://useblocks-partner.jamacloud.com/perspective.req#/containers/12740/details?projectId=59
   :global_id: GID-57934

   The battery management system shall publish a state of charge value on the
   vehicle interface with a period of 100 ms and a tolerance of 10 ms, for as
   long as the system is awake. A missing publication within 110 ms of the
   previous one is a violation of this requirement.

.. req:: The battery management system shall correct the state of charge from the open-circuit voltage after the pack has rested for at least 30 minutes
   :id: JAMA_Rollout_Demo-SYSRQ-13
   :status: draft
   :traces_to: US_STATE_ESTIMATION
   :alm_stream: state-estimation
   :legacy_id: REQ_SOC_REST_CORRECTION
   :jama_id: 12741
   :jama_document_key: Rollout_Demo-SYSRQ-13
   :jama_url: https://useblocks-partner.jamacloud.com/perspective.req#/containers/12741/details?projectId=59
   :global_id: GID-57935

   The battery management system shall replace the counted state of charge with
   the value derived from the measured open-circuit voltage once the absolute
   pack current has stayed below 1 A continuously for at least 30 minutes. This
   bounds the accumulated counting drift each time the vehicle stands still long
   enough for the cell voltages to settle.

.. req:: The battery management system shall restore the state of charge after a power cycle within 2 % of the value reported before shutdown
   :id: JAMA_Rollout_Demo-SYSRQ-14
   :status: draft
   :traces_to: US_STATE_ESTIMATION
   :alm_stream: state-estimation
   :legacy_id: REQ_SOC_PERSISTENCE
   :jama_id: 12742
   :jama_document_key: Rollout_Demo-SYSRQ-14
   :jama_url: https://useblocks-partner.jamacloud.com/perspective.req#/containers/12742/details?projectId=59
   :global_id: GID-57936

   The battery management system shall report, on the first publication after a
   power cycle in which no charge left or entered the pack, a state of charge
   within 2 % of rated capacity of the last value it published before shutdown.
   This is what keeps the displayed charge level from jumping when the vehicle is
   switched off and on again.

.. req:: The battery management system shall report a remaining capacity that never increases over the life of the pack
   :id: JAMA_Rollout_Demo-SYSRQ-15
   :status: draft
   :traces_to: US_STATE_ESTIMATION
   :alm_stream: state-estimation
   :legacy_id: REQ_SOH_CAPACITY_REPORT
   :jama_id: 12743
   :jama_document_key: Rollout_Demo-SYSRQ-15
   :jama_url: https://useblocks-partner.jamacloud.com/perspective.req#/containers/12743/details?projectId=59
   :global_id: GID-57937

   The battery management system shall report a remaining capacity, expressed as
   a percentage of rated capacity, whose successive reported values never
   increase. A newly measured capacity above the currently reported one is
   discarded, so an optimistic single measurement cannot make a worn pack look
   healthier than it was.

.. req:: The battery management system shall flag the state of charge as unreliable when pack current measurements have been unavailable for more than 5 seconds
   :id: JAMA_Rollout_Demo-SYSRQ-16
   :status: draft
   :traces_to: US_STATE_ESTIMATION
   :alm_stream: state-estimation
   :legacy_id: REQ_SOC_INVALID_FLAG
   :jama_id: 12744
   :jama_document_key: Rollout_Demo-SYSRQ-16
   :jama_url: https://useblocks-partner.jamacloud.com/perspective.req#/containers/12744/details?projectId=59
   :global_id: GID-57938

   The battery management system shall set an unreliable flag alongside the
   published state of charge whenever no valid pack current measurement has been
   received for more than 5 seconds, and shall clear the flag only after the
   next open-circuit-voltage correction. The flag is what lets the vehicle stop
   presenting a range prediction it cannot support.


Thermal management
------------------

.. req:: The battery management system shall request coolant flow when the highest cell temperature exceeds 35 °C
   :id: JAMA_Rollout_Demo-SYSRQ-17
   :status: draft
   :traces_to: US_THERMAL_MANAGEMENT
   :alm_stream: thermal-management
   :legacy_id: REQ_COOLING_REQUEST
   :jama_id: 12745
   :jama_document_key: Rollout_Demo-SYSRQ-17
   :jama_url: https://useblocks-partner.jamacloud.com/perspective.req#/containers/12745/details?projectId=59
   :global_id: GID-57939

   The battery management system shall raise a cooling request on the thermal
   interface whenever the highest valid cell temperature is above 35 °C, and
   shall withdraw it once that temperature has fallen to 30 °C or below. The 5 K
   difference between the two thresholds keeps the request from oscillating while
   the pack sits at the limit.

.. req:: The battery management system shall request pack heating when the lowest cell temperature is below 5 °C
   :id: JAMA_Rollout_Demo-SYSRQ-18
   :status: draft
   :traces_to: US_THERMAL_MANAGEMENT
   :alm_stream: thermal-management
   :legacy_id: REQ_HEATING_REQUEST
   :jama_id: 12746
   :jama_document_key: Rollout_Demo-SYSRQ-18
   :jama_url: https://useblocks-partner.jamacloud.com/perspective.req#/containers/12746/details?projectId=59
   :global_id: GID-57940

   The battery management system shall raise a heating request on the thermal
   interface whenever the lowest valid cell temperature is below 5 °C, and shall
   withdraw it once that temperature has risen to 10 °C or above. This is what
   restores the promised charging power on a cold morning instead of leaving it
   low for the whole session.

.. req:: The battery management system shall reduce the permitted discharge power linearly to zero between 55 °C and 60 °C highest cell temperature
   :id: JAMA_Rollout_Demo-SYSRQ-19
   :status: draft
   :traces_to: US_THERMAL_MANAGEMENT
   :alm_stream: thermal-management
   :legacy_id: REQ_POWER_DERATING
   :jama_id: 12747
   :jama_document_key: Rollout_Demo-SYSRQ-19
   :jama_url: https://useblocks-partner.jamacloud.com/perspective.req#/containers/12747/details?projectId=59
   :global_id: GID-57941

   The battery management system shall publish a permitted discharge power that
   falls linearly from the full permitted value at 55 °C to zero at 60 °C
   highest valid cell temperature. The vehicle therefore loses power
   predictably as the pack heats up, instead of being cut off at a single
   threshold.

.. req:: The battery management system shall report a thermal imbalance warning when the spread between highest and lowest cell temperature exceeds 8 K
   :id: JAMA_Rollout_Demo-SYSRQ-20
   :status: draft
   :traces_to: US_THERMAL_MANAGEMENT
   :alm_stream: thermal-management
   :legacy_id: REQ_CELL_TEMP_SPREAD
   :jama_id: 12748
   :jama_document_key: Rollout_Demo-SYSRQ-20
   :jama_url: https://useblocks-partner.jamacloud.com/perspective.req#/containers/12748/details?projectId=59
   :global_id: GID-57942

   The battery management system shall set a thermal imbalance warning on the
   diagnostic interface whenever the difference between the highest and the
   lowest valid cell temperature exceeds 8 K. The warning is what makes uneven
   ageing visible in the workshop before it shows up as lost capacity.

.. req:: The battery management system shall apply the thermal fallback power limit when the coolant actuator does not confirm a request within 2 seconds
   :id: JAMA_Rollout_Demo-SYSRQ-21
   :status: draft
   :traces_to: US_THERMAL_MANAGEMENT
   :alm_stream: thermal-management
   :legacy_id: REQ_THERMAL_ACTUATOR_FAILSAFE
   :jama_id: 12749
   :jama_document_key: Rollout_Demo-SYSRQ-21
   :jama_url: https://useblocks-partner.jamacloud.com/perspective.req#/containers/12749/details?projectId=59
   :global_id: GID-57943

   The battery management system shall publish the thermal fallback power limit,
   defined as 30 % of the full permitted discharge power, whenever a raised
   cooling or heating request has not been confirmed by the coolant actuator
   within 2 seconds. An unconfirmed request means the pack temperature can no
   longer be influenced, so the power the pack is allowed to deliver is capped
   instead.
