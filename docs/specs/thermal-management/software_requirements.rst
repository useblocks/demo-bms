Thermal Management — Software Requirements
==============================================

.. swreq:: The evaluator component shall compute the highest, lowest and spread of the valid cell temperatures once per 100 ms cycle
   :id: SWREQ_TEMP_EXTREMA
   :status: draft
   :refines: ARCH_THERMAL_STATE_EVALUATOR

   The evaluator component shall publish, once per 100 ms cycle, the maximum, the
   minimum and the difference between maximum and minimum of the cell temperature
   samples that carry a cleared invalid flag. A cycle in which no valid sample is
   present publishes no figures and reports the thermal picture as unavailable.

.. swreq:: The evaluator component shall raise the cooling request above 35 °C and withdraw it at or below 30 °C
   :id: SWREQ_COOLING_HYSTERESIS
   :status: draft
   :refines: ARCH_THERMAL_STATE_EVALUATOR

   The evaluator component shall set the cooling request when the highest cell
   temperature is above 35 °C and clear it when the highest cell temperature is
   at or below 30 °C, leaving the request unchanged at any temperature between
   those two thresholds.

.. swreq:: The evaluator component shall raise the heating request below 5 °C and withdraw it at or above 10 °C
   :id: SWREQ_HEATING_HYSTERESIS
   :status: draft
   :refines: ARCH_THERMAL_STATE_EVALUATOR

   The evaluator component shall set the heating request when the lowest cell
   temperature is below 5 °C and clear it when the lowest cell temperature is at
   or above 10 °C, leaving the request unchanged at any temperature between those
   two thresholds.

.. swreq:: The evaluator component shall set the thermal imbalance warning when the temperature spread exceeds 8 K
   :id: SWREQ_IMBALANCE_WARNING
   :status: draft
   :refines: ARCH_THERMAL_STATE_EVALUATOR

   The evaluator component shall set the thermal imbalance warning output in
   every cycle whose computed temperature spread exceeds 8 K, and shall clear it
   in every cycle whose spread is at or below 8 K.

.. swreq:: The actuator interface component shall report a request as unconfirmed when no matching acknowledgement arrives within 2 seconds
   :id: SWREQ_ACTUATOR_ACK_TIMER
   :status: draft
   :refines: ARCH_COOLANT_ACTUATOR_IF

   The actuator interface component shall report the raised request as
   unconfirmed once 2 seconds have passed since it sent the setpoint frame
   without receiving an acknowledgement frame carrying the same request
   identifier. An acknowledgement carrying a different identifier does not stop
   that timer.

.. swreq:: The power limit component shall compute the temperature-driven limit as a linear ramp from 100 % at 55 °C to 0 % at 60 °C
   :id: SWREQ_TEMP_DERATE_RAMP
   :status: draft
   :refines: ARCH_POWER_LIMIT_CALCULATOR

   The power limit component shall compute the temperature-driven share of the
   permitted discharge power as 100 % at or below 55 °C highest cell temperature,
   as 0 % at or above 60 °C, and as the linear interpolation between those two
   points in between.

.. swreq:: The power limit component shall publish the minimum of the temperature-driven and actuator-driven power limits
   :id: SWREQ_LIMIT_MINIMUM
   :status: draft
   :refines: ARCH_POWER_LIMIT_CALCULATOR

   The power limit component shall publish, as the permitted discharge power, the
   smaller of the temperature-driven share and the actuator-driven share, where
   the actuator-driven share is 30 % while the actuator interface reports an
   unconfirmed request and 100 % otherwise.
