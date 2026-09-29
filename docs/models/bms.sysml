// BMS system architecture — SysML v2 textual notation.
//
// This file is the EXPORT of the MBSE tool, which stays the master of the system
// model. The repository never edits it; `ubc script import-models` reads it and
// turns every part definition into a read-only need, linked to the Jama
// requirements it satisfies.
//
// The requirements are MIRRORED here, not authored: each requirement usage
// carries its Jama id as its SysML v2 short name, `<'JAMA_...'>`, which is how
// an MBSE model conventionally references an item whose master is an ALM. The
// `satisfy` relationships are the model's own claim of which subsystem answers
// which requirement — the link the modeller owns.

package BMS {

    doc /* System architecture of the battery management system of a
         * high-voltage traction battery: five subsystems, and which of the
         * system requirements held in Jama each of them satisfies. */

    // --- system requirements, mirrored from Jama by id -----------------------

    requirement <'JAMA_Rollout_Demo-SYSRQ-2'> cellBalancingWindow;
    requirement <'JAMA_Rollout_Demo-SYSRQ-3'> cellVoltageLimits;
    requirement <'JAMA_Rollout_Demo-SYSRQ-4'> packOvercurrent;
    requirement <'JAMA_Rollout_Demo-SYSRQ-5'> cellOvertemperature;
    requirement <'JAMA_Rollout_Demo-SYSRQ-6'> faultReactionTime;
    requirement <'JAMA_Rollout_Demo-SYSRQ-7'> measurementPlausibility;
    requirement <'JAMA_Rollout_Demo-SYSRQ-8'> faultLatch;
    requirement <'JAMA_Rollout_Demo-SYSRQ-9'> faultRecord;
    requirement <'JAMA_Rollout_Demo-SYSRQ-10'> isolationFault;
    requirement <'JAMA_Rollout_Demo-SYSRQ-11'> socAccuracy;
    requirement <'JAMA_Rollout_Demo-SYSRQ-12'> socUpdatePeriod;
    requirement <'JAMA_Rollout_Demo-SYSRQ-13'> socRestCorrection;
    requirement <'JAMA_Rollout_Demo-SYSRQ-14'> socPersistence;
    requirement <'JAMA_Rollout_Demo-SYSRQ-15'> capacityReport;
    requirement <'JAMA_Rollout_Demo-SYSRQ-16'> socInvalidFlag;
    requirement <'JAMA_Rollout_Demo-SYSRQ-17'> coolingRequest;
    requirement <'JAMA_Rollout_Demo-SYSRQ-18'> heatingRequest;
    requirement <'JAMA_Rollout_Demo-SYSRQ-19'> powerDerating;
    requirement <'JAMA_Rollout_Demo-SYSRQ-20'> cellTemperatureSpread;
    requirement <'JAMA_Rollout_Demo-SYSRQ-21'> thermalActuatorFailsafe;

    // --- the system and its subsystems ---------------------------------------

    part def BatteryManagementSystem {
        doc /* The controller that keeps the traction battery inside its safe
             * operating window, reports its state and keeps it at a usable
             * temperature. */

        part cellProtection : CellProtection;
        part stateEstimation : StateEstimation;
        part thermalManagement : ThermalManagement;
        part cellBalancing : CellBalancing;
        part isolationMonitoring : IsolationMonitoring;

        satisfy cellVoltageLimits by cellProtection;
        satisfy packOvercurrent by cellProtection;
        satisfy cellOvertemperature by cellProtection;
        satisfy faultReactionTime by cellProtection;
        satisfy measurementPlausibility by cellProtection;
        satisfy faultLatch by cellProtection;
        satisfy faultRecord by cellProtection;

        satisfy socAccuracy by stateEstimation;
        satisfy socUpdatePeriod by stateEstimation;
        satisfy socRestCorrection by stateEstimation;
        satisfy socPersistence by stateEstimation;
        satisfy capacityReport by stateEstimation;
        satisfy socInvalidFlag by stateEstimation;

        satisfy coolingRequest by thermalManagement;
        satisfy heatingRequest by thermalManagement;
        satisfy powerDerating by thermalManagement;
        satisfy cellTemperatureSpread by thermalManagement;
        satisfy thermalActuatorFailsafe by thermalManagement;

        satisfy cellBalancingWindow by cellBalancing;

        satisfy isolationFault by isolationMonitoring;
    }

    part def CellProtection {
        doc /* Keeps every cell inside the safe window of its chemistry: measures
             * voltage, temperature and current, and opens the high-voltage
             * contactors when a limit is violated. */
    }

    part def StateEstimation {
        doc /* Estimates the state of charge and the remaining capacity, and says
             * when that estimate can no longer be trusted. */
    }

    part def ThermalManagement {
        doc /* Keeps the pack at a usable temperature and derates the permitted
             * discharge power when it runs hot. */
    }

    part def CellBalancing {
        doc /* Brings the cell voltages of the pack back together after a charge
             * session. */
    }

    part def IsolationMonitoring {
        doc /* Watches the insulation between the high-voltage bus and the vehicle
             * chassis. */
    }
}
