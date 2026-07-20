# Research Log — Caliche Mound Solar (23INR0056)

Researched: 2026-07-19  
Researcher: agent  
County: Deaf Smith, TX  
Capacity: 406.6 MW solar PV  
POI: tap 345kV 23906 AJSwope – 23910 Windmill  
CDR Zone: PANHANDLE  
Reported COD: 2027-10-26

---

## Stage 1 — LLC / Parent chain

**Triage carry-forward:** SPV = Caliche Mound Solar, LLC (confirmed via PUCT #35077 IA filing). Developer "Tierra Blanco Solar LLC" appeared on aggregators during triage but was not independently confirmed.

**Deep scan attempts — all blocked:**
- TX Comptroller COA (mycpa.cpa.state.tx.us) → redirects to login-gated comptroller.texas.gov; no programmatic entity lookup possible
- TX SOS SOSDirect (direct.sos.state.tx.us) → requires paid $1/search subscriber account
- SEC EDGAR EFTS full-text search (efts.sec.gov) → HTTP 403 on ~40 separate queries; this IP/environment is uniformly blocked
- SEC EDGAR company browse (sec.gov/cgi-bin/browse-edgar) → HTTP 403
- FERC eLibrary → returns empty page with just "eLibrary" text; no results extractable via WebFetch
- PUCT Interchange (interchange.puc.texas.gov) → HTTP 402 Payment Required on all queries
- OpenCorporates → CAPTCHA wall
- Bizapedia → CAPTCHA wall
- Corporate Wiki → HTTP 403

**Result:** Developer chain NOT verified this session. Prior triage finding (Tierra Blanco Solar LLC) stands as best available but unconfirmed.

---

## Stage 2 — PUCT Interconnection Agreement

PUCT Control #35077 is an Oncor IA filing dated 2023-10-26, confirming IA signed 2023-10-12. PDF contents unread — PUCT Interchange portal returned HTTP 402 on all programmatic queries. PDF would contain exact POI coordinates, milestone schedule, and potentially counterparty/developer identity.

**Action:** Pull PUCT #35077 PDF directly via authenticated browser or PUCT bulk download tool.

---

## Stage 3 — Site candidate / imagery

Not completed. POI substations (AJSwope 23906, Windmill 23910) not geolocated this session. Without site coordinates, Sentinel-2 imagery sweep was skipped.

---

## Stage 4 — Abatement

- Chapter 313: Portal not accessible.
- JETI: Not searched — session budget exhausted before this stage.

**Action:** Search JETI registry at Texas Comptroller for post-2022 Deaf Smith County application by Caliche Mound Solar or Tierra Blanco Solar.

---

## Stage 5 — News / Press

No press releases, PPA announcements, or developer announcements found on any accessible public source:
- Law360: zero results
- CleanTechnica: zero results  
- PV-Tech: zero results
- GlobeNewswire: zero results
- Local TX papers (thecastrocountynews.com): no relevant articles
- TCEQ search: no results for "caliche mound solar"

This is consistent with a pre-announcement project — likely still in development/financing phase with no public press.

---

## COD Assessment

Reported COD: 2027-10-26. IA signed 2023-10-12. Meets 6.9(1): 2025-02-12. Meets all 6.9: NOT YET. The project has slipped 5 times, accumulating ~4.5 years of delay since its original 2020 COD claim. The 2027 date is plausible given the IA milestone, but slip history indicates meaningful probability of further delay.

---

## Summary

Deep scan was largely unsuccessful due to infrastructure access barriers:
1. SEC EDGAR EFTS blocked (HTTP 403) — probably IP/bot filter
2. PUCT Interchange blocked (HTTP 402) — subscription required
3. TX SOS/Comptroller entity databases — require paid accounts or interactive sessions

**Best next steps:**
1. Pull PUCT #35077 IA PDF (needs authenticated access or curl with correct auth)
2. TX SOS entity lookup for Caliche Mound Solar LLC (requires SOSDirect account or TX SOS staff contact)
3. Geolocate AJSwope/Windmill 345kV substations → run Sentinel-2 sweep
4. Search JETI registry for Deaf Smith County / Caliche Mound Solar
