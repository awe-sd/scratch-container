# Triage log — Corralitos Wind 4 (28INR0340)

## T1 start
queue_history.py ran: 12 snapshots, 2025-07-01 → 2026-06-01.
COD drift: 0 changes — 2028-05-31 held since first appearance.
Milestones: Screening started 2025-06-13, Screening complete 2025-09-11, FIS requested 2025-06-24.
FIS approved: — ; IA signed: — ; all 6.9: — ; construction: —
Very early-stage: screening done, FIS pending approval, no IA.

## T2 start
gmaps.py places "Corralitos Wind 4" → 429 Too Many Requests. One retry with alternate query → 429 again. Budget exhausted.
No delivery pins found (API rate-limited, not a negative signal on project existence).

## T3 start
Developer: Las Crestas Wind Energy, LLC (Delaware/TX Foreign LLC, registered 2023-05-03).
Sibling: Corralitos Wind 3 (28INR0339) 196.1 MW, same county/developer.
ercotqueue.com: build-chance 5%, "No IA". One source mentions PUCT Doc 35077_2172 (ETT IA) — may be Wind 3 not Wind 4.
No news, no PPA, no construction articles found.
Saved: sources/t3_web_sweep.md

## T4 start
PUCT Interchange portal → 402 on all direct URL attempts (session-auth required).
DDG search for PUCT docket "Corralitos Wind 4" / "28INR0340" / "Las Crestas Wind" → no direct interchange results found.
T3 hint (Doc 35077_2172 ETT IA) unverifiable — PUCT blocked; may be Wind 3, not Wind 4.
Queue data confirms IA signed = blank → no IA on record. Negative finding.

## T5 start
Ch.313 portal: no direct county/applicant search available; program expired 2022.
JETI DDG search → bot-verification block; no results retrieved.
Normal for 2025-filed project with no IA — no abatement expected yet.
No abatement found.

## T6 start
Site candidate search: ETT Tiempo #80224 / Cenizo / Del Sol substations — no coordinates found via web (bot challenges, no result). No pin from T2, no abatement map, no IA map.
Best candidate: "somewhere in Zapata County" — county only, too coarse for 3×3 chip grid.
SKIP imagery per checklist rule ("no site candidate better than county → skip").
construction_visible: false (not assessed).

## T7 start
Wrote triage_findings.json and triage.md. Turns used: 22. STOP.
