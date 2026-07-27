# Research log — Camino Santiago Solar (22INR0605)
*(Deep scan started 2026-07-20; triage log preserved below)*

## D0 — Skeleton written
findings.json skeleton written with all null values. Triage handoff read: SPV = Camino Solar Project LLC, developer = Cobra Grupo, PUCT portal blocked at triage, no site candidate.

## D1 — IA extraction

**puct.py match 22INR0605 → CONFIRMED**
- Docket 35077-2028, filed 2025-01-02, TSP = Oncor Electric Delivery Company LLC
- Generator = **Camino Solar Project, LLC** (not "Camino Santiago Solar, LLC")
- Signed: Generator 2024-11-27; Oncor 2024-12-06
- PDF: sources/2026-07-20_puct_35077-2028_standard-generation-interconnection-agreement-be.pdf (1616 KB, 50 pages)
- INR found in document text → CONFIRMED

**exhibit.py sheet → 13 sheets rendered**

**Key exhibit pages read:**
- p6 (cover): IA parties confirmed — Oncor + Camino Solar Project, LLC, referencing Facilities Study Agreement dated April 12, 2023
- p7 (signatures): Signed 2024-11-27 (generator, Oscar Manuel Yunta Toledo, Officer) / 2024-12-06 (Oncor, Jim Greer EVP/COO)
- p29 (Exhibit B Time Schedule): **In-Service Date: December 3, 2026 · Trial Operation: January 3, 2027 · Scheduled COD: February 18, 2027**. Notice to proceed deadlines: design/procurement Dec 6, 2024; construction commencement Dec 3, 2024. Right-of-Way coordination by Oct 31, 2025.
- p31: TSP deeds/ROW for Herndon Switch by Jan 23, 2026; 4-hole pads at POI by Oct 9, 2026; generator breakers/SCADA by Nov 5, 2026.
- p36 (Exhibit C Attachment C): TSP Herndon Switch infrastructure — NEW 345kV switchyard, ring bus, connected via 345kV lines to Little Pond Switch (west) and Hog Creek Switch (east).
- p43 (Attachment 1 to Exhibit C): One-line diagram: Herndon Switch ↔ Camino Santiago Solar 196.3 MW; 345kV to Little Pond SW and Hog Creek SW.
- p48 (Exhibit D): Notices — Camino Solar Project LLC @ 580 Westlake Park Blvd #515, Houston TX 77079 (grupocobra.com emails: trentcornelius@, adelfa@, daniel.gonzales@)
- p50 (Exhibit E): Financial security = **Irrevocable Standby Letter of Credit $28,511,804** due by Dec 6, 2024

**COD divergence:** IA Exhibit B COD = 2027-02-18; queue now shows 2027-09-01 → queue slipped 6+ months BEYOND the IA schedule, meaning the IA schedule itself is now stale.

**ch313.py → NEGATIVE:** No Ch.313/JETI match for Milam County. Normal for 2022 queue entry; no abatement filed under this name.

**spv.py → 3 EIA-860M county matches (all county+MW proximity, none name-matching):**
- Yaupon Solar LLC, 200 MW, planned=2026-09 @ 31.0444,-96.8514
- Cattlemen Solar II, 200 MW, planned=2026-10 @ 31.08356,-96.85732
- Orion I Solar (operating), 200 MW, @ 30.99651,-97.00151
None of these is Camino Santiago Solar — EIA 860M has no match by name. "not_in_eia_near_cod" confirmed.

## D2 — Site identification

**IA Exhibit C (p32):** "The Point of Interconnection is located in Milam County, Texas, at the proposed Herndon Switch in TSP's Little Pond SW to Hog Creek SW 345 kV line." Coordinates redacted (CEII) in the filed document.

**Google Places searches:**
- "Camino Santiago Solar" → NO RESULTS
- "Camino Solar Project Milam County Texas" → NO RESULTS (returned unrelated projects)
- "Herndon Texas Milam County" → Herndon Cemetery, Rosebud TX 76570, 31.041296,-96.863594 ✓ (locality confirmed)
- "Little Pond Texas Milam County" → Little Pond Creek 30.986007,-96.937255; BK Burk Little Pond Creek Ranch @ 3500 Co Rd 136, Rosebud TX 76570 ✓
- "Cobra solar Milam County Texas" → NO RESULTS (returned Orion I Solar only)
- "Camino Santiago Solar construction site" → NO RESULTS

**Site estimate:** ~31.01,-96.90 (midpoint of Herndon Cemetery and Little Pond Creek corridor, both confirmed in Milam County near Rosebud TX). Low confidence — exact coords CEII.

**CDSE imagery:** ALL ATTEMPTS FAILED — RemoteDisconnected on every chip/timelapse call (infrastructure issue 2026-07-20). Auth tokens work (CDSE login OK); openEO /result and /jobs endpoints return connection reset before response. Logged as negative evidence — no satellite confirmation possible this run.

**Google Static Map:** HTTP 403 — Maps Static API not enabled for this key. No site map image.

## D3 — Gap fill

**DDG searches:** ALL FAILED (ConnectionError on all backends) — "Herndon Switch substation Milam County", "Hog Creek Switch Texas 345kV", "Herndon Milam County solar interconnection", "Camino Santiago Solar Milam County", "Camino Solar Project Texas Cobra Grupo", "Cobra solar Texas 196 MW Milam County" — all recorded as negative evidence.

**TX Comptroller:** JS-driven portal; GET redirects to search UI — no results obtainable programmatically.

**TX SOS:** Requires paid authenticated session (SOSDirect); not accessible.

**Milam CAD:** Portal JS-blocked — no owner-name search results returned.

**Milam County commissioners court (BoardBook):** No agenda index items mentioning solar/Camino/Cobra/Herndon visible in title listings.

**Grupo Cobra website:** 404 on projects page; homepage has no specific US project listings.

**ch313.py:** NEGATIVE — no Ch.313 or JETI match for Milam County / Camino Santiago Solar.

## D4 — Narrative / D5 — Wrap-up

**eia_history.py 22INR0605:** 3 county+MW candidates; none match entity — Orion I (operating, different owner), Cattlemen II (different owner), Stoneridge (RWE Clean Energy — operating/near-operating, completely different entity). **Camino Santiago Solar is NOT in EIA-860M.** Negative evidence at 14 months out from reported COD.

**queue_history.py:** Confirmed 41 snapshots, 4 COD changes, timeline.md written.

**build_brief.py:** brief.html written (14 KB).

**Dossier and findings.json:** Written. Verdict: real_early, high drift risk, independent COD 2027-Q3 to 2028-Q1.

## Refresh pass — 2026-07-20 (user-ordered, 1M token budget, REFRESH_DIRECTIVE.md)

**Exhibit re-scan (sheets 09-13, full pages):** Confirmed IA docket 35077-2028 contains NO
parcel/boundary/acreage map beyond the Attachment 1 one-line diagram (p43, already in
map_artifacts). Attachments 2/2A/3 and Exhibit D are text-only (SCADA table, comms
diagram, protection requirements, notices). No project_area figure obtainable from this IA.

**puct.py filings 35077 --party "Camino":** 0 results beyond the base SGIA already on
disk — no amendment filed in the docket as of 2026-07-20. Base IA remains the only
contractual document.

**ch313.py resolve --name "Cobra" / --name "Camino":** Both NEGATIVE (same result as
triage) — confirms no Ch.313/JETI filing under any Camino/Cobra name.

**spv.py resolve:** unchanged — only county+MW proximity candidates (Yaupon, Cattlemen II,
Ben Milam/Orion I), none name-matching. No new SPV lead.

**gmaps.py places — 4 variants, ALL HTTP 429** (rate-limited): "Camino Santiago Solar",
"Camino Solar Project LLC Texas", "Cobra Grupo solar Milam County", "Camino Santiago Solar
construction". Infra/quota issue this run, not a negative result — could not complete
Places lookups.

**cdse.py chip retry (31.014,-96.900, 2026-07-15):** Still RemoteDisconnected — same
openEO outage as the prior deep scan. Imagery remains unobtainable both runs.

**search.py "Camino Santiago Solar Milam County Texas":** Top hits: Milam County
Commissioners Court Oct-2022 agenda (title only, not fetched — would need manual PDF
check), Ferrovial 250MW Milam County solar (DIFFERENT project, LinkedIn +
newsroom.ferrovial.com — not Cobra, do not conflate), interconnection.fyi (banned,
suppressed). No direct hit on Camino Santiago Solar itself.

**search.py "Camino Solar Project LLC Cobra Grupo Texas":** Two leads investigated via
WebFetch, BOTH FALSE POSITIVES (name collisions, logged as negative evidence):
- power-technology.com "Camino Solar PV Park" → **Avangrid Renewables** project in
  **California** (57MW, Riverside CA PPA, COD Dec 2025). Unrelated namesake — NOT this
  project. Do not cite.
- spainuscc.org "Grupo Cobra's zero.e nears completion of its First US Solar Project" →
  this is **Barrett Solar Project, Rains County TX** (172 MWDC/125 MWAC, data-center PPA,
  COD March 2026), explicitly zero.e's FIRST utility-scale US solar facility. Camino
  Santiago Solar / Milam County NOT mentioned anywhere in the article. **Decisive negative
  evidence**: if Camino Santiago were further along than Barrett, Cobra's own PR (which is
  actively promoting Barrett + teasing "Bynum Solar" as the next one, April 2026 COD) would
  likely reference it. Camino Santiago is absent from Cobra's public project pipeline
  entirely as of Feb 2026 — consistent with a project still in pre-construction / stalled
  at FIS, not yet worth a press release.

**Milam County Commissioners Court agenda (Oct 2022, newtools.cira.state.tx.us):** title
in search results only; not fetched this pass (low incremental value — 2022 agenda predates
IA signing by 2 years, unlikely to name a then-unsigned generator).

**Conclusion of refresh pass:** No new artifact upgrades the site fix, acreage, or
construction verdict. The Grupo Cobra pipeline negative (Barrett = "first", Camino Santiago
unmentioned) is the one materially new piece of evidence — it corroborates the "real but
slow-moving, no construction yet" verdict rather than contradicting it. CDSE and gmaps.py
both hit infrastructure failures (not negative findings) — imagery/pins remain not
obtainable this run either.

## Second-pass user review (2026-07-20)
- AWS Open Data chips (s2aws.py) fetched 2022/2024/2025/2026 at the POI-triangulated point:
  center of frame shows undeveloped farmland/creek in all 4 years, consistent with
  no_activity_confirmed. Per REFRESH_DIRECTIVE.md's explicit warning, large solar arrays ARE
  visible at the NW/NE frame corners in 2026 (absent 2022) -- these are neighboring Milam
  County projects (Ben Milam/Orion I/Cattleman II corridor), NOT Camino Santiago; not cited
  as construction evidence for this project. Point sits on a 14RQV/14RPV tile seam --
  partial clipping in every frame, known s2aws.py limitation.
