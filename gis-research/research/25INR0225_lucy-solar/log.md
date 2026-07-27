# Triage log — Lucy Solar (25INR0225)

T1 start

## T1 — Queue history

- 37 monthly snapshots (2023-06-01 → 2026-06-01)
- COD drift: 2 changes
  - 2025-05-01 (held June 2023 only)
  - 2026-04-14 (held July 2023 → April 2024)
  - 2027-06-30 (held May 2024 → current; ~12 months out)
- Key milestones: screening done 2023-09-20; FIS requested 2023-06-08; **FIS approved 2026-06-08** (just last month); **IA signed 2024-05-29** (first appeared in Mar-2025 report — ~9 mo data lag)
- No construction milestones set (start, end, energization, sync, COA all blank)
- Capacity: 351.3 MW → 352.21 MW (minor true-up)
- Assessment: IA exists (strong signal), FIS only just approved in June 2026 — COD 2027-06-30 looks aggressive but project is technically active

T2 start

## T2 — Delivery pins

- Queries attempted: "Lucy Solar", "Lucy Solar Concho County"
- Result: HTTP 429 (rate-limited) on both — blocked after 1 retry per rules
- No pins found

T3 start

## T3 — Web sweep

Strong news signal found:
- Groundbreaking held 2026-01-28 in Concho County, TX near Paint Rock
- Lead developer: Hyundai E&C; co-developer: High Road Energy Marketing (TX)
- EPC: Primoris Renewable Energy; O&M: KOMIPO
- Consortium ("Team Korea"): Hyundai E&C, KOMIPO, KIND, PIS Fund, Topsun, EIP Asset Mgmt
- $524M project cost; 350 MW AC / 455 MW DC; target COD mid-2027 (consistent with queue)
- VPPAs with undisclosed RE100 corporate buyers
- No explicit SPV name in press; "Lucy Solar, LLC" per queue identity packet
- Source saved: sources/groundbreaking_sanangelolive_20260128.md
- Additional URLs noted (not fetched to stay in budget): businesswire, pv-magazine, hdec newsroom

T4 start

## T4 — PUCT Interchange

- All requests to interchange.puc.texas.gov returned HTTP 402 (Payment Required / blocked)
- Tried: search by FilingParty "Lucy Solar", general search URL, main search page
- Budget exhausted after 1 retry per endpoint — no IA found via portal
- Note: queue shows iaSigned=2024-05-29, so an IA does exist; portal just inaccessible here
- No PDF downloaded

T5 start

## T5 — Abatements

- Ch.313: Program expired post-2022; multiple pages returned no searchable database — normal for this project era
- JETI: gov.texas.gov JETI URL returned 404; registry not accessible
- No abatement documents found — normal for post-2022 project per checklist
- Note: $524M project with Korean consortium investors likely has negotiated local tax agreements anyway (e.g. Ch.381 county deal); worth chasing in deep scan

T6 start

## T6 — Imagery

- Site candidate: Paint Rock, TX area (31.51°N, 99.82°W) — county seat of Concho County, no precise coords from open sources
- cdse.py chips returned HTTP 401 Unauthorized on all 9 date requests — CDSE credentials not configured in this session
- No contact sheet produced; no imagery reviewed
- Note: groundbreaking was Jan 27, 2026 — construction should be visible in spring/summer 2026 imagery if creds available

T7 start

## T7 — Output

- triage_findings.json written
- triage.md written (10 lines)
- Turns used: ~18
- Deep scan recommended: YES

## End of triage

## Deep scan start — 2026-07-19

### Stage 1: LLC / Parent Chain
- **Groundbreaking news** confirmed from sanangelolive.com: landowner Charles Smith, ~2,900 acres near Paint Rock
- **Developer chain**: Lucy Solar, LLC (SPV, not yet confirmed via SOS) → Hyundai E&C (lead) + Korean consortium (KOMIPO, KIND, PIS Fund, Topsun, EIP Asset Mgmt) + High Road Energy Marketing (US co-dev)
- **EPC**: Primoris Renewable Energy (Primoris Services Corp division)
- **O&M**: KOMIPO
- **Offtake**: Long-term VPPAs with undisclosed RE100 corporate buyers
- TX Comptroller search URL now redirects to search form only — no entity results retrieved; SOSDirect requires subscription
- NEGATIVE: No SEC Reg D filings found (403 blocked); no Comptroller API found

### Stage 2: County Records
- **Concho County CAD** (esearch.conchocad.org): owner search URLs return 404 — CAD search endpoint not accessible via direct URL form; portal auth required
- **PUCT Interchange**: All URLs return 402 Payment Required — IA docs not accessible
- **Ch.313**: Program expired post-2022 — no abatement found; expected for this vintage
- **JETI**: 404 — not accessible
- NEGATIVE: No Ch.313/JETI, no CAD parcels found in open sources

### Stage 3: Site Coordinates
- **Amos Creek Road in Concho County**: 31.4956, -99.7062 (Nominatim)
- **Twin Buttes Reservoir** (Tom Green County): 31.363, -100.554
- POI analysis: Tap on 345kV lines Amos Creek–San Angelo Red Creek and Amos Creek–Twin Buttes; site is near Amos Creek switch in Concho County
- Site candidate refined: ~31.50, -99.71 (near Amos Creek Road, Concho County) vs. Paint Rock 31.51, -99.82
- ARTIFACT: Nominatim coords for Amos Creek Road in Concho County
