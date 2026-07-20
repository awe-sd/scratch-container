# Triage log — 28INR0156 Chimney Rock BESS

## T1 start
- 17 snapshots: 2025-02-01 → 2026-06-01
- COD: 2028-04-10, 0 drift events (held since first appearance)
- Screening started: 2025-02-14; Screening complete: 2025-05-12
- FIS requested: 2024-12-17 (pre-dates first snapshot)
- FIS approved: NOT achieved
- IA signed: NOT achieved
- No construction milestones
- T1 result: early-stage project, no IA yet

## T2 start
- gmaps.py: 429 Too Many Requests on all queries (retried once); 0 pins found
- T2 result: no delivery pins

## T3 start
- DDG blocked (403); used Bing HTML
- Search 1: "Chimney Rock BESS" battery storage Texas — no hits
- Search 2: "Chimney Rock BESS" ERCOT Taylor County — no hits
- Search 3: "Chimney Rock BESS LLC" Texas energy — no hits
- Search 4: 28INR0156 OR Chimney Rock battery Abilene Texas — no hits
- No developer name, no LLC registration, no news found
- T3 result: no web presence detected

## T4 start
- PUCT Interchange direct URL: 402 Payment Required (blocked)
- Bing search for PUCT + "Chimney Rock BESS": CAPTCHA blocked
- Bing search for PUCT + "Chimney Rock" interconnection agreement: no relevant results
- No IA found via any T4 path
- T4 result: IA not found; portal access blocked

## T5 start
- TX Comptroller Ch.313 page: no filterable list accessible via WebFetch
- JETI registry search via Bing: no Taylor County battery results
- Ch.313 expired 2022; project first appeared 2025 — abatement miss is expected
- T5 result: no abatement found (normal for post-2022 BESS)

## T6 start
- Site candidate: Merkel TX (~32.47°N, -100.02°W) inferred from "Butman Camp / Merkel, TX"
  reference found in T3 search — a community named Butman matching the tap node name (76318 BUTMAN)
- cdse.py chip: 401 Unauthorized on all 9 grid points; ~/.config/gis-research.env is placeholder only (no real creds)
- Imagery: BLOCKED — credentials not configured
- T6 result: no imagery acquired; site candidate is low-confidence inference only

## T7 start
- triage_findings.json written
- triage.md written
- T7 complete; turns used: 28
