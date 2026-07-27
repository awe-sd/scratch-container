# Site Derivation — Moccasin Solar (26INR0269 / "Swenson Ranch Solar")

Stonewall County, TX · 603.59 MW solar PV · SPV **Swenson Solar LLC** (ENGIE; Meta PPA)
Site fix as of second-pass review **2026-07-21**.

---

## Bottom line: is there a filing that shows the project's parcel?

**No — no retrievable public filing delineates the project's land boundary.** The two
documents that normally *would* carry a metes-and-bounds boundary both exist but are not
publicly obtainable:

1. **ALTA survey of the property** — the signed Interconnection Agreement (IA) *names* an
   ALTA survey as a Generator→TSP deliverable, but the survey itself is **not attached** to
   the PUCT filing (see quote below). It is a private title document.
2. **County reinvestment-zone / PILOT (tax-abatement) instrument** — Stonewall County
   approved a ~10-year abatement / Payment-In-Lieu-of-Taxes deal for the project
   (KTXS, Apr 2025; Double Mountain Chronicle, "Commissioners Finalize Swenson Solar Deal").
   A reinvestment-zone ordinance typically carries a boundary description, but the primary
   instrument is **not retrievable**: the county commissioners-court minutes page returns
   HTTP 403, Stonewall has **no online CAD/appraisal portal**, and it is a **non-reporting
   county** absent from the Comptroller's Ch.312 registry.

**Therefore the visible construction footprint in the Sentinel-2 imagery is the best
available boundary evidence for this project.** Everything below is the chain that gets
from the one spatial statement in the public record (a text sentence in the IA) to the
coordinate on that footprint.

---

## Step 1 — The only spatial statement in any filing: IA Exhibit "C"

Both signed IA PDFs on disk carry the **identical, text-only** location statement — no map,
no plat, no coordinates. Exhibit "C" is titled *Interconnection Details*:

> **EXHIBIT "C" — INTERCONNECTION DETAILS**
> 1. Substation Name: Moccasin
> 2. Location: Generator's Moccasin Substation ("Substation") will be located in Stonewall
>    County **approximately fourteen (14) miles southeast of Aspermont, Texas.**

Sources (both verified `%PDF`, read this pass):
- `sources/2026-07-19_puct_35077-1924_sgia-ett-swe-moccasin-solar-original.pdf` (62 pp, original SGIA)
- `sources/2026-07-19_puct_35077-2454_sgia-ett-moccasin-first-amended-restated.pdf` (65 pp, First Amended & Restated)

The amendment also **reduced capacity** 817.56 → 615.97 MW inverter (250 → 155 Sungrow units)
— a design downsize, not a relocation; Exhibit "C" location text is unchanged.

### What the IA does NOT contain (full text extracted + keyword-scanned this pass)
- Method note: both PDFs were text-extracted and keyword-scanned (not OCR'd), so an
  image-only exhibit could in principle be missed; the exhibit list itself, however, names
  no land map.
- **No parcel/boundary map, plat, or legal description of the generation site.** Keyword
  scans for `plat / metes / bounds / parcel / acre / latitude / longitude` return only false
  positives ("contem**plat**ed", "**Plant**", "co**ordinate**d") — no land geometry.
- **Exhibit "C-1"** is a *"Conceptual One-Line Drawing of Point of Interconnection"* — an
  **electrical** single-line diagram of the POI, **not** a land map.
- The IA references an **ALTA survey of the property** the Generator must furnish to the TSP,
  confirming a survey exists — but it is **not part of the filing** (see Bottom line #1).

The IA locates the *interconnection facilities*, not the leased solar field: POI is a new ETT
**Cascabel Station** tapping the 345 kV Kirchhoff (Bus 60707) → Clear Crossing (Bus 60515) line.

## Step 2 — Other document classes checked (all negative for a parcel map)

| Source | Result | Strength |
|---|---|---|
| **Ch.313** (Comptroller value-limitation) + **JETI** API | NEGATIVE by INR and by "Swenson" | **Strong / structural** — the queue entry postdates Ch.313's 2022-12-31 statutory expiry; the project is ineligible, so absence is expected, not merely unfound. |
| **Ch.312** (county/city abatement registry) | NEGATIVE | **Weak** — Stonewall is a **non-reporting county**; absence from the registry proves nothing. |
| **County commissioners-court minutes** (ezTask/custom) | NOT HARVESTED | Minutes page `stonewallcounty.org/page/Public.Notices` returns **HTTP 403**; platform handler cannot reach it. |
| **County abatement (news)** | CONFIRMED EXISTS | KTXS (Apr 2025) + Double Mountain Chronicle report the county approved a ~10-yr abatement / PILOT — but no primary boundary instrument obtained. |

Avenue not yet exhausted (left as a lead, not scraped this pass — form-based, same failure
mode as the CAD/Comptroller forms): the **county clerk records portal** (LGS Online Solutions,
`public.lgsonlinesolutions.com`, probe = HTTP 200) is where a recorded reinvestment-zone or
lease-memorandum boundary instrument would live.

## Step 3 — Text → computed point

14 statute miles at bearing ~135° (SE) from Aspermont (33.1346, -100.2265):
initial computed point ≈ **32.9911, -100.0552** (first-pass estimate from the sentence alone).

## Step 4 — Imagery correction onto the graded footprint

Reading Sentinel-2 L2A frames (AWS Open Data COGs), a large rectangular **graded footprint
with an internal road grid** — absent through Jan 2026, present by Apr 2026 — sits ~2–3 km
NE of the text-only estimate, still "≈14 mi SE of Aspermont" and consistent with the IA
bearing. The point was moved onto that footprint:

**Recorded site coordinate: 33.0210, −100.0217** (method `ia_text_plus_imagery`).

### Offset caveat (honest note, not a defect)
On the 4.5 km-buffer frames centered at 33.0210, −100.0217, the visible footprint centroid
lies **~1.5 km SW** of that recorded point (≈ 33.011, −100.038); the recorded point falls on
the **NE interior/edge** of the graded area. The footprint is **fully captured with margin**
in all five frames, so the point was **not** re-fetched or re-centered — the offset is
documented here instead. Google-Maps deep-links built from the recorded point land on the NE
corner of the footprint, not its center.

## Step 5 — Best boundary evidence = the construction footprint

### Is the footprint solar earthwork, or just newly-broken cropland? (the one check that could break the fix)
At 10 m/px the graded pads are texturally similar to bare/plowed fields, and no racking or
substation is resolvable — so the identification rests on **convergence, not pixel proof**:
- **Temporal**: this exact area was undisturbed native brush with an intact drainage network
  across three prior seasons (2024-07, 2025-07, **and 2026-01**), then became a geometric
  graded area in spring 2026. Cropland does not materialize from untouched rangeland in one
  season.
- **Geometry**: the footprint's W/S perimeter is **straight and cuts across the former
  drainage**, with an internal access-road grid — unlike the **terrain-following contour
  rows** of the established cropland on the frame's E edge / SW corner.
- **Context/scale**: location, timing (KTXS: construction late-2025/early-2026) and
  ~5,000-ac scale all match the documented ENGIE/Meta project; a 5,000-ac conversion of
  native rangeland to **dryland cropland** in marginal-rainfall Stonewall County would be
  implausible.
- **Bare→green**: the Apr(bare)→Jul(green) shift is graded ground greening under West-TX
  summer rain, mirroring the surrounding rangeland's own seasonal greening — not cultivation.

Conclusion: consistent with solar civil/earthwork; racking + panels not yet built (as of
2026-07-20). The *site identity* does not depend on this read — it stands on the Step 1–3
location convergence below.

With no filed parcel map, the multi-temporal construction footprint IS the boundary evidence.
Clean 5-frame progression (single tool `s2aws.py`, uniform 4.5 km buffer, this pass):

- `imagery/key/s2_2024-07-01.png` — undisturbed rangeland (scene 2024-07-15)
- `imagery/key/s2_2025-07-01.png` — still undisturbed, green season (2025-07-20)
- `imagery/key/s2_2026-01-15.png` — still undisturbed / pre-construction (2026-01-31)
- `imagery/key/s2_2026-04-15.png` — **large bare-soil cleared footprint appears** (2026-04-26)
- `imagery/key/s2_2026-07-15.png` — **graded blocks + established road grid** (2026-07-20)

(Prior-pass Element84 range-read frames archived under `imagery/_pass1_element84/`.)

---

### Coordinate summary
| stage | lat | lon | basis |
|---|---|---|---|
| text-only estimate | 32.9911 | −100.0552 | 14 mi SE of Aspermont, IA Exhibit C |
| **recorded (imagery-corrected)** | **33.0210** | **−100.0217** | moved onto graded footprint (frame center) |
| footprint centroid (observed) | ≈33.011 | ≈−100.038 | ~1.5 km SW of recorded point |

**Confidence: HIGH that this is the project** (text + bearing + the 2026 construction
footprint + the ENGIE/Meta/Swenson-Ranch 5,000-acre narrative all agree);
**exact centroid ± ~1.5 km** (no filed parcel to pin it).
