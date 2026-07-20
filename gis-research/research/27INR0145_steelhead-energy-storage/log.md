# Research log — Steelhead Energy Storage (27INR0145)

## T1 start
**queue_history.py output:** 30 snapshots (2024-01-01 → 2026-06-01), 1 COD change.

**Milestones achieved:**
- Screening started: 2024-02-07
- Screening complete: 2024-04-29
- FIS requested: 2024-01-04
- FIS approved: NOT achieved
- IA signed: NOT achieved
- All Section 6.9: NOT achieved
- Construction start/end: NOT achieved

**COD drift (1 event):** 2027-07-15 → 2027-09-30 (shift in May 2024). Held stable since.

**Capacity:** 193.66 MW (Jan–Jun 2024) → 192.1 MW (Jul 2024–present). Minor trim.

**Assessment:** Early-stage project. FIS not approved, no IA. Queue-status signal is weak — paper project until FIS/IA materialize.

## T2 start
gmaps.py 429 (rate-limit) on both attempts ("Steelhead Energy Storage", "Steelhead Energy Storage Fannin County Texas"). One retry per rules. **No pins found — blocked.**

## T3 start
DDG search (3 queries). **Key finding: LLC is GRS BESS TEXAS SEVEN, LLC** (not "Steelhead Energy Storage, LLC"). Parent developer: GRS (grs.energy), running a numbered BESS series (Seven, Eight, Ten...) all entered queue early 2024. No press releases found. No construction news. EIA ID 67798 listed as "planning."
Source saved: sources/T3_web_sweep.md

## T4 start
PUCT Interchange returned HTTP 402 on all endpoints (interchange.puc.texas.gov). Session-cookie gated — cannot access without authenticated browser session. **No IA found — portal blocked.**

## T5 start
TX Comptroller Ch.313 page not parseable via WebFetch (no inline data). JETI DDG search: no Steelhead/GRS BESS result. Notably found a different BESS in Fannin Co. (Platinum Energy Storage / Engie, near Savoy — unrelated). Post-2022 project; no abatement expected — normal miss.

## T6 start
Site candidate: BONHAM_P8 substation ~33.582°N, 96.175°W (Bonham TX area, Fannin Co.). Ran 3×3 grid (--buffer-km 2, step ±0.03°) at 2026-06-15. 
- Parallel batch: 7/9 failed 401 (token collision), 2 succeeded (north row: 33.612,-96.145 and 33.612,-96.175).
- Sequential retry: 7/9 still 401. Per rules: one retry done, proceeding with 2 chips.
- Contact sheet read: agricultural fields (left tile) + suburban Bonham edge (right tile). No BESS construction signals (no gravel pad, container rows, substation expansion). Partial coverage — full 3×3 unavailable.
- **No construction visible. Confidence: low (only 2/9 tiles retrieved).**

## T7 start
Wrote triage_findings.json and triage.md. Turns used: ~22. STOP.
