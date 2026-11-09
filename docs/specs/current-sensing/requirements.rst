Current Sensing — Requirements
==============================

.. req:: The battery management system shall measure the pack current with an error of 0.5 % of reading or less
   :id: REQ_CURRENT_ACCURACY
   :status: draft
   :asil: QM
   :traces_to: US_CURRENT_SENSING

   The battery management system shall measure the current flowing through the
   pack between -500 A and +500 A with an error of no more than 0.5 % of the
   reading plus 0.1 A, across the whole operating temperature range of the
   pack, so that charge counting over an 8 hour shift stays within the state of
   charge budget.

.. req:: The battery management system shall detect a pack current above 800 A within 1 ms
   :id: REQ_OVERCURRENT_DETECTION
   :status: draft
   :asil: C
   :traces_to: US_CURRENT_SENSING

   The battery management system shall detect a pack current whose magnitude
   exceeds 800 A within 1 ms of it first exceeding that value, and shall report
   the detection to the contactor control independently of the periodic
   current measurement.
