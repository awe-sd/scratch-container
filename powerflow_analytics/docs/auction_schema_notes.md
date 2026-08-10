# ERCOT CRR / Auction Schema Intelligence Notes

Purpose: valuing ERCOT CRR paths for the Sep-2026 monthly auction (FTRBIDMARKETID = 626091), price classes 2 (OnPeak 5x16) and 6 (OffPeak). Read-only exploration for a later coding agent. All queries run via Snowflake (`awconnect.snowflake.performQuery`), warehouse AI_READ_ONLY, `read_only` profile.

## 1. AW.DBO.FTROPTIONPRICEMARKVIEW and underlying table

`FTROPTIONPRICEMARKVIEW` DDL (via `GET_DDL('VIEW', 'AW.DBO.FTROPTIONPRICEMARKVIEW')`) shows it is built from:

```
FROM aw.dbo.ftrOptionPriceMark AS m_1
INNER JOIN aw.dbo.cpnode ON m_1.sinkcpNodeId = cpnode.cpnodeid          -- sink display name
INNER JOIN aw.dbo.cpnode AS cpnode_1 ON m_1.sourcecpNodeId = cpnode_1.cpnodeid  -- source display name
INNER JOIN aw.dbo.awDateMonthView AS d ON YEAR(priceDate)=d.year AND MONTH(priceDate)=d.month
LEFT OUTER JOIN aw.dbo.ftrBidMarket ON m_1.ftrBidMarketId = ftrBidMarket.ftrBidMarketId
WHERE (markVersionId = 2 AND isomarketid = 6) OR (markVersionId = 1 AND isomarketid <> 6)
```

**Underlying table: `AW.DBO.FTROPTIONPRICEMARK`** — this is where `PRICECLASSID` actually lives (confirmed present in the base table itself, not derived).

Columns (`DESCRIBE TABLE DBO.FTROPTIONPRICEMARK`):
| column | type |
|---|---|
| ISOMARKETID | NUMBER(10,0) |
| SOURCECPNODEID | NUMBER(10,0) |
| SINKCPNODEID | NUMBER(10,0) |
| FTRBIDMARKETID | NUMBER(10,0) |
| EFFECTIVEDATE | DATE |
| PRICEDATE | DATE |
| PRICECLASSID | NUMBER(10,0) |
| PRICEMWH | FLOAT |
| MARKTYPEID | NUMBER(10,0) |
| PRICEDATEENDOFMONTH | DATE |
| MARKVERSIONID | NUMBER(10,0) |

Grain: one row per (isomarketid, sourceCpNodeId, sinkCpNodeId, ftrBidMarketId, priceDate, priceClassId, markTypeId, markVersionId, effectiveDate). Multiple effectiveDate snapshots exist per priceDate (mark curve moves over time as bid-in-progress), so filter to the latest `effectiveDate` (or the view's `markVersionId` rule: `markVersionId=2` for ISOMARKETID=6/ERCOT, else `markVersionId=1`) to get the "current" mark.

`IS_IMPLIED_PRICE` in the view = `CASE WHEN markTypeId > 1 THEN 1 ELSE 0 END` — so `MARKTYPEID = 1` is the "real"/base price, `MARKTYPEID` 2-5 are implied/derived variants (likely successive round or model adjustments — not fully confirmed from data dictionary; empirically markTypeId 5 has by far the largest row count so is probably the primary published mark type. Verify with the mark-market owner if precision matters).

### Key finding: FTRBIDMARKETID = 626091 (2026.SEP.Monthly.Auction) has NO rows in FTROPTIONPRICEMARK

`SELECT * FROM DBO.FTRBIDMARKET WHERE ftrBidMarketId=626091` returns:

| FTRBIDMARKETID | ISOMARKETID | FTRBIDMARKETNAME | ROUNDNUM | OPENDATE | CLOSEDATE | RESULTDATE | FTRBIDMARKETTYPE | TERMBEGINDATE | TERMENDDATE | YESAUCTIONDATE |
|---|---|---|---|---|---|---|---|---|---|---|
| 626091 | 6 | 2026.SEP.Monthly.Auction | 1 | 2026-08-11 | 2026-08-13 | 2026-08-20 | Monthly | 2026-09-01 | 2026-09-30 | 2026-08-01 |

This auction has not opened/cleared yet (opens 2026-08-11, results 2026-08-20 — in the future relative to "today"). So `FTROPTIONPRICEMARK` never has rows keyed to `ftrBidMarketId=626091` itself — **the "mark" for a not-yet-cleared monthly auction period is instead pulled from the most recent overlapping ANNUAL auction** whose term covers that month. For Sep-2026 (which falls in 2026 H2), the relevant annual auctions are the "2026.2nd6.AnnualAuction" sequence (TERMBEGINDATE 2026-07-01 / TERMENDDATE 2026-12-31):

| FTRBIDMARKETID | FTRBIDMARKETNAME | ROUNDNUM | RESULTDATE |
|---|---|---|---|
| 626266 | 2026.2nd6.AnnualAuction.Seq6 | 1 | 2024-04-04 |
| 626265 | 2026.2nd6.AnnualAuction.Seq5 | 2 | 2024-09-05 |
| 626264 | 2026.2nd6.AnnualAuction.Seq4 | 3 | 2025-02-06 |
| 626263 | 2026.2nd6.AnnualAuction.Seq3 | 4 | 2025-07-10 |
| 626262 | 2026.2nd6.AnnualAuction.Seq2 | 5 | 2025-12-04 |
| 626261 | 2026.2nd6.AnnualAuction.Seq1 | 6 | 2026-04-30 |

`FTROPTIONPRICEMARK` rows with `priceDate='2026-09-01'` and `isomarketid=6` exist under these `ftrBidMarketId`s (626261-626266), each with multiple `markTypeId` (1-5) and `markVersionId` (1,2) combos and large row counts (thousands to millions of source/sink pairs x markType combos). **Use `626261` (Seq1, the most recent/most-cleared annual round, resultDate 2026-04-30) as the best "current mark" proxy for pricing the Sep-2026 monthly auction**, filtered to `priceClassId IN (2,6)`.

### Recommended query pattern for a mark

```sql
SELECT sourcecpnodeid, sinkcpnodeid, priceClassId, markTypeId, priceMWH, effectiveDate
FROM AW.DBO.FTROPTIONPRICEMARK
WHERE isomarketid = 6
  AND priceDate = '2026-09-01'
  AND priceClassId IN (2,6)
  AND ftrBidMarketId = 626261         -- most recent overlapping annual auction (Seq1)
  AND sourcecpnodeid = <src> AND sinkcpnodeid = <sink>
ORDER BY effectiveDate DESC, markTypeId
LIMIT 10;
```
Then pick the desired `markTypeId` (start with 5, cross check against 1) and the latest `effectiveDate`.

No sibling tables matched `SHOW TABLES LIKE 'FTROPTIONPRICE%' IN AW.DBO` besides the one table (query returned only 1 row = the table itself catalogued alongside the view name pattern search — re-verify with `SHOW TABLES LIKE '%MARK%' IN AW.DBO` if more mark-related tables are needed later).

## 2. AWVAL.DBO.FWDAUCTIONDECOMPBYPATH — NOT ACCESSIBLE

`SHOW DATABASES` from this read-only role only exposes: `AW`, `AWCOLLECT`, `AWDEV`, `AWOPF`, `AWST`, `SHIFT_FACTORS`, plus Snowflake system databases. **`AWVAL` does not exist / is not granted to this role.** `SHOW TABLES IN AWVAL.DBO` errors with "Object does not exist, or operation cannot be performed."

**Closest available equivalent found in `AW.DBO`: the `DECOMPORTAUCT*` family** (see `SHOW TABLES LIKE '%DECOMP%' IN AW.DBO`):

| table | rows (approx) | purpose |
|---|---|---|
| DECOMPORTAUCTREF | 91 | one row per auction-decomp run: `FTRBIDMARKETID`, `FTRPERIODID`, `PRICECLASSID`, `PSENSHIFTSETID`, `CUTOFFMW`, `CUTOFFCOST` |
| DECOMPORTAUCTBYPATH | 41.1M | per (ref, owner, priceClass, source, sink, ftrBindingId): `EQFLOWMW`, `EQCOST` |
| DECOMPORTAUCTBYPATHALL | 906M | per (ref, source, sink, ftrBindingId), **owner-agnostic**: `PATHSF` (path shift factor), `EQCOST` — this is the one to use for pure path economics, independent of who holds the FTR |
| DECOMPORTAUCTBYCON | 5,261 | per (ref, ftrBindingId): `EQFLOWMW`, `EQCOST` — constraint-level rollup keyed by `FTRBINDINGID` (join to a binding/constraint table, not yet explored) |
| DECOMPORTAUCTBYOWNER | 1.1M | per (ref, ftrBindingId, ftrOwnerId): `EQFLOWMW`, `EQCOST` |
| DECOMPORTAUCTERROR | 28 | error log for the decomp run |

`DECOMPORTAUCTREF` links to `FTRBIDMARKETID` and `PRICECLASSID` directly — so **for the forward/annual auction decomposition, filter `DECOMPORTAUCTREF` to the desired `FTRBIDMARKETID` (e.g. 626261, the Seq1 annual auction covering Sep-2026) and `PRICECLASSID IN (2,6)`, take its `DECOMPORTAUCTREFID`, then join to `DECOMPORTAUCTBYPATH`/`BYPATHALL` on that id + source/sink cpnode**.

The "SF from current auction model x avg shadow price from previous auction" decomposition the user described is NOT literally spelled out as separate columns — `PATHSF` (path shift factor from the current model) and `EQCOST` (the $ decomposition, presumably PATHSF × the historical/prior shadow price for that constraint) are the two outputs; the multiplication appears to already be baked into `EQCOST` per (ref, constraint/binding). To get the "SF x avg shadow price" breakdown explicitly, you'd need `DECOMPORTAUCTBYCON` (constraint-level EQFLOWMW/EQCOST) joined against a constraint shadow-price history table (see FTRRESULTDEFCONSTRAINT / lambda tables in sections 5-6, not yet cross-joined here — flag for the coding agent to verify column-level provenance with the data-eng team if exact decomposition math matters).

Could not confirm sibling tables in `AWVAL.DBO` since the database itself is inaccessible — **flag this as a blocking gap**: either request AWVAL grants, or treat `AW.DBO.DECOMPORTAUCTBYPATHALL` + `DECOMPORTAUCTREF` as the working substitute for forward-auction-model decomposition.

## 3. AW.DBO.DECOMPORTDARTBYPATH (daily DA decomposition) + siblings

`SHOW TABLES LIKE '%DECOMP%' IN AW.DBO` confirms the full `DECOMPORTDART*` family (DA/RT congestion decomposition, i.e. actual settled DART value by path):

| table | rows (approx) | columns (PK cols first) |
|---|---|---|
| DECOMPORTDARTREF | 65,055 | `DECOMPORTDARTREFID` (PK), `CREATEDDATETIME`, `PSENSHIFTSETID`, `ISOMARKETID`, `HE` (hour-ending), `PRICETYPEID`, `PRICECLASSID`, `TOUTSETID`, `DECOMDESCRIPTION`, `CUTOFFMW`, `CUTOFFREVENUE`, `DATE`, `QUERY_ID` |
| DECOMPORTDARTBYPATH | 37.4B | `DECOMPORTDARTREFID`, `FTROWNERID`, `HEDGETYPEID`, `PRICECLASSID`, `SOURCECPNODEID`, `SINKCPNODEID`, `CONGCONSTRAINTID` (composite PK) + `EQFLOWMW`, `EQREVENUE` — **owner-specific** (real FTR holdings), grain = one row per ref (i.e. per hour) per owner per hedge type per path per binding constraint |
| **DECOMPORTDARTBYPATHALL** | 2.6B | `DECOMPORTDARTREFID`, `SOURCECPNODEID`, `SINKCPNODEID`, `CONGCONSTRAINTID` (PK) + `PATHSF`, `EQREVENUE` — **owner-agnostic, this is the one for path valuation / short-risk screening**: grain = one row per ref (= one hour) per path per binding constraint, giving the path's shift factor on that constraint and its $ revenue/cost contribution that hour |
| DECOMPORTDARTBYPOSITION | 10.3B | per (ref, ftrOwnerId?, position) — not detailed further; likely position-level (not path-level) rollup |
| DECOMPORTDARTBYCON | 2.58M | `DECOMPORTDARTREFID`, `HEDGETYPEID`, `CONGCONSTRAINTID` (PK) + `EQFLOWMW`, `EQREVENUE` — constraint-level rollup |
| DECOMPORTDARTBYOWNER | 468M | owner-level rollup |
| DECOMPORTDARTERROR | 51,744 | error log |

**Grain confirmed: `DECOMPORTDARTREF` is per HOUR, not per day** — sample rows show `DATE='2026-08-11'`, `HE=24/16/13`, each with a distinct `PSENSHIFTSETID` and its own `DECOMPORTDARTREFID`. `PRICECLASSID` on the ref row (seen value 3) is unrelated to the price class filter you actually want on `BYPATH`/`BYPATHALL` (2/6) — **filter on the BYPATH/BYPATHALL row's own `PRICECLASSID` where present (BYPATH only, not BYPATHALL, which has no priceClassId column — BYPATHALL is class-agnostic, i.e. it reflects the RT/DA flow decomposition for the path regardless of TOU bucket; roll up to on/off-peak by joining `DECOMPORTDARTREF.HE` against an on/off-peak hour calendar, or by using `DECOMPORTDARTBYPATH` which does carry `PRICECLASSID` directly but is owner-specific).**

Sample `DECOMPORTDARTBYPATH` row: `DECOMPORTDARTREFID=4916, FTROWNERID=2925, HEDGETYPEID=2, PRICECLASSID=2, SOURCECPNODEID=12724, SINKCPNODEID=12647, CONGCONSTRAINTID=117913, EQFLOWMW=0.0, EQREVENUE=0.0`. Sample `DECOMPORTDARTBYPATHALL` row: `DECOMPORTDARTREFID=23001, SOURCECPNODEID=55768, SINKCPNODEID=44610, CONGCONSTRAINTID=61945, PATHSF=-0.028, EQREVENUE=-0.217196`.

`HEDGETYPEID` observed values: `{1, 2}` (meaning not yet confirmed from a dimension table — likely 1=Obligation, 2=Option, matching FTR product types; verify against `FTROWNER`/product docs before using).

**"The mappings using the other decompportdart table" (user's hint) = `DECOMPORTDARTBYCON`**: it gives, per `DECOMPORTDARTREFID` + `HEDGETYPEID`, the `CONGCONSTRAINTID` -> `EQFLOWMW`/`EQREVENUE` totals aggregated across ALL paths bound to that constraint that hour — use it to sanity-check/aggregate at the constraint level, while `BYPATH`/`BYPATHALL` give the per-path breakdown. In practice for the **short-risk screen you want `DECOMPORTDARTBYPATHALL`** (owner-agnostic, path+constraint+hour grain): for a candidate (source,sink), sum `EQREVENUE` grouped by `CONGCONSTRAINTID` and by `DATE` (joined via `DECOMPORTDARTREF.DECOMPORTDARTREFID -> DATE, HE`) over a trailing window to see which constraints drove losses ("short") vs gains ("long") for that path historically.

Recommended join chain for daily short-risk:
```sql
SELECT r.DATE, r.HE, p.CONGCONSTRAINTID, p.PATHSF, p.EQREVENUE
FROM AW.DBO.DECOMPORTDARTBYPATHALL p
JOIN AW.DBO.DECOMPORTDARTREF r ON p.DECOMPORTDARTREFID = r.DECOMPORTDARTREFID
WHERE p.SOURCECPNODEID = <src> AND p.SINKCPNODEID = <sink>
  AND r.DATE BETWEEN <start> AND <end>
ORDER BY r.DATE, r.HE;
```
Then bucket `HE` into on-peak (hours 7-22, i.e. price class 2) / off-peak (price class 6) per ERCOT convention, sum `EQREVENUE` by day/constraint to find recurring short constraints.

## 4. AW.DBO.SPTHRPRICEHOURLYVIEW

Columns (`DESCRIBE VIEW`): `AWDATEID`, `DATE`, `CPNODEID`, `DISPLAYNAME`, `ISOMARKETID`, `ISOMARKETNAME`, `PRICECOMPONENTID`, `PRICECOMPONENT`, `PRICETYPEID`, `PRICETYPE`, `HE`, `PRICE`, `PNODEID`, `NAME`, `VOLTAGE`, `EQUIPMENT`, `TYPE`, `ZONE`, `ZONEID`, `INSERTDATETIME`, `TERMINATEDATE`, `FTRNAME`, `VBNAME`, `WKDAY`, `HOLIDAY`, `SATURDAY`, `SUNDAY`, `HOLIDAYWEEKEND`, `HOLIDAYSUNDAY`, `HOURSONPEAK`, `HOURSOFFPEAK`, `HOURS7X8`, `HOURS2X16`, `HOURS6X8SUNDAY`, `HOURS24`, `REMAP`.

**Grain: one row per (CPNODEID, DATE, HE, PRICETYPEID, PRICECOMPONENTID) — a SINGLE-NODE hourly price, not a path/pair.** This view is multi-ISO (sample row showed `ISOMARKETID=1` = PJM) — **always filter `ISOMARKETID = 6`** for ERCOT.

For ERCOT (`ISOMARKETID=6`), `SELECT DISTINCT PRICECOMPONENTID, PRICECOMPONENT, PRICETYPEID, PRICETYPE` returns only:
| PRICECOMPONENTID | PRICECOMPONENT | PRICETYPEID | PRICETYPE |
|---|---|---|---|
| 1 | LMP | 1 | DA |
| 1 | LMP | 2 | RT |

So for ERCOT there's just one price component (full LMP, not decomposed into energy/congestion/loss here) and two price types (DA, RT). The `HOURSONPEAK`/`HOURSOFFPEAK`/etc. flag columns let you bucket by TOU/price-class without a separate join.

**To compute a path's (source, sink) RT or DA settle for a trailing window**: query this view twice (once per node, `CPNODEID = source` and `CPNODEID = sink`), filter `ISOMARKETID=6`, `PRICETYPEID` (1=DA or 2=RT), `PRICECOMPONENTID=1`, `DATE` in the trailing window, then join on `(DATE, HE)` and compute `sink.PRICE - source.PRICE` as the hourly path spread. Aggregate to daily/on-peak/off-peak using the `HOURSONPEAK`/`HOURSOFFPEAK` flags.

```sql
SELECT s.DATE, s.HE, s.PRICE AS sink_price, so.PRICE AS src_price, s.PRICE - so.PRICE AS spread
FROM AW.DBO.SPTHRPRICEHOURLYVIEW s
JOIN AW.DBO.SPTHRPRICEHOURLYVIEW so
  ON s.DATE = so.DATE AND s.HE = so.HE AND s.PRICETYPEID = so.PRICETYPEID AND s.PRICECOMPONENTID = so.PRICECOMPONENTID
WHERE s.ISOMARKETID = 6 AND so.ISOMARKETID = 6
  AND s.CPNODEID = <sink_cpnodeid> AND so.CPNODEID = <source_cpnodeid>
  AND s.PRICETYPEID = 2 AND s.PRICECOMPONENTID = 1
  AND s.DATE BETWEEN <start> AND <end>
ORDER BY s.DATE, s.HE;
```

## 5. FTR auction results tables

`SHOW TABLES LIKE 'FTR%' IN AW.DBO` full list (name, approx rows):
FTRBIDMARKET (1,849), FTRBIDMARKETPERIOD (7,368), FTRBIDMARKETPERIODCPNODE (1.88M), FTRBIDOWNER (338), FTRBIDS (23.5M), FTROPTIONPRICEMARK (451.6M, see section 1), FTROWNER (3,393), FTROWNER_AWEPPARENT (7), FTRPERIOD (2,607), FTRPOSITIONPERFORMANCEDAILY (1.6B, + two backup/delete-suffixed copies — ignore those), FTRPRICEMARK (116.8M), **FTRRESULTDEFCONSTRAINT (232,130)**, FTRRESULTDEFCONTINGENCY (16,716), FTRRESULTDEFMONITOR (58,201), FTRRESULTMARKMONTHLY (22.0M), **FTRRESULTOPTIONPRICE (39.0M)**, FTRRESULTPOSITION (103.5M), FTRRESULTPOSITIONAWCATALOG (484,799), FTRRESULTPOSITIONAWCONFIRMED (6.2M), FTRRESULTPRICE (46.9M), FTRRESULTSP (2.7M), FTR_OUTPUT_TMP (0, empty).

**`FTRRESULTDEFCONSTRAINT`**: `FTRCONSTRAINTID`, `ISOMARKETID`, `FTRMONITORID`, `FTRCONTINGENCYID` — a thin dimension mapping a constraint id to its monitored element (`FTRMONITORID` -> `FTRRESULTDEFMONITOR`) and contingency (`FTRCONTINGENCYID` -> `FTRRESULTDEFCONTINGENCY`); no source/sink/price columns itself.

**`FTRRESULTOPTIONPRICE`** — the table with **past auction clearing prices (ACPs) by path/price-class**: `FTRBIDMARKETPERIODID`, `SOURCECPNODEID`, `SINKCPNODEID`, `PRICECLASSID`, `PRICEPERIOD`, `PRICEMWH`. Grain: one row per (FTRBIDMARKETPERIODID, source, sink, priceClassId). Sample rows confirm PRICECLASSID 2 and 6 both present. Join `FTRBIDMARKETPERIODID -> FTRBIDMARKETPERIOD.FTRBIDMARKETID` to filter to a specific auction (e.g. prior Sep-of-year monthly auctions, or the annual auctions covering that month) and pull `PRICEMWH` as the historical ACP for that path/class.

```sql
SELECT p.FTRBIDMARKETID, o.SOURCECPNODEID, o.SINKCPNODEID, o.PRICECLASSID, o.PRICEMWH
FROM AW.DBO.FTRRESULTOPTIONPRICE o
JOIN AW.DBO.FTRBIDMARKETPERIOD p ON o.FTRBIDMARKETPERIODID = p.FTRBIDMARKETPERIODID
JOIN AW.DBO.FTRBIDMARKET m ON p.FTRBIDMARKETID = m.FTRBIDMARKETID
WHERE m.FTRBIDMARKETNAME ILIKE '%SEP.Monthly%'   -- e.g. find prior Sep monthly auctions
  AND o.PRICECLASSID IN (2,6)
  AND o.SOURCECPNODEID = <src> AND o.SINKCPNODEID = <sink>
ORDER BY m.RESULTDATE DESC;
```

`FTRRESULTPOSITION` is a holdings/award table (`FTRID`, `FTRBIDMARKETPERIODID`, `FTRBIDMARKETID`, `FTRPERIODID`, `ISOFTRID`, `FTROWNERID`, `TRADETYPEID`, `HEDGETYPEID`, `SOURCECPNODEID`, `SINKCPNODEID`, `PRICECLASSID`, `PRICEPERIOD`, `PRICEMWH`, `MW`, `INVENTORYTYPEID`, `WESTDCTIEID`) — this is what a specific owner was AWARDED (MW and clearing PRICEMWH) in a given auction; useful for finding what actually cleared in past monthly/annual auctions for a path, as opposed to `FTRRESULTOPTIONPRICE`'s pure price-only view.

`FTRRESULTPRICE` (`FTRBIDMARKETPERIODID`, `CPNODEID`, `PRICECLASSID`, `PRICEPERIOD`, `PRICEMWH`) is the single-node analog of `FTRRESULTOPTIONPRICE` (nodal price, not path spread) — path price = sink nodal price - source nodal price, consistent with how `FTRRESULTOPTIONPRICE` is presumably derived.

## 6. Price-class dimension

`SHOW TABLES LIKE '%PRICECLASS%'` in `AW.DBO` found `PRICECLASS` (8 rows) and `PRICECLASSHOUR` (14 rows) — no `AWVAL.DBO` equivalent checked (AWVAL inaccessible, see section 2).

Full dump of `AW.DBO.PRICECLASS`:
| PRICECLASSID | CLASSNAME | DESCRIPTION | NODALCLASSNAME |
|---|---|---|---|
| 1 | OffPeak | OffPeak | Off Peak |
| 2 | OnPeak | OnPeak | On Peak |
| 3 | 24H | 24H | (null) |
| 4 | OnPeak6x16 | OnPeak6x16 | (null) |
| 5 | OffPeak2x16 | Weekend2x16 | 2x16 |
| 6 | OffPeak7x8 | OffPeak7x8 | 7x8 |
| 7 | Standard Fixed | Standard Fixed for Henry Hub | Standard Fixed |
| 8 | Offpeak1x24_6x8 | caisoOffPeak | caisoOffPeak |

**Confirms the task's price classes: PRICECLASSID=2 is "OnPeak" (the 5x16 on-peak weekday block) and PRICECLASSID=6 is "OffPeak7x8" (the 7x8 off-peak block).** Note ERCOT's on-peak defn is Mon-Sat HE7-22 (16 hrs, 6 days = "6x16"), which appears to map to PRICECLASSID=2 generically ("OnPeak") rather than the more specific PRICECLASSID=4 ("OnPeak6x16") — verify which of 2 vs 4 the FTR auction system actually uses for on-peak by cross-checking `PRICECLASSHOUR` (not dumped here due to query budget; do this before coding).

## 7. System lambda + load/wind/solar actuals

**`AW.DBO.ERCOTSYSTEMLAMBDA`**: columns `AWDATEID`, `HE`, `SYSTEMLAMBDA`, `PRICETYPEID`. Grain: one row per (AWDATEID, HE, PRICETYPEID) — hourly ERCOT system lambda (shadow price of the binding energy balance constraint, i.e. approx system marginal energy price pre-congestion). `PRICETYPEID` distinct values are `{1, 2}` — presumably 1=DA, 2=RT (consistent with the DA/RT convention seen in `SPTHRPRICEHOURLYVIEW`/`DECOMPORTDARTREF`, but not independently confirmed via a dimension table here — verify against `FTRRESULTPRICE`/similar PRICETYPEID usage before assuming). `AWDATEID` is a date-dimension surrogate key (seen values like 46244) — join via `AW.DBO.AWDATE`-style table (not explored) or `awDateMonthView`/similar (seen in section 1's view DDL) to convert to a calendar date.

**Hourly ERCOT load actuals and wind/solar generation actuals**: **NOT FOUND under the expected names.** Searched `SHOW TABLES LIKE 'ERCOTLOAD%'` (only estimation/distribution-factor tables: `ERCOTLOADDF`, `ERCOTLOADDISTRIBUTIONFACTORS`, `ERCOTLOADESTIMATION_*`, `ERCOTLOADESTIMATION_BRANCH_MAPPING` (0 rows) — these look like transmission-loss/distribution-factor tooling, not simple load actuals). Searched `SHOW TABLES/VIEWS LIKE '%WIND%'` — only `WEATHERWINDUNITMAPPING` (32 rows) and `WIND_TURBINE_USWTDB_RAW` (76,051 rows, looks like a US wind turbine database reference table, not generation actuals). Searched `%SOLAR%`, `%ACTUAL%`, `%GENACT%`, `%GENERATIONACT%`, `%LOADVIEW%`, `%WINDVIEW%`, `%WINDGEN%`, `%SOLARGEN%` as both tables and views — no hits except `LDFCSTLOADVIEW` and `SELOADVIEWSPP` (load-forecast-related views, not explored further; names suggest "load forecast" and "SE load view SPP" — possibly worth a follow-up `DESCRIBE VIEW` if load actuals turn out to live there). Installed wind/solar capacity over time: not located either — no `%CAPACITY%` table besides ERCOT ancillary-capacity clearing-price tables (`ERCOTDAMCLEARINGPRICESFORCAPACITY`, `ERCOTPUNCAPACITY`, `ERCOTRTCLEARINGPRICESFORCAPACITY*`), which are unrelated (these are ancillary service capacity market prices, not installed nameplate capacity).

**Flag for coding agent**: load/wind/solar actuals and installed capacity likely live either (a) under a naming convention not yet guessed (e.g. an EIA- or ERCOT-source-prefixed table, possibly in `AWCOLLECT` rather than `AW`), or (b) require checking `LDFCSTLOADVIEW`/`SELOADVIEWSPP` and broader `SHOW TABLES IN AWCOLLECT.DBO` (only spot-checked for `%DECOMP%` there, found `FLOWDECOMPPRECALC*` tables which hint AWCOLLECT holds other raw/precalc collection tables worth a fuller sweep). Do a follow-up `SHOW TABLES IN AWCOLLECT.DBO` / `SHOW TABLES LIKE '%ERCOT%' IN AWCOLLECT.DBO` pass before building the system-lambda conditional model.

## 8. CPNODE dimension

**`AW.DBO.CPNODE`** is the join glue. Columns: `CPNODEID`, `PNODEID`, `NAME`, `VOLTAGE`, `EQUIPMENT`, `TYPE`, `ZONE`, `ZONEID`, `INSERTDATETIME`, `TERMINATEDATE`, `ISOMARKETID`, `FTRNAME`, `VBNAME`, `DISPLAYNAME`, `FTRMARKETVALID`, `VBVALID`, `UTCVALID`, `STARTAWDATEID`, `UNIQUENAME`, `ISOSUBREGIONID`.

Grain: one row per CPNODE version (a settlement point can have multiple rows over time as it's renamed/superseded — see `TERMINATEDATE`, sample rows show placeholder terminate date `2079-06-06` for currently-active nodes, and `DISPLAYNAME` values like `'delete 35911'` / `'deprecated-17944'` for retired/merged nodes — **filter `TERMINATEDATE > CURRENT_DATE()` or check `DISPLAYNAME` doesn't start with 'delete'/'deprecated' to get only live nodes**). `ISOMARKETID=6` scopes to ERCOT. `DISPLAYNAME`/`UNIQUENAME` are the human-readable settlement-point names; `PNODEID` links to a separate pricing-node id (used elsewhere, e.g. `SPTHRPRICEHOURLYVIEW.PNODEID`); `FTRNAME`/`VBNAME` are the names used specifically in FTR bidding and virtual-bidding contexts.

`AW.DBO.CPNODE_SHIFTS_VIEW` referenced by the user **does not exist / not authorized** under this role (`View 'AW.DBO.CPNODE_SHIFTS_VIEW' does not exist or not authorized` — could be a typo for a different view name, could be schema-qualified elsewhere, or could require different grants; flag for coding agent to re-check with broader `SHOW VIEWS LIKE '%SHIFT%' IN AW.DBO` if shift-factor-to-cpnode mapping is needed beyond what `PSENSHIFTSETID` in the decomp tables already implies).

**Every table in sections 1-5 that uses `SOURCECPNODEID`/`SINKCPNODEID`/`CPNODEID` joins back to `AW.DBO.CPNODE.CPNODEID`** to resolve a human-readable path name — this is the glue between marks (section 1), auction/DART decomp (sections 2-3), settles (section 4), and FTR results (section 5).

## Coding-agent quickstart

**(a) Price a candidate path's auction cost for Sep-2026 (FTRBIDMARKETID=626091), price classes 2 & 6:**
1. Since 626091 hasn't cleared (opens 2026-08-11, results 2026-08-20), get the "mark" from the most recent overlapping ANNUAL auction: `AW.DBO.FTROPTIONPRICEMARK` filtered `isomarketid=6, ftrBidMarketId=626261 (Seq1, resultDate 2026-04-30), priceDate='2026-09-01', priceClassId IN (2,6), sourcecpnodeid=<src>, sinkcpnodeid=<sink>`, taking the latest `effectiveDate` and preferred `markTypeId` (verify 1 vs 5 semantics first).
2. Cross-check / supplement with **prior actual auction clearing prices** from `AW.DBO.FTRRESULTOPTIONPRICE` joined through `FTRBIDMARKETPERIOD` -> `FTRBIDMARKET` for past Sep-monthly and 2nd-half-annual auctions on the same path/priceClassId, to sanity check the mark against realized ACPs.
3. Resolve `<src>`/`<sink>` cpnode ids from `AW.DBO.CPNODE` by `DISPLAYNAME`/`UNIQUENAME`, filtering `ISOMARKETID=6` and excluding deprecated/deleted rows.

**(b) Compute a path's trailing short-risk from decomp:**
1. Use `AW.DBO.DECOMPORTDARTBYPATHALL` (owner-agnostic, hourly grain) joined to `AW.DBO.DECOMPORTDARTREF` on `DECOMPORTDARTREFID` to get `DATE`/`HE` for each row.
2. Filter `SOURCECPNODEID`/`SINKCPNODEID` to the candidate path, `DATE` to the trailing window.
3. Bucket `HE` into on-peak/off-peak via ERCOT convention (or use `DECOMPORTDARTBYPATH`, which carries `PRICECLASSID` directly, at the cost of being owner-specific — sum across `FTROWNERID` to approximate market-wide if going that route).
4. Group by `CONGCONSTRAINTID` and sum `EQREVENUE` — negative sums flag constraints where the path was chronically "short" (paying congestion) over the window; use `DECOMPORTDARTBYCON` to cross-check constraint-level totals.
5. For the forward/auction-model side of the same analysis (SF-from-current-model x shadow-price-from-prior-auction), use `AW.DBO.DECOMPORTAUCTBYPATHALL` + `DECOMPORTAUCTREF` (filtered to the relevant `FTRBIDMARKETID`/`PRICECLASSID`) as the substitute for the inaccessible `AWVAL.DBO.FWDAUCTIONDECOMPBYPATH`.

**(c) Pull a path's RT settle history:**
1. Query `AW.DBO.SPTHRPRICEHOURLYVIEW` twice (sink cpnodeid, source cpnodeid), `ISOMARKETID=6`, `PRICETYPEID=2` (RT) or `1` (DA), `PRICECOMPONENTID=1` (only LMP exists for ERCOT in this view).
2. Join on `(DATE, HE)`, compute `sink.PRICE - source.PRICE`.
3. Aggregate to on-peak/off-peak using the view's own `HOURSONPEAK`/`HOURSOFFPEAK` flag columns (no separate calendar join needed).

**Known gaps / blockers for the coding agent to resolve before or during build:**
- `AWVAL` database is not accessible from this read-only role at all — either get it granted, or commit to the `AW.DBO.DECOMPORTAUCT*` substitute documented in section 2.
- Load/wind/solar actuals and installed capacity tables were not found under any guessed naming convention in `AW.DBO`; a fuller sweep of `AWCOLLECT.DBO` (and possibly other databases/roles) is needed — start with `LDFCSTLOADVIEW`, `SELOADVIEWSPP`, and `SHOW TABLES LIKE '%ERCOT%' IN AWCOLLECT.DBO`.
- `CPNODE_SHIFTS_VIEW` does not exist/is not authorized under this name — re-verify the actual shift-factor-to-cpnode mapping object.
- `MARKTYPEID` (1-5) and `HEDGETYPEID` (1,2) semantics in the mark/decomp tables were inferred from row-count heuristics and the view's `IS_IMPLIED_PRICE` CASE expression, not from an explicit dimension table — worth 5 minutes of verification before trusting exact values in a pricing model.
- Whether ERCOT's FTR system treats on-peak as `PRICECLASSID=2` ("OnPeak") vs `PRICECLASSID=4` ("OnPeak6x16") was not fully disambiguated — dump `AW.DBO.PRICECLASSHOUR` to confirm hour definitions match ERCOT's 6x16 on-peak convention before trusting PRICECLASSID=2 rows.


