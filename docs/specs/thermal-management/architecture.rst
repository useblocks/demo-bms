Thermal Management — Architecture
=====================================

Component overview
------------------

.. needuml::

   rectangle "Cell AFE chain\n(hardware)" as AFE <<external>>
   rectangle "Coolant pump / heater\n(hardware)" as PUMP <<external>>
   rectangle "Vehicle bus\n(external)" as BUS <<external>>

   {{flow("ARCH_THERMAL_STATE_EVALUATOR")}}
   {{flow("ARCH_COOLANT_ACTUATOR_IF")}}
   {{flow("ARCH_POWER_LIMIT_CALCULATOR")}}

   AFE --> ARCH_THERMAL_STATE_EVALUATOR : cell temperatures
   ARCH_THERMAL_STATE_EVALUATOR --> ARCH_COOLANT_ACTUATOR_IF : cool / heat request
   ARCH_THERMAL_STATE_EVALUATOR --> ARCH_POWER_LIMIT_CALCULATOR : highest cell temperature
   ARCH_COOLANT_ACTUATOR_IF --> ARCH_POWER_LIMIT_CALCULATOR : confirmation timeout
   ARCH_COOLANT_ACTUATOR_IF --> PUMP
   ARCH_THERMAL_STATE_EVALUATOR --> BUS : imbalance warning
   ARCH_POWER_LIMIT_CALCULATOR --> BUS : permitted discharge power

Elements
--------

.. arch:: Thermal State Evaluator
   :id: ARCH_THERMAL_STATE_EVALUATOR
   :status: draft
   :satisfies: REQ_COOLING_REQUEST, REQ_HEATING_REQUEST, REQ_CELL_TEMP_SPREAD

   The Thermal State Evaluator element owns the thermal picture of the pack. Once
   per 100 ms cycle it reduces the valid cell temperatures to three figures —
   highest, lowest and their spread — and derives the cooling and heating
   requests from them using two Schmitt-trigger bands, 35/30 °C for cooling and
   5/10 °C for heating. It also owns the imbalance verdict, raised on a spread
   above 8 K, and it is the only element in this stream that reads temperature
   sensors directly.

.. arch:: Coolant Actuator Interface
   :id: ARCH_COOLANT_ACTUATOR_IF
   :status: draft
   :satisfies: REQ_COOLING_REQUEST, REQ_HEATING_REQUEST, REQ_THERMAL_ACTUATOR_FAILSAFE

   The Coolant Actuator Interface element owns the conversation with the coolant
   pump and the pack heater. It forwards the evaluator's request as a setpoint
   frame and expects an acknowledgement frame carrying the same request
   identifier; a 2 second acknowledgement timer per raised request is what turns
   silence into an explicit unconfirmed verdict for the power limit calculator.
   It never decides a power limit itself and never re-derives a request.

.. arch:: Thermal Power Limit Calculator
   :id: ARCH_POWER_LIMIT_CALCULATOR
   :status: draft
   :satisfies: REQ_POWER_DERATING, REQ_THERMAL_ACTUATOR_FAILSAFE

   The Thermal Power Limit Calculator element owns the permitted discharge power
   the vehicle sees. It computes the temperature-driven limit as a linear ramp
   from 100 % at 55 °C to 0 % at 60 °C highest cell temperature, computes the
   actuator-driven limit as a flat 30 % whenever the actuator interface reports
   an unconfirmed request, and publishes the minimum of the two. Taking the
   minimum is what keeps the two independent causes of derating from cancelling
   each other out.
