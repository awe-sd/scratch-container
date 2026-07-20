# Triage log — Juno 3 Solar (26INR0621)

## T1 start
- 16 snapshots: 2025-03-01 → 2026-06-01
- COD drift: 0 (2027-11-30 held entire history)
- Milestones: Screening started 2025-03-24, Screening complete 2025-06-09, FIS requested 2025-03-18, IA signed 2025-07-01
- FIS approved: NOT YET. No construction milestones.
- Notable: IA signed without FIS approved — unusual but possible per CLAUDE.md.

## T2 start
- gmaps.py places: 429 Too Many Requests on initial call + 1 retry → BLOCKED, no pins found
- pins_found: 0

## T3 start
- Bing: "Juno 3 Solar" Texas → no results (film/NASA/ISP noise only)
- Bing: "Juno 3 Solar LLC" OR 26INR0621 → no results
- Bing: "Juno Solar" Borden County developer → no results
- DDG: 403 blocked
- news_found: false; no developer name surfaced; no LLC confirmation

## T4 start
- No puct_ia_search.py script exists; used WebFetch directly
- PUCT Interchange https://interchange.puc.texas.gov/search/filings/ → 402 on first attempt + retry → BLOCKED
- ia_found: false (portal inaccessible, not confirmed absence)
- NOTE: IA signed date 2025-07-01 per queue data — IA likely exists but couldn't retrieve PDF

## T5 start
- TX Comptroller Ch.313 agreements page → navigation/overview only, no tabular search
- JETI (HB 5) registry page → no dedicated JETI search tool listed, no Borden County data
- abatement_found: false — consistent with post-2022 project (Ch.313 expired 2023); JETI portal not searchable via WebFetch
- Normal finding for a 2026-queue project

## T6 start
- Searched for Buck Canyon 345kV substation coords via Bing + OSM → not found
- No pin (T2 blocked), no abatement map (T5 none), no POI coords
- Site candidate: none better than "somewhere in Borden County" → SKIP imagery per rules
- construction_visible: false (no imagery taken)

## T7 start
- triage_findings.json written
- triage.md written
- turns used: ~19
- DONE

## Deep scan start (2026-07-19)

### D1 — Financial security / milestone correction
- CRITICAL: financialSecurityAndNoticeToProceedProvided = "Yes" in parquet (missed in triage)
- This means: IA signed 2025-07-01 + financial security posted + NTP issued — far more committed than triage suggested
- ginrStudyPhase = "SS Completed, FIS Started, IA" (not the more advanced IA-complete, but NTP is provided)

### D2 — Juno Solar operating plant found (OSM)
- Existing Juno Solar I+II (300 MW combined, operator=SE Juno LLC) found at OSM relation 14474033
- Bounding box: 32.7653–32.7922°N, 101.5978–101.6520°W
- Center: ~32.779°N, 101.625°W
- Start date: 2021-06; plant output 300 MW; EIA ref 63328
- Source: OpenStreetMap overpass query (negative: no separate Juno 3 polygon found yet)
- WHY IT MATTERS: Juno 3 is a follow-on 500 MW project at the same site — developer (SE Juno, LLC / Intersect Power) has track record in Borden County

### D3 — Developer identification (Juno Series history)
- 21INR0026 = Juno Solar Phase I (166 MW, approved commercial op 2021-05-26, facility=SE Juno, LLC)
- 21INR0501 = Juno Solar Phase II (147 MW, approved commercial op 2021-08-09, facility=SE Juno, LLC)
- 21INR0032 = Juno Storage (cancelled 2019)
- 23INR0616 = JUNO SOLAR 3 (9.99 MW, inactivated 2023-05-15 — likely small interconnection placeholder)
- 24INR0457 = JUNO BESS (cancelled 2023-08)
- 26INR0621 = Juno 3 Solar (500 MW, current project, facility=Juno Solar 3)
- Developer chain: SE Juno, LLC → likely Intersect Power (SE = Standard Energy / Intersect brand); need to confirm

### D4 — Buck Canyon 345kV not in OSM
- #59916 Buck Canyon 345kV: not in OpenStreetMap substations database
- This is a new/planned substation to be built for these projects (Juno 3 + Antila Solar 27INR0500 also at same POI)
- ERCOT POI #59916 is a future interconnection point, not yet built; location inferred as near Borden County (consistent with existing Juno site)

### D5 — Co-located projects at Buck Canyon
- 27INR0500 Antila Solar (500 MW, Borden, IA signed 2025-08-13, finSec=Yes, COD 2027-11-30) — at same POI
- 29INR0131 Caesar Solar (181.6 MW), 29INR0132 Caesar Storage (205.5 MW) — later queue projects at same POI

### D6 — PUCT Interchange still 402 blocked; TX SOS requires fee ($1/search); SEC EDGAR 403
- No IA PDF retrieved; no LLC parent chain confirmed beyond "SE Juno, LLC" from queue data
- Negative evidence logged

### D7 — Site candidate established
- Juno 3 is at the same Borden County location as operating Juno Solar I+II
- Site center anchor: 32.779°N, 101.625°W (from OSM operating plant)
- 500 MW project will likely expand north/south of existing footprint
- PROCEEDING TO IMAGERY

### D8 — Satellite imagery results (2026-07-19)
- **2025-01-15**: Only Juno I+II operating plant visible. Lower section = undisturbed terrain. NO construction.
- **2025-10-15**: Same as Jan 2025. Still no new construction south of operating plant.
- **2025-12-15**: FIRST ACTIVITY VISIBLE — multiple rectangular sections of racking/modules installed south of operating plant. Substation yard (bright white) visible at lower left. Construction well underway.
- **2026-06** (present): Further progress — more module block sections installed. Substation construction area still active. Racking pattern consistent with bifacial tracker rows.
- Construction start window: between Oct 2025 and Dec 2025 (likely Nov 2025)
- Stage verdict: **racking** → approaching **substantially_complete** for southern sections
- Center for new project: approximately 32.749°N, 101.625°W (shifted south of operating plant)
- Substation (Buck Canyon 345kV?) at approximately 32.735°N, 101.635°W — under active construction in Jun 2026
- NOTE: ≤6 full-size reads used (s2_2025-12-15, s2_2026-06_south = 2 full reads from imagery set)

### D9 — Developer identity (SE Juno, LLC)
- Operating plant operator in queue data: "SE Juno, LLC" (21INR0026, 21INR0501)
- Juno 3 interconnectingFacility = "Juno Solar 3" (direct successor naming)
- TX SOS not accessible (requires $1 fee); CAD not accessible (dynamic portal)
- Negative: No press releases, SEC filings, or news articles confirming developer identity beyond queue data
- BEST INFERENCE: SE Juno LLC / same developer as Juno I+II; "SE" likely "Standard Energy" or related; Intersect Power was listed as facility for 21INR0032 (a different cancelled project) suggesting the two are separate entities

### D10 — Abatement/IA/land records
- Ch.313 expired 2022 — no JETI agreement found (small Borden County, JETI portal not searchable by WebFetch)
- No CAD parcel data retrieved (dynamic portal not accessible)
- IA signed 2025-07-01 per queue data, financial security + NTP provided
- PUCT Interchange still 402 — IA PDF not retrieved
- Project area: unknown from records (could not access CAD or IA exhibits)

## Deep scan complete (2026-07-19)
- findings.json written
- dossier.md written
- timeline.md regenerated (queue_history.py — 16 snapshots, 0 COD drifts)
- brief.html generated (build_brief.py — 4 images)
- index.json + INDEX.md refreshed (build_index.py — 22 projects)
- FINAL VERDICT: real_active | racking stage | 32.749°N 101.625°W | COD 2027-Q4 | drift risk med
