# Triage log — Cosper Solar (25INR0281)

## T1 start
- 37 snapshots (2023-06-01 → 2026-06-01)
- COD drift: 2025-12-30 → 2026-09-15 → 2027-04-18 → 2027-11-12 (3 changes, ~2yr total slip)
- IA signed: 2025-07-31 (first in 2025-08-01 report)
- FIS approved: 2024-11-01
- Meets 6.9(1): 2025-08-18
- Meets all 6.9: not yet; construction start/end not reported; no energization/sync/COA
- Assessment: real project, IA signed ~1yr ago, pre-construction phase

## T2 start
- gmaps.py: 429 Too Many Requests on both attempts (exact name; name+county). Budget exhausted.
- pins_found: 0 (blocked, not confirmed absent)

## T3 start
- Developer: Gransolar Texas Twenty LLC (SPV); parent = Gransolar Group (Spain), ~48 US projects, ~6.7 GW pipeline
- LLC status: "Forfeited" per tx state records (may be stale/data artifact — common for SPVs)
- PUCT IA filing confirmed: Standard GIA between Oncor and Gransolar Texas Twenty LLC
- KWTX Nov 2023: developer did NOT attend Bell County commissioners court — potential community opposition signal
- EIA completion date: 10/31/2027; ercotqueue.com build-chance: 86%
- news_found: true; saved → sources/t3_web_sweep.md

## T4 start
- PUCT case 35077 confirmed (via DDG): IA filed 2025-07-31 (Item 2238), First Amendment filed 2025-08-26 (Item 2246)
- Both party names confirmed: Oncor Electric Delivery Company LLC + Gransolar Texas Twenty, LLC (Cosper Solar)
- Direct PDF fetch blocked: interchange.puc.texas.gov returns 402 on all URLs — cannot retrieve schedule exhibit
- ia_found: TRUE (case number + filing dates confirmed via DDG); schedule exhibit contents unknown
- Deep scan note: amendment filed ~4 weeks after IA — worth fetching to see if schedule changed

## T5 start
- Ch.313: no results (Cosper Solar / Gransolar Texas Twenty / Bell County) — normal, Ch.313 expired 2022
- JETI: no results — normal for projects in this vintage without confirmed local ISD agreement
- abatement_found: false

## T6 start
- Site candidate: Ding Dong substation area (30.9874, -97.7667) — derived from POI "Tap 138kV 115 Ding Dong - 3630 Copperas Cove Tu"; confidence LOW (infrastructure-derived, no pin or abatement map)
- 3×3 chip grid attempted, 4/9 fetched (403 blocked center + entire south row)
- Contact sheet read: 4 frames cover Killeen/Copperas Cove suburban corridor — no solar panel arrays visible, no construction activity
- construction_visible: false (caveat: center tile blocked; field may be south of grid)
- Budget exhausted; no full-frame reads needed (no activity to zoom in on)

## T7 start
- triage_findings.json written
- triage.md written
- Turns used: ~28 of 35 budget

## D0 start (deep scan)
- Read triage_findings.json/triage.md/factsheet.{json,md}; inventoried sources/ (2 verified IA PDFs already on disk)
  and imagery/ (4/9 chips + contact sheet from triage, low-confidence Ding Dong guess)
- findings.json skeleton written

## D1 IA schedule
- `exhibit.py scan`: original IA (35077-2238) has 2 exhibit-keyword pages (p14, p40); Amendment 1 (35077-2246) has 0
  (it's a 4-page name-correction amendment only, no schedule change — confirmed by reading its full text)
- Extracted via pypdf text (no need to render most pages): filing letter confirms INR 25INR0281 in text (CONFIRMED
  match per playbook rule, not just county+MW). Exhibit "B" Time Schedule (IA p29):
  - Notice-to-proceed/security date: 2025-08-06
  - In-Service Date: 2027-05-13
  - Scheduled Trial Operation Date: 2027-05-25
  - Scheduled Commercial Operation Date: **2027-11-12** (matches queue COD exactly — contractually grounded)
- Exhibit "E" Security Arrangement (IA p50): Irrevocable Standby Letter of Credit, effective on/before 2025-08-06,
  amount **$10,615,572**
- Amendment No. 1 (2025-08-26) is NOT a schedule amendment — it only corrects the Generator's legal name from
  "Cosper Solar" to "Gransolar Texas Twenty LLC" throughout the agreement. Financial security unchanged.
- **MAJOR SITE FIND**: Exhibit "C" / Attachment 1 (IA p44, rendered → sources/..._p44.png) is a one-line diagram
  titled "Maxdale Switch" showing 138kV lines to "Copperas Cove LCRA" and "Ding Dong Substation" — this is a NEW
  tap switch (not the existing Ding Dong substation triage guessed), matching queue POI text exactly
  ("Tap 138kV 115 Ding Dong - 3630 Copperas Cove Tu"). Relaying equipment list (IA p38) also names "Killeen Switch
  line" and "Copperas Cove Sub (LCRA) line" relay panels — consistent with the tap being on the Ding Dong–Copperas
  Cove 138kV line somewhere between Killeen and Copperas Cove.
- Maxdale, TX is a real unincorporated community in Bell County (Wikipedia/TSHA/hometownlocator confirm) — gives a
  geographic anchor distinct from the "Ding Dong" substation itself.
- IA Exhibit B: Generator to provide lat/lon+kmz of solar panel units by 2026-11-13 — not yet in these documents.
- No CAD-visible acreage figures in IA text (no Exhibit with acreage found in text-extracted pages); land-tenure
  clauses (Exhibit C §12c/d "If Generator Owns Land" / "If Generator Does Not Own Land") are boilerplate options,
  don't resolve actual tenure — logged as unresolved.

## END
