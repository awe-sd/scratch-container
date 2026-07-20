# 24INR0570 Marcus Energy Storage — Triage Log

T1 start
queue_history.py: 33 snapshots (2023-10-01 → 2026-06-01), 2 COD changes.
COD drift: 2025-09-01 → 2026-09-01 → 2027-09-01 (slipped 2 years total, ~12 mo each slip).
Milestones: Screening started 2023-06-07, Screening complete 2023-09-01, FIS requested 2023-10-24, FIS approved 2024-09-30.
IA signed: NOT achieved. No construction dates, no energization approvals.
T1 end — project is post-FIS, pre-IA. No construction milestone data.

T2 start
gmaps.py returned HTTP 429 (rate-limited) on both calls — one retry attempted, both blocked.
T2 end — no pins found (tool blocked, not evidence of absence). 0 pins.

T3 start
ercotqueue.com: 1 active project, 0 commissioned, 0 dropped; build probability rated 5%; "No IA".
TX SOS: Marcus Energy Storage LLC formed 2023-08-09, file #0805204410, "In Existence", Dallas TX address.
Cortera address: 321 E Main St, Charlottesville VA 22902 → matches Hexagon Energy (Suite 500) and Blue Creek Energy Storage LLC.
Likely developer parent: Hexagon Energy (Charlottesville VA clean energy developer). No press release for this specific project found.
T3 end — developer identity: Hexagon Energy likely parent; no news/PR specific to Marcus project.

T4 start
PUCT Interchange portal returned HTTP 402 on all attempts (filing search + main page) — portal blocked in this environment. No IA PDF retrievable.
T4 end — IA status unknown from PUCT. Queue data confirms IA not yet signed as of 2026-06-01. No IA document recovered.

T5 start
TX Comptroller Ch.313 page: no direct search available via WebFetch; no specific Marcus/Hexagon result found.
JETI/DDG search: no Chapter 313 or JETI record for Marcus Energy Storage or Hexagon Energy in Brazoria County.
Note: Ch.313 expired 2022-12-31; post-2022 projects (this entered 2023) would need JETI. No JETI record found — normal for early-stage projects.
T5 end — no abatement found (expected for 2023 entry, pre-IA project).

T6 start
Site candidate: Sweeny Co-Gen LP / West Columbia 138kV POI area — lat 29.0728, lon -95.7450 (from POI description + web search).
3×3 chip grid attempted at ±0.03° step, 2-km buffer, 2026-06-01. First chip (29.0428/-95.775) succeeded; 8 of 9 returned HTTP 403 (CDSE token expired mid-run). 403 treated as blocked after one success; did not re-engineer.
Contact sheet: 1/9 chips. Visible: agricultural/forested land, rural road — no gravel pad, no battery container rows, no substation expansion visible. Chip covers SW-offset tile, NOT the POI center.
Construction visible: NO (insufficient coverage; center tile not retrieved).
T6 end — imagery inconclusive; CDSE token blocked 8/9 chips. Site candidate established from POI but imagery coverage inadequate for conclusion.

T7 start
triage_findings.json written. triage.md written.
Turns used: ~28. Deep scan NOT recommended.
T7 end.
