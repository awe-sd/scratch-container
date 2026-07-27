# Triage log — OCI Cobb Creek Solar (25INR0229)

## T1 start

**Queue history:** 44 monthly snapshots (2022-11-01 → 2026-06-01), 5 COD drifts.

| Milestone | Date |
|---|---|
| Screening started | 2022-11-15 |
| Screening complete | 2023-02-09 |
| FIS requested | 2022-11-09 |
| FIS approved | 2024-05-06 |
| IA signed | 2024-07-24 |
| Meets 6.9(1) | 2025-06-11 |
| Meets all 6.9 | NOT achieved |
| Construction start/end | NOT reported |
| Approved for energization/sync/COA | NOT achieved |

**COD drift:** 5 changes. Original claim 2025-06-01 → slipped each year → now 2027-12-31.
Drift of ~2.5 years from initial entry. Current COD 2027-12-31 is plausible but terminal-slip candidate.

**Capacity:** minor oscillation (204.09 → 202.2 → 203.1 MW), settled at 203.1 MW.

**T1 result:** Strong queue presence, IA signed 2024-07-24, 6.9(1) met 2025-06-11. Pre-construction stage.

## T2 start

**gmaps.py:** HTTP 429 on both attempts (rate-limited). Budget spent.
**T2 result:** No pins found. Normal — no retry.

## T3 start

Queries run:
1. DDG HTML: "OCI Cobb Creek Solar" → CAPTCHA block (one retry exhausted)
2. Bing: "OCI Cobb Creek Solar" → 0 relevant hits (OCI = Overseas Citizenship / Oracle noise)
3. Bing: "OCI Cobb Creek Solar" OR "OCI Solar" "Hill County" Texas → 0 relevant hits
4. Bing: "OCI Solar" LLC Texas solar interconnection → 0 relevant hits
5. Bing: "Cobb Creek Solar" Texas → 0 relevant hits

**T3 result:** No news, no developer registration, no announcements found. Project has essentially no public web footprint. No alternate developer name surfaced.

## T4 start

- PUCT Interchange direct URL: HTTP 402 on all attempts (session cookie required, not public)
- Bing site:interchange.puc.texas.gov: CAPTCHA block
- Bing web search for PUCT/IA filings: 0 relevant hits

Note: IA is confirmed signed per queue timeline (2024-07-24). PUCT portal inaccessible.

**T4 result:** IA not retrieved — portal blocked. IA existence CONFIRMED by queue data (milestone date 2024-07-24), but document not accessible in triage.

## T5 start

- TX Comptroller Ch.313 page: returned overview/navigation, no data table
- Comptroller page with county/fuel params: same navigation page, no data
- Bing search Ch.313/JETI + Hill County + OCI/Cobb Creek: 0 relevant hits
- JETI approved projects PDF (gov.texas.gov): HTTP 404

Project entered queue 2022 — Ch.313 expired end-2022 for new applications. JETI replaced it; 
post-2022 entrants can use JETI but there's no public searchable index readily accessible.

**T5 result:** No abatement found. Normal for a 2022-vintage project (Ch.313 closed; JETI registry not publicly indexed in accessible form).

## T6 start

Site candidate evaluation:
- Pins (T2): none (gmaps blocked)
- Abatement map (T5): not found
- IA map (T4): portal blocked
- POI infrastructure: "tap 345kV 1907 Venus - 68090 Sam Sw" — tap on a 345kV line segment. Without transmission line route data, cannot resolve to sub-county lat/lon. Venus substation is in Johnson County; line passes through Hill County but tap location along the route is unknown.

Result: no site candidate better than "somewhere in Hill County" → SKIP imagery per checklist rule.

**T6 result:** SKIPPED — no site candidate. Log: "no site candidate".

## T7 start

Written: triage_findings.json, triage.md
Turns used: ~22
Deep scan recommended: YES

**T7 complete. Triage done.**

## Deep scan — D0/D1 (2026-07-20)

### D0: IA document (PUCT rung 0 — exact INR join match)
- `puct.py match 25INR0229`: hit via INR join table, item 35077-1898, "Standard Generation Interconnection Agreement between Oncor Electric Delivery Company LLC and OCI Hillsboro Solar LLC (OCI Cobb Creek Solar & OCI Cobb Creek ESS) (25INR0229 & 25INR0233)"
- **CONFIRMED**: INR 25INR0229 found in PDF text
- Saved: `sources/2026-07-20_puct_35077-1898_standard-generation-interconnection-agreement-be.pdf`
- SPV name: **OCI Hillsboro Solar LLC** (queue name "OCI Cobb Creek Solar" is project/codename; LLC name differs)

### D0: EIA history
- `eia_history.py 25INR0229 --write`: matched plant 68481 "Hill Solar II" 200 MW Hill Co, entity "Hill Solar II, LLC"
- EIA status progression: (U) ≤50% complete 2025-01→2025-08, (V) >50% 2025-09→2026-03, **(TS) construction complete not yet commercial 2026-04→2026-05**
- EIA planned COD crept: 2025-12 → 2026-01 → 2026-02 → 2026-03 → 2026-06
- **Key divergence**: EIA says construction complete (April 2026); ERCOT queue says COD 2027-12-31

### D1: IA schedule extraction
- Exhibit B dates: In-Service Date(s) = **May 7, 2026**; Trial Operation = **September 1, 2026**; Scheduled COD = **December 1, 2026**
- Security: $16,707,463 surety due 2024-07-31 (Exhibit E)
- POI (Exhibit C): **"proposed Bynum Switch within TSP's Venus–Sam SW 345 kV transmission line, Hill County, TX"** — switch is a NEW Oncor TIF; CEII location redacted
- Equipment: 54× Power Electronics HEM GENIII FS4010M inverters, 203.1 MW net; plus 25INR0233 BESS 201.6 MW
- No IA amendments found (puct.py filings 35077 --party "Oncor" filtered for OCI: only item 1898)

### D2: Site candidates
- EIA-860M: 32.1152, -97.06783 (Hill Co) — county+MW match
- Google Places "Hill II North yard" → 32.136058, -97.061804, near Milford TX — contractor yard pin, ~2.4 km N of EIA coords
- Google Places "Hill Solar I" → 32.167277, -97.069916, 5506 FM934 Itasca TX — sibling project "Hill Solar I" at different location
- **Site converges on NW Hill County near Milford TX** — both independent indicators within ~4 km
- CDSE imagery: **OUT OF CREDITS** (402 Payment Required) — cannot obtain satellite imagery this run
- Google Static Maps API: disabled (403) for this key

### D3: Gap-fill searches
- ch313.py resolve 25INR0229: **NEGATIVE** — no Ch.313 or JETI agreement (expected for 2022+ project)
- search.py "OCI Cobb Creek Solar" Hill County: **FAILED all backends**
- search.py "OCI Solar Power Texas Hillsboro": **FAILED all backends**
- search.py "HEC Renewable Energy America LLC Texas solar": **FAILED all backends**
- search.py "Hill Solar Milford Texas solar project": **FAILED all backends**
- Hill CAD esearch.hillcad.org: JS-rendered, blocks automated fetch — no parcel data retrieved
- PUCT docket filings for OCI: item 35077-1251 "OCI SOL LLC (Golinda)" 2021 — sibling project confirms OCI brand active in ERCOT
- OCI corporate website (oci.com/ocisolar.com): DNS not resolved or redirected
- Web search: ALL backends down for this session

