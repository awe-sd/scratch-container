"""Extend station weather past NOAA's bucket staleness via Iowa Mesonet ASOS.

The noaa-global-hourly-pds bucket truncates ~2025-08-25 and has no 2026 files
(confirmed 2026-08-14). This module patches the gap from the Iowa Environmental
Mesonet ASOS archive (https://mesonet.agron.iastate.edu — the CLAUDE.md-named
fallback) so 2025 completes and 2026 exists → true out-of-sample benchmarking.

Reuses pull_weather's pipeline verbatim (qc_physical → collapse → UTC grid →
interp ≤3h → hour-ending CPT labels), so conventions cannot drift. Mesonet rows
are marked qc_flag='mesonet' (raw-equivalent, different provenance); NOAA data
always wins where present.

Merge per station-year: load existing NOAA parquet if any; fill ONLY hours where
NOAA temp is NaN; write {station}_{year}.parquet in place (2026 = pure mesonet).
zone_weather.py picks the patched files up on its next run, unchanged.

Run:  uv run python load-forecast/src/pull_weather_mesonet.py [--from-date 2025-08-01]
"""
from __future__ import annotations

import argparse
import io
import sys
import time
from pathlib import Path

import pandas as pd
import requests

sys.path.insert(0, str(Path(__file__).parent))
import config as cfg
import pull_weather as pw

MESONET_URL = "https://mesonet.agron.iastate.edu/cgi-bin/request/asos.py"
ISD_HISTORY = cfg.RAW_DIR / "crosswalk" / "isd-history.csv"
CROSSWALK = cfg.DERIVED_DIR / "crosswalk_county_station.csv"


def station_icaos() -> dict[str, str]:
    """crosswalk station_id → Mesonet station code (ICAO, leading K stripped)."""
    cw = pd.read_csv(CROSSWALK, dtype=str)
    hist = pd.read_csv(ISD_HISTORY, dtype=str)
    hist["station_id"] = hist["USAF"] + "-" + hist["WBAN"]
    icao = hist.drop_duplicates("station_id").set_index("station_id")["ICAO"].str.strip()
    out = {}
    for sid in sorted(cw["station_id"].unique()):
        code = icao.get(sid, "")
        if not isinstance(code, str) or len(code) < 3:
            print(f"NEEDS_CONTEXT: no ICAO for {sid} in isd-history — cannot query Mesonet")
            sys.exit(2)
        out[sid] = code[1:] if len(code) == 4 and code.startswith("K") else code
    return out


def fetch_mesonet(code: str, start: str, end: str, session: requests.Session) -> pd.DataFrame:
    """One station's routine-hourly obs [ts_utc, report_type, temp_f, dewpoint_f]."""
    params = {
        "station": code, "data": "tmpf,dwpf",
        "year1": start[:4], "month1": start[5:7], "day1": start[8:10],
        "year2": end[:4], "month2": end[5:7], "day2": end[8:10],
        "tz": "Etc/UTC", "format": "onlycomma", "latlon": "no", "elev": "no",
        "missing": "M", "trace": "T", "direct": "no", "report_type": "3",
    }
    # IEM rate-limits aggressively (429 seen at ~14 stations back-to-back):
    # retry with growing backoff rather than dying mid-batch.
    for attempt in range(5):
        resp = session.get(MESONET_URL, params=params, timeout=300)
        if resp.status_code != 429:
            break
        wait = 30 * (attempt + 1)
        print(f"    429 from IEM — backing off {wait}s")
        time.sleep(wait)
    resp.raise_for_status()
    df = pd.read_csv(io.StringIO(resp.text), na_values=["M"])
    if df.empty or "valid" not in df.columns:
        return pd.DataFrame(columns=["ts_utc", "report_type", "temp_f", "dewpoint_f"])
    return pd.DataFrame(
        {
            "ts_utc": pd.to_datetime(df["valid"], utc=True),
            # rank as METAR so pull_weather.collapse_to_utc_hours prefers it normally
            "report_type": "FM-15",
            "temp_f": pd.to_numeric(df["tmpf"], errors="coerce"),
            "dewpoint_f": pd.to_numeric(df["dwpf"], errors="coerce"),
        }
    )


def patch_station_year(station_id: str, year: int, mesonet_obs: pd.DataFrame) -> dict:
    """Merge mesonet hours into the station-year parquet (NOAA wins where present)."""
    grid = pw.year_utc_grid(year)
    if len(grid) == 0:
        return {"station": station_id, "year": year, "patched": 0, "note": "future year"}
    obs = mesonet_obs.loc[mesonet_obs["ts_utc"].dt.year == year]
    mes = pw.process_observations(obs, grid)
    mes["qc_flag"] = mes["qc_flag"].replace({"raw": "mesonet"})

    path = pw.cache_path(station_id, year)
    if path.exists():
        noaa = pd.read_parquet(path)
        merged = noaa.set_index("ts_local")
        m = mes.set_index("ts_local").reindex(merged.index)
        take = merged["temp_f"].isna() & m["temp_f"].notna()
        for col in ("temp_f", "dewpoint_f", "qc_flag"):
            merged.loc[take, col] = m.loc[take, col]
        out = merged.reset_index()
        n_patched = int(take.sum())
    else:
        out = mes.copy()
        out.insert(0, "station_id", station_id)
        out = out[["station_id", "ts_local", "temp_f", "dewpoint_f", "qc_flag"]]
        n_patched = int(out["temp_f"].notna().sum())
    tmp = path.with_suffix(".parquet.tmp")
    out.to_parquet(tmp, index=False)
    tmp.replace(path)
    return {
        "station": station_id, "year": year, "patched": n_patched,
        "still_nan": int(out["temp_f"].isna().sum()),
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--from-date", default="2025-08-01",
                    help="mesonet pull start (overlap into good NOAA data is fine — NOAA wins)")
    args = ap.parse_args()

    end = str(pd.Timestamp.now().date())
    icaos = station_icaos()
    years = sorted({int(args.from_date[:4]), int(end[:4])})
    years = list(range(years[0], years[-1] + 1))
    print(f"mesonet patch: {len(icaos)} stations, {args.from_date} → {end}, years {years}")

    session = requests.Session()
    results = []
    for i, (sid, code) in enumerate(icaos.items()):  # sequential — be polite to IEM
        if i:
            time.sleep(5)
        obs = fetch_mesonet(code, args.from_date, end, session)
        if obs.empty:
            print(f"  WARNING {sid} ({code}): mesonet returned no rows")
            continue
        for year in years:
            r = patch_station_year(sid, year, obs)
            results.append(r)
            print(f"  {sid} ({code}) {year}: +{r['patched']} hours, {r.get('still_nan', '?')} NaN left")
        del obs
    summary = pd.DataFrame(results)
    if len(summary):
        print("\ntotal patched hours by year:")
        print(summary.groupby("year")["patched"].sum().to_string())
    print("\nnext: rebuild zone weather → uv run python load-forecast/src/zone_weather.py")


if __name__ == "__main__":
    main()
