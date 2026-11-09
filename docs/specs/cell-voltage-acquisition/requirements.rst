Cell Voltage Acquisition — Requirements
=======================================

.. req:: The battery management system shall measure every cell voltage with an error of 2 mV or less
   :id: REQ_CELL_VOLTAGE_ACCURACY
   :status: draft
   :asil: C
   :traces_to: US_CELL_VOLTAGE_ACQUISITION

   The battery management system shall measure the voltage of every cell in
   the pack between 1.5 V and 4.5 V with an error of no more than 2 mV, at
   least every 20 ms, across the whole operating temperature range of the pack.

.. req:: The battery management system shall detect an open cell sense wire within 100 ms
   :id: REQ_OPEN_WIRE_DETECTION
   :status: draft
   :asil: C
   :traces_to: US_CELL_VOLTAGE_ACQUISITION

   The battery management system shall detect an open connection between a
   cell and its voltage measurement input within 100 ms of it occurring, and
   shall report that cell's voltage as invalid rather than as a measured value.
