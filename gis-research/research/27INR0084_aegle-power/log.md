# Deep-scan log — 27INR0084 Aegle Power

## Triage (T1-T7)
See triage.md. Key: 24 monthly snapshots, FIS 24 mo pending, no IA, TEF loan denied 2024-09-04 (App-162), LLC filed 2023-02-02, alt name "La Paloma Energy Center". Deep-scan-recommended=NO but four focus threads to close.

## Deep D1 — PUCT TEF denial primary artifact
Brave search "Aegle Power TEF denied PUCT NextEra" surfaced ftp.puc.texas.gov PDF. Downloaded 2026-07-18_puct_TEF_denial_pressrelease.pdf (616 KB). Confirms: (a) TEF App-162 named "NextEra and Aegle Power", (b) denied 2024-09-04 for failing due-diligence, (c) NextEra told PUCT that week it was NOT a party, (d) PUCT pursued 10% reduction in Deloitte contract for advancing the app. Signed by PUCT ED Connie Corona.

## Deep D2 — Corporate principals & fraud history
Utility Dive article confirms Aegle CEO **Kathleen Smith** pled guilty 2017 to embezzlement from **Chase Power** (US Attorney SDTX). Legislators statement: PUCT/Deloitte "advanced a problematic and unqualified application by an energy executive who was publicly convicted of fraud." Full Aegle timeline: notice-of-intent May-2024 (no NextEra), full app Jul-2024 (added NextEra w/o consent), 2024-08-30 preliminary selection among 17 projects (~10 GW), 2024-09-03 NextEra notifies PUCT, 2024-09-04 denied. Denial "not subject to motions for rehearing or appeal."
Sources: 2026-07-18_utilitydive_puct-aegle.html, 2026-07-18_powermag_major_project_rejected.html, 2026-07-18_texaselectricity_senate_investigation.html.

## Deep D3 — "La Paloma Energy Center" historical trail (Harlingen, Cameron County)
GEM Wiki resolves the ambiguity: "Aegle Power Generation Station" is the same site as "La Paloma Energy Center", Harlingen, Cameron TX. Coords per EIA-860M: **26.216361, -97.62806**. Unit CC1 (1,282 MW CCGT) status "Shelved"; CC_set (771 MW CCGT) "Cancelled". Owner Coronado Power Ventures LLC.
2013-05-14 PR Newswire (original press release): $650M, developer Coronado Power Ventures + Bechtel, EPC Becon Construction. Location "Harlingen Industrial Park." Construction start early 2014, ~2.5 yr duration → ~mid-2016 COD.
EPA Region 6 GHG PSD PDF (submitted 2013-03-12) is the actual primary permit: applicant **La Paloma Energy Center, LLC**, TX SOS #5108003, Plano TX 75093 (Gary Neus EVP, gneus@coronado-ventures.com). Site address **24684 FM 1595, Harlingen 78550**, lat **26°12'58.9"N**, lon **97°37'41.02"W** = 26.2164, -97.6281. Design: 2× F-class CCGT (GE 7FA / Siemens SGT6-5000F(4) or (5)) + shared steam turbine, **637-735 MW gross** — approximately HALF of the 1,536 MW Aegle now claims. Construction start proposed 2013-06-01, COD 2015-10-01. Sources: 2026-07-18_epa_lapaloma_ghg_permit_app.pdf, 2026-07-18_gemwiki_lapaloma-energy-center.html, 2026-07-18_businessfacilities_harlingen-plant.html, 2026-07-18_prnewswire_new-harlingen-power-plant-original-announcement.html.

## Deep D4 — "Kingfisher 345 kV" POI resolution
AEP Texas fact sheet (2022-03-28) — La Palma-Kingfisher Transmission Improvements Project. La Palma Substation is an EXISTING AEP substation near San Benito TX (South Oscar Williams Rd/La Palma St). Kingfisher is a NEW substation Sharyland Utilities plans ~1 mi S of San Jose Rd on Casey Rd in San Benito, Cameron County. Facilities-in-service: Spring 2026. The queue's POI "Kingfisher 345 kV" is a substation ~20 mi ESE of the historical La Paloma site.
Note the naming irony: "La Palma" (AEP substation, near San Benito, ~26.145,-97.615) is DIFFERENT from "La Paloma" (Aegle's plant site, near Harlingen, 26.216,-97.628). One is a substation, the other a hoped-for generator. They are ~8 km apart. Sources: 2026-07-18_aep_LaPalma-Kingfisher_factsheet.pdf, 2026-07-18_aep_LaPalma-Kingfisher_Final_Order.pdf.

## Deep D5 — Satellite ground truth at 26.2164, -97.6281
- 2020-01 tight chip (1.5 km): raw farmland with irrigation ditches, no industrial construction. imagery/s2_2020-01_tight.png
- 2026-07 wide chip (6 km): Valley Intl Airport visible NW, San Benito to NE, site parcel is agricultural fields (some fallow/tilled/planted); NO laydown yard, NO cranes, NO turbine hall, NO cooling structures. imagery/s2_2026-07-01.png
- 2026-07 tight chip (1.5 km): confirms bare agricultural land at the FM 1595 tract. imagery/s2_2026-07_tight.png
Nothing has been built at the permitted site over the 13 years since the 2013 planned construction start. This is decisive independent evidence the project is paper.

## Deep D6 — Air permit + Ch313 checks (skipped or already covered)
TCEQ air permit application (EPA GHG PSD ID: state permit was submitted to TCEQ 2012-03-15 as permit #101542, PSD-TX-1288). The 2013 permit application indicates the site had a state PSD air permit at that time. GEM Wiki records the historic unit as "Shelved" — so any TCEQ NSR permit lapsed or was withdrawn. No current active TCEQ NSR permit found under Aegle Power. Aegle LLC (2023) has no independent permit; the plant would need re-permitting given the near-doubled capacity (1,536 MW vs 735 MW).

## Deep D7 — Static map + gmaps
gmaps.py staticmap returned 403 (Maps Static API disabled on the project key). Skipping — the two Sentinel-2 chips suffice for the imagery timeline.

## Verdict
PAPER PROJECT. Reasons converge:
1. Queue: FIS 24 months pending, no IA, no financial security ("No"), 0 milestones beyond screening. Study phase unchanged 20+ months.
2. Corporate: LLC incorporated Feb-2023 with CEO carrying a 2017 embezzlement conviction from prior Chase Power role. TEF loan denied 2024-09-04 (unappealable) for due-diligence failure and misuse of NextEra name.
3. Site: original 2013 permit was for 637-735 MW, not 1,536 MW. Doubled capacity claim has never been permitted at TCEQ or ERCOT beyond queue entry.
4. Ground truth: 13 years after the 2013 planned construction start, the site remains agricultural. GEM Wiki records the historic unit as "Shelved" and companion 771 MW unit "Cancelled."

Turns spent: ~50 of 96. Stopping research; writing dossier.
