State Estimation — Architecture
===================================

Component overview
------------------

.. mermaid::

   flowchart LR
       SHUNT[["Pack current shunt<br/>(hardware)"]]
       AFE[["Cell AFE chain<br/>(hardware)"]]
       NVM[["Non-volatile memory<br/>(hardware)"]]
       BUS[["Vehicle bus<br/>(external)"]]

       CC["ARCH_COULOMB_COUNTER<br/>Coulomb Counter"]
       OCV["ARCH_OCV_CORRECTOR<br/>Open-Circuit-Voltage Corrector"]
       STORE["ARCH_SOC_STORE<br/>State-of-Charge Store"]
       SOH["ARCH_SOH_TRACKER<br/>Capacity Fade Tracker"]
       VAL["ARCH_ESTIMATION_VALIDITY_MONITOR<br/>Estimation Validity Monitor"]
       PUB["ARCH_STATE_PUBLISHER<br/>Battery State Publisher"]

       SHUNT --> CC
       SHUNT --> VAL
       AFE --> OCV
       CC -- "counted charge" --> OCV
       OCV -- "corrected SOC" --> PUB
       OCV -- "rest-point SOC" --> SOH
       CC -- "throughput window" --> SOH
       STORE <-- "restore / persist SOC" --> OCV
       STORE <--> NVM
       VAL -- "validity flag" --> PUB
       SOH -- "remaining capacity" --> PUB
       PUB --> BUS

Elements
--------

.. arch:: Coulomb Counter
   :id: ARCH_COULOMB_COUNTER
   :status: draft
   :satisfies: JAMA_Rollout_Demo-SYSRQ-11

   The Coulomb Counter element owns the charge integral of the pack. It
   integrates the signed pack current with the trapezoidal rule on a fixed 10 ms
   tick, accumulating in ampere-seconds in a 64-bit fixed-point accumulator so
   that a full day of driving cannot overflow or lose resolution. It exposes the
   accumulated charge and the charge throughput since the last full cycle, and it
   holds no absolute reference of its own — the absolute anchor comes from the
   corrector.

.. arch:: Open-Circuit-Voltage Corrector
   :id: ARCH_OCV_CORRECTOR
   :status: draft
   :satisfies: JAMA_Rollout_Demo-SYSRQ-11, JAMA_Rollout_Demo-SYSRQ-13

   The Open-Circuit-Voltage Corrector element owns the absolute state-of-charge
   anchor and the fused estimate that is published. It detects a rest condition
   with a monotonic timer over ``|current| < 1 A`` and, at 30 minutes of rest,
   replaces the counted value with the value read from a 21-point
   open-circuit-voltage table interpolated linearly on the mean cell voltage.
   Between corrections it reports the anchor plus the counter's delta, which is
   what keeps the fused estimate inside its accuracy band while the vehicle
   drives.

.. arch:: State-of-Charge Store
   :id: ARCH_SOC_STORE
   :status: draft
   :satisfies: JAMA_Rollout_Demo-SYSRQ-14

   The State-of-Charge Store element owns the non-volatile shadow of the
   published state of charge. It writes a two-slot alternating record — value,
   monotonic write counter and checksum — on every shutdown request and
   additionally every 60 seconds while awake, so a power loss between writes
   still leaves one intact slot. On wake-up it hands the higher-counter valid
   slot to the corrector as its starting anchor.

.. arch:: Capacity Fade Tracker
   :id: ARCH_SOH_TRACKER
   :status: draft
   :satisfies: JAMA_Rollout_Demo-SYSRQ-15

   The Capacity Fade Tracker element owns the remaining-capacity figure. It
   derives a capacity candidate from the charge counted between two
   open-circuit-voltage rest anchors that are at least 40 % state of charge
   apart, and passes it through a monotonic clamp that only ever accepts a
   candidate below the currently reported value. The reported figure is a
   percentage of rated capacity and is itself persisted, so it survives a power
   cycle.

.. arch:: Estimation Validity Monitor
   :id: ARCH_ESTIMATION_VALIDITY_MONITOR
   :status: draft
   :satisfies: JAMA_Rollout_Demo-SYSRQ-16

   The Estimation Validity Monitor element owns the trustworthiness verdict for
   the estimate. It watches the pack-current signal with a 5 second staleness
   timer and raises an unreliable verdict when the timer expires, clearing it
   only on notification of a completed open-circuit-voltage correction. It is a
   pure observer: it never modifies the estimate, it only qualifies it.

.. arch:: Battery State Publisher
   :id: ARCH_STATE_PUBLISHER
   :status: draft
   :satisfies: JAMA_Rollout_Demo-SYSRQ-12, JAMA_Rollout_Demo-SYSRQ-16

   The Battery State Publisher element owns the vehicle-facing battery state
   frame. It runs on a dedicated 100 ms cycle and always sends the most recent
   values it holds for state of charge, remaining capacity and the validity flag,
   sending the previous value rather than skipping a cycle if a producer has not
   updated. Decoupling the send cycle from the producers is what makes the
   publication period independent of estimator run time.
