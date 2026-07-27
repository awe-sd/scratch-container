# Research Log — Moccasin Solar (26INR0269)

Stonewall County, TX · 603.59 MW Solar PV · Reported COD 2027-07-06
POI: Tapping 345 kV Line Kirchhoff (Bus# 60707) → Clear Crossing (Bus# 60515)

---

## Session 2026-07-18

### Stage 1 — LLC → Parent Chain


## Stage 1 — LLC → Parent Chain

**2026-07-18: TX Comptroller COA search "Moccasin Solar"** — form-based, not directly accessible via URL. HTML returned but no entity results visible. Sources: saved HTML at sources/2026-07-18_comptroller_coa_moccasin-solar.html. NEGATIVE for direct match.

**2026-07-18: TX Comptroller COA search "Swenson Solar"** — same. No entity results in HTML. NEGATIVE.

**2026-07-18: Web search via Agent** — Found key facts:
- ERCOT queue name: Moccasin Solar. Developer entity in ERCOT: **Swenson Solar LLC**
- Public marketing name: **Swenson Ranch Solar**
- Developer/operator: **ENGIE North America** (Houston, TX)
- EPC: SOLV Energy (via sub-agent web search — NOT independently confirmed from primary source)
- PPA: Meta 100% of output, signed ~Oct 2025
- PUCT control 35077 (IA signed Sep 4, 2024)

Sources:
- sources/2026-07-18_ktxs_stonewall-swenson-solar.html — KTXS article Apr 2025, ~5,000 acres, western Stonewall County, late 2025/early 2026 construction start, grid tie near Jones County
- sources/2026-07-18_pvtech_meta-engie-600mw-ppa.html — PV-Tech Oct 27, 2025, ENGIE+Meta PPA, 600 MW Swenson Ranch Solar, Stonewall County, $900M, 2027 COD
- PR Newswire Oct 27 2025 at https://www.prnewswire.com/news-releases/engie-and-meta-expand-power-purchase-agreements-to-more-than-1-3-gw-in-us-with-addition-of-new-600-mw-solar-project-302594394.html

---

## Stage 2 — County Records

**2026-07-18: PUCT Interchange Control 35077** — fetched IA PDF (62 pp, $2.2MB). Key facts:
- TSP: Electric Transmission Texas, LLC (AEP subsidiary)
- Generator: Swenson Solar LLC
- IA date: Sep 4, 2024
- Location (Exhibit C, Sect 2): "Moccasin Substation will be located in Stonewall County approximately fourteen (14) miles southeast of Aspermont, Texas"
- POI: Cascabel Station (new station on Clear Crossing–Kirchhoff 345 kV line in Jones County)
- Inverters: 250 × Sungrow SG3600UD at 3.270 MW = 817.56 MW inverter capacity
- Financial security: $23,000,000 LC or corporate guaranty to ETT
- Generator address: 1360 Post Oak Blvd STE 400, Houston TX 77056 (ENGIE NA HQ); admin contact Eric Tarantino at 3760 State Street Suite 200, Santa Barbara CA 93105
- Exhibit B (schedule): relative dates (26 mo In-Service, 27 mo Trial, 28 mo COD from conditions precedent date)
Source: sources/2026-07-18_puct_35077_swenson-solar-IA.pdf

**2026-07-18: Stonewall County CAD search** — county has no accessible online CAD portal. DNS failures at all URL patterns. NEGATIVE — noted.

**2026-07-18: TX Comptroller Ch312/313 abatement registry** — form-only interface, cannot query programmatically. KTXS confirmed 10-year county abatement approved Apr 2025. Could not retrieve primary document. NEGATIVE for primary PDF.

**2026-07-18: PUCT Interchange search for "moccasin"** — returned HTTP 402. NEGATIVE via direct URL.

**2026-07-18: TCEQ air permit search** — solar, not required. Expected absence confirmed. NEGATIVE (expected).

---

## Stage 3 — Site Pinpoint

**Derivation**: IA Exhibit C §2 states "Moccasin Substation approximately 14 miles southeast of Aspermont, TX"
Estimate: 14 mi SE (azimuth ~135°) from Aspermont (33.1346, -100.2265) → 32.9911, -100.0552
Google Places: rate-limited (HTTP 429) on all 6 attempts. staticmap API not enabled on key.
Community name: "Swenson" community in Stonewall County likely near Swenson Ranch = another directional pointer.

Confidence: medium — derived from IA text, not parcel or pin. Will cross-check via satellite imagery.

---

## Stage 4 — Satellite Ground Truth

**Initiating present-first chip at 32.9911, -100.0552 (2026-07-01, 6km buffer)**


### Stage 4 — Satellite Ground Truth (continued)

**CDSE auth (cdse.py tool)**: HTTP 401 on all client IDs — credentials in ~/.config/gis-research.env are expired/invalid. Used Element84 Earth Search (public STAC) + COG range-request reads instead.

**Scene used**: S2B_14SLB_20260710_0_L2A (cloud=0.07%, Jul 10 2026) — tile 14SLB covers study area.

**Site coordinate correction**: Initial estimate from IA text (14 mi SE of Aspermont) = 32.9911, -100.0552. After reading Jul 2026 imagery at full 10m/px (IFD0), the graded rectangular blocks were 2-3 km NE. Revised centroid: **33.0210, -100.0217** (~14 miles SE of Aspermont at bearing ~124°, consistent with IA text). Crosshair confirmed via IA bearing calculation.

**Jul 2026 observation (s2_2026-07-10_10mpx.png)**: Large rectangular graded polygons with internal road grid visible right of corrected centroid. Multi-km footprint with sharp edges (not agricultural). Consistent with solar site earthwork.

**Activity crop (s2_2026-07-10_activity_2x.png)**: Zoomed into the structured area. Confirms: organized blocks ~5-7km E-W, 3-4km N-S. Road network established, pads graded to uniform tan.

**Historical comparison (all sourced from Element84 COG range reads)**:
- S2B_14SLB_20241227_0_L2A (Dec 27 2024, 0.07% cloud): NO activity. Undisturbed ranchland.
- S2C_14SLB_20250322_0_L2A (Mar 22 2025, 0.0% cloud): NO activity. Undisturbed ranchland.
- S2B_14SLB_20250824_0_L2A (Aug 24 2025, 19.4% cloud): Cloudy, inconclusive.
- S2B_14SLB_20260121_0_L2A (Jan 21 2026, 0.0% cloud): NO visible grading activity.
- S2B_14SLB_20260710_0_L2A (Jul 10 2026, 0.07% cloud): ACTIVE grading, road network established.

**Verdict**: Construction started between January 2026 and July 2026. Stage = **clearing** (earthwork, road grid). No dark panel-field signature yet at 10m resolution.

**Stage** (IA timeline cross-check): IA Exhibit B gives 26 months to In-Service from conditions precedent (executed Sep 4, 2024) → In-Service ~Nov 2026. Construction active as of Jul 2026 = within expected earthwork phase. Behind the Nov 2026 In-Service date; electrical + panel stage not yet started.

---

## Stage 5 — Synthesis

See dossier.md and findings.json.

---

## Session 2026-07-21 — Second-pass review (site provenance + fresh imagery + abatement hunt)

**Focus of this pass**: nail down the site provenance / "is there a filing that shows the
parcel?", refresh the construction imagery on a clean single-tool progression, and run the
bounded Stonewall abatement hunt.

### Parcel / boundary — the answer is NO filed map exists (verified this pass)
- Re-checked BOTH IA PDFs (full text extraction + keyword scan; not OCR). Exhibit "C" is **text-only** in both the original
  (35077-1924, 62 pp) and First Amended & Restated (35077-2454, 65 pp): *"Generator's
  Moccasin Substation will be located in Stonewall County approximately fourteen (14) miles
  southeast of Aspermont, Texas."* No plat, metes/bounds, coordinates, or acreage.
- Exhibit **"C-1"** = *"Conceptual One-Line Drawing of Point of Interconnection"* — an
  **electrical** single-line, NOT a land map.
- The IA names an **ALTA survey of the property** as a Generator→TSP deliverable — so a
  parcel survey exists — but it is **not attached** to the filing.
- **Ch.313 / JETI**: strong/structural NEGATIVE. Ch.313 expired 2022-12-31 (queue postdates
  it → no application can exist); JETI excludes standalone solar. Neither can produce a
  reinvestment-zone parcel map for this project.
- **Ch.312**: weak NEGATIVE in the Comptroller registry (Stonewall is non-reporting). BUT
  the county **did** designate a reinvestment zone + abatement (see abatement hunt) — that
  county order is the ONE instrument that would map the parcel, and it is not retrievable here.
- **Conclusion**: no retrievable public filing delineates the parcel; the documents that
  would (ALTA survey; county reinvestment-zone instrument) exist but aren't publicly
  obtainable. The **construction footprint IS the best boundary evidence.** Full write-up:
  `sources/SITE_DERIVATION.md`.

### Imagery — clean 5-frame AWS progression (s2aws.py, 4.5 km buffer)
Replaced the mixed prior-pass Element84 frames (archived to `imagery/_pass1_element84/`)
with a uniform set: `imagery/key/s2_{2024-07-01,2025-07-01,2026-01-15,2026-04-15,2026-07-15}.png`.
All read + verified real PNGs, footprint fully inside frame with margin (no re-fetch needed).
- 2024-07-15 & 2025-07-20: undisturbed rangeland; pre-existing farms only at frame edges.
- 2026-01-31: still undisturbed / pre-construction.
- **2026-04-26: large bare-soil graded footprint appears** (sharp rectangular edges, multi-km).
- **2026-07-20: footprint organized into a block grid with an established internal road
  network**; grass on graded pads; no racking/panels at 10 m/px.
- Tightens construction start to **Feb–Apr 2026**; verdict advanced **clearing → grading**.
- Offset note: the recorded point (33.0210,-100.0217) sits at the NE edge of the footprint;
  observed centroid ~1.5 km SW (~33.011,-100.038). Point kept (imagery anchored on it,
  nothing clipped); documented rather than re-fetched.

### Stonewall abatement hunt (bounded)
- `minutes.py harvest --county Stonewall` → **HTTP 403** on the ezTask/custom minutes page
  (`stonewallcounty.org/page/Public.Notices`); 0 PDFs; `resolve 26INR0269` = COUNTY NOT
  HARVESTED. Census had already flagged v_minutes 403.
- Fallback: ONE `search.py "Stonewall County commissioners Swenson Solar abatement"` →
  **Double Mountain Chronicle** ("Commissioners Finalize Swenson Solar Deal", "County
  Approves Tax Deal") + KTXS **confirm a county PILOT/abatement was approved (~Apr 2025)**.
  No primary boundary instrument retrieved. LGS county-clerk portal
  (`public.lgsonlinesolutions.com`, HTTP 200) is the un-exhausted avenue. No banned domains cited.

### Files updated
`findings.json` (site + footprint_centroid + derivation_notes, new `tax_incentives`,
construction verdict/progression/imagery_artifacts), `sources/SITE_DERIVATION.md` (new),
`imagery/key/` (5 new frames; old set archived), then rebuilt `brief.html`.

