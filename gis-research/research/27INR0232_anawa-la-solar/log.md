# Triage log — Anawa La Solar (27INR0232)

## T1 start
- queue_history.py ran: 27 snapshots, 2024-04-01 → 2026-06-01
- COD drift: 0 changes — held at 2027-08-31 since first appearance (2024-04-01)
- Milestones: Screening started 2024-03-29; Screening complete 2024-06-19; FIS requested 2024-04-15
- No FIS approved, no IA signed, no construction milestones achieved
- Status: early-stage — pre-IA, pre-FIS-approval

## T2 start
- gmaps.py: 429 Too Many Requests on both attempts — portal blocked, no pins obtained
- T2 result: 0 pins found (blocked, not negative signal about project)

## T3 start
- DDG search "Anawa La Solar Texas news": multiple tracking sites (infrasure.ai, cleanview.co, interconnection.fyi, ercotqueue.com) — all aggregate queue data, no independent news
- KEY FIND: Project actively for sale via Fractal Energy Storage Consultants; developer = EIA Properties, Ltd.; teaser PDF published 2025
- Fractal listing claims "secured IAs for onsite generation and storage" — CONTRADICTS queue (iaSigned = null as of 2026-06-01). Discrepancy logged in source file.
- Companion BESS project: 27INR0233 (Anawa La BESS, 103.7 MW / 207.4 MWh), same developer, same county
- LLC: Anawa La Solar LLC, filed 2024-01-16, Edinburg TX, active; Bizapedia blocked on detail page
- LLC address per Bizapedia snippet: P.O. Box 118, Edinburg TX 78540 — no site coordinates surfaced
- Teaser PDF: binary/image content, no extractable coords
- ercotqueue.com rates build-chance at 5% (no IA shown)
- Sources saved: sources/fractal_sale_listing.md
- T3 result: news_found=true, developer identified (EIA Properties Ltd), sale process active, IA claim unverified

## T4 start
- PUCT Interchange all endpoints: HTTP 402 (portal blocked/auth wall)
- DDG search for site:interchange.puc.texas.gov: HTTP 403
- T4 result: ia_found=false (portal blocked, not confirmed absent)

## T5 start
- TX Comptroller Ch.313: no searchable online database found; project filed 2024 (post-2022 Ch.313 sunset) — Ch.313 N/A
- JETI registry: jetiregistry.comptroller.texas.gov — DNS not found (registry domain does not resolve)
- DDG search "EIA Properties JETI Hidalgo": 403 blocked
- T5 result: abatement_found=false (normal for post-2022 project; JETI registry inaccessible)

## T6 start
- No pin (gmaps blocked), no IA map, teaser PDF binary-only (no coords), no PUCT IA
- POI "TAP 138 KV 8394 LISTON - 8392 BATES": Hidalgo County — LISTON substation not geolocated via Bing (no results)
- EIA Properties location search: no coordinates found
- Site candidate: "somewhere in Hidalgo County" — county is ~1,600 sq mi, too large for useful imagery
- T6 result: SKIPPED — no site candidate (per rule: skip imagery when county-only)

## T7 start
- Wrote triage_findings.json and triage.md
- Turns used: 28
- STOP
