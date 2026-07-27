# Triage log — 24INR0298 Leighton Solar SLF

T1 start
T1 result: 51 snapshots, 6 COD changes. IA signed 2024-05-28. Meets 6.9(1) 2025-02-13. No construction milestones. COD drift: 2024-11-04 → 2025-11-30 → 2024-11-04 → 2026-10-17 → 2027-04-30 → 2027-09-01 → 2027-11-01 (current). Capacity stable at 183 MW most of history, recently trimmed to 181 MW. Long drift history with signed IA = real project but delayed.

T2 start
T2 result: gmaps.py returned HTTP 429 on both attempts (rate-limited). No pins found. Normal miss.

T3 start
T3 result: Developer = Pine Gate Renewables; SPV = Lavender Solar LLC (not "Leighton Solar SLF LLC"). Location near Groesbeck TX, Limestone County. Developer page (pinegaterenewables.com/lavender-solar/) shows construction 2025-2027, operational Q2 2027. Economic: $50M, ~250 construction jobs, Mart ISD. LLC registration search blocked by CAPTCHA. Saved source: sources/pine_gate_lavender_solar.md. Key find: developer identity confirmed, no press/announcement found beyond developer page.

T4 start
T4 result: PUCT Interchange returning HTTP 402 on all endpoints (FilingParty, Description, main search). Portal blocked — no IA documents retrieved. ia_found = false (from PUCT; note: ERCOT queue shows iaSigned = 2024-05-28, so IA exists but document not retrieved from PUCT).

T5 start
T5 result: TX Comptroller Ch.313 site has no searchable database accessible via WebFetch; JETI page not directly searchable. No abatement records found for Limestone County / Pine Gate / Leighton Solar. Post-2022 project, so Ch.313 unavailable (program expired); JETI miss is normal. abatement_found = false.

T6 start
T6 result: Site candidate = near Groesbeck TX (31.524, -96.534), confidence LOW (developer page only, no pin/abatement map). CDSE auth failed — HTTP 401/403 on all 9 chip attempts (credential issue). No imagery retrieved. construction_visible = false (no data). Deep scan should retry imagery once CDSE creds are refreshed, and should first locate Fernleaf 138kV substation to tighten the site estimate.

T7 start
T7 result: triage_findings.json + triage.md written. Turns used: ~28. Blockers: gmaps 429, PUCT 402, CDSE 401. Key positive signals: IA confirmed, developer page live, Pine Gate identified. Deep scan recommended.

## Deep scan — 2026-07-20

D0: findings.json skeleton written.

D1-IA: puct.py match "Lavender Solar" → PUCT 35077-2221 (Brazos Electric + Lavender Solar LLC, filed 2025-08-11). IA CONFIRMED — cover letter explicitly names "Leighton Solar project in Limestone County". Signed 2024-05-28. Parties: Brazos Electric Power Cooperative (TSP), Lavender Solar LLC (generator). Developer contact: Pine Gate Renewables (pgrenewables.com), Meg Witte PM, Asheville NC 28801. Bank entity FP 2021 Dev Holdco LLC (Fifth Third Bank ABA 042000314).

D1-IA-schedule: Exhibit B Time Schedule: In-Service 2026-05-16, Trial Op 2026-08-31, Scheduled COD 2026-10-31. ORIGINAL IA COD = 2026-10-31 — queue now says 2027-11-01, already slipped ~13 months from contractual.

D1-POI: Exhibit C names Ben Hur Switching Station (69 kV), off CR 616 ~8.5 mi west of Groesbeck, Limestone County. Delivery voltage 69 kV. Single-line diagram: LEIGHTON generator POI on west side of Ben Hur Switching Station; lines to Perry, Leighton (TX), Groesbeck, Reagor Springs. Queue lists "Fernleaf 138 kV" — DISCREPANCY; IA governs. Inverters: 46× Sungrow SG4400UD (180 MW total).

D1-amendments: First Amendment 2025-01-21 — revised Exhibit E security only; schedule unchanged. Second Amendment 2025-05-14 — pushed construction LC due date 5/30/25 → 10/31/25 (5-month slip = construction start delayed). Security: $3.6M engineering LC (eff. 5/31/24) + $8.9025M construction LC (eff. 10/31/25 per Amend 2).

D1-spv: puct.py match "Leighton Solar SLF" → 0 hits. spv.py → no candidates. ch313.py Limestone County → no hits. EIA-860M → NOT in TX slice (negative evidence; logged).

D1-site: IA text says "approximately two (2) miles north of the intersection of FM339 and CR 616 in Limestone County; Texas approximately 8.5 miles west of Groesbeck." → site is near 31.53°N, -96.73°W (estimate; Ben Hur TX locality pin 31.510, -96.728; 2 mi north of FM339/CR616 intersection near Ben Hur). Ben Hur single-line diagram confirms LEIGHTON generator feeds Ben Hur Switching Station (69 kV), with lines to Perry, Leighton TX, Groesbeck, Reagor Springs, Hearne.

D2-imagery: CDSE 402 Payment Required — credits exhausted on openEO endpoint. No satellite imagery retrieved. Construction stage unverified.

D2-gmaps: Google Maps Places returned "Ben Hur, TX 76642 | 31.510448, -96.727764 (colloquial_area,political)" — confirms Ben Hur locality center. No construction pins found for "Lavender Solar", "Leighton Solar", "Leighton Solar construction". Static map API returned 403 (Maps Static API not enabled).

D3-ch313/jeti: ch313.py with "Lavender Solar", "Leighton Solar SLF", "Pine Gate", Limestone County — all NEGATIVE. JETI current agreements (11 total) — no solar projects, no Limestone County, no Mart ISD. Developer page references "Abatement Rehearing Site Orientation Map (Jan 2025)" — a county Ch.312 abatement proceeding is likely but documents not retrieved.

D3-web: Developer page (Sep 2025 update) confirms: 180 MW, construction 2025-2027, operational Q2 2027, Mart ISD taxes. FP 2021 Dev Holdco, LLC = bank account entity (Pine Gate corporate structure). Limestone County commissioners court portal (CivicClerk) not accessible via WebFetch (JS only). limestonecad.com CAD portal not accessible.

D3-search: All DDG/search backends failed (ConnectionError) this session.

D4-eia: NOT in EIA-860M — negative evidence for project claiming COD Nov 2027.

D5-wrap-up: queue_history.py → 51 snapshots, 6 COD changes. eia_history.py → NOT in EIA-860M (negative, logged).
