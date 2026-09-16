System Requirements (imported from DOORS)
===========================================

.. warning::

   **Generated file — do not edit by hand.** Written by
   ``tools/import_sysreqs.py`` from ``docs/external/doors/needs.json``.
   Re-generate it with::

      ubconnect csv from-csv -c docs/external/doors/import.toml
      python3 tools/import_sysreqs.py

   These are the **customer's** requirements, owned in their DOORS instance and
   imported from a committed export of one baseline (``docs/external/doors/bms_sysreqs_v1.csv``).
   Nothing in this project may edit them: an edit here is overwritten by the next
   import, and the customer would never see it. To map one onto this project, add
   a ``covers`` link on the :need:`user story <US_CELL_PROTECTION>` that answers it.

.. note::

   6 structural row(s) in the export (section headings) were dropped rather
   than imported. A heading is document structure, not a requirement, and no
   user story could ever satisfy one.

22 system requirement(s), each owing an incoming ``covers`` link from the user
story that answers it. One with no such link is the **mapping backlog** — a
customer requirement this project has not yet claimed — and is reported by
``ubc agent gaps`` against the ``user_stories`` stage. Ask the engine what to do
about one with ``ubc agent next --id <SYS_ID>``.

.. sys_req:: Cell overvoltage protection
   :id: SYS_1011
   :status: approved
   :doors_id: BMS-SYS-1011
   :doors_module: /BMS/System Requirements
   :asil: ASIL C
   :verification_method: Test

   The battery management system shall disconnect the traction battery from the high-
   voltage circuit when the voltage of any cell exceeds 4.25 V for longer than 100 ms.

   **Rationale (customer).** Sustained overvoltage plates lithium on the anode and is a
   primary thermal-runaway initiator.

.. sys_req:: Cell undervoltage protection
   :id: SYS_1012
   :status: approved
   :doors_id: BMS-SYS-1012
   :doors_module: /BMS/System Requirements
   :asil: ASIL C
   :verification_method: Test

   The battery management system shall disconnect the traction battery from the high-
   voltage circuit when the voltage of any cell falls below 2.50 V for longer than 100
   ms.

   **Rationale (customer).** Deep discharge dissolves the copper current collector and
   causes internal short circuits on the next charge.

.. sys_req:: Pack overcurrent protection
   :id: SYS_1013
   :status: approved
   :doors_id: BMS-SYS-1013
   :doors_module: /BMS/System Requirements
   :asil: ASIL C
   :verification_method: Test

   The battery management system shall disconnect the traction battery from the high-
   voltage circuit when the pack discharge current exceeds 400 A for longer than 50 ms.

   **Rationale (customer).** Sustained overcurrent exceeds the thermal rating of the
   cell tabs and the contactor weld limit.

.. sys_req:: Cell overtemperature protection
   :id: SYS_1014
   :status: approved
   :doors_id: BMS-SYS-1014
   :doors_module: /BMS/System Requirements
   :asil: ASIL C
   :verification_method: Test

   The battery management system shall disconnect the traction battery from the high-
   voltage circuit when the temperature of any cell exceeds 60 degC.

   **Rationale (customer).** Above 60 degC the separator begins to lose mechanical
   integrity.

.. sys_req:: Contactor opening time
   :id: SYS_1015
   :status: approved
   :doors_id: BMS-SYS-1015
   :doors_module: /BMS/System Requirements
   :asil: ASIL D
   :verification_method: Test

   The battery management system shall de-energise both high-voltage contactor channels
   within 10 ms of issuing a protective disconnect command.

   **Rationale (customer).** The reaction time budget for the vehicle-level safety goal
   allocates 10 ms to the contactor stage.

.. sys_req:: Protective disconnect latching
   :id: SYS_1016
   :status: approved
   :doors_id: BMS-SYS-1016
   :doors_module: /BMS/System Requirements
   :asil: ASIL D
   :verification_method: Test

   The battery management system shall keep the traction battery disconnected after a
   protective disconnect until the fault has been cleared by a qualified service
   procedure.

   **Rationale (customer).** An intermittent fault condition must never silently re-
   close the high-voltage circuit.

.. sys_req:: State of charge accuracy
   :id: SYS_1021
   :status: approved
   :doors_id: BMS-SYS-1021
   :doors_module: /BMS/System Requirements
   :asil: ASIL A
   :verification_method: Test

   The battery management system shall report the pack state of charge with an absolute
   error of no more than 3 percent across the full operating range.

   **Rationale (customer).** Range estimation and charge planning at vehicle level
   depend on this accuracy.

.. sys_req:: State of health reporting
   :id: SYS_1022
   :status: approved
   :doors_id: BMS-SYS-1022
   :doors_module: /BMS/System Requirements
   :asil: QM
   :verification_method: Analysis

   The battery management system shall report the pack state of health with an absolute
   error of no more than 5 percent over the service life of the pack.

   **Rationale (customer).** Warranty assessment and residual value estimation rely on a
   trustworthy capacity-fade figure.

.. sys_req:: Power limit prediction
   :id: SYS_1023
   :status: approved
   :doors_id: BMS-SYS-1023
   :doors_module: /BMS/System Requirements
   :asil: ASIL A
   :verification_method: Test

   The battery management system shall report the maximum charge and discharge power
   available for the next 10 seconds.

   **Rationale (customer).** The drive inverter and the charger both need a forward-
   looking limit to avoid tripping protection.

.. sys_req:: Low temperature charge accuracy
   :id: SYS_1024
   :status: draft
   :doors_id: BMS-SYS-1024
   :doors_module: /BMS/System Requirements
   :asil: ASIL A
   :verification_method: Test

   The battery management system shall maintain the stated state of charge accuracy down
   to a pack temperature of -20 degC.

   **Rationale (customer).** Cold-climate markets report the largest range-estimation
   complaints.

.. sys_req:: Active cooling activation
   :id: SYS_1031
   :status: approved
   :doors_id: BMS-SYS-1031
   :doors_module: /BMS/System Requirements
   :asil: QM
   :verification_method: Test

   The battery management system shall request active cooling when the highest cell
   temperature exceeds 40 degC.

   **Rationale (customer).** Sustained operation above 40 degC accelerates calendar
   ageing disproportionately.

.. sys_req:: Preconditioning before fast charge
   :id: SYS_1032
   :status: approved
   :doors_id: BMS-SYS-1032
   :doors_module: /BMS/System Requirements
   :asil: QM
   :verification_method: Test

   The battery management system shall request pack heating when the lowest cell
   temperature is below 0 degC and a fast charge session has been requested.

   **Rationale (customer).** Fast charging below freezing causes lithium plating and
   permanent capacity loss.

.. sys_req:: Cell temperature uniformity
   :id: SYS_1033
   :status: review
   :doors_id: BMS-SYS-1033
   :doors_module: /BMS/System Requirements
   :asil: QM
   :verification_method: Analysis

   The battery management system shall keep the temperature difference between the
   hottest and coldest cell below 5 K during normal operation.

   **Rationale (customer).** Temperature spread drives divergent ageing and therefore
   pack-level capacity loss.

.. sys_req:: Cell balancing window
   :id: SYS_1041
   :status: approved
   :doors_id: BMS-SYS-1041
   :doors_module: /BMS/System Requirements
   :asil: QM
   :verification_method: Test

   The battery management system shall equalise the cell voltages when the difference
   between the highest and lowest cell exceeds 50 mV.

   **Rationale (customer).** Cell divergence reduces the usable capacity of the whole
   pack to that of its weakest cell.

.. sys_req:: Balancing during charging
   :id: SYS_1042
   :status: draft
   :doors_id: BMS-SYS-1042
   :doors_module: /BMS/System Requirements
   :asil: QM
   :verification_method: Test

   The battery management system shall continue cell balancing while the pack is being
   charged.

   **Rationale (customer).** The charge phase offers the longest uninterrupted window in
   which balancing is effective.

.. sys_req:: Insulation resistance monitoring
   :id: SYS_1051
   :status: approved
   :doors_id: BMS-SYS-1051
   :doors_module: /BMS/System Requirements
   :asil: ASIL C
   :verification_method: Test

   The battery management system shall continuously measure the insulation resistance
   between the high-voltage circuit and the vehicle chassis.

   **Rationale (customer).** Loss of isolation exposes the vehicle body to high voltage
   and is a direct electrocution hazard.

.. sys_req:: Isolation fault indication
   :id: SYS_1052
   :status: approved
   :doors_id: BMS-SYS-1052
   :doors_module: /BMS/System Requirements
   :asil: ASIL C
   :verification_method: Test

   The battery management system shall indicate an isolation fault to the driver and
   record it when the insulation resistance falls below 500 ohm per volt.

   **Rationale (customer).** The threshold is mandated for high-voltage vehicle
   circuits.

.. sys_req:: Over-the-air firmware update
   :id: SYS_1061
   :status: draft
   :doors_id: BMS-SYS-1061
   :doors_module: /BMS/System Requirements
   :asil: QM
   :verification_method: Test

   The battery management system shall support over-the-air update of its firmware with
   the ability to roll back to the previously installed version.

   **Rationale (customer).** Field campaigns must not require a workshop visit for every
   software defect.

.. sys_req:: Secure boot
   :id: SYS_1062
   :status: draft
   :doors_id: BMS-SYS-1062
   :doors_module: /BMS/System Requirements
   :asil: ASIL B
   :verification_method: Review

   The battery management system shall verify the authenticity of its firmware before
   executing it.

   **Rationale (customer).** A forged firmware image would defeat every protection
   function in this specification.

.. sys_req:: Diagnostic service interface
   :id: SYS_1063
   :status: approved
   :doors_id: BMS-SYS-1063
   :doors_module: /BMS/System Requirements
   :asil: QM
   :verification_method: Test

   The battery management system shall provide diagnostic services in accordance with
   ISO 14229 over the vehicle diagnostic bus.

   **Rationale (customer).** Workshop tooling across the vehicle programme is
   standardised on UDS.

.. sys_req:: End-of-line current sensor calibration
   :id: SYS_1064
   :status: draft
   :doors_id: BMS-SYS-1064
   :doors_module: /BMS/System Requirements
   :asil: QM
   :verification_method: Inspection

   The battery management system shall support calibration of its current sensor offset
   during end-of-line production testing.

   **Rationale (customer).** Uncalibrated sensor offset is the dominant error term in
   coulomb counting.

.. sys_req:: Safety event data recording
   :id: SYS_1065
   :status: draft
   :doors_id: BMS-SYS-1065
   :doors_module: /BMS/System Requirements
   :asil: QM
   :verification_method: Test

   The battery management system shall record the 30 seconds of pack measurements
   preceding any protective disconnect and retain them for later retrieval.

   **Rationale (customer).** Field failure analysis currently depends on reproducing the
   fault on a bench.
