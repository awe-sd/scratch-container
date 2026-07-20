# Triage log — Charolais Solar (21INR0380)

T1 start
- 75 snapshots (2020-04-01 → 2026-06-01)
- COD drift: 2022-12-15 → 2023-12-15 → 2025-12-15 → 2026-12-15 (3 changes, now 4 years delayed from original)
- Milestones: Screening started (2019-08-05), Screening complete (2019-10-31), FIS requested (2020-04-27)
- FIS approved = NEVER; IA signed = NEVER; no construction milestones at all
- Project has been in queue ~5 years with no FIS approval — significant development lag
T1 done

T2 start
- gmaps.py: 429 Too Many Requests on all 3 attempts (rate-limited); no pins obtained
- T2 result: 0 pins found (API blocked, not a project signal)
T2 done

T3 start
- Developer identified: RWE Solar Development, LLC
- LLC: Charolais Solar, LLC — incorporated 2021-09-28, Texas, active
- Investment entity: Charolais Solar Investments, LLC — Form D equity raise 2022-12-06, $8,573,410
- ercotqueue.com: 5% build probability (no IA)
- No press releases, no official RWE announcements found
- Saved to sources/web_sweep_t3.md
T3 done

T4 start
- PUCT Interchange: all URL attempts return HTTP 402 (session/cookie auth required) — portal blocked
- DDG search for IA/docket: CAPTCHA blocked
- No IA located; consistent with queue_history showing iaSigned = never
- T4 result: no IA found (portal blocked, negative finding, consistent with milestone data)
T4 done

T5 start
- TX Comptroller Ch.313: main list page not directly queryable via WebFetch; no Charolais Solar/RWE entries surfaced
- DDG search for Ch.313/JETI: no results found for Charolais Solar + Matagorda
- Post-2022 project with no IA — JETI miss is normal (Ch.313 sunset end-2022, JETI for newer projects)
- T5 result: no abatement found (normal for this vintage/status)
T5 done

T6 start
- Site candidate: POI "tap 345kV 44000 W A Parish - 5915 STP" — "STP" = South Texas Project nuclear plant area, Matagorda County (~28.794°N, 96.047°W); confidence LOW (POI inference only, no pin)
- No pin from gmaps (blocked), no IA map, no abatement map — using POI infrastructure inference
- cdse.py chips: HTTP 401 Unauthorized on all attempts — CDSE credentials not valid/loaded
- No imagery obtained; cannot assess construction activity
T6 done

T7 start
- Wrote triage_findings.json and triage.md
- Turns used: ~28
T7 done — STOP
