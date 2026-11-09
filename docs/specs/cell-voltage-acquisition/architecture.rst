Cell Voltage Acquisition — Architecture
=======================================

Elements
--------

.. arch:: Cell Monitoring Front End
   :id: ARCH_CELL_MONITORING_FRONT_END
   :status: draft
   :satisfies: REQ_CELL_VOLTAGE_ACCURACY, REQ_OPEN_WIRE_DETECTION

   The Cell Monitoring Front End element measures the voltage of up to 16
   series cells per module, runs the open-wire diagnosis on every sense input,
   and reports the results over an isolated daisy-chain link. It is a bought
   component; its behaviour is pinned down by the supplier specifications of
   this stream rather than by software requirements.
