# Research log — Laurel Wind Energy Center (27INR0056)

## Deep scan start — 2026-07-19

**Starting from triage (2026-07-18):** IA confirmed signed Oct 2024, Meets 6.9(1) Sep 2025, COD drifted 3×, capacity downsized ~502→306.6 MW Aug–Sep 2025. CDSE auth failed in triage; GMaps 429-blocked.

---

## Stage 1 — LLC / parent chain

- **pv-tech.org search "nova clean energy"**: Nova Clean Energy acquired a 1 GW Texas solar+wind portfolio from BNB Renewable Energy, Apr 2024. Source: pv-tech.org search results page (retrieved 2026-07-19). Project name "Laurel Wind Energy Center" consistent with the 306.6 MW wind portion of that portfolio. Developer identity = Nova Clean Energy confirmed as lead.
- **infrasure.ai** (commercial intel, unverified): developer = Nova Clean Energy; SPV = Laurel Energy Center LLC; offtake = CPS Energy (physical PPA); EPC = Wanzek Construction (MasTec Renewables); lenders cited (DNB, CIBC, NAB, DZ Bank) — financial figures may be conflated with related Clearway/Cedro Hill context; do not rely on lender names.
- **TX SOS**: SOSDirect is behind a paywall; TX Comptroller entity search is a JS-only form, could not retrieve results for "Laurel Wind Energy Center" or "Laurel Energy Center LLC."
- **novacleane.com / novacleane.energy**: both DNS ENOTFOUND — company website not publicly resolvable.
- **SEC EDGAR full-text**: HTTP 403 on all search endpoints.
- **BNB Renewable Energy site**: DNS ENOTFOUND.
- **pv-tech article (direct URL)**: HTTP 404 — article URL not canonical; only summary available via search results page.

*Conclusion: Nova Clean Energy developer chain confirmed to high confidence via pv-tech summary of Apr 2024 acquisition. SPV name (Laurel Energy Center LLC vs. Laurel Wind Energy Center LLC) unconfirmed — no primary LLC filing retrieved. CPS Energy offtake and Wanzek EPC are commercial intel only.*

---

## Stage 2 — County records

- **Pecos CAD (pecoscad.org)**: Searched via GET form (SearchOption=basic): "laurel wind" → count=0; "laurel" → count=0; "nova clean" → count=0; "wind energy" → count=0; "wind" → count=0; "wanzek" → count=0. No parcels under any project/developer name. Expected for pre-construction wind (land is leased, stays under landowner names). Confirmed CAD portal accessible (Harris Govern / Pritchard & Abbott platform, 2026-07-19).
- **Tax abatements (Ch.312/313/JETI)**: Post-2022 wind projects ineligible for Ch.313; JETI registry not publicly searchable. Absence expected, not evidence of paper project.
- **PUCT Interchange portal**: HTTP 402 on all URL patterns; portal is JS-only, AJAX search endpoint returns 404. IA not retrievable via curl/WebFetch in this environment. Negative: portal blocked, not confirmed absent.
- **FAA OE/AAA portal (oeaaa.faa.gov)**: All search endpoints return 404 (portal appears to require JS/session). Turbine-specific coordinates not obtained. This is a hard limit — decisive positive evidence missing.
- **Pecos County commissioners court minutes**: No accessible online archive found (county website DNS fails).

*Project area: not determinable — no abatement app, IA, or CAD acreage doc retrieved.*

---

## Stage 3 — Site pinpoint

- **Delivery-pin trick (gmaps.py places)**: HTTP 429 rate-limited on all attempts (triage used up allowance). No new pins retrieved.
- **POI anchor**: "Solstice to Bakersfield (Bus# 60404–76002) 345kV Ckt 2 line tap" → Bakersfield TX is a small town ~30 mi SW of Fort Stockton in Pecos County at approx 30.891°N, 102.298°W. Wind turbines would be sited on mesas within ~15-30 km of the 345kV tap point.
- **Confidence**: LOW. Bakersfield is a town-level anchor only; no turbine-specific pin, parcel, or FAA filing coordinate obtained.

---

## Stage 4 — Satellite imagery

- **CDSE auth status**: token auth returned HTTP 401 Unauthorized on all calls after the first chip (token expired/invalidated, password 403 on re-auth). Only 3 chips succeeded.
  - `s2_2026-07-01.png` (6 km, Bakersfield anchor 30.891, -102.298): undisturbed desert mesa + Bakersfield town (circular irrigation), road junction. No turbine pads, no clearing, no access roads.
  - `grid_S.png` (2 km, 30.771, -102.298): undisturbed mesa/arroya terrain. No construction activity.
  - `grid_NW.png` (2 km, 31.001, -102.418): undisturbed desert mesa, canyon features. No construction activity.
  - Three chips in N, E, W directions failed (403/RemoteDisconnected).
- **Verdict**: No activity visible in 3 of 8 intended chips; 5 chips not retrieved. Coverage of the 30-km wind search radius is **partial** — cannot definitively conclude no_activity across the full project footprint. However, the 3 chips showing undisturbed terrain, combined with no FAA OE filings found and no CAD activity, are consistent with pre-construction / no construction started.

---

## Stage 2 (continued) — News / developer

- **CPS Energy news pages**: HTTP 404 on all specific URL guesses (2024, 2025 renewables pages).
- **MasTec investor press releases**: Timeout / no Laurel Wind mention in news listing.
- **Wind-Watch, thewindpower.net**: 404s on search URLs.
- **PR Newswire, GlobeNewswire**: keyword filter not functional via API; no Laurel Wind or Nova Clean Energy results in general listing.
- **pv-tech.org**: Only the Apr 2024 BNB→Nova acquisition summary; no Laurel Wind-specific article found.
- **4coffshore.com**: HTTP 403.

---

## Wrap-up — 2026-07-19 (budget ~80%)

Stopping research. Writing findings.json, dossier.md, running deterministic commands.
