# Research Log — 21INR0324 Board Creek Wind

## 2026-07-19 — Initial triage session

### Task
Ownership/parent chain, TX Comptroller entity, PUCT IA control numbers, press releases, VPPA/offtake for ERCOT 21INR0324 "Board Creek Wind" — 299.2 MW wind, Navarro/Limestone counties, ENGIE North America, IA signed 2021-08-19.

### Methods Attempted

**TX Comptroller (mycpa.cpa.state.tx.us / comptroller.texas.gov):**
- Original URL redirected to comptroller.texas.gov/taxes/franchise/account-status/search
- Page is a JavaScript SPA — GET requests with `?name=Limestone+Wind` return only the empty form shell
- API endpoint (api.comptroller.texas.gov) returned 403 Forbidden
- Result: **BLOCKED — requires browser with JS execution**

**PUCT Interchange (interchange.puc.texas.gov):**
- All search URL attempts returned HTTP 402 Payment Required
- Tried: `/search/filings/`, `/Filings/search.aspx`, with companyName params
- Result: **BLOCKED — 402 on all endpoints tried**

**ENGIE North America website:**
- Fetched sitemap: post-sitemap.xml + project-sitemap.xml
- Found project slug **"limestone"** in project sitemap
- Fetched engie-na.com/limestone/ — confirmed: 301 MW wind, Navarro County TX, ERCOT, COD 2022
- Fetched engie-na.com/engie-adds-more-than-650-mw-to-u-s-operations/ — **KEY FIND**: Limestone Wind PPAs with LyondellBasell, Stanley Black & Decker, Whirlpool Corporation; COD end-2022

**SEC EDGAR full-text search:**
- All efts.sec.gov endpoints returned 403 Forbidden

**FERC eLibrary:**
- elibrary.ferc.gov search endpoints returned only "eLibrary" text (JS-rendered, not crawlable)

**Business Wire / PR Newswire:**
- businesswire.com/news/home/20210803005388 — repeatedly timed out (60s timeout)
- prnewswire.com search — no relevant results in rendered content

**OpenCorporates:**
- Returned CAPTCHA/HAProxy challenge

**Wikipedia, GlobalEnergyMonitor, GEM.wiki:**
- No entry found for Board Creek Wind or Limestone Wind

**EIA API:**
- DEMO_KEY rate-limited (429, retry-after: 57245s)

**TheWindPower.net:**
- Search returned unrelated farms (wrong URL mapping)

**Google Search:**
- All google.com searches returned empty/error pages (bot-blocked)

### Key Findings

1. **Queue name ≠ public name**: ERCOT "Board Creek Wind" = ENGIE's "Limestone Wind"
2. **Capacity**: 299.2 MW (queue) / ~300–301 MW (as built)
3. **COD**: End of 2022
4. **Developer/owner**: ENGIE North America (long-term owner and operator)
5. **Ultimate parent**: ENGIE S.A. (Paris)
6. **Offtake**: LyondellBasell + Stanley Black & Decker (VPPA, ~Aug 2021) + Whirlpool
7. **SPV name**: Not found in any public source

### Remaining Gaps
- SPV LLC legal name
- PUCT IA control numbers
- Registered agent / TX SOS details
- VPPA financial terms

### Token budget
Exhausted at ~402,000 tokens. Files written per budget_hook.py instruction.
