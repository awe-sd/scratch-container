# Triage log — Raven Storage (24INR0210)

## T1 start

**Queue history**: 45 snapshots, 3 COD changes (4th value = current).
- COD drift: 2024-11-30 → 2025-04-15 → 2025-10-01 → **2026-07-31** (current, held since 2024-10-01)
- Key milestones achieved: screening complete 2022-04-26, FIS approved 2025-09-16, IA signed 2024-06-04, Meets 6.9(1) 2025-10-28, Meets all 6.9 2025-10-29
- No construction start/end, no energization, no sync, no commercial operation dates
- Capacity crept: 101.83 → 101.4 → 103.53 MW (last change 2026-02-01)
- **IA signed 2024-06-04** — strong signal. All 6.9 met 2025-10-29. COD 13 days from today.

T1 result: Active project, IA signed, all milestones met. COD claim is extremely tight (2026-07-31 = 13 days). 3 prior COD slips.

## T2 start

**Delivery pins**: gmaps.py rate-limited (HTTP 429). Web searches (Bing) for "Raven Storage" + Wharton and "Raven Storage LLC" + Texas returned no relevant results — only bird/nature content. No pins found.

T2 result: 0 pins. Normal for a project with no public-facing web presence yet.

## T3 start

**Web sweep**: 5 searches — project name + ERCOT, LLC name + Texas, capacity variants (103/103.53 MW), POI infrastructure (Wallis/East Bernard 138kV), TX Comptroller entity lookup. All returned no relevant results. TX Comptroller lookup redirected to CAPTCHA-gated form (blocked). No developer name, parent company, news, or press releases found.

T3 result: No web presence found. Developer identity unknown. Normal for quiet pre-COD projects.

## T4 start

**PUCT Interchange**: interchange.ercot.com → ENOTFOUND (DNS). interchange.puc.texas.gov → HTTP 402 (auth-gated, blocked). Bing search for "Raven Storage" + PUCT/IA returned no results. IA signed date 2024-06-04 confirmed in queue data but document not accessible.

T4 result: IA existence confirmed via queue milestone (iaSigned = 2024-06-04). Document not retrievable — portal blocked. No schedule exhibit available.

## T5 start

**Abatements**: TX Comptroller Ch.313 pages returned no searchable data (tool navigational only). Bing search for Wharton County + Ch.313/JETI + battery returned no results. Note: Ch.313 expired 2022-12-31; project screened 2022 so would have needed to apply pre-expiry. No JETI application found (normal — JETI is new and thin on public records).

T5 result: No abatement found. Normal for battery projects; land footprint is small and abatement incentive is low.

## T6 start

**Imagery**: Site candidate = POI infrastructure (Wallis–East Bernard 138kV line, Wharton County). Center estimate: 29.636°N, 96.065°W (Wallis substation). Ran 3×3 chip grid at 2 km buffer, 2026-07-01. CDSE dropped 6/9 parallel connections (RemoteDisconnected); 3 chips landed: r1c2 (29.666,−96.065), r2c1 (29.636,−96.095), r3c2 (29.606,−96.065). Contact sheet generated. Visual review: agricultural/rural landscape, partial cloud cover, no BESS footprint visible (no gravel pad, no parallel container rows). Grid coverage partial (~33%) — confident the visible area has no construction activity; uncovered cells (esp. center-east, south-east) remain uninspected.

T6 result: No construction signal in 3 available chips. Coverage incomplete. Imagery inconclusive due to CDSE instability.

## T7 start

Wrote triage_findings.json and triage.md. Turns used: ~22. STOP.

T7 result: Complete.
