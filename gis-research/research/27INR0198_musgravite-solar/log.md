# Triage log — Musgravite Solar (27INR0198)

## T1 start
- Script: `uv run gis-research/scripts/research_tools/queue_history.py 27INR0198`
- 28 monthly snapshots (2024-03-01 → 2026-06-01)
- COD drift count: 1 (2027-05-28 → 2027-11-01, shifted at 2025-10-01 snapshot)
- Milestone dates:
  - Screening started: 2024-03-22
  - Screening complete: 2024-06-19
  - FIS requested: 2024-03-06
  - FIS approved: 2025-10-06
  - IA signed: 2025-05-20 (first appeared in 2026-02-01 snapshot)
  - No 6.9 milestones, no construction start/end, no energization/sync/COD approvals
- **T1 result:** IA is signed (strong signal); project has cleared FIS. No construction milestone yet. 1 COD slip.

## T2 start
- gmaps.py: 429 Too Many Requests on all 4 queries (exact name; name+county; LLC name; name+solar). One retry attempted, still 429.
- **T2 result:** No pins found (rate-limited, not a project signal).

## T3 start
- Query 1: DDG "Musgravite Solar" Texas → developer identified: **BT Thompson Solar, LLC**; location pinned to LaRue, Henderson County TX; multiple tracker sites confirm 100.6 MW, 2027 COD
- Query 2: DDG "BT Thompson Solar" + "Musgravite" → no parent company, no press releases; only 1 project on file per ercotqueue.com
- Query 3: DDG "BT Thompson Solar" Texas LLC → TX SOS File #0805261272, filed 2023-10-11, address: 13612 Midway Rd Ste 200, Farmers Branch TX 75244; bizapedia blocked (security check, counted as 1 retry)
- No press releases or financing news found. No traditional news coverage.
- Sources saved: none (no unique project-specific pages beyond aggregator summaries)
- **T3 result:** Developer = BT Thompson Solar LLC (Farmers Branch TX), single-project developer, filed Oct 2023. No news/PR. Location claim: LaRue, Henderson County.

## T4 start
- PUCT Interchange search (FilingParty=Musgravite Solar): HTTP 402 Payment Required
- PUCT Interchange search (FilingParty=BT Thompson Solar): HTTP 402 Payment Required
- PUCT Interchange root: HTTP 402 Payment Required
- One retry attempted (BT Thompson name), still blocked.
- **T4 result:** Portal blocked (402), cannot confirm IA filing. IA is recorded as signed (2025-05-20) in the queue data, but no PUCT document retrieved.

## T5 start
- TX Comptroller Ch.313 page: no searchable database returned via WebFetch (page doesn't render data table)
- DDG search for Ch.313/JETI + Musgravite/BT Thompson + Henderson County: no results
- Note: Ch.313 expired 2022-12-31; project filed 2023-10-11, so post-cutoff — JETI (replacement) would be applicable. No JETI hit found.
- **T5 result:** No abatement found. Normal for a 2023-filed project (post-Ch.313 expiry); JETI miss is expected at this stage.

## T6 start
- Site candidate: LaRue, Henderson County TX (32.1169, -95.6747) — from T3 web sweep (futuregrid.io + cleanview.co cited LaRue as location)
- Ran 9-point 3×3 grid chips in parallel; 7 failed (CDSE RemoteDisconnected under parallel load); 2 auto-succeeded (top row NW+N). Re-ran center chip serially — succeeded.
- 3 chips available: (32.1169,-95.6747), (32.1469,-95.6747), (32.1469,-95.7047) — all 2026-06-01 ±15d, 2 km buffer
- Contact sheet read: ~50-70% cloud cover across all three chips. Visible ground = rural forest/agricultural patchwork. No solar arrays, no grading, no equipment staging visible in cloud-free windows.
- No activity spotted → no re-center or baseline chip needed (full-size reads saved for deep scan)
- **T6 result:** No construction visible. Cloud contamination limits confidence; imagery inconclusive but consistent with pre-construction. Site candidate confidence: LOW (LaRue is a town centroid, not a surveyed parcel location).

## T7 start
- Wrote triage_findings.json (ia_found=true, construction_visible=false, deep_scan_recommended=true)
- Wrote triage.md (10-line summary)
- **Turns used: ~28**
- DONE.

## DEEP D0-D1 start (2026-07-20)
- Wrote findings.json skeleton (D0 checkpoint).
- `puct.py match 27INR0198` (rung 0/1, keys ['Musgravite Solar','Musgravite']): **0 candidates.** No IA on disk, no docket-INR join hit either (checked `_reference/puct_inr_join.json` directly for '27INR0198' string — 0 matches across 1743 entries).
- `spv.py resolve 27INR0198`: 1 candidate — EIA-860M plant-name match: entity **BT Thompson Solar, LLC**, plant "Musgravite Solar" 100.6MW, planned COD 2027-12, coords **32.16995, -95.5803**. This is a DIFFERENT location from triage's LaRue web-guess (32.1169,-95.6747) — EIA coords are a real candidate to re-chip.
- `puct.py match 27INR0198 --key "BT Thompson Solar"`: **0 candidates** — SPV name alone doesn't surface a docket filing either. IA remains unverified despite queue's iaSigned=2025-05-20 claim.
- `ch313.py resolve 27INR0198`: **NEGATIVE** — no Ch.313 or JETI match for 'Musgravite Solar'. Confirms triage T5.
- `tceq.py resolve 27INR0198 --county Henderson --keyword Musgravite --storm`: **NEGATIVE** — no 'MUSGRAVITE' hit among Henderson Co AIR facilities/permits/owners. 5 unrelated generation facilities in county (AVI Energy solar array Malakoff, Forest Grove/Trinidad steam electric, Tanzanite energy storage) — none tied to this SPV.
- `search.py "Musgravite Solar Henderson County Texas"`: no project-specific hits (tax-zone article, EnergySage directory, PUC org manual — noise).
- `search.py "BT Thompson Solar LLC Texas"` / `"BT Thompson Solar" Musgravite` / `"BT Thompson Solar" bizapedia`: surfaced bizapedia listing **BT THOMPSON SOLAR, LLC in Farmers Branch, TX** (matches triage TX SOS File #0805261272) — NOT yet fetched/verified. Also surfaced sibling shell-name pattern: BT Martin Solar, BT Brown Solar, BT Cantwell Solar, BT Cooke Solar, BT Coniglio Solar — all Farmers Branch/Dallas TX. "BT" naming pattern strongly resembles **Belltown Power Texas LLC** (real multi-hundred-MW TX solar developer, confirmed via belltownpower.com PRs: 330MWdc portfolio construction-start 2021, 750MW sold 2020) — LEAD, not confirmed.
- `search.py "Musgravite Solar LaRue Texas 100 MW"`: no direct hits (only EnergySage local-installer noise + Wikipedia solar-in-Texas overview) — LaRue location claim from triage remains web-aggregator-sourced only, unconfirmed by any primary doc.
- gmaps.py places (BT Thompson Solar / Musgravite Solar Henderson County): **HTTP 429** both queries — still rate-limited as in triage T2.
- exhibit.py scan: "no PDFs under sources/" — expected, no IA on disk yet.
- **D1 result so far:** IA unverified (queue claims signed but no PUCT filing found under any key tried). SPV candidate = BT Thompson Solar, LLC (EIA-860M only, not cross-verified). Possible parent lead = Belltown Power Texas. Site coordinate candidates now TWO: LaRue web-guess (low confidence, 32.1169,-95.6747) vs EIA-860M coords (32.16995,-95.5803) — haversine distance = **10.7 km apart**, not the same site; need independent tiebreak (POI cross-check next).
- `puct.py match 27INR0198 --key "Belltown Power"`: 2 candidates by name, both downloaded — **BOTH ARE FALSE MATCHES for a different project.** Filing 35077-1454 (Rayburn Electric Coop ⟷ Belltown Power Texas, dated 2022-07-15) is the ERCOT SGIA for **"Tanzanite Storage" (22INR0549)** — confirmed by reading page 1 (filing receipt names project "TANZANITE STORAGE / 22INR0549" explicitly). Filing 35077-1409 is "Sowers Storage" (22INR0552), same developer. Neither PDF's INR or project name matches 27INR0198/Musgravite — the earlier PROBABLE flag (Henderson county + 100.6 MW string match) was a coincidental false-positive exactly like the Space City/Camino traps the playbook warns about. **Do NOT cite these PDFs as Musgravite evidence.** They DO independently confirm: (a) "BT" = Belltown Power Texas is real and active in Henderson/Rayburn-Coop territory (different POI/TSP though — Rayburn Electric Coop, not the Oncor-adjacent Coffee/New York taps in Musgravite's POI text), (b) Belltown Power Texas files IAs as "BT Power Texas" — a naming style consistent with "BT Thompson Solar" as one of its project-SPV shells.
- POI cross-check: queue POI text is "Tap 138 kV (6855) Coffee - (6849) New York." Both are REAL Henderson County places, not aggregator noise: Wikipedia (via search.py + WebFetch) confirms **Coffee City, TX** at 32.1160,-95.4994 and **New York, TX** (unincorporated community, ~11 mi east of Athens) at 32.1700,-95.6700. Computed haversine distances: EIA-860M candidate coords (32.16995,-95.5803) sit only **3.0 km from the Coffee↔New York midpoint** and are roughly equidistant from both endpoints (9.7 km from Coffee, 8.4 km from New York) — geometrically consistent with a tap mid-span on the 138kV line joining them. By contrast, the triage's LaRue web-guess (32.1169,-95.6747) is off-axis (16.5 km from Coffee vs 5.9 km from New York — lopsided, not consistent with a tap between the two named points). **Site candidate updated: 32.16995,-95.5803 (medium confidence, cross-validated by POI geometry) supersedes LaRue.**
- Overpass API (OSM substation lookup) and OpenGridMap TX nodes CSV: no "Coffee" or "New York" named substation nodes found (OpenGridMap CSV only has "Coffee Port Substation" in Rio Grande Valley, unrelated AEP asset — false lead, discarded). Overpass main+kumi.systems mirrors both returned errors (406 / no output) — logged as tool failure, not a site negative.
- D1 IA ladder exhausted at rung 3 without a confirmed IA: rung 0 (INR join) miss, rung 1 (exact name keys incl. SPV) miss, rung 2 (SPV/registry resolvers: ch313 negative, tceq negative) done, rung 3 (Belltown Power name search) surfaced 2 filings but both verified as a DIFFERENT project (Tanzanite/Sowers Storage, 22INR0549/22INR0552) — false positive, discarded per playbook county+MW-neighbor warning. **No signed IA artifact obtained for 27INR0198 despite queue's iaSigned=2025-05-20 claim.** contractual_schedule will be empty/null — this is itself evidence (see D4).

## D2 imagery — CDSE OUTAGE (2026-07-20)
- Attempted chips at corrected site (32.16995,-95.5803, POI-cross-validated): single-chip foreground calls (90s, 150s timeouts) and 3 parallel background `chips` calls (2km buffer grid N/center/S) ALL failed with `RemoteDisconnected` after escalating backoff (15s/45s/120s). Background jobs left running 12+ min with zero output before being killed.
- Observed a separate container process (unrelated agent's watchdog) polling CDSE every 30 min expecting "CDSE PENALTY LIFTED" — confirms this is a KNOWN FLEET-WIDE CDSE capacity outage as of 2026-07-20 ~18:00, not specific to this project or query.
- **No satellite imagery obtained for the corrected site.** Triage's 3 chips (2026-06-01, LaRue centroid, now-superseded coordinates) remain the only imagery on disk — low evidentiary value since they're at the wrong location.
- Decision: will retry CDSE once more near end of run; otherwise construction verdict stays `unknown` (imagery-blocked), logged as a hard limitation, not guessed.

## D3 gap-fill (2026-07-20)
- Henderson CAD (esearch.henderson-cad.org) has an owner-name search form ("Last Name First Name" format) but a guessed query-string URL 404'd — no working API discovered without browser interaction; deferred (WebFetch cannot submit forms).
- search.py "Musgravite solar project news groundbreaking Texas": 2 banned queue-tracker results suppressed; remaining hits all unrelated (McCarthy TX solar overview, Sunraycer/Lupinus/Eagle Springs 620MW NE-TX portfolio -- confirmed different developer/project via follow-up search, Hyundai/Entergy Legend&Lone Star gas plants, Electrek general TX solar-growth piece). **No Musgravite-specific news coverage found** — consistent with triage T3.
- opencorporates.com: BT Thompson Solar LLC record (us_tx/0802952595) exists but WebFetch hit a CAPTCHA/bot-check wall — no registration date/agent/address extracted. TX Comptroller taxable-entity search (comptroller.texas.gov/taxes/franchise/account-status/search, redirected from mycpa.cpa.state.tx.us/coa/) requires only an Entity Name field but WebFetch cannot submit interactive forms — deferred, logged as a tool limitation (not a negative finding on the entity itself).

## D1 continued — PUCT docket window search around iaSigned=2025-05-20
- `puct.py ia "Musgravite Solar" --signed 2025-05-20` (browses docket around that date, no exact-name hit): surfaced item 35077-2141 (filed exactly 2025-05-20, Oncor + "Adapture Solar Development, LLC (Sol Marina En...)") — fetched + tiled + read page 1: **CONFIRMED DIFFERENT PROJECT** (Sol Marina Energy Center, INR 26INR0241/26INR0242, dated 2025-04-25). Same-day coincidence with Musgravite's iaSigned date only — discarded, removed from sources/ (do not keep false-lead artifacts on disk).
- `puct.py filings 35077 --from 2025-05-15 --to 2025-05-25` (all TSPs, ±5 days): 8 filings total in window — CenterPoint/Bypass BESS, Oncor/Acker BESS, Oncor/Oystercatcher Solar amend, Brazos Electric ×3 (Alina/Dos Rios/Comanche Solar), Oncor/Adapture (Sol Marina, checked above), TNMP/Momentum Headcamp. **None reference Musgravite, BT Thompson, or Henderson County by name.**
- `puct.py filings 35077 --match "Thompson"` and `puct.py search "Thompson Solar" --field desc`: both **0 results** — "BT Thompson Solar" (or "Thompson" alone) does not appear as a filed party/description anywhere in the docket-35077 index. Either (a) the IA was filed under a different legal/project name (common — queue name vs. filed name mismatches per playbook), or (b) despite the queue's iaSigned=2025-05-20 flag, no IA was actually filed with PUCT as of the last docket index refresh (2026-07-19).
- **FINAL D1 VERDICT: IA claim UNVERIFIED.** Exhausted the full systematic ladder (rung 0 INR-join, rung 1 exact-name incl. SPV, rung 2 registry resolvers ch313/tceq, rung 3 Belltown-Power/BT-prefix search, plus an ad-hoc date-window scan across all TSPs) without a single confirmed or probable document. Two coincidental county/date matches (Tanzanite/Sowers Storage; Sol Marina Energy Center) were caught and discarded as false positives, not cited. `contractual_schedule` will be empty in findings.json — the negative result itself is evidence for D4.

## D2/tooling — final outage status (2026-07-20, end of run)
- CDSE: retried once more near end of run (100s timeout) — still `RemoteDisconnected` through full 15s/45s/120s backoff. Outage persisted for the full session. **No imagery obtained for the corrected (POI-cross-validated) site coordinates.**
- gmaps.py places: retried multiple times across the session — still HTTP 429 throughout. **No delivery/business pins obtained.**
- gmaps.py staticmap: separate, unrelated failure — HTTP 403 "Maps Static API not enabled" for this API key/project (a config issue, not rate-limiting). No site map image obtainable this run either way.
- Henderson CAD owner-name search: form exists but requires interactive submission; WebFetch cannot POST/submit — no parcel lookup possible without a browser tool.
- opencorporates.com BT Thompson Solar LLC record: blocked by CAPTCHA wall via WebFetch.
- TX Comptroller taxable-entity search: requires interactive form submission — WebFetch cannot submit.
- **Net effect: this deep scan is paper-trail-only.** No satellite imagery, no map pins, no IA, no CAD parcel, no Ch313/JETI, no TCEQ storm NOI, no news coverage — all channels either returned genuine negatives or were blocked by tool/infrastructure failures outside this agent's control. Site coordinate rests on a single independent geometric cross-check (POI text vs. two real named places), not multi-angle convergence — confidence capped at MEDIUM per playbook Stage 3 (agree/disagree logic), and construction stage is UNKNOWN, not guessed.

## D5 wrap-up (2026-07-20)
- `queue_history.py 27INR0198`: 28 snapshots, 1 COD change (2027-05-28 -> 2027-11-01 at 2025-10-01 snapshot). Flagged anomaly: iaSigned=2025-05-20 milestone didn't first appear in queue report until 2026-02-01 (9-month lag).
- `eia_history.py 27INR0198 --write`: name-match to EIA plant 68903 'Musgravite Solar', entity BT Thompson Solar LLC. 13 monthly EIA-860M reports (2025-05 -> 2026-05) all agree: planned COD 2027-12, capacity 100.6 MW, coords 32.16995,-95.5803, status unchanged "(L) Regulatory approvals pending. Not under construction" — decisive second-source confirmation of both the SPV candidate and the site coordinate, and independent evidence construction has not started as of the latest report.
- Removed 2 false-lead PDFs from sources/ (Tanzanite/Sowers Storage IAs, coincidental county+MW match, verified different INR) before running build_brief — do not want brief.html citing evidence for a different project.
- `build_brief.py 27INR0198`: brief.html rebuilt, correctly shows 0 sources (accurate — no verified artifact obtained this run).
- `build_index.py`: refreshed research/index.json + INDEX.md (171 projects).
- Wrote dossier.md (verdict real_early, independent COD 2028-Q1, drift risk high) and final findings.json pass.
- **RUN COMPLETE.** Turns used: well under the 120 cap. Token spend: ~140-150k of 400k budget (~37%).
