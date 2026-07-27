# Triage log — Cachena Storage SLF (23INR0077)

## T1 start
- 71 snapshots, 2020-08-01 → 2026-06-01
- COD drift: 5 changes (2023-06 → 2024-06 → 2024-12-31 → 2025-12-31 → 2026-12-31 → **2027-04-29** current)
- Capacity: 100→102.5 MW (2020-08 to 2022-02) then **dropped to 0.0 MW** from 2022-03 onward — highly anomalous
- Milestones: Screening started 2020-08-21, Screening complete 2020-10-16, FIS requested 2020-08-17
- **FIS never approved, IA never signed, no construction milestones, no 6.9 milestones**
- Project has been in queue 6 years with zero progress past screening — RED FLAG

## T2 start
- gmaps.py: HTTP 429 on both attempts (rate-limited) — no pins found
- 0 pins logged

## T3 start
- DDG: CAPTCHA blocked both queries
- Bing: "Cachena Storage SLF", "Cachena+Wilson County", "Cachena Storage ERCOT" — all returned unrelated results, no hits
- No news, no developer name, no LLC registration found
- news_found: false

## T4 start
- PUCT interchange.puc.texas.gov: FilingParty="Cachena Storage" → 0 results
- PUCT description contains "Cachena" → 0 results
- No IA found; ia_found: false

## T5 start
- Ch.313 agreement-docs.php: no "Cachena" or "Wilson County" storage hits (Ch.313 expired 2022 anyway)
- JETI: program explicitly excludes "energy storage facilities" — ineligible by statute
- abatement_found: false

## T6 start
- Site candidate: no pin, no IA/abatement map. POI is "Tap 345KV Elmcreek-Old Hickory" in Wilson County.
  Best guess: Floresville area (29.13N, 98.16W) — county seat on the 345kV corridor.
- cdse.py 3×3 grid (lat 29.09–29.15, lon 98.13–98.19): ALL 401/403 — CDSE creds invalid/expired
- Imagery: no chips obtained; construction_visible: false (blocked, not negative observation)

## T7 start
- triage_findings.json written
- triage.md written
- deep_scan_recommended: false
- Turns used: ~22
- STOP

---

## Note — 2026-07-21 (companion-project retraction pointer, light touch)

This project never went to deep scan and its own T6 site guess (29.13,-98.16,
Floresville county-seat centroid, low confidence) does NOT reference the
misattribution found in the companion project. Flagging anyway since 23INR0077 shares
the same POI/SPV as **23INR0027 Cachena Solar SLF** (same tap, same interconnecting
entity Clear Fork Creek Solar LLC / Enbridge): that companion project's site was
re-derived 2026-07-21 (retracting a wrong footprint that belonged to a different,
unrelated project, Hoke Solar 23INR0231) to **29.2579,-97.8057** via a TCEQ
stormwater-NOI address, geocoded independently by two services (Esri ArcGIS + Google
Places, agree to ~0.5 mi) — see `research/23INR0027_cachena-solar-slf/findings.json`
`site`/`retraction`. If/when this project goes to deep scan, use that point (not the
29.13,-98.16 county-centroid guess above) as the starting site anchor. No imagery
exists for this project (triage-only; CDSE was blocked 401/403 at the time), so there
is nothing to delete or re-fetch here.
