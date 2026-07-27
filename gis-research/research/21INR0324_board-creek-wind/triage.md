# Triage: 21INR0324 Board Creek Wind (Limestone Wind)

**Date:** 2026-07-19  
**Researcher:** Agent (automated)  
**Status:** TRIAGE COMPLETE — gaps remain on SPV name and PUCT control numbers

---

## Key Finding: Queue name ≠ Public name

ERCOT queue entry **21INR0324 "Board Creek Wind"** is the same asset publicly marketed by ENGIE North America as **"Limestone Wind"**. Confirmed via:
- ENGIE NA project page (engie-na.com/limestone/) — 301 MW, Navarro County TX, ERCOT, COD 2022
- ENGIE NA press release 2023-03-20 — Limestone Wind in "Navarro & Limestone Counties, TX, 300 MW"

---

## Project Profile

| Field | Value |
|---|---|
| ERCOT INR | 21INR0324 |
| Queue name | Board Creek Wind |
| Public name | Limestone Wind |
| Capacity (queue) | 299.2 MW |
| Capacity (as built) | ~300–301 MW |
| Technology | Wind |
| Counties | Navarro and Limestone, TX |
| Market | ERCOT |
| POI | 345kV 3386 Outlaw Switch |
| Transmission owner | Oncor |
| IA signed | 2021-08-19 |
| COD | End of 2022 |

---

## Ownership / Parent Chain

```
SPV LLC (name unconfirmed — likely "Limestone Wind Project LLC" or "Board Creek Wind LLC")
  └─ ENGIE North America Inc.  (Houston, TX)
       └─ ENGIE S.A.  (Paris, France — ultimate parent)
```

ENGIE NA describes itself as "a long-term owner and operator" of the project.

---

## Offtake / VPPA

Three VPPA/PPA customers confirmed (ENGIE press release 2023-03-20):

1. **LyondellBasell**
2. **Stanley Black & Decker** — VPPA announced ~2021-08-03 (Business Wire PR #20210803005388; article timed out but deal structure confirmed as VPPA)
3. **Whirlpool Corporation**

Stanley Black & Decker had stated a goal of "achieving carbon neutrality by 2030" and sourcing "100% of US and Canada electricity" from renewables.

---

## Sources Found

- **ENGIE NA project page:** https://www.engie-na.com/limestone/
- **ENGIE NA press release (2023-03-20):** https://www.engie-na.com/engie-adds-more-than-650-mw-to-u-s-operations/
- **Business Wire PR (SBD VPPA, ~2021-08-03):** https://www.businesswire.com/news/home/20210803005388/en/ (timed out; not fully fetched)

---

## What Was NOT Found

| Item | Status | Why |
|---|---|---|
| SPV LLC legal name | NOT CONFIRMED | TX Comptroller SPA (JS-only), TX SOS SOSDirect (login required) |
| PUCT IA control numbers | NOT FOUND | PUCT Interchange returned HTTP 402 for all search queries |
| Registered agent / officers | NOT FOUND | Same barriers as above |
| VPPA terms (MW, price, tenor) | NOT FOUND | Not in public press releases |
| FERC MBR filings | NOT FOUND | FERC eLibrary returns only "eLibrary" text (JS-only) |

---

## Next Steps

1. **TX SOS SOSDirect** (direct.sos.state.tx.us) — search "Limestone Wind" and "Board Creek Wind" — requires browser/interactive session
2. **TX Comptroller** (comptroller.texas.gov/taxes/franchise/account-status/search) — same; needs JS execution
3. **PUCT Interchange** — need to access via browser at interchange.puc.texas.gov; search company name "Limestone Wind" and "Oncor" with date ~2021
4. **Business Wire PR** — fetch businesswire.com/news/home/20210803005388 (currently timing out; retry)
5. **FERC eLibrary** — search "Limestone Wind Project" in full-text search for MBR filings
