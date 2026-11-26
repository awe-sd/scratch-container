# tasks/01_crosswalk.md
Objective: build crosswalk_county_station.
Steps: pull ACS 2023 B01003 for all TX counties (Census API) → join ERCOT
county→zone map → keep counties covering ≥90% of zone population (expect
8–12 per zone) → assign nearest ASOS airport station to each county
centroid (≤50 km, else share neighbor's station; ASOS grade only, ≥10 yr
record) → compute weights. Expect ~5–8 distinct stations per zone.
Accept: weights sum to 1.0 per zone; every station has ≥95% hourly
coverage 2015–2026; crosswalk committed as versioned CSV.
