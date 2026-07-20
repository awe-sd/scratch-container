# Triage log — 25INR0502 Longday BESS SLF

## T1 start
- queue_history.py ran OK — 36 snapshots (2023-07-01 → 2026-06-01)
- COD drift: 2026-07-15 → 2027-07-15 → 2027-03-15 → 2027-12-15 (4 reported CODs, 3 changes)
- Capacity: 204.77 MW (first snapshot 2023-07) → 0.0 MW (all subsequent snapshots 2023-08 onward) — large capacity collapse
- Milestones achieved: Screening started 2023-07-31, Screening complete 2023-10-27, FIS requested 2023-07-20
- No FIS approved, no IA signed, no 6.9 milestones, no construction dates
- T1 complete

## T2 start
- gmaps.py places "Longday BESS SLF" → HTTP 429 Too Many Requests
- gmaps.py places "Longday BESS SLF Kinney County Texas" → HTTP 429 (one retry, exhausted per rules)
- 0 pins found — T2 negative (tool blocked, not a site signal)
- T2 complete

## T3 start
- Developer identified: Longday Solar LLC (TX SOS #0805032739, filed 2023-04-25, Corpus Christi TX)
- Registered agent: Hummingbird Capital LLC
- Sibling project: 25INR0501 (Longday Solar SLF) — 200.8 MW solar, same county, same developer
- Third-party build-chance estimate: 5% (ercotqueue.com)
- COD shift noted in newsletter (2025-03-18): Mar 2027 → Dec 2027 (matches queue data)
- Kinney County pursuing tax abatement with Longday Solar (civicweb.net/document/81135 — not fetched in triage)
- energystorageconsultants.com teaser PDF links project to "American Wind and Solar" PV+BESS pairing
- No PUCT/IA filings found via web sweep
- Saved: sources/t3_web_sweep.md
- T3 complete

## T4 start
- PUCT Interchange interchange.puc.texas.gov → HTTP 402 on all search endpoints (FilingParty=Longday BESS SLF, FilingParty=Longday Solar, description=Longday BESS SLF)
- Portal blocked — cannot retrieve IA or other filings
- No IA confirmed — T4 negative
- T4 complete

## T5 start
- TX Comptroller Ch.313 page: no searchable agreement data on that landing page; Kinney County not confirmed
- TX Comptroller JETI page: no registry entries visible; requires dedicated JETI subpage
- Kinney County civicweb doc/81135: meeting agenda packet, no solar abatement content (T3 lead was a false hit)
- No abatement confirmed for this project — T5 negative (consistent with post-2022 project; Ch.313 expired)
- T5 complete

## T6 start
- Site candidate from POI: Brackettville 138kV substation, described NE of Brackettville on FM 334
  → estimated coords ~29.34°N, 100.38°W (substation NE of town center)
- cdse.py chip: HTTP 401/403 on all 9 grid chips — CDSE credential/token failure (401 Unauthorized)
- Imagery blocked — T6 negative (tool blocked, not a site signal)
- construction_visible: unknown (cannot assess)
- T6 complete

## T7 start
- Wrote triage_findings.json
- Wrote triage.md
- Turns used: ~22
- T7 complete — STOP
