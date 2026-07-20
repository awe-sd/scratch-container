# Triage log — Armadillo Solar (21INR0421)

Triage date: 2026-07-18

---

## T1 start (budget 2 — completed)

**queue_history.py output:** 82 snapshots (2019-09-01 → 2026-06-01), 6 reported-COD changes.

**Milestone dates:**
- Screening started: 2019-08-28
- Screening complete: 2019-11-22
- FIS requested: 2019-08-28
- FIS approved: 2025-10-08
- IA signed: 2021-02-02
- Meets 6.9(1): 2025-02-12
- Meets all 6.9: 2025-10-31
- Construction start/end, energization, synchronization, commercial operation: NONE

**COD drift (6 changes):**
- 2021-12-31 → 2022-12-31 → 2023-09-28 → 2024-10-15 → 2025-10-15 → 2026-12-31 → 2026-10-27
- Current reported COD: 2026-10-27 (held since 2026-04-01)

**Capacity changes:** Started at 200 MW (2019), briefly 204 MW, then trimmed to 150.48 MW in Feb 2026.

**T1 assessment:** Project has been drifting COD for 5+ years with NO construction milestone dates and NO energization approvals. FIS approved very late (Oct 2025). IA signed early (Feb 2021). Meets all 6.9 only as of Oct 2025. A 2026-10-27 COD with zero construction milestones is extremely aggressive — this looks like a paper project or early-construction at best.

---

## T2 start (budget 4)

gmaps.py blocked: HTTP 429 (rate-limited) on all 3 queries ("Armadillo Solar", "Armadillo Solar Navarro County", "Armadillo Solar LLC"). Budget exhausted. **No pins found.**

---

## T3 start (budget 5)

**Web sweep — key findings:**

- **Developer:** AES Corporation (acquired from Ørsted Onshore North America LLC ~2024)
- **Location confirmed:** ~8 miles SE of Corsicana, Navarro County TX, off US 287, ~2,000 acres
- **Status:** Under construction — Navco Chronicle confirms "Set to begin construction in Spring 2025"; Road ROW amendment with Navarro County signed 2025-04-28 (active ground coordination)
- **GEM Wiki:** Lists as "under construction" (403 on fetch; title confirmed by DDG)
- **COD discrepancy:** AES.com shows COD 2027; ERCOT queue shows 2026-10-27 — queue is optimistic vs. developer's own page
- **Capacity discrepancy:** AES.com still shows 204 MW; ERCOT queue trimmed to 150.48 MW Feb 2026
- **Phase 2:** 27INR0614 at ~201 MW expected 2027
- **Tax abatement:** Navarro County agreement from 2020, amended post-AES acquisition
- Sources saved: `sources/aes_project_page.md`

**T3 assessment:** High credibility project — major developer (AES), confirmed under construction Spring 2025, county-level documents, IA signed. COD 2026-10-27 is optimistic vs. AES's own 2027 projection.

---

## T4 start (budget 6)

PUCT Interchange portal returned HTTP 402 on all URL variants (interchange.puc.texas.gov, puc.texas.gov/interchange). Portal blocked — cannot retrieve IA filings. **Budget: 4 of 6 calls used, all blocked.**

Note: ERCOT queue confirms `iaSigned = 2021-02-02` so the IA exists. Could not verify PUCT docket or milestone schedule exhibit during triage.

---

## T5 start (budget 4)

**Ch.313 search:** TX Comptroller Ch.313 page has no searchable database — no online list of agreements by county/applicant. Could not confirm Ch.313 directly from portal. However, T3 web sweep confirmed a "tax abatement agreement with Navarro County from 2020, amended post-AES acquisition" — consistent with a Ch.313 with Mildred ISD (mentioned in AES project page). **Abatement likely exists; not confirmed from official registry.**

**JETI registry:** JETI page (HB 5) has no searchable database visible. Post-2022 project with AES as developer; JETI is plausible but cannot confirm during triage.

**T5 result:** Abatement signal POSITIVE from T3 secondary sources (Navarro County + Mildred ISD named). Official download not available from portal.

---

## T6 start (budget 8)

**Site candidate identified:** 9316 S US Highway 287, Corsicana TX → coordinates 32.0707, -96.4426 (Nominatim geocode; source: DDG search surfaced address from county/AES docs). Confidence: MEDIUM (address from secondary source, not PUCT IA map).

**Imagery attempt:** cdse.py returned HTTP 401 Unauthorized — CDSE_PASSWORD not set in ~/.config/gis-research.env. Imagery blocked.

**T6 result:** Site candidate established from address evidence; imagery not available due to auth failure.

---

## T7 start (budget 6)

triage_findings.json and triage.md written. Turns used: 22.

**Run complete.**






