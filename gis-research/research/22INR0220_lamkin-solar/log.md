# Triage log — Lamkin Solar (22INR0220)

## T1 start
**Queue history:** 76 snapshots (2020-03-01 → 2026-06-01)

COD drift (3 changes):
- 2022-12-31 held 2020-03 → 2022-03
- 2023-12-31 held 2022-04 → 2022-12
- 2025-12-31 held 2023-01 → 2025-01
- 2027-08-08 held 2025-02 → 2026-06 (current)

Capacity: 100.0 MW → 101.5 MW (stable since 2020-05)

Milestone dates:
- Screening started: 2019-06-24
- Screening complete: 2019-09-18
- FIS requested: 2020-03-13
- FIS approved: 2022-07-11
- IA signed: **2025-03-06** ← key signal
- Meets 6.9(1): 2025-04-23
- Meets all 6.9: NOT achieved
- Construction start/end: NOT reported
- Energization / sync / COD approvals: NOT achieved

**T1 assessment:** IA signed March 2025, 6.9(1) cleared April 2025. No construction dates
reported. Current COD 2027-08-08 is the 4th reported date — significant prior slippage.

## T2 start
gmaps.py returned HTTP 429 (rate-limited) on first call and retry. No pins found.
**T2 result: 0 pins. Normal — no delivery infrastructure yet.**

## T3 start
DDG CAPTCHAs blocked most searches after first hit. Key findings from accessible results:
- cleanview.co / infrasure.ai / interconnection.fyi / ercotqueue.com all list the project as active, ~102 MW, Comanche County TX, expected online 2027
- **Developer/SPV name: "Comanche Solar, LLC"** (not "Lamkin Solar LLC") — counterparty on GIA with Brazos Electric Power Cooperative
- ercotqueue.com rates build-chance at 81% (IA + FIS complete)
- No major news, no controversy found
- TX SOS / Comptroller direct search blocked by CAPTCHA

No pages saved to sources/ (no unique-content pages found, only aggregators).

**T3 result: news_found=false (no primary news), developer name = Comanche Solar LLC / Brazos Electric counterparty**

## T4 start
All PUCT Interchange endpoints returned HTTP 402 on every attempt. Portal entirely blocked in this environment.
T3 results mention a GIA filed under PUCT §25.195(e) with Brazos Electric as counterparty — this suggests IA exists in PUCT system but could not be retrieved.

**T4 result: ia_found=false (blocked portal, not confirmed absence). GIA likely exists per T3 secondary sources.**

## T5 start
Ch.313 database search found:

**App. No. 1785 — Comanche Solar, LLC / Hamilton ISD**
- Application date: 2022-05-09 (posted 2022-05-12)
- Agreement executed: 2023-01-12
- First full tax year: 2027 (consistent with reported COD 2027-08-08)
- Status: Agreement phase, annual reporting underway (2023 + 2024 Form 772 on file)
- PDF links retrieved but all PDFs unreadable as binary via WebFetch tool

Note: Hamilton ISD is in Hamilton County — project may straddle Comanche/Hamilton county line, or Hamilton ISD extends into Comanche County. Consistent with POI "tap 69kV 258 Hamilton - 273 Gustine" (Hamilton substation to Gustine, Comanche County).

JETI search not attempted (Ch.313 program closed to new applicants 2022; existing application found).

**T5 result: abatement_found=true. Comanche Solar LLC / Hamilton ISD, App. 1785, agreement 2023-01-12, first full tax year 2027.**

## T6 start
Site candidate derived from POI ("tap 69kV 258 Hamilton - 273 Gustine") and Ch.313 Hamilton ISD:
- Hamilton, TX: ~31.70°N, -98.13°W
- Gustine, TX: ~31.85°N, -98.40°W
- Midpoint estimate: ~31.77°N, -98.26°W (moderate confidence — POI line infrastructure)

CDSE chip attempt at center (31.77, -98.26) returned HTTP 401 Unauthorized — credentials not available in ~/.config/gis-research.env.

**T6 result: site_candidate identified (lat 31.77, lon -98.26, confidence medium), imagery SKIPPED (CDSE auth failure). construction_visible=false (no imagery).**

## T7 start
Wrote triage_findings.json and triage.md.
**Turns used: ~22. T1–T7 complete.**

## Deep scan D1 — 2026-07-20

**puct.py match** with `--key "Comanche Solar"` found 1 candidate: 35077-2140,
"Standard Generation Interconnection Agreement between Brazos Electric and Comanche
Solar", filed 2025-05-19. Saved to sources/. Verified PROBABLE by tool (county+MW in
text); manually verified CONFIRMED by reading the cover letter, which names "the
Lamkin Solar project in Comanche County, TX" explicitly (page 1 of PDF text).

**ch313.py resolve --name "Comanche"** (no county-code match on direct INR run, since
Ch.313 keys on school district not county) found App #1785, Comanche Solar LLC /
Hamilton ISD, applied 2022-05-09, agreement executed. Downloaded app, appamend1, agmt,
cert PDFs.

**spv.py resolve** and **ch313.py resolve 22INR0220** (bare) both returned negative —
project name "Lamkin Solar" doesn't textually match "Comanche Solar" so the deterministic
INR-keyed resolvers miss; only `--name`/`--key` free-text found it. Logging as a
resolver-naming gap, not evidence of a paper project.

**GIA Exhibit B (Time Schedule)**: Scheduled Commercial Operation Date = 08/08/2027 —
EXACTLY matches the queue's reported COD. In-Service = later of 1100 days from NTP or
03/31/2027. Trial Operation = "To be determined". This is the single most decisive
artifact: the reported COD is not a stale queue guess, it is the contractual date in a
signed 2025 GIA.

**GIA Exhibit C**: POI = Brazos Electric's 69kV Switching Station on FM 260, ~1 mile
from Lamkin, TX, Comanche County. Plant = 101.5 MW nominal, 28x 3.625MW inverters.

**GIA Exhibit E**: financial security = $9.5M irrevocable standby LOC, effective within
2 business days of execution — real money posted, strong reality signal.

**GIA one-line diagram + vicinity map** (rendered pages, sources/*_p35.png, *_p36.png):
vicinity map states exact site coordinates for the "PROPOSED POI": 31°48'12.68"N,
98°17'11.53"W = 31.80352, -98.28654 decimal. This is a MUCH tighter and more authoritative
fix than the triage's POI-midpoint estimate (31.77, -98.26) — using this for site.lat/lon.
Drawing dated Dec 2021, "Lamkin Solar 100MW" (pre-uprate label; queue capacity firmed at
101.5MW later, consistent).

**Ch.313 App #1785 Figure 1 map** (sources/2026-07-20_comptroller_ch313-1785-app_p24.png):
"Comanche Solar Project School District Overview" — shows project boundary (red outline)
just southwest of Lamkin, TX, inside the green Hamilton ISD polygon, inside the blue
Comanche County outline. Prepared by "Jared Feske", branded "CORE Solar" logo — candidate
developer name, needs corroboration. Cross-check: boundary location is visually consistent
with the GIA vicinity-map pin (both place the site adjacent to Lamkin, TX, SW side).

**Ch313 app Tab 9 / Tab 16 (Description of Land / Exhibit A)**: 5 parcels, all owned by
"JKS Cattle & Land" — Parcel IDs 11186 (552.92 ac), 11137 (101.47 ac), 11124 (70.4 ac),
11151 (23.95 ac), 11134 (278.14 ac). Total = 1,026.88 acres. Comanche Solar LLC is lessee
(land_tenure = leased), landowner = JKS Cattle & Land.

**Ch313 app Tab 7/8 (Description of Qualified Investment/Property, amendment #1 06/06/2022)**:
"~100 MWac ... approximately 254,700 solar panels and approximately 28 inverters."
"Construction of the Project is expected to commence in 2027 and is anticipated to be
complete in the fourth quarter of 2027." NOTE: this 2022-filed schedule (construction
starts 2027) is now stale vs. the 2025 signed GIA (COD 08/08/2027) — consistent direction,
Ch313 filing was conservative/early-stage language.

**Ch313 app_p29.png (job-waiver letter, April 2022)**: letterhead = "CORE Solar",
1221 South Mopac Expressway, Suite 225, Austin, TX 78746, coresolarllc.com. Signed by
Greg Nelson, President. This is the clearest developer identification found —
CORE Solar (aka CORE Solar LLC) is the developer behind the Comanche Solar, LLC SPV.

**Ch313 agmt.pdf (Findings of Hamilton ISD Board of Trustees, Nov 28 2022)**: confirms
agreement executed; App #1785; Texas Taxpayer ID #32070105377 for Comanche Solar LLC;
2027 direct employment spike of 402 (construction-year modeling) then drops to 2
permanent jobs — standard solar economic-impact profile, no red flags.

## D2 — site + imagery, 2026-07-20

Site fix: using IA vicinity-map printed coordinates (31.80352, -98.28654) — see D1 log.
This supersedes the triage's POI-midpoint estimate (31.77, -98.26); the IA map value is a
surveyed/plotted site coordinate from the interconnection engineering drawing, not a
line-midpoint guess. Cross-check: Ch313 Figure 1 map shows the project boundary just SW
of Lamkin, TX, inside Hamilton ISD — visually consistent.

**CDSE imagery: BLOCKED.** `cdse.py chip` failed with RemoteDisconnected on the full
median-reducer graph. Diagnosed with a minimal load+save openEO graph (bypassing the
median/scale steps) -> got a clean HTTP 402 PaymentRequired: "You do not have sufficient
credits to perform this request" (CDSE marketplace credits exhausted, account-level,
not project-specific). This is a fleet-wide quota exhaustion, not a per-request bug —
logging as negative evidence; no satellite imagery obtainable this run.

`gmaps.py places "Lamkin Solar"` -> HTTP 429 Too Many Requests (retried after 20s, same).
`gmaps.py places "Comanche Solar Lamkin"` -> HTTP 429 again.
`gmaps.py staticmap` -> HTTP 403 "Maps Static API is not activated on your API project."

**Construction/imagery verdict: UNKNOWN (imagery-blocked), not no_activity.** All three
imagery/mapping tool paths (CDSE chip, Google Places, Google Static Maps) failed for
account/quota reasons unrelated to this specific project. Cannot visually confirm
construction stage this run. Site location itself is HIGH confidence from the IA's own
engineering drawing (see D1); only the satellite ground-truth check is missing.

## D3 — gap-fill, 2026-07-20

**search.py "CORE Solar Lamkin Comanche County Texas"** -> hit thecomanchechief.com
article (primary local news, saved). CORE Solar's own coresolarllc.com/projects page
returned an empty JS-redirect shell via curl (client-side rendered SPA, "/lander" —
could not extract project list without a JS-capable fetcher; logging as inconclusive,
not negative).

**thecomanchechief.com article (Jul 22, 2021, updated Jul 27 2021)** — saved to sources/.
Key facts: public hearing 2021-07-19, Comanche County Commissioners Court; CORE Solar
reps Randy Jenkins and Julius Horvath presented; landowner named as **James Shelton**
("whose land encompasses the entire project"); neighbor **Mark Willingham** (attorney,
land borders 3 sides) raised concerns; commissioners declined to create a Ch.312
reinvestment zone (no vote) -> county-level tax abatement did NOT happen, but this does
NOT block the project ("does not mean Core Solar cannot still create the solar plant").
Separately, the Ch.313 Hamilton ISD abatement proceeded independently (confirmed executed
2023-01-12 per Ch.313 docs). Projected county revenue if abated: ~$1.2M over 10 years
($100,200/yr) — quantifies project as real, not speculative, in the eyes of county's own
outside counsel (Bob Bass, Allison Bass & Magee LLP) in 2021.

**Comanche CAD parcel search** (esearch.comanchecad.org, direct curl — WebFetch proxy
429'd, curl worked): parcels 11186 and 11134 (of 5 total from Ch.313) BOTH confirmed
owned by "JKS CATTLE & LAND, LLC" (Owner ID 58262, mailing 115 Ada Ct, Granbury TX
76048). Geographic ID SGU-04-136, ag-use valuation. Cross-validates the Ch.313 Tab 9/16
land description exactly (parcel IDs, acreage, legal descriptions match). Saved both
parcel pages to sources/. "JKS" plausibly ties to James Shelton (the landowner named in
the 2021 news article) but this is inference, not confirmed — logging as unconfirmed link.

**search.py "Lamkin Solar Comanche County construction"** and **"Comanche Solar LLC
2026"** — both returned an unrelated namesake: the Xcel Energy "Comanche Solar Project"
near Pueblo, Colorado (Comanche coal plant site) dominates search results. No additional
2024-2026 Texas-specific news, no construction-start articles, no press releases found
for the actual Lamkin/Comanche Solar (TX) project beyond the 2021 hearing coverage and
the Ch.313 filings already on hand. Logging as negative evidence — this project has a
thin public news footprint (typical for a mid-size solar project after initial
permitting coverage).

## D5 — deterministic wrap-up, 2026-07-20

**queue_history.py 22INR0220** -> timeline.md: 76 monthly snapshots (2020-03 -> 2026-06).
Reported COD has held stable at 2027-08-08 since 2025-02-01 (17 consecutive monthly
snapshots) — matches the signed GIA date. 3 total historical COD changes since 2020, but
0 changes since the IA was signed (2025-03-06); the current COD is the contractually
locked date, not a moving target. No construction-start/end, energization, sync, or
COD-approval milestones reported yet (expected pre-construction stage).

**eia_history.py 22INR0220 --write** -> "NOT in EIA-860M (TX slice)". Negative evidence,
expected for a project that has not yet started construction / reported to EIA-860M —
consistent with pre-construction status, not a red flag on its own.
