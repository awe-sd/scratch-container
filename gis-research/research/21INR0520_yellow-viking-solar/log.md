# Triage log — Yellow Viking Solar (21INR0520)

## T1 start

**queue_history.py** — 69 snapshots (2020-10-01 → 2026-06-01)

**COD drift (3 changes):**
| COD | Held from | Until |
|---|---|---|
| 2022-12-26 | 2020-10-01 | 2021-12-01 |
| 2024-07-26 | 2022-01-01 | 2023-09-01 |
| 2026-11-07 | 2023-10-01 | 2025-04-01 |
| 2027-07-13 | 2025-05-01 | 2026-06-01 |

**Milestone status:**
- Screening started: 2020-10-23 ✓
- Screening complete: 2021-01-12 ✓
- FIS requested: 2020-08-20 ✓
- FIS approved: — (never)
- IA signed: 2022-10-25 (first appeared in reports 2024-01-01) ✓
- 6.9(1), All 6.9, Construction start/end, Energization, Sync, COD: all —

**Capacity changes:**
- 288.99 MW (2020-10 → 2025-04) → significantly downsized
- 170.86 MW (2025-05 → 2026-02)
- 171.13 MW (2026-03 → present)

**T1 summary:** IA signed but no FIS approved, no construction milestones. COD slipped 3x (~5 years total drift from 2022 to 2027). Large capacity downsize (~41%) in 2025. Active queue as of 2026-06.

---

## T2 start

**gmaps.py places** — HTTP 429 Too Many Requests on all 3 attempts (exact name, name+county, LLC name). API rate-limited; one retry attempted per checklist rule. No pins found.

**T2 result:** 0 delivery pins. Normal — no map evidence of a named solar facility in Google Places for this project.

---

## T3 start

**Web sweep results:**

1. **Global Energy Monitor (gem.wiki)** — "Yellow Viking solar farm" listed as solar PV pre-construction, Somervell County TX. No URL saved (no direct article).
2. **cleanview.co** — "170 MW solar farm, Somervell TX, expected online 2027." No article saved (aggregator only).
3. **Lydian Energy / BusinessWire (2026-02-17)** — **$689M full-stack financing closed** for Yellow Viking Solar, 170 MWac / 210 MWdc. Construction-to-term loan + tax credit bridge. 100 MW PPA with investment-grade offtaker. Lenders: CIBC + MUFG. → saved to sources/lydian_financing_businesswire.md
4. **hcnews.com** — Hood County News article: county "unanimously voted to acknowledge that tax abatement agreement with Yellow Viking Development One, LLC was no longer active." → 403 blocked; content not retrievable.

**Developer chain:** European Energy (Danish, original developer; PM Knud Erik Andersen) → sold to **Lydian Energy** (~2023). SPV: **Yellow Viking Development One, LLC**.

**T3 summary:** Strong news signal. Financing closed Feb 2026 — construction-to-term structure implies shovel-ready. Tax abatement reported as no longer active (reason/date unknown — hcnews blocked). 2027 COD plausible given Feb 2026 financing close.

---

## T4 start

**PUCT Interchange search** — HTTP 402 on all 3 URL attempts (FilingParty=Yellow Viking Solar; FilingParty=Yellow Viking; alternate with Description=interconnection). Portal blocked; one retry attempted per rules.

**T4 result:** IA not confirmed via PUCT. Queue data shows iaSigned=2022-10-25 (appeared in reports Jan 2024) — IA exists per ERCOT data. Could not retrieve PDF or milestone schedule exhibit. Note for deep scan: search PUCT Interchange with alternate party names (Lydian Energy, Yellow Viking Development One, European Energy) for the IA document.

---

## T5 start

**TX Comptroller Ch.313 search** — Comptroller site does not expose a direct searchable Ch.313 database via URL parameters; pages returned program index only. DDG search for "Yellow Viking" + Ch.313/abatement found hcnews.com reference to a county tax abatement with Yellow Viking Development One, LLC that was voted "no longer active" (Feb date, year unclear). No Ch.313 application PDF found.

**JETI registry** — project is 2021 vintage; JETI replaced Ch.313 in 2023. Project predates JETI, would have filed Ch.313 if it filed anything. No JETI entry expected.

**T5 result:** Abatement WAS in place (county-level, not necessarily Ch.313 state-level); now reported terminated. hcnews article blocked (403 earlier). Reason for termination unknown. Note for deep scan: retrieve hcnews article or Somervell County appraisal district records for abatement history and termination reason.

---

## T6 start

**Site candidate:** POI anchor — Comanche Peak Nuclear Plant at ~32.298°N, 97.790°W (Oncor 345kV tap). No pin or abatement map available. Confidence: low (POI = interconnection point, not field center).

**Imagery:** 3×3 grid, step ±0.03°, buffer 2km, 2026-07-01 ±15d. All 9 chips retrieved cleanly.
- Contact sheet read: no solar panel arrays or construction visible in any tile
- Center tile (32.298, -97.790): Comanche Peak Nuclear Plant + Squaw Creek Reservoir clearly identifiable
- Surrounding tiles: wooded hills, rural farmland, reservoir arms — no panel grids
- Grid covers ~±6km from POI; actual solar field may be south near Glen Rose (Somervell county seat at ~32.24°N, 97.75°W) — not captured

**T6 result:** No construction visible within POI vicinity. Consistent with "pre-construction" status per GEM Wiki and absence of construction milestones in queue. Grid placement may have missed actual site — deep scan should locate parcel and re-run imagery over correct coordinates.

---

## T7 start

Wrote triage_findings.json and triage.md. Run complete.

**Turns used: ~28. Steps completed: T1–T7.**

**Blockers:** gmaps 429 (T2), PUCT 402 (T4), hcnews 403 (T5), GEM Wiki 403 (T3).
**Key finds:** IA confirmed via queue; $689M Lydian Energy financing Feb 2026; county abatement terminated; no construction visible in imagery; site not precisely located.

---

## D1 — IA schedule extraction (2026-07-20)

**Original IA** (PUCT 35077-1523, signed 2022-10-25, filed 2022-11-22):
- Exhibit B: In-Service 2024-04-18, Trial Op 2024-05-01, COD **2024-07-26**
- NTP for construction: 2023-08-18
- Exhibit C: POI in **Hood County** TX, Nautilus Switch in Comanche Peak–Timberview Switch 345kV line, on **FM 2174, ~25 miles west of Cleburne**
- Equipment: 78 inverters × 4.004 MVA = 312.312 MVA / 288.99 MW (original capacity)
- Inverter type: SMA SC4400 UP
- Exhibit E: Irrevocable standby LC effective on/before 2022-10-18 (amount not yet extracted)
- Sources: sources/2026-07-19_puct_35077-1523_interconnection-agreement-between-oncor-electric.pdf

**Amendment No. 1** (PUCT 35077-2154, filed 2025-06-13):
- Exhibit B: In-Service **2027-05-13**, Trial Op **2027-05-28**, COD **2027-07-13**
- NTP for construction: **2025-07-01** (key: this date is now past — construction notice was due ~12 months ago)
- Exhibit E: LC structure unchanged (amount still needs extraction from p8 further text)
- Sources: sources/2026-07-19_puct_35077-2154_amendment-no-1-to-the-standard-generation-interc.pdf

**Amendment No. 2** (PUCT 35077-2493, filed 2026-05-27):
- Exhibit B: Same schedule as Amend 1 (In-Service 2027-05-13, COD 2027-07-13)
- NTP for construction: 2025-07-01 unchanged
- Sources: sources/2026-07-19_puct_35077-2493_amendment-no-2-to-the-standard-generation-interc.pdf

**Amendment No. 3** (PUCT 35077-2523, signed 2026-07-02, filed 2026-07-09 — 11 DAYS BEFORE TODAY):
- Only change: equipment updated to 45 inverters × 4.312 MVA = 194.04 MVA / **172.80 MW** dispatched
- Schedule UNCHANGED — COD still 2027-07-13
- INR confirmed in title: "GINR 21INR0520"
- Sources: sources/2026-07-19_puct_35077-2523_amendment-no-3-to-the-standard-generation-interc.pdf

**Key site clue from IA:** Generator Switchyard located adjacent to Oncor's Nautilus Switch, FM 2174, Hood County, ~25 miles west of Cleburne TX. This is the definitive location anchor — must search FM 2174 / Hood County, NOT Somervell County centroid.

**EIA coords:** 32.31664, -97.62889 — candidate (from factsheet). Somervell County is the queue county but Hood County is where the POI/switchyard is per IA text.


---

## D2 — Site pinpoint attempt + imagery (2026-07-20)

**Site location triangulation:**
- IA Exhibit C: Nautilus Switch, FM 2174, Hood County TX, ~25 miles west of Cleburne
- GEM wiki search snippet: "4,078-acre site in southeast Hood County, Texas" (403 on direct fetch)
- EIA-860M coords: 32.31664, -97.62889 (Lydian Energy / Yellow Viking Solar plant)
- Somervell County abatement: project spans Hood AND Somervell county lines (both counties had/have abatements)
- Best estimate: SE Hood County near Hood/Somervell/Johnson county convergence, FM 2174 corridor

**Google Places:** 0 pins found for all variants (Yellow Viking Solar, Viking Solar Hood County, Lydian Energy solar Hood County)

**Hood County CAD:** 0 parcels under Yellow Viking / Lydian / European Energy — expected for leased ranchland; land held under landowner names

**Somervell CAD:** 0 hits via search

**CDSE imagery:** BLOCKED — openeo/result endpoint returns HTTP 402 "insufficient credits." Sentinel-2 imagery cannot be obtained for this project. Verdict: imagery-less.

**SCS Salon articles:** 404 (site under upgrade as of 2026-07-07)

**Hood County News:** 403 on all fetch attempts

**Log: negative imagery evidence** — CDSE returned 402 on 2026-07-20; unable to verify construction stage via Sentinel-2 for this project.

---

## D3 — Gap-fill search results (2026-07-20)

**Financing (BusinessWire, saved as sources/lydian_financing_businesswire.md):**
- $689M construction-to-term + tax credit bridge
- 100 MW PPA with investment-grade offtaker
- CIBC + MUFG as lenders
- 170 MWac / 210 MWdc capacity confirmed

**Hood County abatement termination:** February 2025 voted "no longer active" per hcnews.com snippet. Reason unknown (403 on fetch). This is Hood County abatement only — Somervell County abatement was being extended/amended per Feb 2024 hearing.

**Amendment No. 3 (July 2, 2026 — 18 days ago):** Changed equipment from 78 inverters (288.99 MW) to 45 inverters x 4.312 MVA = 172.80 MW dispatched. Schedule unchanged. Active contract modification confirms project is still live.

**Key concern:** Construction NTP deadline per Amend 1 was July 1, 2025. That date is now 12 months past with no ERCOT construction-start milestone flagged and no visible construction pins. Project may have NTP'd without public announcement.


---

## D4/D5 synthesis (2026-07-20)

**EIA history (eia_history.py):**
- Plant 67222 "Yellow Vikings" — Lydian Energy, matched county+prime-mover+MW
- Status history: (P) Planned → (L) Regulatory approvals pending, not under construction (2025-02 → 2026-05)
- EIA COD: 2026-11 → 2026-10 → 2027-10 (latest, 1 quarter past contractual 2027-07)
- EIA coords: 32.31664, -97.62889

**LC amounts (Amend 1 Exhibit E, p9 rendered):**
- Initial: $4,724,586 by Oct 18, 2022
- Step-up: $13,784,627 by July 1, 2025

**Amendment 3 (signed 2026-07-02, filed 2026-07-09):**
- Equipment-only update: 45 inverters × 4.312 MVA = 172.80 MW dispatched
- Schedule unchanged: In-Service 2027-05-13, COD 2027-07-13
- Confirms active contract modification 18 days before research date

**Verdict: real_early — HIGH confidence**
- Strong capital signal ($689M, CIBC+MUFG, closed Feb 2026)
- Active IA amendments (Amend 3 signed this month)
- $13.8M LC posted
- BUT: not yet under construction as of May 2026; NTP deadline 12 months past; 4.5-yr drift history
- Independent COD: 2027-Q4; drift risk: HIGH

**D5 wrap-up complete:**
- queue_history.py: timeline.md refreshed (69 snapshots, 3 COD changes)
- eia_history.py --write: eia_history.json written
- build_brief.py: brief.html (13KB, 37 sources)
- build_index.py: 154 projects indexed


## D3 — Second-pass user review: ch313 re-check + site verification + imagery fix (2026-07-20)

**User complaint:** missing Ch.313, missing parcel boundary, imagery "just random."

- **Ch.313 re-checked systematically** (`ch313.py resolve 21INR0520`, `--county Hood`,
  `--county Somervell`, `--name "Yellow Viking"`, `--name Lydian`): all five NEGATIVE. This
  is a genuine absence (pre-2023 SPV with no Ch.313/JETI filing), not a missed lookup --
  consistent with the log's earlier manual-search finding.
- **No parcel/site-plan exhibit exists in any of the 4 PUCT filings** (original IA + 3
  amendments) -- confirmed via full sheet-index read of all 4 PDFs. Exhibit C (p30) is text
  only; the sole drawing in the docket is p40, a one-line diagram of Nautilus Switching
  Station (not a parcel/boundary map). There is nothing to add here; the brief's
  `map_artifacts` already points at the correct (only) exhibit page.
- **Root cause of "random" imagery**: the triage-stage 3x3 grid (contact_sheet +
  9 tiles, all deleted this pass) was centered on a POI candidate the deep scan explicitly
  rejected once EIA coordinates were found -- but imagery was never re-fetched at the
  corrected point because CDSE returned 402 credit-exhaustion at the time. The stale grid
  sat in `imagery/` as if it were current.
- **Site re-verified via OSM/Overpass** (`lz4.overpass-api.de`, plain-text POST,
  `User-Agent` header required to avoid 406): FM 2174 and a 345kV line both present within
  5 km of 32.31664,-97.62889 (matches IA Exhibit C text); `is_in()` query places the point in
  **Somervell County**, matching the ERCOT queue's own county field exactly (GEM wiki's
  "Hood County" claim likely describes the switchyard side of a documented tri-county
  convergence, not the plant itself).
- **New AWS Open Data chips** (`s2aws.py`, 3.2/3.2 km buffer) fetched for 2022-06, 2024-06,
  2025-07, 2026-06 at the verified point, plus one 7 km-wide check. All show only
  pre-existing sand/limestone quarry pits near the interconnect -- no solar development in
  any year. This is consistent with EIA's "(L) not under construction" status and the
  passed NTP deadline; recorded as pre_construction with a clean 4-year negative
  observation, not "unverified."

## D4 — minutes.py pilot payoff (2026-07-21)

The new commissioners-court minutes pipeline (minutes.py harvest/index/resolve — built
because Somervell reports nothing to the Ch.312 registry) resolved 21INR0520 to two
Somervell CC meeting files dated 2024-02-12, closing the "outcome not retrievable" gap
from the original scan:
- First Amendments to BOTH abatement agreements (2021-10-29 and 2023-08-14) PASSED —
  signed motion + signed amendments attached to the meeting record.
- Completion date extended 2024-12-31 -> ON OR BEFORE 2026-12-31 (now ~6.5 months ahead
  of the contractual COD 2027-07-13 — a compounding schedule squeeze).
- Company notice address changed to Tomohiko Ono / VP, renewables-grid-solutions@
  osakausa.com, copy to OSAKA GAS USA CORPORATION (Houston) — a document-verified
  ownership datapoint sitting between the European Energy origin and the Lydian Energy
  entity in EIA-860M. Both artifacts copied to sources/.
