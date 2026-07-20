# Triage log — 27INR0572 Kilby1 Part 1 Small Block Simple Cycle

T1 start
- queue_history.py: 9 snapshots (2025-10-01 → 2026-06-01), 0 COD changes
- COD: 2027-11-04 held stable across all snapshots
- Screening started 2025-10-21, Screening complete 2026-01-06
- FIS requested 2025-10-16; FIS approved = NOT ACHIEVED
- IA signed = NOT ACHIEVED; no construction milestones at all
- Early-stage project: only screening done + FIS requested

T2 start
- gmaps.py: 429 rate-limited on all attempts (tried exact name, name+county, name+LLC); one retry done per rule; no pins found
- T2 result: 0 pins

T3 start
- DDG HTML: CAPTCHA blocked
- Bing query "Kilby1 Part 1 Small Block Simple Cycle": no results
- Bing query "Kilby1 LLC Texas ERCOT": no results
- Bing query "Kilby Solstice Substation Reeves County": STRONG HIT — Kilby Project = Engine No. 1 ("Transform Power"), ~2.5 GW gas for AI data centers West Texas, 20-yr Microsoft PPA, GE Vernova turbines reported
- Bing "Engine No. 1 Kilby": CAPTCHA on engine1.com; corroborating signal from prior snippets
- Saved notes to sources/T3_web_sweep_notes.md
- Developer: Engine No. 1 (Transform Power initiative). INR "Part 1 Small Block" = phased buildout of larger Kilby portfolio
- news_found: TRUE

T4 start
- interchange.puc.texas.gov: HTTP 402 (auth required) — blocked on both base URL and direct search param
- Bing site:interchange.puc.texas.gov: CAPTCHA blocked
- Bing "Kilby interconnection agreement ERCOT": no IA docket found, but confirmed developer entity: "Energy Forge One LLC" (Chevron wholly-owned subsidiary), Chevron + Engine No. 1 JV, first power 2027
- Bing "Energy Forge One PUCT ERCOT": no IA filings surfaced
- Budget exhausted. IA not found via triage. ia_found: FALSE
- HOWEVER: strong commercial signal — first power 2027 aligns with COD 2027-11-04

T5 start
- TX Comptroller ch313 page: no searchable database accessible via WebFetch
- Bing ch313/JETI Reeves County: no application found for Kilby/Energy Forge One/Transform Power
- Post-2022 gas project — JETI miss is normal; Ch.313 expired for new applications after 2022
- abatement_found: FALSE
- ADDITIONAL CONTEXT from T5 Bing: confirmed CNBC reporting — Energy Forge One LLC (Chevron wholly-owned) + Engine No. 1, 2.5 GW gas West Texas, Microsoft ~2.7 GW data center electricity deal

T6 start
- Best site candidate assessment: no pin (gmaps 429), no abatement map, no IA, Solstice Sub coords not found via Bing, TCEQ portal URL-based search non-functional
- kilby.com confirms Reeves County but no city/coords
- Rule: "If nothing better than 'somewhere in the county', SKIP imagery"
- SKIPPING imagery — no site candidate precise enough for 3x3 grid
- construction_visible: UNKNOWN

T7 start
- Wrote triage_findings.json and triage.md
- Turns used: ~22
- STOP

## Deep scan start — 2026-07-19

### D1: Developer chain confirmation
- kilby.com/about confirms: Chevron (Energy Forge One LLC) + Engine No. 1 + Joulent + Microsoft + GE Vernova + Solar Turbines
- 20-yr PPA with Microsoft signed June 22, 2026 (kilby.com newsroom)
- Project location: Reeves County near Pecos TX
- Source: sources/T1_web_sweep_notes.md

### D2: TCEQ air permits found — CRITICAL POSITIVE SIGNAL
- Permit 181895 / PSDTX1684 / GHGPSDTX260 filed Oct 16, 2025
- Full plant capacity: 2,595-2,869 MW (15 simple-cycle + 2 combined-cycle turbines)
- Public hearing: June 10, 2026; status: PENDING as of research date
- This is the MANDATORY air permit (NSR) — its existence is a strong "real project" signal
- Source: DDG search, EIP Oil & Gas Watch; saved to sources/T1_web_sweep_notes.md

### D3: Site timing confirmed
- kilby.com/project: "2026: site prep, engineering, equipment fabrication; 2027-2028: construction, phased power generation"
- Consistent with 27INR0572 COD 2027-11-04 for "Part 1 Small Block"
- Queue shows NO IA signed yet (as of 2026-06-01 snapshot)

### D4: Solstice Substation coordinates found
- OSM Way 500535889 = Solstice Sub, AEP 345/138 kV
- Centroid: 30.948533, -103.361719 — Pecos County (not Reeves County)
- Queue project listed in Reeves County = plant ~north of substation, near county line
- Starting imagery at Solstice Sub centroid and searching NW toward Reeves County

### D5: PUCT Interchange — still 402 blocked
- No IA found on PUCT portal (confirmed 402 again in deep scan)
- Queue shows iaSigned = NOT ACHIEVED as of 2026-06-01
- No IA = no contractual schedule; COD 2027-11-04 is ERCOT queue estimate only

### D6: FID status — critical
- Energy Capital HTX article (Jun 23, 2026): "final investment decision expected later in 2026"
- This means FID had NOT been taken as of the article date (6 weeks before today)
- No IA signed (confirmed by queue as of 2026-06-01)
- These two facts together mean: real project, real permits, but investment/construction commitment NOT yet locked

### D7: GE Vernova turbine contract confirmed
- "GE Vernova will supply most of the plant's power capacity" — from Energy Capital HTX article
- Solar Turbines (Caterpillar) supplies additional capacity
- This is the strongest "real project" signal: turbine suppliers confirmed by credible trade press
- However: no specific order/delivery dates published; no confirmation of turbine delivery started

### D8: Total plant capacity = 2.67 GW (≠ queue capacity)
- kilby.com/about & news: 2.67 GW total; TCEQ application: 2,595–2,869 MW
- Queue 27INR0572 = 371 MW "Part 1 Small Block" = first phase only
- 15 simple-cycle + 2 combined-cycle turbines across full plant (per TCEQ)
- "Phased, modular approach" = 371 MW Part 1 is just the first block

### D9: Imagery — no construction visible
- Two S2 chips (2026-07-01): Solstice Sub area (30.9485, -103.3617) and north of sub (31.05, -103.40)
- Both show undisturbed desert/ranch land, no construction activity
- Could not capture Pecos city outskirts directly (CDSE auth expired)
- Note: gas plant site may be closer to Pecos city (not near Solstice Sub)
- Imagery verdict: no_activity (with caveat: exact site coordinates uncertain)

### D10: Site coordinates assessment
- Solstice Sub: 30.948533, -103.361719 (Pecos County, not Reeves County!)
- Microsoft data center + power plant: "near Pecos TX" = Reeves County
- Probable plant location: within 10-15 miles of Pecos, likely along I-20 or US-285 corridor
- No pins found (gmaps 429 rate-limited), no county parcel data found
- Best estimate: lat 31.40, lon -103.50 (Pecos TX area) — low confidence, cannot validate with imagery

### D11: PUCT ERCOT queue milestones (as of 2026-06-01)
- FIS requested 2025-10-16, NOT approved
- No IA signed → no contractual COD schedule
- COD 2027-11-04 = ERCOT queue estimate only, not bound to a signed IA
