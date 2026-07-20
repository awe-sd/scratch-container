# Triage log — Charger Solar (23INR0047)

T1 start
- queue_history.py ran OK: 73 snapshots (2020-06-01 → 2026-06-01)
- COD drift: 6 changes. Slippage: 2023-03-31 → 2026-09-18 (~3.5 years)
- IA signed: 2021-06-05 ✓
- FIS approved: 2025-09-22 ✓
- Meets all 6.9: 2025-07-24 ✓
- Approved for energization: 2026-06-30 ✓ (most recent snapshot)
- Construction start/end: not reported
- Capacity trimmed: 407.84 → 406.77 → 397.15 MW
T1 result: active, well-progressed project; energization-approved but no sync/COD approval yet; COD claim 2026-09-18 is 6 weeks out from today (2026-07-18)

T2 start
- gmaps.py 429 on first call, 429 on retry — API rate-limited, blocked
- No delivery pins found
T2 result: 0 pins (gmaps blocked)

T3 start
- DDG search 1: project+INR → 8 hits; developer = J-Power USA / AP Solar 4, LLC; construction start announced 2025-09-02; COD Q3 2026
- DDG search 2 (Refugio): CAPTCHA blocked
- J-Power construction PR fetched: confirms Refugio County, 345 kV substation, ~400 MW, Q3 2026 COD target, construction started Sep 2 2025
- J-Power project page fetched: confirms Refugio County, joint dev J-POWER USA + AP Solar Holdings
- LLC name search: CAPTCHA blocked
- Saved source: sources/jpowerusa_construction_start.md
T3 result: news_found=true; developer=J-Power USA + AP Solar Holdings (AP Solar 4 LLC SPV); construction started ~2025-09-02; COD Q3 2026

T4 start
- PUCT interchange portal is JavaScript SPA — POST/GET returns shell HTML only; no API endpoint accessible without a browser session
- DDG T3 snippet confirmed docket 35077 exists referencing "23INR0047 to ERCOT from AP Solar 4, LLC" — IA docket confirmed by reference
- PDF direct URL (35077_1670_1332670.PDF) returned 402 — cannot fetch
- ia_found: CONFIRMED by reference (docket 35077); schedule exhibit not retrieved
T4 result: IA confirmed by reference; schedule exhibit unread — deep scan should fetch directly

T5 start
- BUDGET WARNING received (80%) — skipping T5 abatements search (post-2022 project, JETI miss expected anyway)
T5 result: skipped due to budget; normal for 2023 project

T6 start
- Construction confirmed started 2025-09-02 per J-Power press release; ~10 months elapsed
- No precise site pin (gmaps blocked); Refugio County centroid only
- Skipping imagery per budget; construction status inferred from press release
T6 result: skipped due to budget; construction_visible presumed active based on press release

T7 start
- Wrote triage_findings.json and triage.md
- Turns used: ~28
- Budget warning hit at T4; T5/T6/T4-deep skipped; T7 completed
T7 result: DONE

## Deep scan — 2026-07-19

DS1 start — LLC chain / Stage 1
- J-Power USA project page confirms: 394 MWac, construction phase, AP Solar Holdings joint developer
  Source: https://www.jpowerusa.com/projects/ (saved via triage as jpowerusa_construction_start.md)
- Press release archive confirms only one release (Sep 2, 2025) — no 2026 COD announcement yet
- AP Solar Holdings website (apsolarholdingsllc.com): DNS not found — no public site
DS1 result: developer=J-Power USA + AP Solar Holdings; SPV=AP Solar 4, LLC; parent=Electric Power Development Co. (Tokyo)

DS2 start — PUCT IA deep read
- Downloaded PUCT item 1670 PDF (2.3 MB): "Second Amended and Restated ERCOT Standard Generation IA between AEP Texas Inc. and AP Solar 4, LLC (Charger Solar)" dated 8/29/2023
  Artifact: sources/2026-07-19_puct_35077_ap-solar-4-IA.pdf
- Also downloaded executed version from ZIP (item 1670 companion):
  Artifact: sources/2026-07-19_puct_35077_ap-solar-4-IA-exec.pdf
- KEY Exhibit C finding: "Charger Substation will be located in Refugio County approximately 7.2 miles southeast of the intersection of US HWY-77 and TX-239 in Tivoli, Texas"
- POI: "TSP's Static Station" — 345kV line between Angstrom station and STP (South Texas Project nuclear plant). One-line diagram (Exhibit C-1) shows tap "To Angstrom" and "To STP" — matches queue description exactly.
- Equipment: 540 × TMEIC PVU-L0840GR inverters, 0.753 MW each = 406.62 MW nominal (aligns with 397.15 MW net in queue)
- Milestone dates from Exhibit B (relative to Original Agreement Jun 5, 2021):
  - In-Service: 43 months = 2025-01-05 [PASSED — schedule already exceeded]
  - Trial Op: 45 months = 2025-03-05 [PASSED]
  - Scheduled COD: 48 months = 2025-06-05 [PASSED]
  → These are 2nd AR dates; there must be a 3rd amendment or separate extension (queue now shows 2026-09-18)
- Financial security (Exhibit E): $20,000,000 posted
DS2 result: IA confirmed, milestone dates per 2nd AR already passed, no amendment found in PUCT docket 35077 searches

DS3 start — Site pinpoint (Stage 3)
- TX-239 per Wikipedia: runs Kenedy → Austwell; intersects US-77 at McFaddin, Refugio County
- IA text says "intersection of US HWY-77 and TX-239 in Tivoli" but TX-239 crosses US-77 at McFaddin, not Tivoli
- Interpretation: IA uses "Tivoli" as nearest town name loosely; actual intersection is McFaddin area
- McFaddin (US-77 × TX-239) approximate: 28.09N, 97.28W (TxDOT/general knowledge)
- 7.2 miles SE of McFaddin = 28.014, -97.200 (bearing 135°)
- Alternative: if intersection actually in Tivoli (28.456, -96.889), 7.2mi SE = 28.382, -96.805 → coastal/bay area
  — This alternative lands in/near San Antonio Bay, which is implausible for a solar farm
- Therefore: McFaddin interpretation is more credible (site inland, in agricultural Refugio County)
- Site lat/lon estimate: 28.014, -97.200 (±3-4 km, low-medium confidence)
- gmaps Places: rate-limited (429), no delivery pin found
DS3 result: site ~28.01, -97.20 (inland near McFaddin area); confidence LOW — no parcel or pin confirmation

DS4 start — Satellite imagery (Stage 4)
- CDSE imagery: pulled chips centered on coastal estimate (28.382, -96.805) — all showed bay/coastline, wrong area
  No solar construction visible (wrong location; cloud cover additional issue)
- CDSE token error (HTTP 403) after ~8 chips — can't pull new chips for correct inland estimate
- Could not confirm construction stage via imagery — images from wrong location (coastal error)
DS4 result: imagery inconclusive — coordinate error + API block prevented inland site search

DS5 start — Queue history
- queue_history.py ran: 73 snapshots (2020-06-01 → 2026-06-01); 6 COD changes
- Milestone: Approved for energization 2026-06-30 ← DECISIVE — physical construction complete, ERCOT grid hookup approved
- COD drift path: 2023-03-31 → 2024-05-31 → 2025-05-31 → 2026-06-05 → 2026-07-05 → 2026-08-31 → 2026-09-18
- Latest COD 2026-09-18 is 11 weeks from today (2026-07-19)
DS5 result: energization approved 2026-06-30 means testing/commissioning phase; Sep 18 COD is plausible but tight

DS6 start — Additional records search
- TX Comptroller Ch.313/JETI: no portal access (returns overview page); no agreements found for AP Solar or Refugio County
- Refugio County commissioners court website: DNS not resolved (refugiocounty.org → redirect to unrelated domain)
- Refugio CAD: JavaScript-based portal, no API endpoint found; could not search by owner name
- Marathon Capital (financial advisor): transaction page 404 not found
- SEC EDGAR: 403 errors on API
DS6 result: county records (CAD, abatement, commissioners) not accessible; negative evidence logged
