# Triage log — Fagus Solar Park 3 SLF (26INR0524)

## T1 start

queue_history.py → 25 snapshots (2024-06-01 → 2026-06-01), 2 COD changes.

COD drift: 2026-04-01 → 2026-09-30 → 2027-05-19 (slipped ~13 months total).
MW drift: 186.83 → 186.36 → 169.59 (trimmed ~17 MW, last change 2025-12).

Milestones achieved:
- Screening started: 2024-06-03
- Screening complete: 2018-07-06 (anomaly — predates INR entry; possible legacy/re-entry)
- FIS requested: 2024-05-30
- FIS approved: 2026-06-23 (very recent — just last month)
- IA signed: 2019-02-21 (anomaly — predates INR by 5 years; first appeared 2024-11-01 report)
- Meets 6.9(1): 2024-12-19
- Meets all 6.9: not achieved
- Construction start/end: not reported
- Approved for energization/sync/commercial operation: not achieved

Notable: IA signed date (2019-02-21) and screening complete (2018-07-06) predate the INR
by several years, suggesting this may be a re-entry or successor to an earlier project.
FIS approved only 2026-06-23 — very fresh; no construction milestones yet.

## T2 start

gmaps.py → HTTP 429 on first call, retry also 429. Tool rate-limited; no pins retrieved.
No delivery pins found (tool blocked, not necessarily absent).

## T3 start

DDG HTML: CAPTCHA on both queries — blocked.
Bing: "Fagus Solar Park 3" + Childress Texas → only botanical results (Fagus = beech genus), no solar project.
Bing: "Fagus Solar Park 3 SLF" LLC Texas → same, no hits.
Bing: "Fagus Solar" Texas developer → no hits.
Developer identity unknown; no news, PR, or registration found.
No sources/ pages saved.

## T4 start

PUCT Interchange /search (filingparty=fagus solar): HTTP 402 — session/auth required.
Retry (description=fagus solar): HTTP 402 again.
Portal blocked; no IA found via this route.
Note: IA signed date in queue (2019-02-21) is anomalous — may be a legacy project re-entry
with a pre-existing IA carried over, OR a data artifact.

## T5 start

TX Comptroller Ch.313: No dedicated searchable database accessible via WebFetch;
page links to Ch.380/381/312 only. Ch.313 program ended 2022; no Fagus Solar entry found.
JETI registry PDF (governor.texas.gov): SSL cert mismatch — blocked.
No abatement found. Normal for a 2024-entry project; Ch.313 expired.

## T6 start

Site candidate evaluation:
- T2 pins: none (tool blocked)
- T5 abatement map: none
- T4 IA map: none (portal blocked)
- POI: "60501 Tesla 345 kV" — attempted OSM Nominatim + Bing for substation coords; no results.
- No site candidate better than "somewhere in Childress County."
SKIP imagery per checklist rule. Logging: "no site candidate".

## T7 start

triage_findings.json written.
triage.md written.
Turns used: ~28. Deep scan recommended.
STOP.

## 2026-07-20 Deep scan started

### D0 — Skeleton written
- findings.json skeleton created; triage_findings.json + factsheet.json read

### D1 — IA discovery (puct.py match rung 0 — exact INR join)
- 3 confirmed IAs via INR join table:
  - 35077-1923: 5th Amended IA, filed 2024-09-06, CONFIRMED
  - 35077-2001: 6th Amended IA, filed 2024-12-04, CONFIRMED
  - 35077-2433: 7th Amended IA, filed 2026-03-17, CONFIRMED
- All downloaded to sources/

### D1 — Exhibit C (Interconnection Details) — DECISIVE
- Exhibit C (both 5th and 7th amendments): Fagus Substation ~8 miles SE of Childress, TX
- POI: ETT Tesla 345 kV line, terminates at first dead-end structure outside Fagus Substation fence
- 7th amendment Exhibit C confirms INR breakdown:
  - Phase 1: 50 units × 3.3729 MW = 168.64 MW (#20INR0091)
  - Phase 2: 50 units × 3.3729 MW = 168.64 MW (#25INR0672)
  - Phase 3: 42 units × 4.0948 MW = 171.98 MW (#26INR0524) — THIS project
  - Total: 509.26 MW at inverter terminals
- Inverter: Sungrow SG4400UD-MV (645 Vac) — Phase 3

### D1 — Developer CONFIRMED: Greenalia
- Exhibit D: notices@greenalia.us; vgonzalez@greenalia.es
- Greenalia = Spanish renewable energy developer

### D1 — Time Schedule
- Original IA execution date = 2019-02-21 (queue iaSigned date)
- 5th amendment Phase 3 COD: 84 months from Original = 2026-02 (was 2026-04-01 in queue — consistent)
- 7th amendment Phase 3 COD: 99 months from Original = 2027-05-21 (queue says 2027-05-19 — exact match confirms calc)
- Phase 3 Trial Operation (7th amendment): 97 months from Original = 2027-03-21

### D1 — Security
- 7th amendment Exhibit E: $19,500,000 security posted for TIF construction

### D1 — EIA data (factsheet)
- EIA-860M Operating: "Fagus Solar Park" 331.6 MW OPERATING at 34.35099, -100.0493 (= Phases 1+2)
- EIA-860M Planned: "Greenalia Solar Power Misae III" 169.6 MW planned 2027-05 at 34.20349, -100.0404 (= Phase 3 / this INR)

### SPV
- spv.py resolved: Greenalia entity: "Greenlia Solar Power Misae III, LLC" (EIA-860M planned) — likely typo for Greenalia
- Entity name in IA exhibits: Greenalia (email domain greenalia.us / greenalia.es)


### D3 — Gap-fill
- ch313.py resolve: NEGATIVE — no Ch.313/JETI match for Fagus Solar Park 3 SLF; Ch.313 1613 exists for Excel Advantage (Phases 1+2 predecessor), 2021
- search "Greenalia Fagus Solar Childress": GEM wiki + renewablesinfo (banned) only
- search "Misae III construction": GEM wiki confirms pre-construction; Misae II $388M financing closed ~2025
- Childress County 30-day notice (Ch.312): downloaded and imaged — confirms Greenalia Solar Power MISAE III LLC, 197 MWAC, $221.4M, Sep 2024 hearing
- Comptroller Ch.313 cert 1613: Excel Advantage Services LLC (Phases 1+2), 2021 — NEGATIVE for Phase 3
- Google Places "Greenalia Childress Texas solar": MISAE SOLAR PROJECT, 385 FM1033, Childress TX — DECISIVE site pin
- CDSE imagery: ALL FAILED with RemoteDisconnected (service outage) on 2026-07-20
- gmaps.py staticmap: FAILED (Maps Static API not enabled on key)

### D1 — 6th amendment key detail
- Notice table (6th amend Exhibit D): Greenalia Solar Power Misae III LLC c/o Excel Advantage Services LLC dba Misae Solar Park II [DIA]; US Controller, Greenalia; Helmsley Building 230 Park Ave Suite 2840 NYC NY 10169; Santander Bank

### D5 — Wrap-up tools
- queue_history.py: 25 snapshots, 2 COD changes; written to timeline.json + timeline.md
- eia_history.py --write: matched EIA plant 67123 (full Fagus Solar Park operating entity); EIA shows OP Dec 2025 (= Phases 1+2); Misae III planned entity not yet in monthly 860M with COD history; written to eia_history.json
- dossier.md: written
- findings.json: final update


## Imagery pass (user-flagged, 2026-07-21)

User flagged this project as missing research -- actually missing only imagery (ran
during the CDSE outage). AWS chips fetched at the campus pin (4 dates 2024-2026) plus
one at Phase 3's own EIA planned point:
- Campus frames show major array construction 2025->2026 -- attributed to PHASES 1+2
  (EIA plant 67123: UC-2024 -> >50%-2025 -> OPERATING 2025-12), NOT this INR. Explicit
  neighbor-array caution added to findings so the panels are never miscited as Phase 3.
- Phase 3's EIA planned point (34.20349,-100.0404, 16 km south): undeveloped
  rangeland/breaks, no grading (2026-07-10, 0% cloud). Verdict stays no_activity,
  now imagery-supported at both candidate anchors.
- Site confidence split: campus/POI high; Phase-3 parcel medium (no parcel map exists
  in any filing yet -- the Ch.312 notice map is the whole reinvestment zone).
