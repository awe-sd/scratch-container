# Triage log — 24INR0410 NRG Greens Bayou 6 (TEF-Due Diligence)

## T1 start
queue_history.py: 47 snapshots (2022-08-01 → 2026-06-01), 3 COD changes.
- COD drift: 2024-12-31 → 2025-06-01 → 2026-06-02 → **2028-05-01** (current)
- IA signed: 2025-02-07 ✓
- FIS approved: 2025-08-14 ✓
- Construction start/end: not reported
- MW: 455 → 445 (trimmed 2024-10)
- Zone: HOUSTON

## T2 start
Pins found:
- "NRG Energy - Greens Bayou Plant" @ 29.820520,-95.220319 | 12070 Old Beaumont Hwy, Houston TX 77049
  (Existing plant complex — "Greens Bayou 6" = likely unit addition at this site)
- Same pin returned for county/gas/Houston variants; no distinct new-site pin found.
- Confidence: HIGH this is the correct site (existing NRG plant, same name family).

## T3 start
DDG search 1 ("NRG Greens Bayou 6 gas turbine"): Results summarized — news found.
  - North Channel Star (Aug 2025): "construction of a 455-MW electricity generation plant"
  - ercotqueue.com: 445 MW Gas, Harris County, build-chance 90%, expected online 2028
  - CleanView: "planned 445 MW natural gas power plant...Expected online 2028"
  - Developer confirmed: NRG Greens Bayou 6, LLC (NRG Energy subsidiary)
  - Purpose: address projected capacity shortfalls in Texas market
DDG search 2 (TCEQ/TEF): CAPTCHA blocked, 1 retry exhausted → negative log.
DDG search 3 (TEF/PUCT): CAPTCHA blocked → negative log.
North Channel Star article URL → 404. BizJournals → blocked.
news_found: YES (multiple third-party sources confirm project; no direct TCEQ/TEF URLs retrieved)

## T4 start
PUCT Interchange (interchange.puc.texas.gov): ALL endpoints returning HTTP 402 — portal blocked/requires auth.
One retry on different URL → same result. Negative log: IA filing not retrievable via WebFetch.
Web search for docket via Bing/DDG: CAPTCHA blocked on both.
ia_found: CANNOT CONFIRM via portal (IA signed date 2025-02-07 IS in the ERCOT queue data — existence strongly implied but PDF not retrieved)

## T5 start
TX Comptroller Ch.313: No searchable database directly accessible; JETI page no agreement list.
No Ch.313 or JETI entry found for NRG Greens Bayou 6 in Harris County via portal.
Note: post-2022 gas projects unlikely Ch.313 (program expired 2022); JETI is the successor.
abatement_found: NO (expected for a project this recent; not a red flag)

## T6 start
Site candidate: 29.820520,-95.220319 (NRG Greens Bayou Plant, 12070 Old Beaumont Hwy, Houston TX) — HIGH confidence, from gmaps pin.
Chips: 5/9 fetched (3 RemoteDisconnected errors on parallel calls; center + n/nw/w/sw retrieved).
Contact sheet: existing large industrial complex visible at center — large building structures, highway adjacency (I-10 corridor). No active construction features (cranes, laydown yards, fresh earthworks) visible at Sentinel-2 resolution.
construction_visible: NO (at triage resolution; baseline comparison not run — budget constraint)

## T7 start
Wrote triage_findings.json and triage.md. Turns used: ~28. DONE.

---
## Deep scan — 2026-07-19

## D1 — SEC EDGAR: NRG Energy 10-K (FY2025) + Q3 2025 + Q1 2026 10-Q
Source: NRG Energy Inc. CIK 0001013871; accession 0001013871-26-000004 (10-K FY2025), 0001013871-25-000025 (Q3 2025 10-Q), 0001013871-26-000012 (Q1 2026 10-Q)

KEY FINDINGS:
1. **Entity confirmed**: "NRG Greens Bayou 6 LLC, an indirect wholly-owned subsidiary of the Company" — confirms LLC structure and parent (NRG Energy, Inc.).
2. **Technology**: "443 MW natural gas-fueled peaker plant" — simple-cycle gas turbine (peaker), not combined cycle.
3. **TEF Loan**: $370M loan signed Nov 20, 2025 with PUCT at 3.000% fixed, due 2045. "Third TEF Loan."
4. **Construction status**: "currently under construction" — confirmed in both 10-K (as of 12/31/2025) and Q1 2026 10-Q (as of 3/31/2026). NOT just planning.
5. **TEF loan disbursements**: $95M drawn as of Jan 31, 2026 (per 10-K); $112M carrying value (and $117M disbursed per Q1 2026 10-Q) as of March 31, 2026. Construction spend pace: ~$22M/month average Jan-Mar 2026.
6. **Commercial operation target**: "expected mid-2028" — consistent across 10-K and Q1 2026 10-Q (no change).
7. **TEF due-diligence timeline**: "On March 13, 2025, the PUCT approved the Greens Bayou 6 project to move into due diligence" — confirms the "(TEF-Due Diligence)" in queue name, milestone was approved.
8. **Turbine/EPC**: Feb 13, 2025 NRG signed strategic Project Development Agreement with **GE Vernova** (GEV) and **Kiewit subsidiary TIC** for up to 5.4 GW of new gas-fired projects. NRG also entered "two slot reservation agreements with GEV for the procurement of 2.4 GW of 7HA gas turbines" — while those are for combined cycle projects, GEV relationship confirmed; peaker turbine vendor not specifically named but GEV/GE is the primary relationship.
9. **Existing Greens Bayou plant**: 327 MW, natural gas, ERCOT; Unit 6 is an addition to this brownfield site.
10. **Equity guarantee**: "The Company signed an equity contribution agreement and guaranty with respect to the Third TEF Loan" — NRG corporate guarantee, strong financial backing.
Artifacts: sources/2026-07-19_sec_nrg-2025-10k-greens-bayou-excerpts.txt, sources/2026-07-19_sec_nrg-2026q1-10q-greens-bayou-excerpts.txt

## D2 — TCEQ Air Permit Search
TCEQ airperm/index.cfm and crpub portals: ALL session-gated (CAPTCHA or error state). Could not retrieve permit number programmatically.
Could not confirm TCEQ NSR permit via automated search.
Log: TCEQ air permit search BLOCKED (portal session-gated). Negative result on programmatic access.
Note: Per SEC filings, project is actively under construction with $112M disbursed — air permit MUST exist for construction to proceed. Absence of retrieval ≠ absence of permit.

## D3 — PUCT TEF Docket
PUCT Interchange returns HTTP 402 on all direct URLs; JS-rendered portal, cannot retrieve docs.
From SEC Q3 2025 10-Q (verified): "On March 13, 2025, the PUCT approved the Greens Bayou 6 project to move into due diligence." This IS from an SEC-filed primary document — confirms PUCT docket activity.
Log: PUCT portal access blocked. TEF docket number not retrieved. Existence confirmed via SEC filings.

## D4 — Turbine procurement
GE Vernova + Kiewit/TIC strategic agreement signed Feb 13, 2025 for up to 5.4 GW NRG gas projects; 7HA turbine slot reservations (2.4 GW) for combined cycle. Greens Bayou 6 is a peaker — turbine type not separately specified in SEC text but consistent with GEV relationship.
Source: NRG Q3 2025 10-Q at pos 2746748.

## D5 — HCAD property search
search.hcad.org blocked (HTTP 403 from WebFetch and 0 results from curl). Cannot retrieve parcel records.
Log: HCAD search blocked. Parcel/acreage not retrieved.

## D6 — Imagery
Triage imagery (5 chips, June 2026, center + N/NW/SW/W): existing large industrial complex at site. No new construction features visible at 10m resolution (brownfield addition — new CT unit would be compact; not distinguishable from existing structures at S2 resolution).
New imagery attempts: CDSE token auth failed (401 Unauthorized). Could not acquire 2024 baseline or 2026-07 chip.
Existing contact_sheet.png and s2_center_2026-06-01.png reviewed — consistent with active industrial site; no large earthworks or new clearing visible but this is expected for a brownfield CT addition (compact footprint, within existing plant boundary).

## D7 — North Channel Star article
Original URL 404. Triage noted: "construction of a 455-MW electricity generation plant" (Aug 2025 article per triage search result). URL not retrievable. Content not saved.

## Summary of evidence confidence:
- Developer/LLC: HIGH (SEC 10-K, multiple filings)
- Construction status (actively under construction): HIGH (SEC 10-K + Q1 2026 10-Q, $112M disbursed)
- COD (mid-2028): HIGH (consistent across all SEC filings from Q3 2025 through Q1 2026)
- Technology (443 MW natural gas peaker): HIGH (SEC 10-K definition table)
- TEF loan ($370M, 3%, due 2045): HIGH (SEC 10-K notes)
- Turbine vendor: MEDIUM (GEV relationship confirmed; specific turbine for peaker not stated)
- TCEQ air permit: UNCONFIRMED (portal blocked; logically must exist given active construction)
- PUCT IA filing details: UNCONFIRMED (portal blocked; existence inferred from queue data + SEC)
- HCAD parcel/acreage: UNCONFIRMED (blocked)
- Satellite construction evidence: NOT VISIBLE at S2 resolution (brownfield, compact CT, expected)
