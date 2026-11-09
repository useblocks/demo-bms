Cell Voltage Acquisition — Supplier Specifications
==================================================

.. supplier_spec:: The front end shall measure each cell input with a total error of 1.5 mV or less
   :id: SUP_AFE_MEASUREMENT_ACCURACY
   :status: draft
   :specifies: ARCH_CELL_MONITORING_FRONT_END

   The supplied front end shall measure each of its 16 cell inputs between
   1.5 V and 4.5 V with a total error of no more than 1.5 mV over -40 °C to
   105 °C and over its service life, and shall complete a conversion of all
   inputs within 5 ms. The 0.5 mV margin to the system requirement is kept for
   the wiring and the busbar drop.

.. supplier_spec:: The front end shall flag an open sense input within 50 ms
   :id: SUP_AFE_OPEN_WIRE_DIAGNOSIS
   :status: draft
   :specifies: ARCH_CELL_MONITORING_FRONT_END

   The supplied front end shall detect an open connection on any cell sense
   input within 50 ms, shall set a per-input fault flag readable over the
   daisy-chain link, and shall be delivered with a safety manual supporting
   use in an ASIL C function.
