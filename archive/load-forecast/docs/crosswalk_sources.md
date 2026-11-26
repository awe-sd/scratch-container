# Crosswalk sources & decisions (built 2026-08-14)

## Sources

| Input | Source | Pulled | File |
|---|---|---|---|
| County population | Census PEP 2023 county estimates (`POPESTIMATE2023`), static file — https://www2.census.gov/programs-surveys/popest/datasets/2020-2023/counties/totals/co-est2023-alldata.csv | 2026-08-14 | `data/raw/crosswalk/co-est2023-alldata.csv` |
| County centroids | Census 2023 Gazetteer TX counties (INTPTLAT/INTPTLONG) — https://www2.census.gov/geo/docs/maps-data/data/gazetteer/2023_Gazetteer/2023_gaz_counties_48.txt | 2026-08-14 | `data/raw/crosswalk/2023_gaz_counties_48.txt` |
| County → weather zone | **User-provided** (sdalvi, 2026-08-14), built from the internal `ercotDataDictionary` SQL table — not a public download | 2026-08-14 | `data/raw/crosswalk/ercot_county_weatherzone.csv` |
| Station metadata | NOAA ISD history — https://www.ncei.noaa.gov/pub/data/noaa/isd-history.csv | 2026-08-14 | `data/raw/crosswalk/isd-history.csv` |

**Population-source deviation from CLAUDE.md's original "ACS 2023 5-yr B01003":** the
Census ACS API now requires an API key (302 → missing_key.html, confirmed
2026-08-14). Per sdalvi's ruling we use the keyless PEP 2023 estimates file —
same 2023 vintage, county totals within ~1-2% of ACS, weights materially
unchanged. sdalvi has requested an API key; switching back to ACS later is a
one-line change in `src/build_crosswalk.py` (`POP_URL`/`load_population`).
The vintage stays frozen either way (CLAUDE.md hard rule 2).

## Split-county resolutions (counties with multiple WZ rows → one zone)

| County | Zones in mapping | Assigned | Rationale |
|---|---|---|---|
| COLLIN | NORTH, NORTH_CENTRAL | NCENT | Plano/McKinney/Frisco — DFW metroplex |
| WILLIAMSON | NORTH_CENTRAL, SOUTH_CENTRAL | SCENT | Round Rock/Georgetown — Austin metro |
| GRAYSON | NORTH, NORTH_CENTRAL | NCENT | Sherman/Denison |
| TAYLOR | SOUTH_CENTRAL, WEST | WEST (→ excluded from SCENT) | Abilene is the population center, in the West zone |

## Ambiguous split counties (excluded, no override)

27 split counties have no override and are excluded from zone attribution.
Only one exceeds the 2% materiality threshold for an in-scope zone:

- **KAUFMAN (EAST / NORTH_CENTRAL): 2.0% of NCENT — needs a ruling.**
  Forney/Terrell are DFW exurbs, so NCENT inclusion is defensible. Currently
  excluded; NCENT coverage is 91.2% without it.

All others are small relative to their candidate zones (ARCHER, BURLESON,
COOKE, DELTA, FREESTONE, FRIO, HENDERSON, HUNT, JACK, KARNES, MEDINA, NAVARRO,
SHACKELFORD, YOUNG, …).

## Dropped non-county rows

CUIDAD ACUNA, MATAMORAS, MEXICO, NUEVEO LAREDO, OKLAHOMA, PIEDRAS NEGRAS,
PITTSBURG (a city in Camp County, not a TX county), REYNOSA.

## Result (data/derived/crosswalk_county_station.csv)

22 county rows; 21 distinct stations (COAST 6, NCENT 9, SCENT 6); per-zone
population coverage 91.2/91.2/91.3%; weights sum to 1.0 per zone; every
selected station's ISD record spans 2015→2025. Note: Dallas county's nearest
station is Love Field and Tarrant's is Meacham, so DFW airport itself is not
in the set — expected under nearest-to-centroid assignment.
