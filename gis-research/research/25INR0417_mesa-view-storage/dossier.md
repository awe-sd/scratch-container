# Dossier — Mesa View Storage (25INR0417)

Researched 2026-07-19 · site ~31.22, -102.22 (low confidence) · verdict **unclear**

## 1. Verdict

- **unclear** — Queue milestones are real (IA signed, NTP issued, FIS approved) but developer is anonymous, no financing found, and satellite imagery was blocked; cannot confirm construction stage
- Construction: **unknown** — CDSE auth locked on both attempts; no imagery obtained
- Site: ~31.22, -102.22 — POI inference only, low confidence ([satellite view](https://www.google.com/maps/@31.22,-102.22,5000m/data=!3m1!1e3))
- COD: reported 2027-07-15 → independent **2028-Q1**, drift risk **high** (6 prior slips; FIS only Jun 2026; no developer ID)

## 2. Site identification

- Derivation: POI text "Tap 345 kV KINGMTSW (#842) to NORTMC (#76000)" — KINGMTSW = King Mountain Switch West near King Mountain Wind Farm (Wikipedia: 31.2378°N, 102.2378°W); EIA-860 BESS cluster in Upton County at 31.21–31.26, −102.12 to −102.32
- **Stated project area: unknown** — no IA exhibit, no CAD parcel, no abatement doc; imagery footprint unverified
- Cross-checks: EIA-860 King Mountain Wind Ranch 1 at 31.2092, −102.2417; Upton County BESS at 31.2392, −102.3217; King Mountain Solar at 31.2359, −102.1229
- Not obtainable: exact KINGMTSW coordinates (CEII); delivery pin (gmaps.py rate-limited); PUCT IA coordinates exhibit

## 3. Ownership & money

| Entity | Role | Evidence |
|---|---|---|
| Mesa View Storage, LLC | SPV | Queue record (interconnectingFacility field) |
| Unknown | developer/owner | 0 SEC hits, 0 TX Comptroller hits, no news |
| Unknown | EPC | not identified |
| Unknown | PPA/offtaker | not identified |

- Financing: unknown — no announcement found anywhere; 0 SEC filings

## 4. Land & county records

- Tenure: **unknown** — leased assumed (0 CAD parcels under Mesa View Storage in Upton CAD owner search)
- Abatements/agreements: none found (Ch.313/JETI post-2022 not applicable; no Ch.312)
- CAD: 0 hits under "Mesa View Storage" or variants via uptoncad.org API — expected for leased ranchland in early-stage project

## 5. Interconnection & contractual schedule

- POI per queue data: "Tap 345 kV KINGMTSW (#842) to NORTMC (#76000)" — 251.3 MW Stand-Alone BESS, CDR Zone WEST
- IA document: NOT RETRIEVED — PUCT Interchange requires JavaScript; control number unknown

| IA document | Signed | Financial security posted |
|---|---|---|
| Original IA | 2024-09-09 | Not determined (IA doc not retrieved) |

| Milestone | Queue-reported |
|---|---|
| IA Signed | 2024-09-09 |
| Financial Security + NTP | First reported 2026-03-01 snapshot |
| FIS Approved | 2026-06-11 |
| Construction Start | Not reported (through Jun 2026) |
| Scheduled COD (claimed) | 2027-07-15 |

- Queue-history COD drift ([timeline.md](timeline.md)): **6 changes** — 2025-05-31 → 2026-05-16 → 2026-10-31 → 2027-01-29 → 2027-06-15 → 2027-07-15; in reports since 2023-04-01 (39 monthly snapshots)
- Capacity change: 501.9 MW → 250.0 MW → 251.3 MW (Aug–Oct 2024)

## 6. Satellite timeline

| Date | Observation | Frame |
|---|---|---|
| All dates | No imagery obtained — CDSE auth locked (concurrent session limit) | — |

- Verdict: **unknown** — all satellite attempts blocked; construction stage cannot be assessed

## 7. COD assessment

- Reported 2027-07-15 is ungrounded by a retrieved IA schedule — cannot confirm it reflects a real contractual date
- NTP was issued by ~Feb/Mar 2026, but no construction start reported through Jun 2026 snapshot — 3-4 month gap post-NTP with no ground activity reported
- FIS only approved 2026-06-11 — critical grid-modeling gate just cleared; typically precedes final IA amendment with updated schedule
- 6 COD slips averaging 4–6 months each; every prior COD has missed
- Build window Jul 2026→Jul 2027 is 12 months — tight but physically possible for 251 MW BESS if mobilization starts immediately
- Against: no developer ID, no financing, no EPC, no construction start; FIS just cleared; 6 slips on record
- For: IA signed 18 months ago, NTP issued, FIS now complete, Upton County substation infrastructure established (multiple BESS online nearby)
- **Independent estimate: 2028-Q1, drift risk high** — absent imagery or developer confirmation, the pattern of slips and late FIS clearance suggests another 6-12 month slip past reported Jul 2027

## 8. Could not determine

- Developer / parent company identity (anonymous LLC; TX SOS paid-only; no web presence)
- EPC, PPA offtaker, financing status
- IA document and contractual schedule exhibits (PUCT Interchange JS-only, access blocked)
- Financial security amount
- Satellite construction stage (CDSE auth blocked — account locked for concurrent sessions from prior triage run)
- Precise site coordinates (POI inference only; no delivery pin, no parcel, no IA exhibit)
- KINGMTSW substation exact coordinates (CEII-redacted in ERCOT network model)
