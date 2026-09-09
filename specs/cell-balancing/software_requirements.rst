Cell Balancing — Software Requirements
=========================================

.. swreq:: The supervisor component shall open a balancing session when a charge session ends and close it once the settled spread is at or below 20 mV
   :id: SWREQ_BALANCING_SESSION_WINDOW
   :status: draft
   :refines: ARCH_BALANCING_SUPERVISOR

   The supervisor component shall open a balancing session on the transition of
   the charge-session-ended input from false to true, and shall close that session
   in the first cycle whose settled cell voltage spread is at or below 20 mV, or
   in the first cycle whose accumulated qualifying time has reached 8 hours,
   whichever occurs first. A session closed on the spread reports the outcome as
   met; a session closed on the elapsed time reports it as missed.

.. swreq:: The supervisor component shall accumulate qualifying time only while the pack current is at or below 0.5 A and every valid cell temperature is between 15 °C and 45 °C
   :id: SWREQ_BALANCING_PRECONDITION_GATE
   :status: draft
   :refines: ARCH_BALANCING_SUPERVISOR

   The supervisor component shall add a cycle's duration to the session's
   accumulated qualifying time only when the magnitude of the pack current is at
   or below 0.5 A and every cell temperature sample carrying a cleared invalid
   flag lies between 15 °C and 45 °C inclusive. A cycle failing either condition
   shall leave the accumulated time unchanged rather than resetting it, and shall
   request the release of every bleed channel.

.. swreq:: The supervisor component shall request bleeding only for cells whose settled voltage exceeds the pack minimum by more than 20 mV
   :id: SWREQ_BALANCING_TARGET_SELECTION
   :status: draft
   :refines: ARCH_BALANCING_SUPERVISOR

   The supervisor component shall include a cell in the requested bleed set when
   its settled voltage exceeds the lowest settled cell voltage of the pack by more
   than 20 mV, and shall exclude every other cell. A pack that has not yet been
   continuously at rest for 30 minutes is not settled, and shall yield an empty
   requested bleed set.

.. swreq:: The driver component shall energise at most four bleed channels at once and never two adjacent channels
   :id: SWREQ_BLEED_CHANNEL_LIMIT
   :status: draft
   :refines: ARCH_CELL_BLEED_DRIVER

   The driver component shall reduce the requested bleed set to an energised set
   holding at most four channels, containing no two channels whose indices differ
   by one, and shall admit the requested channels in descending order of the
   cell's excess over the lowest settled cell voltage of the pack, resolving equal
   excesses by ascending channel index.

.. swreq:: The driver component shall clear every energised bleed channel when release is requested
   :id: SWREQ_BLEED_ALL_CLEAR
   :status: draft
   :refines: ARCH_CELL_BLEED_DRIVER

   The driver component shall de-energise every currently energised bleed channel
   on a release request, and shall report an empty energised set until the next
   bleed request. The release request shall take effect regardless of the bleed
   set most recently requested.
