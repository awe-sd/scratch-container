# Site Derivation & Cluster Attribution — Juno 3 Solar (26INR0621)

**Second-pass review, 2026-07-21.** Borden County, TX · 500 MW solar · POI #59916 Buck Canyon 345kV.
Triggered by the complaint that the prior coordinate had no documented source and that a
multi-project solar cluster risked being misread. That complaint is **substantially correct** — see below.

---

## 1. Where the OLD coordinate came from (provenance audit)

The prior deep run recorded:

> `site.lat = 32.749, site.lon = -101.625`
> `method = "OSM relation 14474033 (operating Juno I+II plant center 32.779N, 101.625W) + imagery-derived shift south for new expansion footprint"`
> `confidence = "high"`

**This provenance is weak and the "high" confidence label is unjustified.** The chain was:

1. **No first-party rung fired.** gmaps was 429-blocked in triage (0 pins); the PUCT Interchange was
   402-blocked (no IA PDF); Juno 3 is not in EIA. So there was no pin, no IA exhibit, and no EIA record.
2. **The anchor is an operating *neighbor* plant, not Juno 3.** OSM relation 14474033 was taken to be the
   operating "Juno I+II" plant and placed at 32.779N, **-101.625W**. The coordinate was then **shifted
   ~3 km south by eye** ("imagery-derived shift") to 32.749, -101.625 to guess a "new expansion footprint."
3. **The eyeball shift landed on top of a *different* operating plant.** 32.749/-101.625 sits ~0.9 km from
   **ENGIE Long Draw Solar** (operating 225 MW, 2020, EIA 32.741/-101.622). The imagery "construction"
   the prior run reported was that operating plant plus its neighbors — not Juno 3.

This is exactly the Tiger-Solar / EIA-centroid / neighbor-array failure pattern: an undocumented coordinate,
anchored on an operating neighbor, stamped "high confidence." **Retracted.**

---

## 2. The corrected site anchor (documented rung)

A defensible, first-party anchor **does** exist — it was retrieved by the sibling **Antila Solar (27INR0500)**
run and applies directly to Juno 3, because the two share one transmission project:

- **PUCT CCN docket 59199** — *"Juno Solar 3 and Antila Solar 345 kV Transmission Lines Project"* filed by
  **Wind Energy Transmission Texas, LLC (WETT)**. Its **Figure 1-1 Project Location Map**
  (`2026-07-21_ccn59199-figure1-1_juno3-antila-location-map.png`, copied into this dir) explicitly labels
  **"Proposed Juno Solar 3 and Antila Solar Collector Stations"** north of US-180, ~1 mi ENE of the
  FM 1054 / US-180 junction, west of Gail, Borden County.
- **Juno 3's own signed IA** — PUCT docket **35077-2184**, *"Generation Interconnection Agreement between
  WETT and SE DC DevCo, LLC for the Juno Solar 3 Project"* (`2026-07-21_puct_35077-2184_juno-solar-3-IA.pdf`,
  copied into this dir). Effective **July 1, 2025** (matches the queue `iaSigned`), POI = **"Buck Canyon 345kV
  switching station … in Borden County"**, connected by a **345 kV gen-tie**, financial security posted (Exhibit E).
  Its **Exhibit J — Interconnection Details** (rendered: `2026-07-21_puct_35077-2184_juno-solar-3-IA_p34.png`)
  states verbatim: *"Name: Juno Solar 3 … Point of Interconnection is located in Borden County, Texas at TSP's
  Buck Canyon 345kV switching station … 128 Sungrow SG4400UD-MV-US inverters … Solar inverter powered
  photovoltaic modules."* This is first-party, project-specific evidence — not an inference from a neighbor.
- **Google Places** cross-check: "Juno Solar SB Energy" pin at **32.7672, -101.6508** — coincident with the
  CCN collector-station location and with the Antila anchor.

**Corrected anchors:**

| Feature | Lat/Lon | Source | Confidence |
|---|---|---|---|
| Juno 3 / Antila collector-station (generation) site | **~32.767, -101.651** | CCN 59199 Fig 1-1 + IA 35077-2184 + gmaps pin | medium (documented, but co-located with the operating Juno complex — the *new* panel footprint is not yet separable) |
| Buck Canyon 345kV switching station (POI #59916) | **~32.719, -101.636** | gmaps "Long Draw Substation" + CCN (Buck Canyon co-located with existing Long Draw switching station, Vealmoore Rd) | medium |

The old anchor (32.749, -101.625) is ~3 km SE of the corrected collector site and coincides with operating ENGIE Long Draw Solar.

---

## 3. The multi-project cluster ("two existing solar projects")

The user's "two existing solar projects there" are the two **operating** solar plants in the western Borden
cluster (~-101.62 to -101.65, near the Long Draw substation hub):

| Plant / project | ID | Status | Lat/Lon | How identified |
|---|---|---|---|---|
| **Juno Solar Project** (operating predecessor) | EIA plant 63328 / queue 21INR0026 + 21INR0501 | **Operating 2021**, 305.6 MW (IP Juno LLC) | EIA 32.773/**-101.391** — *bad, ~22 km E*; true location ~32.78/-101.61 per imagery, POI Long Draw 138kV | EIA-860M; queue history; imagery (NE array) |
| **ENGIE Long Draw Solar** | EIA plant 62845 | **Operating 2020**, 225 MW (GDF Suez / ENGIE) | 32.741/-101.622 | EIA-860M; imagery (SE array) |
| Borden County BESS | EIA plant 66804 | Operating 2024, 150 MWh | 32.722/-101.639 | EIA-860M; Ch.312 "Dairy Bank" zone |
| **Juno 3 Solar** *(this project)* | queue 26INR0621 / IA 35077-2184 / IF "Juno Solar 3" | **Queued, IA signed, pre-construction** | collector ~32.767/-101.651; POI Buck Canyon 345kV | CCN 59199, IA 35077-2184 |
| **Antila Solar** (co-located, shares POI) | queue 27INR0500 / IA 35077-2227 | Queued, IA signed 2025-08-13, pre-construction | ~32.767/-101.651 (co-located) | CCN 59199 (own research dir) |
| Lyra Solar / Lyra Storage (same developer, diff POI) | 27INR0434 (IF "Juno Solar 4") / 26INR0636 (IF "JUNO BESS I") | Queued, IA signed | POI Muleshoe #59922 (NOT Buck Canyon) | queue; IAs 35077-2185/2225 |
| Caesar Solar / Caesar Storage (same POI, earlier stage) | 29INR0131 / 29INR0132 | Queued, no IA | POI #59916 Buck Canyon 345kV | queue |

**Developer:** the whole SB Energy cluster shares one SPV — **SE DC DevCo, LLC** (SB Energy, 3 Lagoon Dr
Suite 280, Redwood City CA) is the named Generator on the Juno Solar 3, Antila, Lyra Solar and Lyra BESS IAs.
This is distinct from the *operating* Juno's EIA owner "IP Juno, LLC" (an equity/ownership label); the queue
`interconnectingFacility` codenames confirm succession: Juno 3 Solar = "Juno Solar 3", Lyra Solar = "Juno Solar 4".

**Abatements (Ch.312, Borden County):** four county rows, none is Juno 3 — #4303 "IP Juno Reinvestment Zone"
(operating Juno), #4302 "BNB Long Draw Solar", #3676 "BNB Oxbow Solar" (a *separate* project — not Juno 3),
#15389 "Dairy Bank" (Borden County BESS). No Ch.313/JETI/Ch.312 filing for Juno 3 (weak negative).

---

## 4. Imagery attribution (corrected anchor, Sentinel-2 AWS)

Frames at the corrected collector anchor **32.767, -101.651**, 5.0 km buffer
(`imagery/corrected/s2_2024-07-01.png`, `s2_2025-07-01.png`, `s2_2026-07-15.png`):

- The solar footprint is **identical across July 2024, July 2025 and July 2026** — a large operating array in
  the NE (attributed to the operating **Juno Solar**, ~305 MW) and a second block cluster in the SE
  (attributed to operating **ENGIE Long Draw Solar**, 225 MW).
- Both arrays are **fully built in the July 2024 baseline — a full year before Juno 3's IA (July 2025).**
  Therefore neither array is Juno 3. **No new large-scale solar construction is visible** at the documented
  Juno 3 collector site as of July 2026; that land remains undeveloped rangeland in all three frames.
- This also confirms the operating Juno arrays sit at ~-101.61/-101.65 (not EIA's -101.391).

**Prior "active construction since Nov 2025 / racking installed Dec 2025 → Jun 2026" is RETRACTED.** The prior
Oct-2025 "pre-construction" and Dec-2025 "construction-active" key frames show the *same* built arrays — the
apparent change was seasonal colour / sun-angle variation over operating plants, read as progress.
(Epistemic note: this proves the old imagery captured operating neighbours; it does **not** prove Juno 3 will
not be built. It means construction status at the documented site is **not yet visible** — consistent with a
pre-construction 2027-COD project whose interconnection depends on the still-pending CCN.)

---

## 5. How to verify this location yourself

The corrected anchor is not my estimate to take on trust — it is a legal-filing location you can check
independently. In rough order of authority:

1. **CCN 59199 Figure 1-1 map** (`2026-07-21_ccn59199-figure1-1_juno3-antila-location-map.png`, in this dir).
   Open it: the box labeled **"Proposed Juno Solar 3 and Antila Solar Collector Stations"** is north of the
   US-180 line, roughly midway between the Dawson/Borden county line (west) and Gail (east), ~1 mi ENE of the
   FM 1054/US-180 junction. "Buck Canyon Station (WETT)" is co-located with the existing "Long Draw Switching
   Station" to the SW. Filed by WETT with the Texas PUC — the strongest single source.
2. **IA Exhibit J** (`..._juno-solar-3-IA_p34.png`, in this dir) — reads "Name: Juno Solar 3 … POI … at TSP's
   Buck Canyon 345kV switching station … Borden County." Confirms the project name ↔ POI binding.
3. **Corrected Sentinel-2 frames** (`imagery/key/s2_2024-07-01.png`, `s2_2025-07-01.png`, `s2_2026-07-15.png`).
   Compare them to the CCN map: the operating arrays sit where the map shows existing plants; the labeled
   collector-station land is still bare. If Juno 3 were built you'd see new arrays there — you don't.
4. **Browser satellite** — open `https://www.google.com/maps/@32.767,-101.651,5000m/data=!3m1!1e3` (tilt to
   satellite). You'll land on the operating solar complex NW of the Long Draw/Buck Canyon substation area,
   matching the CCN map. Google Places also returns a "Juno Solar SB Energy" pin at 32.7672, -101.6508 here.
5. **Independent re-derivation** — pull the two source PDFs fresh from PUCT Interchange
   (`interchange.puc.texas.gov`): docket **35077** item **2184** (the IA) and docket **59199** item **2** (the
   CCN application). Both are public.

Confidence is **medium**, not high, and here is exactly why: the collector-station site is *co-located with the
operating Juno Solar complex*, so at 10 m Sentinel-2 resolution the NEW panel footprint cannot yet be separated
from the operating arrays — the CCN map gives the collector-station **point**, not a fenced project boundary.
The honest statement is "documented to the collector-station location; exact new-array footprint TBD."

## 6. Verdict implication

Split the two axes the prior run fused:

- **Reality: real / committed.** Independent of the debunked imagery — signed IA (35077-2184, eff 2025-07-01),
  financial security posted, named SPV (SE DC DevCo / SB Energy), active WETT CCN (59199). Real project.
- **Location: corrected** to ~32.767, -101.651 (documented), old anchor retracted.
- **Construction: not visibly started** as of 2026-07 (prior "racking" retracted).
- **COD: 2027-11-30 reported → high drift risk.** The 345 kV gen-tie + Buck Canyon switching station are a new
  WETT build whose CCN (59199) was still in a SOAH contested hearing as of April 2026; no construction visible
  July 2026. Independent estimate ~2028.
