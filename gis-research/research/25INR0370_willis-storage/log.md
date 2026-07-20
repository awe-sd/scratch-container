# Triage log — Willis Storage (25INR0370)

## T1 start

queue_history.py ran: 40 snapshots, 2023-03-01 → 2026-06-01, 3 COD changes.

**Milestones achieved:**
- Screening started: 2023-03-27
- Screening complete: 2023-06-24
- FIS requested: 2023-03-13
- FIS approved: 2024-11-08
- IA signed: 2025-04-07
- Meets 6.9(1): 2025-07-07
- Meets all 6.9: NOT YET
- Construction start/end, energization, synchronization, COA: all blank

**COD drift (4 values, 3 changes):**
- 2025-12-31 (original, Mar 2023 – Jul 2023)
- 2026-09-07 (Aug 2023 – Sep 2024)
- 2027-04-13 (Oct 2024 – Mar 2025)
- 2027-08-13 (Apr 2025 – Jun 2026, current)

**MW:** Started 178.0, trimmed to 176.13 MW (Sep 2023), stable since.

**T1 summary:** IA signed Apr 2025, 6.9(1) met Jul 2025, no 6.9 full yet. COD has slipped ~20 months from original. No construction milestones recorded. Active, real project with IA in place.

## T2 start

gmaps.py places — 429 Too Many Requests on first attempt and retry. No pins found.
Queries attempted: "Willis Storage", "Willis Storage Rains County Texas"
Result: 0 pins. (Rate-limited; not a signal about the project.)

## T3 start

Searches: "Willis Storage battery ERCOT Texas", "Belltown Power Willis Storage", "BT Majewski Storage Rains County"

**Developer confirmed:** Belltown Power. SPV name is **BT Majewski Storage LLC** (per community opposition site and ercotqueue.com) — NOT "Willis Storage LLC" as in the identity packet.
- Also seen as: BT Willis Storage LLC (infrasure.ai), Belltown Power Texas 2 LLC (EIA listings)

**Community opposition:** rainscountysafetycoalition.org has a dedicated page opposing this project (BESS fire/safety framing). Confirms project is real and known locally.

**No news/PR found.** No site address surfaced. No permit records found online.

Source saved: sources/t3_web_sweep.md

## T4 start

PUCT Interchange portal returns 402 Payment Required on all direct URLs. Used DDG search instead.

**IA FOUND:** PUCT Control Number 35077, Item 2125, filed 2025-05-01
- Agreement date: 2025-04-07 (matches queue milestone iaSigned = 2025-04-07 ✓)
- Parties: Oncor Electric Delivery Company LLC ↔ BT Majewski Storage, LLC
- Type: Standard Generation Interconnection Agreement, §25.195(e)
- PDF URL: interchange.puc.texas.gov/Documents/35077_2125_1494627.PDF — returns 402, unreadable during triage

**POI / milestone schedule:** Not extracted — PDF inaccessible. Deep scan should retrieve parties/POI page and milestone schedule exhibit.

## T5 start

TX Comptroller Ch.313 page: no direct search result for Rains County + energy storage. JETI registry: no hits via DDG search for Belltown/Majewski/Willis + Rains County + JETI.

**Result:** No abatement found. Expected — Ch.313 expired 2022; JETI registry is sparse for new projects. Not a negative signal for a 2023-queue project.

## T6 start

Site candidate: "Emory North" substation POI — no coordinates found in web searches. Used Emory TX city center (32.874°N, 95.570°W) as anchor (county seat, substation logically north of town).

3×3 chip grid, ±0.03° step, 2km buffer, date 2026-07-01. Contact sheet: contact_sheet_2026-07-01.png.

**Contact sheet observation:** Mostly agricultural and forested land. Lake Fork Reservoir occupies eastern tiles. No cleared gravel pad, bare soil staging, or BESS container rows visible in any tile. No construction signal at this scale/resolution.

No activity spotted → no full-size frame reads consumed (within budget). Imagery inconclusive due to uncertain substation coordinates — Emory North could be outside this grid. Confidence: LOW on site candidate.

## T7 start

Wrote triage_findings.json and triage.md. Turns used: ~22. Stopping.

**Triage complete.**
