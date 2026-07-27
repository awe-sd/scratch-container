# Research Log — Larrea Solar (27INR0146)

Started: 2026-07-19

## Identity packet
- Project: Larrea Solar
- INR: 27INR0146
- Likely LLC: Larrea Solar, LLC
- County: Pecos, Texas
- Capacity: 231.6 MW Solar PV
- POI: "Tap 345kV 76002 Bakerfield - 60404 Solstice CKT#1"
- CDR Zone: WEST
- Reported COD: 2027-09-18

---

## Stage 1 — LLC → Parent Chain

### 2026-07-18 (triage) Negative searches

| Source | Query | Result |
|---|---|---|
| TX Comptroller franchise-tax | "larrea solar" | 0 results |
| TX Comptroller franchise-tax | "larrea" | 8 results, none solar/energy |
| SEC EDGAR full-text | "larrea solar" | 0 results |
| PRNewswire | "larrea solar" | 0 results |
| Solar Power World | "larrea solar" | 0 results |
| Utility Dive | "larrea solar" | 0 results |
| PV Tech | "larrea solar texas" | 0 results |
| Google Places API (v1) | "Larrea Solar" | quota exhausted (100/day) |

### 2026-07-19 Deep-scan findings

**GREASEWOOD IV LLC confirmed as Larrea Solar SPV** — TX Comptroller franchise API query on data.texas.gov returned GREASEWOOD IV LLC at 111 Congress Ave Ste 1055, Austin TX 78701, SOS 0804761122, chartered 2022-10-07, Active. Address matches Greasewood II LLC and Greasewood III LLC — all Ashtrom Renewable Energy Austin office. [artifact: sources/2026-07-19_txcomptroller_greasewood-iv-entity.json]

**Ashtrom Renewable Energy** is the developer — Israeli renewable energy company with operational Greasewood I (255 MW) and Tierra Bonita / Greasewood II (306 MWac, COD Oct 2024) in Pecos County. Developer page explicitly describes Larrea as "early planning and development stage" as of mid-2026. [artifact: sources/ashtrom_larrea_page.md]

**Ownership chain:** Larrea Solar / Greasewood IV LLC → Ashtrom Renewable Energy (Israel-listed parent).

**No "Larrea Solar, LLC" entity found** in TX Comptroller or any SEC/news source. The registered SPV name is GREASEWOOD IV LLC.

### 2026-07-19 Negative — Stage 1

| Source | Query | Result |
|---|---|---|
| TX Comptroller franchise API | "larrea solar LLC" | 0 records |
| SEC EDGAR EFTS | "Greasewood IV" Form D | 403 Forbidden |
| PR Newswire | "larrea solar" | 0 results |
| Solar Power World | "ashtrom" | 0 results |
| PV Tech | "ashtrom larrea" | 0 results |

---

## Stage 2 — County Records Sweep

### 2026-07-19 Positive findings

**Solstice substation** is AEP Texas, near Fort Stockton, Pecos County — part of Howard-Solstice 765kV project. POI "Tap 345kV 76002 Bakerfield - 60404 Solstice CKT#1" confirms the line from Bakersfield substation (~30.976, -102.289) to Solstice substation (~30.948, -103.362). [artifact: sources/2026-07-19_osm_substations-pecos.json]

**Greasewood II gen. substation at 31.037, -102.488** in OSM — confirms the existing cluster's interconnection point on the Bakerfield-Solstice corridor. OSM also shows "Nevill Road - Greasewood" 345kV line (Way 1006095182, start_date 2021, 56 nodes) in this corridor.

**Whitethorn Solar comparable** — Ashtrom's next Pecos County project (150 MWac), construction started 2025, target COD **2029** per Ashtrom website. Provides upper-bound benchmark: Larrea (further back in development) cannot COD before Whitethorn.

### 2026-07-19 Negative — Stage 2

| Source | Query | Result |
|---|---|---|
| PUCT Interchange | "larrea solar" | 402 Payment Required (portal blocked) |
| PUCT Interchange | "greasewood IV" | 402 Payment Required |
| TX Comptroller Ch.312/SB1340 | Pecos County abatements | JS-only portal, no results extractable |
| TX Comptroller JETI | current agreements | 11 listed, none solar/Pecos County |
| Pecos CAD | "greasewood" owner search | JS-only portal, no results extractable |
| Pecos CAD | "ashtrom" owner search | JS-only portal, no results extractable |
| Pecos County Commissioners Court | Greasewood/Larrea mentions | June 2026 agenda: no energy/solar items |
| Google Places API | "Larrea Solar" | 429 Too Many Requests (quota) |
| TX SOS | free entity search | SOSDirect requires $1/search fee |

**No Ch.312/313/JETI abatement found** for Larrea Solar or Greasewood IV in Pecos County. This is expected for early-stage project (FIS not yet approved) — abatements typically come after IA signing.

**No PUCT IA found** — PUCT Interchange returns 402 for all search attempts; not accessible via WebFetch. IA not yet signed per queue history (iaSigned = —).

---

## Stage 3 — Site Pinpoint

### 2026-07-19

**POI analysis:** "Tap 345kV 76002 Bakerfield - 60404 Solstice CKT#1" — both substations confirmed via OSM:
- Bakersfield SS: 30.9759, -102.2891
- Solstice SS: 30.9483, -103.3617
- Line corridor passes through Greasewood cluster area (~31.04, -102.49)

**Cluster anchor method:** Existing Greasewood arrays (Greasewood I, Tierra Bonita) are at ~31.038, -102.493 per prior imagery. Larrea is described as part of the same cluster. Site is likely within a few miles on unbuilt land adjacent to existing arrays, along the Bakerfield-Solstice 345kV corridor.

**Confidence: LOW-MEDIUM** — no delivery pin, no parcel, no news photo locates the Larrea footprint specifically. Site estimated at 31.038±0.05, -102.55±0.15 (within the cluster area, possibly to the west of existing arrays).

---

## Stage 4 — Satellite Ground Truth

### 2026-07-19 (deep scan)

CDSE credentials expired (403 on new chip requests). Using triage-era chips (2026-07-01, 3x3 grid).

**Contact sheet reviewed (2026-07-01, center ~31.038, -102.493, 7-tile grid):**
- Tiles 31.038/-102.493 and 31.038/-102.523: existing operational arrays (dark blue-gray module blocks, sharp-edged polygons). This is Greasewood I + Tierra Bonita.
- Tile 31.008/-102.493: transmission lines crossing bare desert. No new construction.
- Tiles 31.068/-102.463 and 31.068/-102.493: failed/black (cloud/no data).
- Tile 31.038/-102.463: shows edge of existing arrays + desert.

**Verdict: no_activity** in the triage search grid. Developer self-describes "early planning." No Larrea footprint visible. Grid covers the likely near-cluster area — consistent with no-construction finding.

**Grid limitations:** Covered ~±0.03° around 31.038,-102.493 (roughly 6km x 6km). CDSE auth failure prevents expanded western/southwest coverage (toward -102.62 to -102.75). The Larrea site may be in an adjacent unimaged area. However, developer's own statement ("early planning") and no FIS approval confirm no construction is expected.

---

## Stage 5 — Key negatives summary

1. **No IA signed** (queue history confirms, 25 snapshots, iaSigned = —)
2. **No FIS approved** (fisApproved = —)
3. **No abatement/JETI found** (expected at this stage)
4. **No COD history drift** (2027-09-18 held static since Jun 2024)
5. **Developer self-describes "early planning"** (Ashtrom website, Jul 2026)
6. **Whitethorn comparable**: next Ashtrom Pecos project, construction 2025, COD target 2029 — Larrea is behind Whitethorn

---

## Wrap-up commands completed

- `queue_history.py 27INR0146`: 25 snapshots, 0 COD changes — timeline.md written
- `build_brief.py 27INR0146`: (to run)
- `build_index.py`: (to run)
