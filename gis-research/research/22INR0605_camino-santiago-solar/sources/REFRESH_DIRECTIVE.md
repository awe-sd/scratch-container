# Refresh directive — Camino Santiago Solar 22INR0605 (user-ordered, 2026-07-20)

The prior deep scan collected NOTHING beyond the IA (35077-2028 sheets are on disk).
This refresh has a 1M token budget for an EXHAUSTIVE document hunt. Milam County,
196.3 MW solar, queue COD 2027-09-01.

Work every rung to a conclusion or an explicit negative, saving ARTIFACTS (a URL in
a note is not an artifact):
1. IA 35077-2028: render + read ALL exhibits/attachments (exhibit.py scan/render) —
   site map, milestone schedule + financial security amounts → contractual_schedule.
   Check the docket index for AMENDMENTS beyond the base SGIA (puct.py match runs
   rung-0 automatically).
2. SPV chain: spv.py resolve; TX Comptroller taxable-entity + TX SOS for the SPV's
   registered agent/officers → developer family. Places pin (gmaps.py places) for
   both queue name and SPV name — beware name-collision traps.
3. Ch.313/JETI: ch313.py resolve + check ALL Milam-county ISDs by district name
   (Cameron/Milano/Rockdale/Thorndike/Buckholts/Gause ISDs) in the cached lists.
   Milam = the Quantum corridor county (Eastbell Milam Solar II 24INR0208 is nearby;
   several Ch.313s exist there) — download any matching application/agreement/
   FINDINGS PDFs and render their exhibits.
4. County records: Milam CAD owner search (SPV + variants); commissioners court
   minutes (search.py); reinvestment-zone orders.
5. EIA: eia_history (name + SPV name variants; beware operating-plant false matches —
   the guard will flag them); if absent = negative evidence.
6. TCEQ: n/a for solar (record expected-absence, don't chase).
7. News/PR: developer announcements, PPA, financing (search.py; banned aggregators
   are hook-blocked — futuregrid.io was cited for this very project once: never again).
8. Imagery: fresh chips at the documented site fix (map-derived, never guessed),
   wide-first, ≤6 image reads.

Deliverables: complete findings.json (all keys evidenced), dossier.md, brief.html
with contractual_schedule table incl. financial-security amounts + map artifacts.
