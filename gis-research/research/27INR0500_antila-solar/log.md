# Research log — Antila Solar (27INR0500)

Research date: 2026-07-20
County: Borden, TX | 500 MW solar PV | POI: #59916 Buck Canyon 345kV | Reported COD: 2027-11-30

## D0 — Skeleton written

Factsheet key gaps: no SPV resolved, no verified IA, not in EIA-860M, 0 COD slips (held 2027-11-30 since 2025-04-01, 15 snapshots).
Financial security IS posted — real-project signal. IA signed 2025-08-13 (queue-claimed, unverified).

## D1 — IA extracted

**puct.py match 27INR0500**: Found filing 35077-2227 "Generation Interconnection Agreement between Wind Energy Transmission Texas, LLC and SE DC DevCo, LLC for the Antila Solar Project" — saved unverified.

**Manual verification**: PDF pages 2, 11, 34 confirm parties + project name + county + POI. Renamed to verified:
`sources/2026-07-20_puct_35077-2227_antila-solar-IA.pdf`

**Key IA findings**:
- TSP: Wind Energy Transmission Texas (WETT)
- Generator/SPV: SE DC DevCo, LLC
- Effective date: 2025-08-13
- POI: Buck Canyon 345kV switching station, Borden County, TX (Exhibit C)
- Equipment: 200× Sungrow SG3600UD-MV inverters (Exhibit C, item 4)
- Trial Op: 2027-06-15 | Scheduled COD: 2027-11-15 (Exhibit B, page 31)
- Initial security: $100,000 within 10 business days (Exhibit B)
- Juno Solar 3 IA also contingent (signed same day by same parties)
- Study results still TBD as of IA execution; schedule subject to change
- Notice address: SE DC DevCo, 3 Lagoon Drive Suite 280, Redwood City CA 94065; email @sbenergy.com → SB Energy is developer

**SPV/parent chain**: SE DC DevCo LLC → SB Energy (via email domain + matching Redwood City address)

**spv.py resolve 27INR0500**: PUCT index flagged SE DC DevCo from filing description.

**ch313.py resolve 27INR0500**: NEGATIVE — no Ch.313 or JETI application matches. Borden County (2025+) project may be post-Ch.313 sunset; JETI search shows no hit.

**eia_history.py 27INR0500**: NOT in EIA-860M — negative evidence logged.

**CCN docket 59199**: WETT filed Jan 2026 to amend CCN for "Buck Canyon to Juno Solar 3" transmission line. Active SOAH hearing as of April 2026. This is the TIF (transmission interconnection facilities) needed for Antila and related projects. Hearings ongoing — CCN not yet granted as of latest filings (April 2026).

**Negative searches logged**:
1. "SE DC DevCo SB Energy Antila Solar Borden County Texas" — DDG FAILED
2. "SB Energy Antila Solar 500 MW Borden Texas" — FAILED
3. "SB Energy "Borden County" solar Texas 2027" — FAILED
4. "SE DC DevCo LLC Texas solar ERCOT" — FAILED
5. "Buck Canyon 345kV WETT Wind Energy Transmission Texas substation Borden County" — FAILED

## D3 — Gap-fill / County records

**ch313.py resolve 27INR0500**: NEGATIVE — no Ch.313 or JETI match.
**eia_history.py 27INR0500**: NOT in EIA-860M. Negative evidence.

**CCN docket 59199** (sources/2026-07-20_puct_59199-2_wett-ccn-buck-canyon-juno.pdf):
- Filed 2026-01-29 by WETT for "Buck Canyon to Juno Solar 3 and Antila Solar 345kV Transmission Lines"
- Two ~8.4-mile single-circuit 345kV lines, ~1.3 GW combined (each ~500 MW), Borden County only
- Collector Stations: directly north of US 180, ~1 mile ENE of FM 1054 N/US 180 intersection
- TIF construction: Aug 2026–Apr 2027, energize May 2027
- CCN SOAH contested case active April 2026 (Staff requested hearing on merits March 2026)
- FAS submitted Dec 2025, no ERCOT objections

**Figure 1-1 project location map** extracted from CCN EA Appendix A:
- Shows labeled "Proposed Juno Solar 3 and Antila Solar Collector Stations" NE of US 180 junction
- Buck Canyon Station (WETT) ~3.2 miles SW
- Saved: sources/2026-07-20_puct_59199-ccn-figure1-1_project-location-map.png

Additional negative searches (6-11): all DDG FAILED — SB Energy portfolio, Borden CAD, SE DC DevCo.

## D2 — Site + imagery

**Google Places "WETT-Buck Canyon Switching Station"**: 32.718751, -101.635460, 9294 Vealmoore Rd FM 1054, Gail TX 79738 — THIS IS THE POI. Site will be adjacent/nearby.

**Google Places "Antila Solar"**: NO RESULTS — no construction pin yet.
**Google Places "SE DC DevCo Antila Solar Borden Texas"**: NO RESULTS.

**CDSE imagery**: Connection failing (RemoteDisconnected) on all attempts to /result endpoint. Async batch jobs return 402 PaymentRequired. Token cache exists. openEO catalog endpoint reachable. Issue is server-side at the synchronous processing endpoint.

**Google Places "Juno Solar SB Energy"**: 32.767155, -101.650809, O'Donnell TX — this is the co-located collector station site for both Antila Solar and Juno Solar 3.
Confirmed consistent with CCN Figure 1-1 map (collector station box NE of US 180 junction).

## D5 — Wrap-up

**queue_history.py 27INR0500**: 15 snapshots, 0 COD changes (2027-11-30 stable 2025-04→2026-06)
**eia_history.py 27INR0500 --write**: NOT in EIA-860M
**dossier.md**: written 2026-07-20
**findings.json**: final update 2026-07-20



---
# Second-pass review — 2026-07-21

## Developer — CONFIRMED via full campaign (primary source)
Read all four PUCT 35077 campaign IAs: -2184 Juno Solar 3, -2185 Lyra Solar, -2225 Lyra BESS, -2227 Antila. ALL = WETT + SE DC DevCo, LLC = SB Energy. Antila's prior chain (SE DC DevCo / SB Energy) is correct and now corroborated across the whole campaign. The "Juno" name trap noted in SITE_DERIVATION: SB Energy's new "Juno Solar 3/4" vs Intersect Power's existing "Juno Solar Project" (op 2021) vs ENGIE's existing "Long Draw Solar".

## Site CORRECTION (map exhibit vs Places pin)
Prior anchor 32.7672,-101.6508 came from a Google Places pin that geocoded to "O'Donnell TX" and sits ~8.6 km too far WEST — at the Buck Canyon/Long Draw switching-station area, NOT the solar collector. Re-rendered CCN 59199 EA Fig 1-1 at high res (…figure1-1…_hires.png): the Juno 3 + Antila Collector Stations are just N of US-180 ~7 mi W of Gail, co-located (~0.5 km) with the Lyra collector complex (cross-ref Lyra CCN 59183 Fig 2-1 aerial, on the "Juno DC, LLC" parcel). New anchor **32.772,-101.559** (method ccn_59199_figure_1-1_map, conf medium-high). Pruned the 87 MB image-only figure appendix + one duplicate IA PDF (re-fetch: puct.py fetch 59199 2).

## Registries (re-run)
ch313/JETI NEGATIVE (structural). ch312: 4 Borden zones (Oxbow #3676, BNB Long Draw #4302, IP Juno #4303, Borden BESS #15389) — all other/existing projects, none names Antila/SE DC DevCo, none links a harvested PDF (pdf=None). eia_history --write: NOT in EIA-860M.

## Imagery (NEW — s2aws.py, prior run had none; 5.0 km buffer @ 32.772,-101.559, tile 14SKB)
Read 3 frames. 2024-07-18 & 2025-07-20 (cloud 0.0%): collector site BARE rangeland; existing ENGIE Long Draw Solar array at W edge (NOT Antila). 2026-07-20: NEW bright ~1 km graded/cleared area at the collector complex, absent 2025 -> early site preparation. The denser 2026 Lyra time series (co-located, same scene) documents the ramp: clearing by 2026-03, graded pad by 2026-05, expanding through 2026-07. Construction verdict -> early_site_preparation_observed; project verdict -> real_active.
