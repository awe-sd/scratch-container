# Triage log — Santa Garcias Solar (26INR0143)

## T1 start
- Queue history: 37 snapshots (2023-06-01 → 2026-06-01)
- Milestones: Screening started 2023-06-28, Screening complete 2023-09-22, FIS requested 2023-06-07
- IA signed: 2025-12-31 (appeared in Jan 2026 snapshot)
- FIS approved: NOT achieved
- Construction start/end: NOT achieved
- COD drift: 3 CODs reported
  1. 2026-05-31 held 2023-06 → 2024-11 (18 months, then slipped)
  2. 2029-02-01 held 2024-12 → 2025-06 (slipped back again)
  3. 2028-05-30 held 2025-07 → 2026-06 (current)
- COD drift count: 2 changes (original → 2029 → 2028); significant slip from original optimistic 2026 target
- IA signed end of 2025 is a positive signal; FIS not yet approved is a gap

## T2 start
- gmaps.py: HTTP 429 Too Many Requests on all 3 queries (rate-limited). One retry attempted, still blocked.
- Pins found: 0 (API blocked, not a project signal)

## T3 start
- "Santa Garcias Solar" Texas: no results (DDG bot wall, Bing returned holiday/Santa Claus noise)
- "Santa Garcias Solar LLC" Kleberg: no results
- "Santa Garcias" solar energy Kleberg: no results
- SEC site search: CAPTCHA blocked
- No web presence found; no developer name, no news, no press releases
- news_found: false

## T4 start
- PUCT Interchange direct URL: HTTP 402 (requires authenticated session, not accessible via WebFetch)
- Bing search for "Santa Garcias Solar" + PUCT/interconnection: no results
- Bing search for "26INR0143" + interconnection: no results
- IA signed date exists in queue (2025-12-31) but PDF not retrievable during triage
- ia_found: false (from web; queue confirms IA signed date exists — treat as ia_known_unsigned_pdf)

## T5 start
- TX Comptroller Ch.313 page: navigation/index only, no searchable data returned
- JETI registry search: no results for Santa Garcias Solar or Kleberg County solar projects
- abatement_found: false
- Note: Ch.313 expired 2022; post-2022 project so absence is normal; JETI not found is also normal at early stage

## T6 start
- No pin from T2 (API blocked)
- No IA PDF to extract map from
- No abatement application with site map
- POI: "Tap 138kV 8515 Alazan - 8458 Barney Davis" — Barney Davis is known NRG facility in Corpus Christi (Nueces Co.); Alazan substation not geolocatable from web searches; project in Kleberg County (south of Nueces); tap point location unknown
- Site estimate = "somewhere in Kleberg County" — per checklist, SKIP imagery
- site_candidate: null (no confirmed coordinate)
- construction_visible: false (no imagery run)

## T7 start
- triage_findings.json written
- triage.md written (8 lines)
- Turns used: ~22
- STOP

## D1 — Deep scan start (2026-07-19)

### Stage 1 — LLC / parent chain

- TX Comptroller taxable entity API (data.texas.gov resource 9cir-efmm): searched "Santa Garcias Solar" → 0 results. **No franchise tax record found.** 2026 entry, LLC may not yet have paid; absence is inconclusive but notable.
- OpenCorporates API (us_tx): "Santa Garcias Solar" → 0 results. Not yet indexed or not registered under this exact name.
- TX SOS direct search: SOSDirect requires authenticated/paid session — not accessible.
- Web searches (DDG, Bing, Google): zero press releases, zero news, zero developer attribution for "Santa Garcias Solar." Project is dark.
- PUCT Interchange: returns HTTP 402 (requires authenticated session). IA exists (queue shows signed 2025-12-31) but PDF not retrievable via WebFetch.
- Developer: UNKNOWN. No web presence found. Cannot establish parent chain from Stage 1 alone.

### Stage 2 — County records

- Kleberg CAD (klebergcad.org): searched "Santa Garcias" → **No results** (confirmed HTML response). LLC not yet recorded as property owner. Consistent with leased land or land not yet transferred.
- Kleberg CAD: searched "solar" → results page same as above (no hits visible; JS datatable may suppress).
- TX Comptroller Ch.313/JETI: No abatement found for Santa Garcias Solar or Kleberg County solar. Ch.313 expired 2022; JETI not yet found (normal for early-stage 2026 entry).
- Note: Project name likely refers to "Santa Garcias Ranch" — a large historic ranch in Kleberg/Jim Wells County area. This may help identify the landowner.

### Stage 3 — Site pinpoint

- GMaps API: still returning HTTP 429 (rate-limited). All place queries blocked.
- Overpass/Nominatim search for Alazan substation: **FOUND — AEP 138kV substation at lat=27.5599, lon=-97.5022, Kleberg County** (OSM way 487230433). Operator: American Electric Power. Voltage: 138kV. Tagged as "distribution" substation, 60Hz.
- POI: "Tap 138kV 8515 Alazan - 8458 Barney Davis" = tap on the 138kV line between Alazan substation and Barney Davis Power Plant (NRG, Corpus Christi, Nueces County). This line runs roughly NNW–SSE along the South Texas coast corridor.
- Nominatim also returned: "Alazan Field Gathering" industrial area at 27.4582, -97.5979 (same Kleberg County area, ~12km SW of the substation). This is a natural gas gathering facility — likely unrelated, but confirms industrial activity in the county.
- "Santa Garcias Creek" / "Santa Garcias Bay" searches returned no OSM nodes. The ranch name may refer to a private land grant.
- Site candidate: The project tap is on the 138kV line between Alazan sub (27.5599, -97.5022) and Barney Davis (27.835, -97.42). OSM confirms this 138kV line (AEP-operated) runs roughly east from Alazan toward Nueces County. Closest 138kV segment to Alazan: way 487230452 (lat 27.560, lon -97.502 to -97.313). Site is somewhere along this Kleberg County corridor.
- Note: "Santa Garcias" name points to historic South Texas ranchland. No GPS node for this specific community in OSM.

### Stage 4 — Satellite imagery

- Chip centered on Alazan Substation (POI anchor): 27.5599, -97.5022, 2026-07-01, 3km buffer
  → **Undisturbed green agricultural land. No grading, no solar construction visible.** Heavy cloud cover over ~30% of frame. This is the POI area, not necessarily the site centroid.
  → Result: no_activity at POI. Site footprint could be anywhere within ~10km of this tap.
- Note: 265 MW solar = ~1,200–1,800 acres. Site has NOT been pinpointed; imagery at substation is necessary but not sufficient to judge the site. Cannot confirm no_activity project-wide.
- Budget constraint: no additional chips run.

### Stage 5 — Wrap-up note

- Developer identity: UNKNOWN — zero web presence, zero TX comptroller hits, zero OpenCorporates hits, zero CAD hits.
- PUCT IA: exists (queue), but Interchange returns HTTP 402 for unauthenticated access; PDF not retrieved.
- Site: NOT PINPOINTED — POI anchor known (Alazan Sub, 27.5599, -97.5022), but no parcel, no pin, no abatement map to locate site footprint.
- Project signals: IA signed (1 signal); all others negative or unavailable.
