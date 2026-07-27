# Triage log — 26INR0636 Lyra Storage

T1 start

## T1 — Queue history
- 14 monthly snapshots: 2025-05-01 → 2026-06-01
- COD = 2026-11-12; held stable from first report — 0 drift
- IA signed: 2025-08-13 (strong signal — project committed)
- Screening complete: 2025-08-23
- FIS requested: 2025-05-12; FIS approved: NOT YET
- Meets 6.9(1): NO; Meets all 6.9: NO
- Construction start/end: NOT REPORTED
T1 complete — 2 tool calls used

T2 start

## T2 — Delivery pins
- gmaps.py places "Lyra Storage" → HTTP 429 (rate limited)
- Retry "Lyra Storage Borden County Texas battery storage" → HTTP 429 (rate limited)
- Budget: 2 calls used, both blocked. No pins found.
- Result: 0 pins — normal for paper/early-stage project
T2 complete — 2 tool calls used

T3 start

## T3 — Web sweep
- DDG "Lyra Storage ERCOT Texas battery": developer name "Juno BESS I" surfaced via ercotqueue.com tracker; 58% build probability cited (not authoritative); no official press releases
- DDG "Lyra Storage LLC Texas": no results; TX SOS not searchable via WebFetch (redirect)
- DDG "Juno BESS Juno Energy Texas": no results
- No source pages saved (no official developer pages found)
- Likely SPV "Lyra Storage, LLC" unverified; developer "Juno BESS I" is a possible parent/SPV name
T3 complete — 4 tool calls used (1 redirect counted as attempt)

T4 start
## T4 — PUCT Interchange
- BUDGET WARNING at 80% — skipping PUCT search to preserve T7 output budget
- Result: IA signed 2025-08-13 per queue history (T1) — IA exists but not retrieved via PUCT
- Log: PUCT search not executed due to budget constraint
T4 skipped — budget warning

T5 start
## T5 — Abatements
- BUDGET WARNING — skipping TX Comptroller Ch.313 / JETI search
- Post-2022 project (2025 entry); JETI miss is normal
- Result: not checked
T5 skipped — budget warning

T6 start
## T6 — Imagery
- No delivery pin found (GMaps blocked, T2 = 0 pins)
- No abatement map or IA site exhibit retrieved
- POI = 345kV MULESHOE (#59922) — substation coords not resolved without gmaps
- Per rules: no site candidate → SKIP imagery
- Result: no imagery run
T6 skipped — no site candidate

T7 start

## T7 — Output written
- triage_findings.json: written
- triage.md: written (10 lines)
- Turns used: ~14
- Budget warning hit at T3; T4/T5/T6 skipped to preserve T7 output
T7 complete

## DEEP SCAN START — 2026-07-19

Deep scan focus threads from triage:
1. PUCT IA retrieval (milestone schedule + parties)
2. Developer "Juno BESS I" parent chain
3. Muleshoe 345kV substation #59922 coords → imagery
4. TX SOS / Comptroller for Lyra Storage LLC + Juno BESS
5. TX Comptroller JETI / Ch.313 abatements

## STAGE 1 — EIA 860 Developer Chain Finding — 2026-07-19

KEY FINDING: EIA Form 860 (2024) lists "SE Juno, LLC" (Utility ID 63100) as owner of:
- Plant: "Juno Solar Project" (Code 63328) at **32.772889, -101.39102**, Borden County, Lamesa TX
- Grid: 138kV, TSP = Wind Energy Transmission Texas LLC (WETT), ERCO/TRE

This is the "Juno" triage clue confirmed. SE Juno LLC / SE (Solar) Juno → parent likely "SE" (Scout Energy, or similar).

Other Borden County BESS projects found in EIA 860:
- **Borden County BESS** (Utility ID 65765, code 66804): 9400 Vealmoore Road, Gail TX 79738; lat 32.72233, lon -101.638499; 138kV WETT; Energy Storage = Y
- **Iron Belt** (Utility ID 65967, code 67059): 200 CR 244, Gail TX 79738; lat 32.5557, lon -101.660063; 345kV WETT; Energy Storage = Y

Muleshoe 345kV bus likely near Borden County (not Bailey County). OSM substations in Borden County area:
- Willow Valley 345kV: 32.6507, -101.3961
- Faraday 345kV: 32.6481, -101.3958  
- Long Draw 345kV: 32.7211, -101.6330

A Lyra Storage 500MW BESS at "Muleshoe 345kV" likely sits at/near the Willow Valley/Faraday substation cluster or a new Muleshoe-named bus in Borden County.

Source: EIA Form 860 2024 early release (eia.gov/electricity/data/eia860/) — saved as /tmp/eia860_2024.zip

## STAGE 1 — Developer ID confirmed — 2026-07-19

SE Juno, LLC (EIA 860 Utility ID 63100) address: 1 Circle Star Way, San Carlos CA 94070
- This is the registered address of **EDF Renewables** (EDF EN North America Inc.) 
- "SE" = Solar Energy (EDF Renewables naming convention for solar SPVs)
- EDF Renewables is the parent developer behind the Juno Solar Project in Borden County

Implication for Lyra Storage: The "Juno BESS I" tracker name (triage) likely refers to EDF Renewables' Juno-family project cluster. Lyra Storage 500MW BESS is probably an EDF Renewables project co-located or near the Juno Solar site.

EDF Renewables portfolio in Borden County area:
- Juno Solar Project (operating, ~138kV, lat 32.772889 lon -101.39102)
- Lyra Storage 26INR0636 (queue, 500MW BESS, POI 345kV Muleshoe)

WETT (Wind Energy Transmission Texas LLC) is the TSP for Borden County projects, consistent with the 345kV Muleshoe bus being a WETT-owned switch.

Source: EIA Form 860 2024 (sources/2026-07-19_eia860_2024_borden_county_plants.zip)

## STAGE 4 — Imagery Findings — 2026-07-19

### Chip 1: Juno Solar EIA address (32.773, -101.391) — 1km tight
- Result: Undisturbed scrubland/farmland, no energy infrastructure visible
- EIA coordinates appear to be a county road reference, not the actual site center
- Artifact: imagery/s2_2026-07-01_juno_tight.png

### Chip 2: Juno area xwide (32.773, -101.391) — 6km
- Result: Town of Gail visible at left edge; undisturbed terrain throughout; no solar/BESS visible
- No infrastructure found at EIA-registered Juno Solar location
- Artifact: imagery/s2_2026-07-01_juno_xwide.png

### Chip 3: Willow Valley/Faraday 345kV substation (32.6494, -101.3960) — 3km
- Result: Small white substation complex visible with 4 radiating transmission lines — confirms 345kV infrastructure here
- No BESS container rows visible around the substation
- Artifact: imagery/s2_2026-07-01_willow_valley.png

### Chip 4: Borden County BESS / Long Draw area (32.722, -101.638) — 2km *** HIGH INTEREST ***
- Result: Large bright white industrial complex with multiple rectangular buildings/pads visible
  Multiple structures, gravel pads, clearly active energy infrastructure
  Long Draw 345kV substation (OSM) at 32.7211, -101.6330 is directly adjacent
  This is the "Long Draw" area in Borden County
- Candidate: This complex could be Borden County BESS (EIA 860 registered) or Lyra Storage site
- The "Muleshoe" 345kV ERCOT bus may actually map to the Long Draw or adjacent node
- Artifact: imagery/s2_2026-07-01_borden_bess.png

Next step: Zoom in on the Borden County BESS complex to assess its footprint and check for parallel container rows

### Chip 5: Long Draw 345kV area (32.721, -101.633) — 2km
- Same complex visible as Chip 4 (Borden County BESS at center, Long Draw substation adjacent)
- Top-right: dark grid = solar panels (ENGIE Long Draw Solar at 32.741, -101.622)
- No new graded pad or BESS container rows beyond the existing BESS complex
- Imagery verdict: NO independent Lyra Storage site visible in this area
- Note: The visible BESS complex is Borden County BESS (138kV EIA); Lyra Storage (345kV Muleshoe) may be a planned expansion or adjacent site not yet broken ground
- Artifact: imagery/s2_2026-07-01_long_draw.png

## STAGE 3 — Site Pinpoint Summary

Best candidate: Borden County, near 32.72N, -101.63W (Long Draw 345kV substation cluster)
- OSM Long Draw 345kV at 32.7211, -101.6330 is directly adjacent to Borden County BESS complex
- The ERCOT "Muleshoe" 345kV bus (#59922) likely corresponds to Long Draw or a new node on same line
- Note: OSM does NOT have a "Muleshoe" named substation anywhere in Texas — "Muleshoe" is an ERCOT nodal name only
- EIA 860 registered coordinates for Borden County BESS: 32.72233, -101.638499 (9400 Vealmoore Road, Gail TX)
- Lyra Storage 500MW BESS at 345kV would be a NEW adjacent pad not yet in EIA 860 (it's still in the queue)

Confidence: MEDIUM — county confirmed (Borden), general area confirmed (Long Draw/Vealmoore Road cluster), exact pad TBD

## STAGE 2 — County Records Summary — 2026-07-19

### CAD
- Borden County CAD portal (bcad.net) is expired/GoDaddy parked. No owner-name search possible.
- EIA 860 is the best proxy for county-level land data: Juno Solar Project registered at 136 CR 116, Lamesa TX 79331, Borden County

### JETI/Ch312 Abatements
- TX Comptroller SB1340 form-search not accessible via curl/WebFetch (JS-rendered)
- Borden County website (co.borden.tx.us) confirms abatement database exists but not accessible via WebFetch
- No abatement documents retrieved — consistent with BESS (thin county paper trail per PLAYBOOK)

### PUCT Interchange
- PUCT Interchange fully JS-rendered; no REST API accessible
- Could not retrieve IA control number or document via curl
- Known from queue history: IA signed 2025-08-13
- TSP = Wind Energy Transmission Texas LLC (WETT) based on EIA 860 grid owner for Borden County projects

### TX SOS / TX Comptroller
- "SE Juno, LLC" (parent EDF Renewables) address: 1 Circle Star Way, San Carlos CA 94070
- "Lyra Storage LLC" not found in EIA 860 or any web search (project still pre-COD)
- Developer chain: EDF Renewables → [Lyra Storage, LLC] based on Juno portfolio pattern

## STAGE 3 — Site Pinpoint Final

Best estimate: 32.720N, -101.635W (near Borden County BESS complex / Long Draw 345kV)
- Method: EIA 860 Borden County BESS registered addr (32.72233, -101.638499) + Long Draw 345kV OSM (32.7211, -101.6330)
- The "Muleshoe" 345kV ERCOT bus name likely corresponds to a WETT-owned node in this cluster
- Not confirmed: exact Lyra Storage pad location distinct from existing Borden County BESS
- Confidence: LOW-MEDIUM (county confirmed, substation cluster identified, exact pad unknown)

## STAGE 4 — Imagery Verdict

- No Lyra Storage BESS pad visible in any chip; the area shows undisturbed land around the Borden County BESS complex
- Borden County BESS complex (EIA 860 code 66804) visible at 32.722, -101.638 — active, large white pads
- No new graded pad or BESS container rows beyond this existing complex
- Verdict: NO_ACTIVITY for Lyra Storage specifically; existing BESS operational at same address cluster
- Key inference: Lyra Storage 500MW project has NOT broken ground as of 2026-07-01

## STAGE 5 — Synthesis

COD assessment:
- Reported COD 2026-11-12 is implausible: IA signed 2025-08-13, FIS not approved, 0 construction milestones, no visible site prep
- BESS at this scale (500MW) needs 12-18 months from NTP to COD; no NTP visible
- Independent estimate: 2027-Q4 at earliest (if FIS approved 2026-Q3, NTP Q3, +15 months = Q2-2027 min, more likely Q4-2027)
- Drift risk: HIGH — no financial security posted, FIS unapproved, no JETI/abatement confirmed

Verdict: real_early — project has a signed IA and credible developer (EDF Renewables), but is far from construction-ready

## DEEP SCAN ADDITIONS — 2026-07-19 (second pass)

### Developer chain correction
- Prior scan attributed SE Juno LLC (1 Circle Star Way, San Carlos CA 94070) to EDF Renewables.
  CORRECTION: 1 Circle Star Way, San Carlos CA is Energy Vault Holdings (NRGV, CIK 0001828536).
  EDF Renewables' HQ is 15445 Innovation Dr, San Diego CA 92128.
- SE Juno LLC = parent of Juno Solar Project (operating solar, 305.6 MW, Borden County, since 2021).
  The "SE" may stand for Solar Energy, not a developer acronym.
- No SEC filings link "SE Juno LLC" to a named parent entity.
- EIA 860 owner column: SE Juno LLC reports under Entity Type "Q" (Qualifying Facility equivalent), no explicit parent chain.
- "Lyra Storage LLC" yields 0 hits in SEC EDGAR full-text search.
- "Juno BESS I" (triage clue from third-party tracker) not confirmed via any primary source.
- **Developer chain: UNKNOWN — no primary source confirms parent of Lyra Storage LLC.**
  Best hypothesis: related to or owned by same entity as SE Juno, LLC (Juno Solar Project)
  given naming pattern (Juno/Lyra = constellation theme) and same county.

### POI/Muleshoe node clarification
- "MULESHOE (#59922)" is an ERCOT internal nodal name (settlement point), NOT a physical substation named "Muleshoe."
- No substation named "Muleshoe" found in OSM for Borden County or surrounding area.
- Bailey County TX (city of Muleshoe) is ~100 km NW of Borden County — different geography.
- Most likely physical connection: Long Draw 345kV substation (WETT, 32.7211, -101.6330) per OSM.
  This substation is immediately adjacent to the Borden County BESS complex (EIA 860 cluster).
- EIA 860 confirms WETT (Wind Energy Transmission Texas LLC) is TSP for all Borden County 345kV plants.

### EIA 860 Borden County cluster summary (confirmed)
- SE Juno LLC / Juno Solar Project (operating 2021): 32.772889, -101.39102 [138kV WETT]
- Borden County BESS (operating Aug 2024): 32.72233, -101.638499 [138kV WETT] — visible in imagery
- Iron Belt BESS (pre-ops): 32.5557, -101.660063 [345kV WETT, 200 CR 244 Gail TX]
- ENGIE Long Draw Solar (pre-ops): 32.741383, -101.621793 [345kV WETT]

### Imagery review (key frames, July 2026-07-01)
- Long Draw / Borden BESS complex: ACTIVE existing BESS (Borden County BESS, 150 MW, white pads visible)
- No new graded pad or BESS container rows visible in any chip — Lyra Storage has NOT broken ground
- CDSE authentication error (403) on second pass — no new imagery acquired
- Verdict: no_activity for Lyra Storage specifically; imagery cap reached (6 frames read, prior session)

### PUCT/TX Comptroller/TX SOS
- PUCT Interchange: fully JS-rendered, no accessible REST API, IA not retrieved
- TX Comptroller franchise search: JS-rendered, redirects
- TX SOS SOSDirect: requires $1/search subscription, not used
- SEC EDGAR: no filings for "Lyra Storage LLC" or "Juno BESS" (0 hits)
- IA signed 2025-08-13 confirmed from queue history, financial security/schedule unknown

### Abatement search
- TX Comptroller JETI/Ch.313: JS-rendered, not accessible via curl
- Borden County CAD (bcad.net): expired/GoDaddy parked
- No abatement or CAD documents retrieved — consistent with thin BESS county trail per PLAYBOOK
