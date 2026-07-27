# Site derivation — Indigo Solar 21INR0031 (user-directed, 2026-07-20)

Source: IA 35077-2447 **Attachment C-3 "Project Overview Map"** (page 42), extracted to
`sources/ia_35077-2447_attC3_map_p42.png` — list this in `site.map_artifacts`.

Map anchors (read from the rendered page):
- Project boundary polygons cluster around a **"New Lone Star Station"** on the
  **Existing Lone Star Transmission 345kV line** (line runs E-W along County Road 164)
- **County Road 151** bounds the northern polygons; **FM 1085** runs N-S on the east
  side; **Dry Creek** crosses the southern lobe; "Fisher" county label at west edge
- Scale bar: full cluster spans ~2.5 miles E-W
- Co-located storage (legend): Indigo Storage 24INR0496, Storage 2 25INR0528,
  Storage 3 25INR0529, Storage 4 25INR0530 — 60 MW each at the new station

Cross-check (independent): EIA-860M plant "Indigo Solar & Storage", entity
**Innovative Solar 245 LLC** (same SPV as the IA counterparty — Lone Star
Transmission IA + 3 amendments in the docket index), coords **32.62806, -100.236,
Fisher County**, planned COD 2027-05, capacity history 175→330 MW, status (P).

=> Working site fix: **32.628, -100.236** (medium confidence: EIA self-reported point
consistent with C-3 road/line geometry). To verify visually: chip this point wide
(3 km buffer) and match the boundary polygons + CR-151/FM-1085/Dry Creek geometry;
CDSE was connection-saturated by the parallel fleet at time of writing — retry.
verdict-relevant: rename the IA PDF from unverified_* only after eyeballing parties
page (Innovative Solar 245, LLC ↔ Lone Star Transmission, LLC).

## LOCATION VERIFIED (2026-07-20, deterministic)
OSM/Overpass within 4 km of 32.628,-100.236 names: County Road 151, County Road 164,
FM 1085, and a 345kV power line — every Attachment C-3 anchor present at this point
(plus CR 160/161/163/165 of the same grid). C-3 is labeled "Conceptual"/not-to-scale,
so visual road alignment against chips is expected to be loose; the road NAMES are the
verification. Verify chip: imagery/s2_2026-07_verify-4km.png (0.1% cloud) — bright pad
at center = New Lone Star Station area.
