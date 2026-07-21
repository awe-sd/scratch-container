# County commissioners-court minutes / clerk-records web census

**Assembled 2026-07-21.** Scope: all **195 distinct counties** in the current active
ERCOT queue (latest snapshot, active-queue exclusions). Method: 18 Haiku subagents
(web search + fetch) produced candidate URLs; every URL was then **independently
HTTP-probed** with live platform fingerprinting (`data/reference/county_minutes_census.json`
carries the per-URL verdicts as `v_website`/`v_minutes`/`v_clerk`). Numbers below count
only probe-verified-live URLs — the census is deliberately conservative.

## Headline numbers (probe-verified)

| Measure | Count / 195 |
|---|---|
| Official county website found + live | 176 |
| — exists but unverifiable from this container (bot-block 403 / broken TLS chain / timeout) | +15 |
| — genuinely not found | 2 (Palo Pinto, Uvalde) + 2 wrong-URL (Wichita*, Eastland) |
| **Commissioners-court minutes/agenda page live** | **152 (78%)** |
| **County clerk online records portal live** | **107 (55%)** |

*Wichita's recorded homepage hostname is wrong but its minutes and clerk URLs verify fine.

## Minutes platforms (live pages only)

| Platform | Counties | Scrape difficulty |
|---|---|---|
| **ezTask / CIRA** (TX Assoc. of Counties' own hosting program) | **58** | Easy — static PDF link pages, one template family |
| CivicPlus / CivicEngage | 24 | Easy-medium — consistent agenda-center URL scheme |
| CivicClerk | 14 | Easy — JSON API behind the portal |
| custom PDF pages | ~17 | Medium — per-county but simple |
| Legistar (Granicus) | 6 | Easy — documented REST API |
| Revize / EasyDocs / Destiny / CivicWeb / AgendaSuite / Granicus / others | ~33 | Medium — small clusters |

**Three template families (CIRA + CivicPlus + CivicClerk) cover 96 of the 152 counties
with online minutes.** Legistar's public API adds 6 more with near-zero effort.

## Clerk records portals (live, 107 counties)

Fragmented vendor market: Neumo (16), Tyler family (≈20 across variants), LGS (10),
Kofile (6), TexasFile (5), US-Recorder/PublicSearch/others (small clusters). Most
require per-search interaction (not bulk-downloadable) — useful as a per-project
lookup rung, not as a bulk archive target.

## Route forward (recommendation)

1. **Minutes harvester, platform-by-platform** (highest leverage first):
   CIRA/ezTask (58) → CivicClerk JSON (14) → CivicPlus (24) → Legistar API (6).
   Each family is one scraper; per county it's a handful of new PDFs per month
   (commissioners courts meet 1-4×/month), so a monthly incremental pull is tiny.
2. **Index, don't read**: store PDFs under `data/reference/county_minutes/<county>/`
   (gitignored) + a text-extraction index (INR-style keyword scan: project names, SPV
   names, "reinvestment zone", "abatement", "solar", "wind", "battery") — the same
   pattern as `inr_harvest.py`'s docket→INR join. The index becomes a resolver:
   `minutes.py resolve <INR>` → meetings that mention the project/SPV/zone.
3. **Backfill depth**: most portals expose 2-5+ years of archives — enough to cover the
   whole current queue's development window.
4. The 43 counties without online minutes are mostly tiny (Kenedy, Loving, King...) —
   they publish legal notices in local papers instead; treat as per-project manual rungs.
5. Clerk portals: keep as a documented per-project lookup table (the census JSON already
   carries the URL + vendor per county); no bulk harvest.

## Provenance / caveats

- Agent-collected URLs are only as good as one pass; the probe layer catches dead links
  but not *missed* links — counties marked "none-found" for minutes may still have them
  behind an unusual nav path. Treat "none-found" as weak-negative (same convention as
  ch312.py).
- 15 sites are bot-hostile (403) or have broken TLS from this container; their minutes
  URLs often still work (Galveston, Anderson, Brewster, Jack, Kerr, Eastland).
- Session note: the first agent wave burned the harness WebSearch session budget (200);
  retry/fix waves ran on `search.py` (OAuth bridge). Future re-census should use
  `search.py` from the start.
