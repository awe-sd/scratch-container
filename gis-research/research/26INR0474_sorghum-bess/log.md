# Research Log — Sorghum BESS (26INR0474)

Researcher: Claude Sonnet 4.6
Date: 2026-07-19
County: Wharton, Texas
Capacity: 208.9 MW BESS
POI: #44060 Blue Substation 345kV
CDR Zone: SOUTH
Reported COD: 2027-12-01

---

## Stage 1 — LLC & Parent Chain


### 2026-07-19 | Local parquet query — developer ID
- Query: ercot_generation_interconnect_view.parquet, INR=26INR0474
- FOUND: interconnectingFacility = "Greenbelt ERCOT BESS Holdings, LLC"
- POI: #44060 Blue Substation 345kV, Wharton County, SOUTH zone
- Reported COD (latest): 2026-12-01 (file date 2024-04-01) / 2027-12-01 (since 2025-11-01)
- Blue Substation context: "Maleza Solar/Storage" (21INR0220/456) also at Blue-Hillje 345kV line in Wharton; "Blue Creek Energy Storage" (25INR0545) also Wharton County
- Source: internal parquet (ercot_generation_interconnect_view.parquet) — NOT a saved artifact

### 2026-07-19 | Timeline from queue_history.py
- IA signed 2025-01-08
- FIS approved 2024-11-13
- COD shift: 2026-12-01 → 2027-12-01 (12-month slip, shown in 2025-11-01 snapshot)
- No construction start/end dates reported
- Source: timeline.md


### 2026-07-19 | Latest parquet snapshot — LLC name changed + node confirmed
- In the latest (2026-06-01) snapshot, interconnectingFacility = "Blue Creek BESS, LLC" (changed from "Greenbelt ERCOT BESS Holdings, LLC" seen in earlier snapshots)
- Node #44060 also called "BLU 345kV" — confirming "Blue Substation" = node BLU in Wharton County
- Other project at same node: 25INR0741 Hollywood Solar Repower (9.9 MW, developer "RED TAILED HAWK SOLAR LLC", IA signed 2025-10-21)
- Hillje substation = node #44200 (a well-known AEP substation at ~29.03°N, 96.24°W)
- Source: local parquet query — internal, not saved artifact


## Stage 1 — LLC & Parent Chain (deep scan)

### 2026-07-19 | TX Comptroller API search — Blue Creek BESS, LLC found
- Query: Texas Open Data Socrata API (data.texas.gov/resource/9cir-efmm.json), taxpayer_name LIKE '%BLUE CREEK BESS%'
- FOUND: "BLUE CREEK BESS, LLC" — taxpayer_number=32094125351, registered 2024-03-08
  - Address: 1100 W 6TH ST, AUSTIN TX 78703 (county 227 = Travis)
  - SOS file: 0805456191, status Active, right_to_transact=A
- Source: TX Open Data Socrata API call — saved as sources/2026-07-19_txcomptroller_blue-creek-bess-franchise.json
- WHY: Confirms the SPV/interconnecting entity; connects to Greenbelt Renewable Energy at same address

### 2026-07-19 | TX Comptroller API — Greenbelt entities at same address
- Query: taxpayer_address LIKE '1100 W 6TH ST%', city='AUSTIN'
- FOUND: "GREENBELT RENEWABLE ENERGY LLC" — registered 2020-04-02, same address
- FOUND: "GREENBELT RENEWABLE ENERGY HOLDINGS LLC" — registered 2024-06-19, same address
- ALSO FOUND at same address: AVALON BESS LLC (2024-03-08, same day as Blue Creek BESS), MINERAL WIND LLC, LAS MUJERES SOLAR LLC, SHAFTER LAKE WIND LLC, COTTONWOOD CREEK WIND LLC — all appear to be sister projects
- Source: TX Open Data Socrata API — saved as sources/2026-07-19_txcomptroller_1100-w6th-entities.json
- WHY: Establishes parent chain — Blue Creek BESS, LLC → Greenbelt Renewable Energy LLC → Greenbelt Renewable Energy Holdings LLC (holding company); developer = Greenbelt Renewable Energy, Austin TX

### 2026-07-19 | TX Comptroller API — "Sorghum BESS LLC" not found
- Query: taxpayer_name LIKE '%SORGHUM%BESS%' — no results
- "Sorghum BESS" appears to be the project name only; the legal entity is "Blue Creek BESS, LLC" (renamed from "Greenbelt ERCOT BESS Holdings, LLC" in the ERCOT parquet)
- Negative evidence logged per PLAYBOOK rule 3

### 2026-07-19 | Greenbelt Renewables website — Blue Creek BESS confirmed as project name
- URL: https://greenbeltrenewables.com/projects/
- FOUND: "Blue Creek BESS | 208 MW | Wharton County, TX | Battery Storage" — exactly matches queue record
- Project page (https://greenbeltrenewables.com/projects/blue-creek-bess/) is sparse — no coordinates, no status, no EPC
- Source: saved as sources/2026-07-19_greenbeltrenewables_projects.html + sources/2026-07-19_greenbeltrenewables_blue-creek-bess.html
- WHY: Confirms project is actively listed by developer; provides company team: Philip Moore, Charlie Smith (co-founders), Brett Rollow PE (transmission), Emily Obradovich (finance), Lucas Buseck (development)

### 2026-07-19 | Ownership chain confirmed
- SPV: Blue Creek BESS, LLC (formerly "Greenbelt ERCOT BESS Holdings, LLC" in early ERCOT parquet)
- Developer/owner: Greenbelt Renewable Energy LLC, 1100 W 6th St, Austin TX 78703
- Holding co: Greenbelt Renewable Energy Holdings LLC (registered 2024-06-19, same address)
- ERCOT queue project name "Sorghum BESS" does NOT match developer's own project name "Blue Creek BESS" — different names for the same project
- Sister projects at same address: Avalon BESS LLC (Fort Bend County TX, 522 MW), Mineral Wind LLC, Las Mujeres Solar LLC

## Stage 2 — County Records

### 2026-07-19 | PUCT Interchange — blocked
- Queried: https://interchange.puc.texas.gov/search/filings/?DocumentDescription=Sorghum+BESS, Blue+Creek+BESS
- Result: HTTP 402 Payment Required — portal requires paid subscription
- Negative evidence logged; IA not retrievable via this route
