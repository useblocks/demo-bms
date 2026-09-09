Cell Balancing — Architecture
=================================

Component overview
------------------

.. mermaid::

   flowchart LR
       AFE[["Cell AFE chain<br/>(hardware)"]]
       SHUNT[["Per-cell shunt resistors<br/>(hardware)"]]
       CHG[["Charge controller<br/>(internal)"]]

       SUP["ARCH_BALANCING_SUPERVISOR<br/>Balancing Supervisor"]
       DRV["ARCH_CELL_BLEED_DRIVER<br/>Cell Bleed Driver"]

       AFE -- "cell voltages, cell temperatures" --> SUP
       CHG -- "charge session ended" --> SUP
       AFE -- "pack current" --> SUP
       SUP -- "requested bleed set" --> DRV
       SUP -- "release all" --> DRV
       DRV --> SHUNT

Design context
--------------

Two constraints shape this split, and both come from the recorded review of
``REQ_CELL_BALANCING_WINDOW``, which flagged that the requirement bounds neither
the spread present when a charge session ends nor the current that counts as
"at rest", and does not say what happens when a precondition breaks part-way
through the window. The requirement is not changed here; the design closes the
three open points at this level instead, and the software requirements below
state them as numbers.

**Entry spread and shunt sizing.** The 8-hour deadline only holds against a
bounded starting spread. This design is sized for an entry spread of up to
80 mV: passive shunt balancing at 100 mA removes roughly that much from a
large-format cell inside the window, so the deadline is met without moving to
active balancing. A pack that ends a charge session further apart than 80 mV is
outside what this design promises, and the supervisor reports the session as
incomplete rather than silently missing the deadline.

**Where the two responsibilities part.** The supervisor decides *whether*
balancing may run and *which* cells should be bled; the driver decides *how many
channels may be energised at once*. That is a real boundary and not a layering
convention: the concurrency cap exists because adjacent shunt resistors share a
thermal path on the AFE board, which is a property of the hardware the driver
talks to and has nothing to do with the balancing objective the supervisor
pursues. Keeping the cap out of the supervisor is also what lets the supervisor
ask for the full ideal bleed set every cycle and stay stateless about hardware.

Elements
--------

.. arch:: Balancing Supervisor
   :id: ARCH_BALANCING_SUPERVISOR
   :status: draft
   :satisfies: REQ_CELL_BALANCING_WINDOW

   The Balancing Supervisor element owns the balancing session: when it opens,
   how long it may run, and which cells it asks to bleed. It opens a session when
   the charge controller reports a charge session ended, and closes it when the
   settled spread has reached 20 mV or when 8 hours of qualifying time have
   elapsed, whichever comes first.

   Only *qualifying* time counts toward the 8 hours: time in which the pack is at
   rest (pack current at or below 0.5 A in magnitude) and every valid cell
   temperature lies between 15 °C and 45 °C. This is the element's answer to the
   requirement's unstated disturbed-window case — the clock pauses rather than
   restarting or lapsing, so a pack that is briefly disturbed still gets its full
   8 hours of usable balancing time, and a pack that is disturbed continuously
   never reports a met deadline it did not earn.

   The element evaluates the spread on settled voltages only. It treats the pack
   as settled once it has been continuously at rest for 30 minutes, which is the
   relaxation allowance the parent requirement's second sentence folds into the
   window. Until then it holds the bleed set empty rather than acting on
   polarisation voltages that would name the wrong cells.

.. arch:: Cell Bleed Driver
   :id: ARCH_CELL_BLEED_DRIVER
   :status: draft
   :satisfies: REQ_CELL_BALANCING_WINDOW

   The Cell Bleed Driver element is the only element in this stream that touches
   the shunt hardware. It takes the bleed set the supervisor asks for and reduces
   it to the set it is safe to energise this cycle, then holds those channels
   until the next request.

   Two hardware limits shape that reduction. Adjacent shunt resistors share a
   thermal path on the AFE board, so the driver never energises two neighbouring
   channels at the same time. The board's total dissipation budget caps the number
   of simultaneously energised channels at four. When the requested set exceeds
   what those two limits allow, the driver serves the cells with the largest
   excess over the pack minimum first, so the spread closes at the fastest rate
   the hardware permits and the remaining cells are served on later cycles.

   The element also owns the release path: a single call clears every channel, and
   the supervisor uses it whenever a session closes or a precondition breaks. That
   path is deliberately not derived from an empty bleed set — an explicit release
   is what makes "stop bleeding now" independent of whatever the selection logic
   would return.
