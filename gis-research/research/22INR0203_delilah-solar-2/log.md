# Research Log — Delilah Solar 2 (22INR0203)

Research started: 2026-07-19  
County: Lamar, TX | Capacity: 317.58 MW Solar PV | POI: 345 kV TTRSW 11688 | Reported COD: 2026-09-30

---

## Stage 1 — LLC → Parent Chain

### 2026-07-19 — Stage 1: LLC → Parent Chain

**Developer confirmed: Invenergy (Chicago)**
- Sibling project Delilah I (22INR0202) confirmed Invenergy developer + WEC Energy Group (90% stake)
- "Delilah" + "Samson" are a 5-phase ~1,300 MW portfolio on 18,000 acres in NE Texas (Lamar/Red River County)
- Samson I offtaker: AT&T; Delilah I offtakers: Honda (200 MW VPPA) + Tesla (100 MW VPPA)
- No WEC stake announced yet for Delilah 2; no PPA announced
- Sources to save: WEC PR for Delilah I acquisition, Invenergy COD PR for Delilah I

**Key URLs found:**
- Invenergy Delilah I COD: https://invenergy.com/news/invenergy-developed-delilah-i-solar-reaches-commercial-operations-in-texas
- WEC PR Delilah I acq: https://www.prnewswire.com/news-releases/wec-energy-group-to-acquire-90-ownership-of-delilah-i-solar-energy-center-302129255.html
- WEC PR Samson I acq (5-phase portfolio context): https://investor.wecenergygroup.com/investors/news-releases/press-release-details/2023/WEC-Energy-Group-to-acquire-80-ownership-of-Samson-I-Solar-Energy-Center/default.aspx

**TX Comptroller search**: JS-rendered, requires live browser — will try alternate fetch approach
**TX SOS SOSDirect**: requires paid login


### 2026-07-19 — Stage 2: County records / PUCT

- PUCT interchange search for "Delilah Solar" and "Delilah Solar 2": HTTP 402 — NEGATIVE
- Lamar CAD esearch.lamarcad.org owner search "delilah solar": HTTP 404 — NEGATIVE  
- Lamar CAD esearch.lamarcad.org owner search "invenergy": HTTP 404 — NEGATIVE
- TX Comptroller Ch.313 agreements page: no Lamar County solar entries listed — NEGATIVE
- TX Comptroller taxable entity search (mycpa.cpa.state.tx.us): JS-rendered, redirects to search page — NEGATIVE (could not fetch)
- SEC EDGAR full-text search "Delilah Solar 2": 403 forbidden — NEGATIVE
- WEC Infrastructure portfolio page (wec-inf.com): DNS not found — NEGATIVE

### 2026-07-19 — Stage 3: Site pinpoint

- gmaps.py places "Delilah Solar 2": HTTP 429 Too Many Requests — NEGATIVE
- gmaps.py places "Delilah Solar 2 construction": HTTP 429 — NEGATIVE  
- gmaps.py places "Invenergy Delilah Solar Lamar County": HTTP 429 — NEGATIVE
- POI "345 kV TTRSW 11688": not resolved to coordinates; CEII likely applies
- Site lat/lon: NOT DETERMINED this session

### 2026-07-19 — Stage 4: Satellite

- No imagery obtained — site not pinned, cannot chip without lat/lon

### 2026-07-19 — Key positive findings

- **Approved for synchronization 2025-01-13** (from queue timeline) — strongest real-project signal; plant is built and energized
- **Developer confirmed: Invenergy** via WEC PR for sibling Delilah I (sources/2026-07-19_prnewswire_wec-delilah-i-acquisition.html)
- **Likely investor: WEC Energy Group** (confirmed 90% in Delilah I; not announced for Delilah 2)
- **11 COD drifts** across 86 monthly snapshots (2019-05 to 2026-06)
- **Invenergy Delilah I COD announcement saved** (sources/2026-07-19_invenergy_delilah-i-cod-announcement.html)
- IA signed 2020-12-22 per ERCOT queue

