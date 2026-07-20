# Deep-scan log — EmberGreen (28INR0090)

## Triage recap
- SPV: EmberGreen Energy Center LLC (Sugar Land TX, filed 2026-02-04). Dev: EmberClear (Canadian).
- 900→1036 MW capacity bump Aug 2025 in queue. FIS approved 2026-04-21. No IA.
- PUCT TEF docket 56455: $432M loan NOI APP 00000130 — but triage was WRONG (see T25).
- Prior 2026-06-15 chip @29.400,-96.080 (Hungerford CDP): agricultural, no activity.

## T24 TCEQ air permit — DECISIVE HIT
- Search: DDG "EmberGreen Wharton TCEQ air permit NSR" → records.tceq.texas.gov docs.
- **TCEQ EGU Standard Permit Reg No 178642 ISSUED 2024-12-20** (one day after submittal).
- Applicant: EmberGreen Energy Center LLC, Raj Suri, 4410 Dusty Meadow Ln, Sugar Land TX.
- Site: **"Ray Road, County Road 229, Wharton, Texas 77488"** (greenfield).
- **Two Simple Cycle Natural gas CTGs, combined nominal 900 MW**, SCR+CEMS for NOx/CO.
- Total emissions: 212.56 tpy NOx, 248.04 tpy CO. RE RN112104302, Customer CN606335743.
- Reviewer Grace King, Section Mgr Michael Partee. Project 386532. Fee $900. No PSD/NA review.
- Applicant commits to obtain Title V permit before operation begins.
- Artifacts: [sources/2026-07-18_tceq_notification-letter_178642.pdf](sources/2026-07-18_tceq_notification-letter_178642.pdf), [sources/2026-07-18_tceq_technical-review_178642.pdf](sources/2026-07-18_tceq_technical-review_178642.pdf)
- **Note:** Permit says 900 MW nominal — queue shows 1036 MW since Aug 2025.
  Bump not reflected in permit; may require amendment before larger unit(s) can be built.
- **Note:** "Received 12/19/2024, issued 12/20/2024" — 1-day turnaround under EGU Standard
  Permit (30 TAC 116.602) bypasses full case-by-case NSR review. Consistent with
  Oil&Gas Watch's characterization of "flood of gas plants" using this streamlined pathway.

## T25 Site pinpoint — OSM Nominatim
- OSM Ray Road: 29.3706388, -96.0921401 (Wharton County, 77448)
- OSM County Road 229 seg 1: 29.3640913, -96.0922667 (77448)
- OSM County Road 229 seg 2: 29.3689436, -96.0904485 (77488)
- Site center inferred: **29.3695, -96.0912** — intersection of Ray Rd & CR 229 south of US-59
- ~3.4 km SW of triage's Hungerford center (29.400, -96.080); the triage chip did NOT include
  the actual permitted site.
- Method: TCEQ permit address text → OSM road geometry → intersection lat/lon (5 dp).
- Cross-checks: GEM wiki "approximate" 29.28, -96.22 is ~13 km SW (imprecise); the TCEQ
  permit's precise "Ray Road, County Road 229" text is authoritative.

## T26 Satellite — Ray Road site chip
- Ran chip lat 29.3695 lon -96.0912 date 2026-06-01 buffer 3 km, window ±30 d.
- Read: agricultural land, small rural roads, no clearing/laydown/pad/crane activity.
  US-59 highway visible NE. Cropland with mixed dark/tan fields.
- Consistent with pre-construction (FIS approved 2026-04-21, no IA, permit issued Dec 2024
  but no construction commencement observed 18 months later).
- Artifact: [imagery/key/s2_2026-06-01_rayroad.png](imagery/key/s2_2026-06-01_rayroad.png)
- Baseline chip retry (2024-10-15, pre-permit): CDSE token 403/401 blocked repeatedly.
  Skipped baseline; the 2026-06-01 chip alone shows no_activity 6 months before reported COD.
- Contact sheet: [imagery/contact_sheet.png](imagery/contact_sheet.png) (2 frames, 2026-06-01 & 2026-06-15).

## T27 PUCT TEF docket search — NEGATIVE
- Query: interchange.puc.texas.gov control 56455 → "Sky2 TEF NOI Filing Sky2 Summary Page"
  — 56455 is NOT EmberGreen (triage was wrong; Sky2 is a different TEF applicant).
- Party-name search fields (FilingParty, UtilityName, FilingDescription) require a
  control number too; can't reverse-lookup by party alone.
- Bing / Google site: puc.texas.gov / DDG for "EmberGreen" TEF docket: no direct hit.
  Probed candidate control numbers 55814 55771 56472 56227 56320 — all unrelated.
- **Result:** correct EmberGreen TEF NOI control number not obtainable via public web
  search; the $432M NOI APP 00000130 reference is only sourced from power-technology.com,
  not verifiable via primary PUCT filing.

## T28 Turbine OEM confirmation — NEGATIVE
- Bing "EmberGreen" turbine order + GE Vernova/Siemens/Mitsubishi: no relevant hits.
- Aug 2024 power-technology.com: "discussions ongoing with leading manufacturer" (unnamed).
- No subsequent public announcement found. As of 2026-07-18: **no confirmed turbine order.**
- Critical for 2028-01-01 COD: heavy-frame gas turbines have 3-5 year lead times.
  Absence at 18 months to COD = major reality signal against the reported COD.

## T29 EmberClear corporate track record — LIMITED
- emberclear.com: "site undergoing maintenance" — content unavailable both direct and via
  Wayback / DDG (bot-checked).
- Prior triage evidence: Lincoln Land Energy Centre IL "ongoing" as of Aug 2024 power-technology.com.
- Cannot verify current Lincoln Land status or EmberClear balance-sheet via web search.
- Birdsboro PA (2019, $700M) — no recent operational data pulled.
- **Result:** developer track record limited to Aug 2024 press claim; recent financial /
  execution signals not verifiable.

## T30 Wharton CAD parcel — NEGATIVE (blocked)
- esearch.whartoncad.net: React/Vue SPA — HTML has no server-rendered parcel data.
- No public JSON API surface. Query for owner "EmberGreen" not answerable via curl/WebFetch.
- **Result:** parcel-level land tenure not established. Consistent with expected pattern:
  a Dec 2024 permit issuance for a Feb 2026 TX foreign filing suggests the LLC may not yet
  hold recorded fee title (may be under option/purchase agreement).

## Summary evidence table
- REAL signals: TCEQ Standard Permit 178642 ISSUED; specific greenfield address; specific
  emissions table + SCR/CEMS engineering; developer's track record on 2 prior US plants;
  gas-supply arrangement named (ConocoPhillips / Matterhorn); consistent queue milestones
  (FIS approved 2026-04-21).
- PAPER signals: no IA signed 18 months from reported COD; no confirmed turbine order
  (heavy-frame lead time 3-5 yr); no visible construction 6 months before reported COD;
  developer website down; TEF loan status unverifiable; capacity bumped 900→1036 MW post-permit.

## Verdict
- **real_early** — the TCEQ permit + specific site + SCR/CEMS engineering + developer with
  prior US plants proves this is a real proposed project, not a shell. But 2028-01-01 COD
  is not achievable: no IA, no turbine, no construction 6 months from claimed COD.
- Independent COD: **2030-Q4 at earliest**, more likely 2031+. Drift risk **HIGH**.
