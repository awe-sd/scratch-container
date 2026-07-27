# Dossier — Hanson Solar (ERCOT INR 23INR0086)

Researched 2026-07-17. All claims below are traceable to artifacts in `sources/` or `imagery/`
and to the chronological log in `log.md`. Banned queue-aggregator sources (interconnection.fyi,
cleanview.co, etc.) surfaced repeatedly in generic web searches but were never opened or cited.

## 1. Identity & verdict

- **Project**: Hanson Solar (solar) + co-located Hanson Storage (battery), Coleman County, TX.
- **Interconnecting entity**: Hanson Solar, LLC — a single-project SPV of **Cypress Creek
  Renewables (CCR)**, a national utility-scale solar/storage developer.
- **Verdict: REAL, ACTIVELY UNDER CONSTRUCTION** (`real_active`). This is not a paper filing:
  it has a signed interconnection agreement and amendment with Oncor, a fully executed Chapter
  313 school tax agreement with three years of annual compliance reports, a closed
  non-recourse project financing (Nov 2025) naming an EPC and lenders, and — most decisively —
  Sentinel-2 imagery showing a ~3,000-acre parcel matching the project's own site plan
  transitioning from raw farmland to extensive graded/cleared civil works between March and
  September 2025, with grading essentially complete site-wide by 2026.

## 2. LLC → parent chain

| Entity | Relation | Evidence |
|---|---|---|
| Hanson Solar, LLC | project SPV | Named party on Ch313 filing and PUCT interconnection agreement |
| Cypress Creek Renewables (CCR) | developer/owner/operator ("parent" in commercial sense) | PR Newswire release: CCR "closes financing for Hanson Solar"; CCR's Improvements Map (Ch313 Tab 11) is titled "Cypress Creek Renewables" / "Hanson Solar, LLC"; CCR CEO Sarah Slusser quoted on the project |
| TIC – The Industrial Company | EPC contractor (not corporate parent) | PR Newswire; Google Places pin literally named "TIC Hanson solar"; TIC is a Kiewit Corporation subsidiary |
| Meta (offtaker, not owner) | PPA/environmental-attribute counterparty | pv-magazine-usa.com (Mar 2025), PR Newswire (Nov 2025) |
| Cummings Westlake / O'Hanlon Demerath & Castillo | Ch313 tax consultants | Signature pages inside the Ch313 application PDF |

No free public TX SOS / OpenCorporates record was found under the exact name "Hanson Solar,
LLC" (full-text SOS entity search requires a paid SOSDirect account, out of scope). The chain
above is established through convergent primary/press sources rather than a single registry
lookup.

## 3. Land tenure

**Leased, not purchased.** The Ch313 application's own "Improvements Map" (Tab 11, filed 2021)
explicitly labels a "Leased land border" around the ~3,000-acre reinvestment zone, and Tab 9
("Description of Land") is answered "Not Applicable" — consistent with the applicant not owning
the underlying land. Independently, a Coleman County Appraisal District (CAD) owner-name search
for "Hanson Solar", "Hanson", "Cypress Creek", and "Cypress Creek Renewables" returned **zero**
parcel records in all four cases — exactly what is expected when land is leased from
individual ranch owners who remain the taxpayer of record. We did not identify the specific
underlying landowner names (not derivable from the packet, and not guessed).

## 4. Site location

- **Coordinates: 31.6950 N, -99.5315 W** — method: **imagery** (satellite feature match),
  confidence: **high**.
- Derivation: a wide-frame (6 km buffer) Sentinel-2 true-color chip centered on an initial
  Google Places delivery-pin coordinate revealed a distinctive irregular (L-shaped, notched)
  cleared/graded polygon roughly 1.5–2 km northeast of the pin. This polygon's shape was
  pixel-matched against the boundary drawn on Cypress Creek's own Ch313 "Improvements Map"
  (project boundary + reinvestment zone) — an essentially exact shape match, including the
  northward notch where that map places the collector substation.
- **Four independent cross-checks converge within ~3.5 km of this point, with no contradiction**:
  1. Google Places delivery pin "TIC Hanson solar", 6725 FM503, Valera, TX 76884
     (31.692543, -99.548231) — a construction-logistics pin registered under the EPC's name.
  2. The PUCT interconnection agreement's plain-language POI description: "The Fisk Switch will
     be located approximately 12 miles southwest of Coleman, TX directly west of CR 362."
  3. OpenStreetMap/Overpass: a populated place named "Fisk" at 31.6710, -99.4892 (the
     namesake of "Fisk Switch"), ~3.4 mi from our site point.
  4. The Ch313 vicinity map, which places the project boundary just south of Coleman, in
     Panther Creek CISD, near the Valera community.
- The exact geographic coordinates of the Point of Interconnection itself (the Fisk Switch /
  generator substation tie point) were **not** obtainable — Oncor's filing letter states station
  equipment detail in Exhibit C was redacted as CEII (Critical Energy/Electric Infrastructure
  Information) before PUCT filing.

## 5. Point of interconnection (from the primary interconnection agreement, not a queue aggregator)

Per the signed ERCOT Standard Generation Interconnection Agreement (Oncor Electric Delivery
Company LLC ⟷ Hanson Solar, LLC, dated Sept 20, 2023): "The Point of Interconnection is located
in Coleman County, Texas, at the **Fisk Switch** within TSP's **Brown Switch – Central Bluff
Switch 345 kV Transmission line**." This matches the identity packet's POI description exactly
("tap 345kV 1444 Brown - 11406 Central Bluff") — independently confirmed via the *signed IA
itself*, filed with PUCT under Oncor's standing informational-filing docket (Control No. 35077),
not via any queue tracker.

Generating equipment per Exhibit C: 104× SMA SC4400UP-US inverters (457.6 MVA nameplate,
dispatched 396 MW solar) plus a co-located BESS — 79× Tesla Megapack inverters (118.5 MVA
nameplate, dispatched 101.4 MW) under a companion INR (24INR0057, "Hanson Storage").

## 6. Construction timeline — from the IA itself (contractual schedule)

| | Original IA (signed 9/20/2023) | Amendment No. 1 (signed 6-7/2024, filed 8/15/2024) |
|---|---|---|
| In-Service Date | May 8, 2025 | **December 3, 2026** |
| Trial Operation | May 20, 2025 | **December 17, 2026** |
| Scheduled Commercial Operation | October 21, 2025 | **April 17, 2027** |

The amended Commercial Operation Date, **April 17, 2027, matches the identity packet's reported
COD (2027-04-17) exactly.** This confirms the reported date is the utility's real contractual
schedule (not a placeholder or fabrication) — it does **not**, by itself, prove the date is
achievable; that requires independent evidence (see §7). Note the schedule already slipped
~18 months once, between the 2023 original and the 2024 amendment, before construction had
even begun — relevant context for drift risk.

Letters of credit posted with Oncor as project security: $11.3M effective Nov 2023, rising to
$13.4M by Dec 2025 — real financial commitment behind the agreement, not merely a paper filing.

## 7. Satellite ground truth (Sentinel-2, independent of any filing)

Monthly (Jul 2024–Jul 2026) and dekad (Apr–Jul 2026) composites, ~3 km center point, read
frame-by-frame (see `imagery/` and `log.md` for the full series and `timelapse.gif`):

- **2024-07 through 2025-03**: undisturbed farmland/pasture across the entire project
  footprint. No construction signal.
- **2025-03-01 → 2025-04-01: first activity.** A bright, reflective, L-shaped graded pad
  appears precisely at the substation location shown on Cypress Creek's own Improvements Map.
  This is a tight bracket (absent 3/1, present 4/1) — **first_activity_seen ≈ 2025-04**.
- **2025-06**: grading/clearing has spread across roughly the southeastern half to
  two-thirds of the ~3,000-acre polygon.
- **2025-09**: grading now covers essentially the entire polygon, including the northern
  section that was still natural as of June.
- **2025-12 → 2026-03**: internal road/parcel grid sharpens; small green patches appear
  (candidate re-seeding of completed grading); some darker, more uniform rectangular
  patches appear from March 2026 that are a plausible early racking/panel signal.
- **2026-06/2026-07 (latest, incl. dekad frames through 2026-07-11)**: bare/graded footprint
  now spans nearly the full boundary; multiple small light-toned structures visible (plausible
  inverter/transformer/O&M pads); no clear, unambiguous full-field panel signature (the
  uniform blue-gray block a completed utility-scale solar array typically shows) is visible.
  Recent frames (June 11 → July 11) show a broadly stable graded footprint — no further
  large-scale expansion in the last ~6 weeks, consistent with the site having moved past bulk
  earthwork into equipment/electrical installation.

**Important honesty note**: Sentinel-2's 10 m resolution cannot definitively distinguish
installed racking/panels from bare graded soil in true color. The verdict below is my best
read of the available imagery, not a certainty.

**Construction verdict: `racking`** (transitioning from site-wide grading, complete by ~Sept
2025, into an equipment-installation phase from ~March 2026 onward) — chosen over
`substantially_complete`/`operating` because no unambiguous panel-field signature was observed.

## 8. COD assessment

- **Reported (claim)**: 2027-04-17.
- **Contractually confirmed**: the same date appears as the Scheduled Commercial Operation
  Date in the Oncor–Hanson Solar IA Amendment No. 1 (filed with PUCT Aug 2024) — this is a
  real, signed, TSP-countersigned schedule, not a marketing claim. This is the strongest single
  piece of evidence in this dossier, but it demonstrates the date is *grounded*, not that it is
  *on track* — the two questions are separate.
- **Independent construction-pace read**: imagery shows civil works (grading/roads) essentially
  complete site-wide by Sept 2025, with a stable, extensive graded footprint through July 2026
  and equipment-stage signals appearing from ~March 2026 — i.e., construction has been
  progressing roughly in step with the amended schedule (In-Service Date Dec 3, 2026 is ~5
  months out from the latest clear imagery), not stalled.
- **Independent COD estimate: 2027 Q2** (April–June 2027), i.e. no material change from the
  contractual date, based on observed pace.
- **Drift risk: medium.** Reasoning: (a) the schedule has already slipped once by ~18 months
  during the pre-construction/interconnection phase (Oct 2025 → Apr 2027), showing this
  project is not immune to schedule risk; (b) as of the latest available imagery (~July 2026)
  a full panel/racking signature could not be confirmed, leaving ~5 months to In-Service Date
  with the final electrical-installation stage not visually verified; against this, (c)
  financing has closed, an EPC (TIC/Kiewit) is engaged, the offtake (Meta) is signed, and
  the graded footprint is essentially complete across the whole site — all real-project
  markers pointing toward on-schedule delivery rather than further slippage. Net: not "low"
  (unverified final stage + one prior slip) but not "high" either (all financing/construction
  fundamentals are in place) — **medium** is the honest call.

## 9. What could NOT be determined

- Exact GPS coordinates of the Fisk Switch / generator substation tie point (CEII-redacted).
- Underlying ranch-owner names on the leased parcels (CAD has no records under the LLC/developer
  name, as expected for a lease; the true owners were not identifiable from the research packet).
- Definitive confirmation of installed racking/PV modules vs. bare graded earth, due to Sentinel-2's
  10 m resolution ceiling — the "racking" verdict is a best-available read, not a certainty.
- Any TX Secretary of State corporate filing detail for "Hanson Solar, LLC" specifically (full-text
  SOS/OpenCorporates search returned nothing free; SOSDirect requires a paid account).
