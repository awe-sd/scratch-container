# Summer-2026 constraint study — August watch-list + 6945 wind-skew

*analytics-dev side project. Data: one-time read-only pull from AW (SQL Server dbo)
into `analytics/data/*.parquet` on 2026-07-14. No DB tables touched.*

Sources: `congHrPrice` (hourly binding shadow prices, DA=priceTypeID 1 / RT=2,
congTypeID 1) joined to `congDefConstraint`/`congDefMonitor`/`congDefContingency`,
`ercotLoadView` (WZ actual load), `windGenAct`/`solarGenAct` isoZone 67 (ERCOT_ALL),
`ercotWindRegionHourly` (regional wind). Constraint naming variants deduped by
parsing monitored element + contingency out of `isoConstraintName` (`ckey`).

## 1. Highest net-load days, summer 2026 (peak hourly net load = load − wind − solar)

Top days: **Jul 13 (66.9 GW net!), Jul 6, Jul 7, Jul 4, Jul 8, Jun 15, Jul 3, Jun 1,
Jul 1, Jun 22, Jul 5, Jun 19, Jul 12, Jun 16, May 28** (full table:
`summer26_daily_load_ranking.csv`). Jul 13 peaked at only 73.3 GW load but 66.9 GW
net — a renewable-drought day; the early-July run is the stress period the August
list keys off.

## 2. August watch-list (`august_watchlist.csv`, scored)

Score = top-day presence + shadow-price mass on top days + net-load lift
+ Aug-2025 prior + last-3-week trend.

### A. Peak-load-driven with an Aug-2025 pedigree (expect them back in August)
| Constraint (elem \| cont) | Evidence |
|---|---|
| **SANA 138/69 xf \| SCOLBAL8** | lift 1.6, Aug-25: 30 days, max SP $3,475 |
| **TWINBU–HARGROVE 138 \| DBAKCED5** | 14/15 top days; Aug-25: 31 days, max SP $2,834 |
| **LPLMK–LPLNE 115 \| SBWDDBM5** | 15/15 top days; Aug-25 all 31 days (Lubbock area) |
| **SCRCV–KNAPP 138 \| DMTSCOS5** | 14/15 top days; Aug-25: 28 days, max SP $1,036 |
| **BRAUNIG–HOWARD 345 \| DSKYCAL5** | lift 3.8 (San Antonio load pocket); Aug-25: 19 days |
| **DUNLAP–DECKER 138 \| SDAFAUS8** | lift 7.1 (Austin); Aug-25: 15 days |
| **INTF AJO_ZO (base)** | interface, 15/15 top days; Aug-25 all 31 days, max SP $980 |

### B. New-in-2026 and ramping into the peak (no Aug-25 history — explosion candidates)
| Constraint | Evidence |
|---|---|
| **SEA 138/69 xf \| DFRYTM58** | lift 1.8, $26k SP on top days, $41.7k in last 3 weeks — hottest new name |
| **CRDSW–OLNEY 69 \| D/SGRMGRS8** | 14/15 top days, max SP $2,710, $60k SP last 3 weeks combined |
| **LAKENASW–SAMATHIS 69 \| DBAKCED5** | 14/15 top days, max SP $2,761, $66k SP on top days |
| **SALDS–SONTERRA 138 \| DSALHUT5** | $30.8k SP last 3 weeks, all recent |
| **MEXTP–ITALY 69 \| SBLURDH8/SBLAWDB8** | load-driven (lift 2–4.8), max SP $624 |
| **6945 MGSES–CATSW 345 \| SRGRMGS5** | 13/15 top days, RT max SP $1,184 — see §3 |

Honorable mentions: NLARSW–PILONCIL 138, PALOUSE–WOLFCAMP 138 (DBIGSCH5),
TREADWEL–YELWJCKT 138 (DBIGKEN5), NEWMAN–WALNUT1 138 (El Paso-ish, lift 4.9).

## 3. 6945 (MGSES 345 kV → CATSW 345 kV) — West vs Panhandle wind skew

Summer-2026 hourly universe 1,754 hrs; 667 binding (DA 640, RT 164; dominant
contingency **SRGRMGS5**, minor MRGRMGS5). New constraint family (first defs
Dec-2025) — no Aug-2025 prior.

**The skew is real and it is LOW West wind relative to Panhandle**, not high-West:

- Binding hours: West wind **6.7 GW vs 9.4 GW** in non-binding hours (−0.35 σ);
  Panhandle roughly flat (−0.11 σ); **Pan-minus-West spread +0.37 σ**.
- P(bind) grid (Pan × West terciles): highest at **low-West wind (0.44–0.61)**
  across all Panhandle terciles, and within low-West, mid/high Panhandle raises it
  (0.61 vs 0.44). High-West wind kills it (0.13–0.21).
- Load: binding skews to **high system net load (+0.50 σ)** but **LOW West-zone
  load (−0.48 σ)**; RT SP corr with West-zone load −0.46. So the user-hypothesized
  "high West load + high Pan wind" is half-right: it's **high Panhandle-relative-
  to-West wind, LOW West-zone load, high system net load**. Best cell: low
  West-load tercile × high (Pan−West) spread → **P(bind)=0.79**.

August read: 6945 should spike on high net-load evenings when West wind dies
while Panhandle carries — exactly the renewable-drought/peak pattern of Jul 4–13.

## Caveats
- Regional wind after 2026-05-14 comes from `ercotWindRegionHourly` rows flagged
  isActual=0, but their 5-region sum matches ERCOT_ALL actual wind 1:1 (corr
  1.000) — treated as actuals with a stale flag.
- `windGenActByWeatherZone`/`solarGenActByWeatherZone` are dead (stop 2025-01-13).
- `ercotCongConstRecord`/`ercot_sppCongConstRecord` analyst notes end in 2020 —
  no 2026 analyst overlay available.
- DA binds ~4× more hours than RT; watch-list mixes both (sp_sum dominated by DA
  except where noted).
