# Triage log — 27INR0297 Tolivar Power Plant (TEF- Due Diligence)

## T1 start
- Script: queue_history.py — 25 snapshots 2024-06-01 → 2026-06-01
- COD drift: 2027-04-15 → 2027-05-06 (1 change, ~21 days slip, minimal)
- Capacity change: 225.6 → 224.5 MW (minor trim)
- IA signed: 2025-07-01 ✓
- FIS approved: 2025-06-23 ✓
- Meets 6.9(1): 2025-08-04 ✓
- Meets all 6.9: 2026-06-16 ✓ (just achieved, very recent)
- Construction start/end: not reported
- Strong milestone progression through full ERCOT queue process

## T2 start
- gmaps.py places "Tolivar Power Plant" → HTTP 429 Too Many Requests
- gmaps.py places "Tolivar Power Plant Reeves County Texas" → HTTP 429 (retry exhausted)
- Result: 0 pins found (blocked portal, one retry per rule)

## T3 start
- Developer: Pecos Power Plant, LLC (Houston TX, formed May 2024, TX SOS 0805541651)
- PUCT PGC registration docket 56666 (filed May 2024 for natural gas facility)
- Phase 2 exists: 28INR0413 (~225 MW), combined ~453 MW total
- Location: "Pecos, Reeves County" per gem.wiki (site 403)
- TCEQ air permit: not found via web search; portal session-blocked
- TEF: name contains "(TEF- Due Diligence)" but no TEF docket surfaced in search
- gem.wiki 403, oilandgaswatch.org 403
- Saved: sources/t3_web_sweep.md

## T4 start
- interchange.puc.texas.gov → HTTP 402 on all endpoints (auth/session required)
- DDG search for PUCT IA docket → no results
- DDG search for TEF docket on puc.texas.gov → no results
- PUCT docket 56666 (from T3) is PGC registration, not IA
- IA milestone is shown as achieved 2025-07-01 in ERCOT queue data (T1)
- IA docket number not found via public web search; PUCT portal blocked
- Result: IA_FOUND = true (milestone confirmed via ERCOT data) but PDF not retrieved

## T5 start
- TX Comptroller Ch.313: portal not navigable via WebFetch (no filterable data returned)
- JETI: DDG search returned CAPTCHA block
- No Ch.313 or JETI abatement found — normal for post-2022 project (Ch.313 expired 2022)
- Result: abatement_found = false

## T6 start
- Site candidate: SE of Pecos TX near COWPEN substation (TNMP 138kV) ~31.38°N, 103.44°W
  Source: POI "38043 COWPEN" + DDG search "COWPEN substation Reeves County" → "~1.1 mi NE of FM 1450 / CR 107 intersection SE of Pecos"
- cdse.py chip 3×3 grid centered 31.38,-103.44 → HTTP 401/403 on all 9 (CDSE creds invalid)
- Imagery: blocked — credentials not configured; construction_visible = unknown

## T7 start
- Wrote triage_findings.json
- Wrote triage.md
- Turns used: ~28
- Blockers this run: gmaps.py 429 (T2), PUCT interchange 402 (T4), CDSE 401 (T6)
- Key finding: TCEQ air permit not found — mandatory for gas recip; critical gap for deep scan
- STOP

## DEEP SCAN START — 2026-07-19

Deep scan threads:
1. TCEQ STEERS air permit (mandatory NSR for gas recip) — TCEQ EAS portal
2. TEF docket on PUCT interchange
3. LLC parent chain beyond Pecos Power Plant LLC
4. COWPEN substation precise lat/lon
5. PUCT IA filing PDF retrieval
6. Reeves County CAD parcel search
7. Imagery at COWPEN area

## D1 — TCEQ air permit search (mandatory for gas recip)
- TCEQ www.tceq.texas.gov/search: "Tolivar Power Plant" → **NO RESULTS** (2026-07-19)
- TCEQ www.tceq.texas.gov/search: "Pecos Power Plant Reeves" → **NO RESULTS** (2026-07-19)
- TCEQ STEERS portal (www15.tceq.texas.gov/crpub/) → 0-byte response (session-based, no curl access)
- TCEQ www2.tceq.texas.gov/airperm/ → 503 Service Unavailable
- **FINDING: No TCEQ air permit found for this mandatory-NSR gas reciprocating project — strong paper-project signal**

## D2 — Satellite imagery (first chip)
- CDSE chip: 31.38N, 103.44W, 2026-07-01, 3km buffer → imagery/s2_2026-07-01.png
- Observation: desert/scrubland landscape along diagonal road (likely IH-20 corridor); rectangular
  infrastructure in center-left (consistent with substation/existing facility); image somewhat
  washed/overexposed (summer desert conditions); NO visible construction activity — no laydown yards,
  no cranes, no industrial build signatures
- Need: wider chips and multiple angles to confirm; the site may not be at exactly 31.38,-103.44

## D3 — TEF / PUCT Texas Energy Fund
- PUCT TEF page (www.puc.texas.gov/industry/electric/business/texas-energy-fund/default.aspx) loaded via curl
- As of Jun 24, 2026: 8 finalized In-ERCOT loan agreements (4,994 MW, $3.65B) — Tolivar NOT among them
- Current queue: 4 applications in due diligence, 2,233 MW total
- CRITICAL: Dec 31, 2026 = last day for PUCT initial loan disbursements — Tolivar must complete DD by then
- Tolivar is "(TEF- Due Diligence)" = still in DD phase, no loan agreement signed
- Source artifact: sources/2026-07-19_puct_tef-in-ercot-loan-program-page.html ✓

## D4 — SEC EDGAR for Kinetik Holdings (KNTK)
- SEC EDGAR search "Pecos Power Plant" found 1 hit: Kinetik Holdings Inc. 8-K filed 2026-05-07
- Filing period: 2026-05-06; accession 0001692787-26-000089; Kinetik = Permian Basin midstream gas
- Kinetik = natural gas transmission in Permian Basin = potential gas supply customer for Tolivar
- Could confirm: (a) Tolivar is being built as gas demand exists, OR (b) Kinetik has its own Pecos power plant
- Could not retrieve document text (SEC 403); need to investigate further
