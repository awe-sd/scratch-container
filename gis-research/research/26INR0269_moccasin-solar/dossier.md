# Dossier — Moccasin Solar / Swenson Ranch Solar (26INR0269)

Researched 2026-07-18 · site 33.0210, -100.0217 · verdict **real_active**

## 1. Verdict

- **real_active** — [PV-Tech Oct 2025](sources/2026-07-18_pvtech_meta-engie-600mw-ppa.html): ENGIE+Meta 600 MW PPA signed for "Swenson Ranch Solar," Stonewall County, $900M, 2027 COD; Stonewall County 10-yr abatement approved April 2025; $23M financial security posted per [signed ETT IA](sources/2026-07-18_puct_35077_swenson-solar-IA.pdf)
- Construction: **clearing/grading**, first activity between 2026-01 and 2026-07 ([earliest clear negative Jan 2026](imagery/key/s2_2026-01-21_10mpx.png), [graded Jul 2026](imagery/key/s2_2026-07-10_10mpx.png))
- Site: 33.0210, -100.0217 — IA text "14 miles SE of Aspermont" + imagery shape cross-check, medium confidence ([satellite view](https://www.google.com/maps/@33.0210,-100.0217,5000m/data=!3m1!1e3))
- COD: reported 2027-07-06 → independent **2027-Q4 to 2028-Q1**, drift risk **medium** (earthwork only as of Jul 2026, 12 mo to reported COD aggressive for 600 MW)

## 2. Site identification

- Derivation: IA Exhibit C "14 miles SE of Aspermont, TX" → initial calc 32.9911, -100.0552; graded blocks in [Jul 2026 frame](imagery/key/s2_2026-07-10_10mpx.png) located ~3 km NE → revised centroid 33.0210, -100.0217 ([activity crop](imagery/key/s2_2026-07-10_activity_2x.png))
- **Stated project area: ~5,000 acres** per [KTXS article Apr 2025](sources/2026-07-18_ktxs_stonewall-swenson-solar.html) — imagery footprint of graded blocks appears consistent (~3,500–5,000 ac estimate at 10 m/px)
- Cross-checks: IA text places Moccasin Substation "SE of Aspermont" ([IA](sources/2026-07-18_puct_35077_swenson-solar-IA.pdf)); [KTXS](sources/2026-07-18_ktxs_stonewall-swenson-solar.html) says "western Stonewall County, grid tie near Jones County" — consistent with Cascabel Station on the Kirchhoff–Clear Crossing 345 kV line (Jones Co.)
- Not obtainable: parcel IDs (no Stonewall CAD online portal), exact Cascabel Station coordinates (CEII)

## 3. Ownership & money

| Entity | Role | Evidence |
|---|---|---|
| Swenson Solar LLC | SPV | [IA](sources/2026-07-18_puct_35077_swenson-solar-IA.pdf) Exhibit D — Generator party |
| ENGIE North America / ENGIE IR Holdings LLC | developer/owner | [IA](sources/2026-07-18_puct_35077_swenson-solar-IA.pdf) Exhibit D bank wire payable to ENGIE IR Holdings LLC; [PV-Tech](sources/2026-07-18_pvtech_meta-engie-600mw-ppa.html) names ENGIE as developer |
| Meta Platforms | PPA offtaker | [PV-Tech Oct 2025](sources/2026-07-18_pvtech_meta-engie-600mw-ppa.html) — 600 MW PPA, "Swenson Ranch Solar," $900M, 2027 COD |
| EPC | unknown | not identified; [KTXS](sources/2026-07-18_ktxs_stonewall-swenson-solar.html) mentions "350+ construction jobs" — no contractor named |

- Financing: Meta PPA executed Oct 2025; no NTP/financing-close press release found; $23M security posted with ETT at IA execution ([IA Exhibit E](sources/2026-07-18_puct_35077_swenson-solar-IA.pdf))

## 4. Land & county records

- Tenure: **leased** — [KTXS](sources/2026-07-18_ktxs_stonewall-swenson-solar.html) describes "approximately 5,000 acres" in western Stonewall County; no purchase mentions
- Abatements: Stonewall County **10-year tax abatement approved April 2025** per [KTXS](sources/2026-07-18_ktxs_stonewall-swenson-solar.html); Ch.312 (county level); TX Comptroller JETI/Ch.313 search returned form-only results — no Swenson or Moccasin entries found
- CAD: Stonewall County has no online CAD portal; county website returned no parcel search tool; 0 parcels searchable under LLC or developer name

## 5. Interconnection & contractual schedule

- POI per signed IA: "Cascabel Station (a new ETT station tapping the 345 kV line from Kirchhoff Bus# 60707 to Clear Crossing Bus# 60515)" ([IA Exhibit C](sources/2026-07-18_puct_35077_swenson-solar-IA.pdf))
- Equipment (Exhibit C): 250 × Sungrow SG3600UD inverters × 3.270 MW nameplate = 817.56 MW inverter capacity; substation name "Moccasin"

| IA document | Signed | Financial security posted |
|---|---|---|
| Original IA ([pdf](sources/2026-07-18_puct_35077_swenson-solar-IA.pdf)) | 2024-09-04 | $23,000,000 (ETT) |

| Milestone | IA Exhibit B (relative from conditions precedent) |
|---|---|
| In-Service | +26 months |
| Trial Operation | +27 months |
| Scheduled COD | +28 months |

- Anchor date for relative schedule not confirmed from IA text alone; "Meets all 6.9" = 2026-04-21 (likely final condition) → relative schedule implies COD ~Aug 2028 if anchored there; earlier if anchored to IA execution (~Jan 2027) — this ambiguity is a material uncertainty
- Queue-history COD drift ([timeline.md](timeline.md)): **2 changes** — 2027-07-06 → 2027-06-01 (2025-02 to 2025-07) → back to 2027-07-06 (2025-08 onward)

## 6. Satellite timeline

| Date | Observation | Frame |
|---|---|---|
| 2024-12 | Undisturbed ranchland/brush | [png](imagery/key/s2_2024-12-27_10mpx.png) |
| 2025-03 | Undisturbed — no activity | [png](imagery/key/s2_2025-03-22_10mpx.png) |
| 2025-08 | Partly cloudy (19.4%), inconclusive | [png](imagery/key/s2_2025-08-24_10mpx.png) |
| 2026-01 | Clear (0% cloud), no visible grading | [png](imagery/key/s2_2026-01-21_10mpx.png) |
| 2026-07 | **Active grading** — large rectangular cleared blocks, road grid, multi-km footprint | [png](imagery/key/s2_2026-07-10_10mpx.png) |

- Verdict: **clearing** — earthwork and road grid visible at 10 m/px; no racking signal; activity onset between Jan 2026 and Jul 2026 (Aug 2025 frame cloudy, narrows to ~H1 2026)

## 7. COD assessment

- Reported 2027-07-06 reflects developer's own projection; the IA has a relative schedule whose absolute anchoring is ambiguous
- As of Jul 2026 the site is in earthwork/clearing — road grid established, pads being graded; no racking or electrical work visible at 10 m/px
- A 600 MW utility solar build from earthwork-start typically requires 18–24 months (civil, foundations, racking, collection, substation, commissioning); with construction likely starting ~Q1–Q2 2026, on-time 2027-07 would require a ~14–16 month build — aggressive but not impossible for a well-funded ENGIE project with >200 inverters pre-ordered
- Positive signals: ENGIE developer (proven large-scale execution), Meta PPA counterparty, $23M security posted, county abatement approved — financing and offtake de-risked
- Risk: no EPC contractor identified, IA schedule relative not fixed, one prior COD oscillation (minor), capacity was downscaled 25% in Aug 2025 (from ~810 → 603 MW) — some re-optimization occurred mid-development
- **Independent estimate: 2027-Q4 to 2028-Q1, drift risk medium**

## 8. Could not determine

- Exact anchor date for IA relative milestone schedule (conditions precedent satisfaction date not found in IA text reviewed)
- EPC contractor identity
- Parcel IDs or acreage from county records (no Stonewall CAD portal)
- First construction activity date tighter than Jan–Jul 2026 (Aug 2025 scene cloudy; no CDSE access for finer dekad bracketing)
- TX SOS filing for Swenson Solar LLC (SOSDirect paid; Comptroller COA returned no entity match)
