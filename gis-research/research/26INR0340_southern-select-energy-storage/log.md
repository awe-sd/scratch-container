# Research Log — Southern Select Energy Storage (26INR0340)

Researched: 2026-07-19  
County: Galveston, TX | 204.76 MW Battery | POI: TNHEIGHTS_1 bus 38740 | Zone: HOUSTON  
Reported COD: 2027-05-24

---

## Stage 1 — LLC → parent chain

**Research date:** 2026-07-19 (manual web-fetch pass)

All six requested lookups were attempted exhaustively. Summary of actual content retrieved:

### Search 1: "Southern Select Energy Storage" LLC Texas
- Bing returned zero relevant results (no match for this exact phrase).
- DuckDuckGo returned CAPTCHA wall, no results accessible.
- Google returned error pages, no results accessible.
- **Result: No hits.**

### Search 2: "Southern Select Energy Storage" Galveston battery storage
- Same outcome — all search engines blocked or returned no matching results.
- **Result: No hits.**

### Search 3: "Southern Select Energy Storage" ERCOT developer
- Same outcome.
- **Result: No hits.**

### Search 4: "TNHEIGHTS" substation Galveston Texas energy storage
- Same outcome — no accessible results.
- **Result: No hits.**

### Search 5: site:sec.gov "Southern Select Energy Storage"
- SEC EDGAR full-text search API (efts.sec.gov) returned HTTP 403 on all endpoints.
- EDGAR company search (browse-edgar) returned HTTP 403.
- **Result: No SEC filings found. Cannot confirm or deny.**

### Search 6: SEC EDGAR company browse — https://www.sec.gov/cgi-bin/browse-edgar?company=southern+select+energy...
- HTTP 403 Forbidden on all EDGAR browse endpoints.
- **Result: Not retrievable from this environment.**

### Additional lookups attempted and results:

**GLEIF LEI registry:** `{"data":[]}` — no LEI record for "Southern Select Energy Storage". No GLEIF registration.

**Domain / Wayback Machine:**
- `southernselectenergystorage.com` — no archived snapshots in Wayback Machine (`"archived_snapshots": {}`). Domain does not appear to exist or was never crawled.
- `southernselectenergy.com` — same result, no archived snapshots.

**Texas SOS (direct.sos.state.tx.us):** Requires paid login credentials; no public search accessible from this environment.

**OpenCorporates:** CAPTCHA wall, no data returned.

**Bizapedia, CorporationWiki, Manta, Bizstanding:** All returned 403 Forbidden or security-check blocks.

**PUCT Interchange portal:** HTTP 402 — requires subscription (confirmed blocked, consistent with triage note).

**Texas Comptroller franchise search:** Redirected to generic search page with no results.

**TCEQ:** No results found for "southern select energy" in permit databases.

**EIA:** No plant data found for "SOUTHERN SELECT" in Texas.

**Press wire services (PR Newswire, BusinessWire, GlobeNewswire, AccessWire):** No press releases found for "Southern Select Energy Storage".

**LinkedIn:** No company profile page found (404).

### Conclusion

Zero public web presence confirmed for "Southern Select Energy Storage LLC":
- No news articles
- No press releases
- No SEC filings accessible
- No GLEIF LEI
- No website (domain unregistered / uncrawled)
- No accessible TX SOS record (portal paywalled)
- No EIA plant record (project not yet operational)

The entity name "Southern Select Energy Storage" does not surface in any publicly accessible commercial registry, news outlet, or regulatory filing reachable from this environment. Developer/parent chain remains **unknown**. The PUCT IA PDF (blocked, requires interchange.puc.texas.gov subscription) is the highest-probability source for identifying the counterparty/developer, as IA documents typically name the applicant entity and often the parent.

**Recommended next steps:**
1. TX SOS lookup via paid SOSDirect account — search "Southern Select Energy" for LLC registration and registered agent (likely a CT Corporation / CSC / National Registered Agents address pointing to the true developer)
2. PUCT Interchange IA PDF for 26INR0340 (docket search via a subscribed account) — will name the applicant
3. Check ERCOT Market Participant registration — if the project has a DUNS/QSE already assigned, the QSE name may hint at the developer family

