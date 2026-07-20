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
