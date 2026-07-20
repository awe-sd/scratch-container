# Triage log — Aldrin 138 BESS (25INR0421)

## T1 start
- `queue_history.py` ran OK — 38 snapshots, 2 COD changes
- Screening started 2023-05-15, screening complete 2023-08-11
- IA signed 2024-04-18 ✓
- FIS approved 2025-08-22 ✓ (late; IA came first — unusual)
- Meets 6.9(1) 2024-05-06
- Meets all 6.9: NOT achieved
- COD drift: 2025-07-15 → 2026-03-01 → 2027-07-01 (2 slips, ~24 months total drift)
- No construction start/end, no energization/synchronization/commercial operation milestones
- Result: project is IA-signed + FIS-approved, but NOT fully through 6.9, no construction in record

T2 start
- gmaps.py places: 429 Too Many Requests on attempt 1 (exact name) and retry (name+county)
- No pins found — BLOCKED, logged negative per rules

T3 start
- DDG search "Aldrin 138 BESS": aggregator hits only (interconnection.fyi, ercotqueue.com, infrasure.ai, cleanview.co, gridstatus.io)
- Developer name clarified: "Aldrin Energy Storage LLC" (not "Aldrin 138 BESS LLC")
- interconnection.fyi newsletter notes IA date shifted Feb 2024 → Apr 2024 (consistent with queue data)
- ercotqueue.com reports build-chance 86% (aggregator metric, not primary source)
- No original news/PR, no press releases, no Texas SoS registration hit
- DDG CAPTCHA blocked on developer name + developer+project queries (2nd/3rd queries blocked)
- No sources saved — all aggregator mirrors, not direct project pages
- Result: developer ID confirmed; no primary news/PR found

T4 start
- PUCT Interchange: 402 Payment Required on all endpoint attempts (FilingParty=Aldrin 138 BESS, FilingParty=Aldrin Energy Storage, root URL)
- BLOCKED — cannot access PUCT Interchange via WebFetch; portal requires session/auth
- IA existence confirmed via queue (signed 2024-04-18) but PDF not retrievable this pass
- Result: IA exists per queue data; PDF content/schedule unknown; no milestone schedule extracted

T5 start
- TX Comptroller Ch.313 page: no downloadable list accessible via WebFetch; no Brazoria/Aldrin hit
- JETI registry page: "Error Loading Page" — data not returned
- Result: no abatement found — normal for post-2022 battery project without JETI

T6 start
- Site candidate: POI = North Alvin TNMP 138kV; no pin, no abatement map; estimated ~29.44-29.47°N, 95.24°W (north of Alvin, TX)
- CDSE auth failures on 8/9 chip attempts (HTTP 401/403); 1 chip retrieved: 29.44,-95.24, 2026-07-01, 2km buffer
- Image read: suburban/semi-rural Alvin area; no BESS gravel pad or container rows visible; not confirmed at substation
- Construction verdict: NOT VISIBLE — image likely off-target; substation exact coords unknown
- No contact sheet generated (only 1 chip); used 1 full-size read

T7 start
- triage_findings.json written
- triage.md written
- turns used: ~28
- DONE

## Deep scan — 2026-07-19

### D1 Source review
- Aldrin site home: "550 MW BESS, less than 12 acres, directly next to an electrical substation, major electrical corridor, Brazoria County" — key: <12 acres, adjacent to substation
- Aldrin site footer: "© 2025 Vesper Energy" — developer confirmed Vesper Energy
- Aldrin mailing address: 1722 Routh Street Suite 900 Dallas TX 75201 (Vesper Energy address)
- TX Comptroller (aldrinenergystorage-com_home.html): Aldrin Energy Storage LLC, ACTIVE, DE formation 2022-12-19, Co-CEO Juan Suarez (Albuquerque NM = Vesper HQ), registered agent CSC-Lawyers
- Vesper Energy about page: Founded as Lendlease Energy Development (2015) → Magnetar Capital acquired 2020 → rebrand Vesper Energy → GCM Grosvenor joined 2023 equity; Co-CEOs Juan Suarez + Mark Rostafin

### D2 Substation coords resolved
- Overpass API confirmed: North Alvin Substation at 29.45902, -95.25754 (TNMP 138kV, OSM way 174401064)
- This is the confirmed POI — site is "directly next to" this substation per developer website
- Previous triage chip at 29.44,-95.24 was ~2km off — explains no BESS visible
- New imagery search required at 29.45902,-95.25754

### D3 Owner/developer chain
- Aldrin Energy Storage LLC → Vesper Energy (Juan Suarez = Co-CEO of both) → Magnetar Capital (majority, acquired 2020) + GCM Grosvenor (equity, 2023)
- Note: Website says "550 MW" but queue shows 207 MW — either a different Aldrin project or website is for the broader portfolio/earlier version

### D4 gmaps still 429; PUCT Interchange still 402 — negative logged

### D5 Imagery analysis
- 500m chip at 29.4590,-95.2575 (2026-07-01): North Alvin substation clearly visible — white rectangular transmission facility near image center. Adjacent land shows some cleared/disturbed area to the west/southwest. NO parallel container rows, NO gravel pad with equipment characteristic of operating BESS. Ground around substation appears partially cleared but not yet developed as BESS.
- 2km chip (2026-07-01): full context — semi-rural setting, Highway 35 corridor. No distinguishable BESS activity.
- 2km chip (2025-11-01): similar to 2026-07-01 frame — no activity change visible.
- Verdict: **no_activity** or **pre-construction** at 2026-07-01. No BESS containers, no gravel pad. Substation is confirmed at OSM coords. Site footprint (<12 acres per developer site) would be ~200m x 250m — visible if containers were installed but none seen.
- CDSE rate-limited for large (4-6km) and historical chips; baseline comparison unavailable. 4 full-size reads used of 6 cap.

### D6 Other negative searches
- PUCT Interchange API/site: requires JS rendering; curl gets HTML shell only — cannot retrieve IA PDF; docket number not identified
- Brazoria County CAD portal: requires JS; owner-name search for "Aldrin" returned no accessible results
- Brazoria County commissioners court: access denied (403)
- Google Places, Maps Static API: gmaps.py 429/403 — no pins found
- Vesper Energy projects page: does not list Aldrin specifically (shows 5 highlighted projects of 16 GW pipeline)
- Developer site FAQ/contact/benefits: no exact site address disclosed (only "directly next to an electrical substation, Brazoria County")
- TX SoS registration: entity confirmed through Comptroller (file no. 0804862187, eff. 2022-12-19)
- Note: Developer website says "550 MW" vs queue 207 MW — website appears to describe an earlier/larger planned scope; current INR is for 207 MW phase
