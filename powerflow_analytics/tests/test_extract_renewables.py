import pandas as pd

from pfa.extract import renewables


def _fake(monkeypatch, canned):
    calls = []

    def q(sql, database="AW"):
        calls.append(sql)
        return canned

    monkeypatch.setattr(renewables.mssql, "query", q)
    return calls


def test_wind_region_hourly_window_and_optional_region(monkeypatch):
    canned = pd.DataFrame({"TimeStamp": []})
    calls = _fake(monkeypatch, canned)
    assert renewables.wind_region_hourly("2026-04-01", "2026-09-28") is canned
    assert "ercotWindRegionHourly" in calls[0] and "TimeStamp >= '2026-04-01'" in calls[0]
    assert "TimeStamp < '2026-09-28'" in calls[0] and "windRegion = " not in calls[0]
    calls = _fake(monkeypatch, canned)
    renewables.wind_region_hourly("2026-04-01", "2026-09-28", region="West")
    assert "windRegion = 'West'" in calls[0]


def test_solar_hourly_zone_and_window(monkeypatch):
    canned = pd.DataFrame({"HE": []})
    calls = _fake(monkeypatch, canned)
    assert renewables.solar_hourly("2026-04-01", "2026-09-28") is canned
    sql = calls[0]
    assert "solarGenAct" in sql and "isoZoneID = 67" in sql
    assert "d.date >= '2026-04-01'" in sql and "d.date < '2026-09-28'" in sql
