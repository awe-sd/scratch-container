# Deep scan log — 23INR0070 Chillingham Solar
## Session: 2026-07-20

---

### D0 — Skeleton
findings.json skeleton written. EIA factsheet shows construction complete but not yet operating; EIA coords 31.006, -97.262. Queue approved-for-sync 2024-09-04, no COD approval through 2026-06.

---

### D1 — IA Schedule (original IA: 35077-1390, signed 2022-02-04)

**DEVELOPER IDENTIFIED**: Exhibit D names **8minute Solar Energy** (acamargo@8minute.com, 250 Sutter St. Suite 600, San Francisco, CA 94108) as the Generator contact — this IS the developer behind 250LB 8ME LLC / Chillingham Solar LLC.
- Artifact: sources/2026-07-19_puct_35077-1390_interconnection-agreement-between-oncor-electric.pdf, p.44 (Exhibit D)

**SPV name change confirmed**: 250LB 8ME LLC → Chillingham Solar LLC per Amendment 3.

**POI location**: Bell County East Switching Station ("Bell County East Switch") on the east side of Shaw Road, Bell County TX, at TSP's dead-end structure. Connects to Temple Switch, Sandow Switch, TNP One 345kV lines.
- Artifact: original IA Exhibit C §2

**Original IA schedule (Exhibit B)**:
- In-Service: May 11, 2023
- Trial Operation: May 22, 2023
- Scheduled COD: September 19, 2023
- Financial security: $3,088,904 by 2022-02-04; $6,979,820 by 2022-09-02 (irrevocable standby LCs)

**Equipment**: 116 Power Electronics FS3225M inverters @ 3.3 MVA each = 384.66 MVA gross, dispatched at 359.37 MW. Co-located storage (23INR0079): 75 SMA Sunny Central Storage 2500-EV @ 2.25 MVA = 168.75 MVA, 153.75 MW.

---

### D1 — Amendment No. 3 (35077-1985, signed 2024-10-21)

Generator party name changed to: Chillingham Solar LLC (formerly 250LB 8ME LLC)
Signed by: Benjamin Lindermeier, VP Development.

**Amendment 3 schedule (Exhibit B, solar 23INR0070)**:
- In-Service Date: May 15, 2024
- Scheduled Trial Operation: September 4, 2024
- Scheduled COD: **December 31, 2024** ← already past; no commercial operation in queue through Jun 2026
- Communication facilities in place: March 29, 2024 (solar)
- Generator Transmission Line installed (Shaw Road, east side): March 15, 2024

CRITICAL: Amendment 3 COD was Dec 31, 2024 — plant should have been operating 7 months ago per contractual schedule, yet queue shows no COD approval and EIA says "construction complete, not yet operating." This is a blocking issue, not a typical slip.

EIA nearby plant: Five Wells Solar Center (Operating, 30.999, -97.259) — very close to Chillingham coords (31.006, -97.262); different entity but same area. May share substation / POI infrastructure.

---

---

### D1 — Amended & Restated SGIA (35077-2251, signed 2025-08-07)

**ENGIE North America confirmed as operator**: Exhibit D names "Chillingham Solar LLC c/o ENGIE North America, Attn: Eric Tarantino, 3760 State Street Suite 200, Santa Barbara CA 93105; eric.tarantino@engie.com". Operations center: assetman@engie.com, (713) 636-1182. 8minute Solar Energy no longer appears.
- Artifact: sources/2026-07-19_puct_35077-2251_amended-and-restated-standard-generation-interco.pdf

**Signatory**: Ricky Davis, Vice President (Chillingham Solar LLC / ENGIE) on 2025-08-06; Robert Holt, Director (Oncor) on 2025-08-07.

**Latest contractual COD: September 30, 2025** (Exhibit B):
- In-Service: May 15, 2024
- Scheduled Trial Operation: September 6, 2024
- Scheduled COD: **September 30, 2025** ← most current contractual obligation
- Plant is now 9.8 months past this contractual COD with no commercial operation approval in queue (through 2026-06) or EIA

**Article 2.1.B termination trigger**: Oncor may terminate IA if COD not achieved within 1 year of scheduled COD = **September 30, 2026**. This is ~10 weeks away — significant pressure on developer.

**Inverter change**: 91 Sungrow SG4400UD-MV-US @ 4.4 MVA = 400.4 MVA gross, dispatched at 358.58 MW generator terminals / 352.39 MW at 34.5 kV bus. Original was 116 Power Electronics FS3225M units. Capacity held at 352.39 MW.

**Co-tenant structure formalized**: Chillingham Solar LLC and Chillingham Storage LLC jointly own Co-Tenant Switchyard Facilities and Co-Tenant Transmission Line to Bell County East Switch at 345 kV.

**COD slip chain (D1 complete)**:
- Original SGIA (Feb 2022): COD Sep 19, 2023
- Amendment 3 (Oct 2024): COD Dec 31, 2024
- Amended & Restated (Aug 2025): COD Sep 30, 2025
- Queue as of Jun 2026: COD Aug 31, 2026
- EIA latest planned COD: Jun 2026
- EIA status: "Construction complete, but not yet operating"

The plant was approved for synchronization Sep 4, 2024 — it has been energized/grid-connected for 10+ months. No COD approval. This is not a construction delay — it is a COD-declaration delay (commercial/regulatory/contractual issue).

---

### D1 — Amendment No. 4 / co-tenant (35077-2049, filed 2025-01-17)

**CONFIRMED storage IA, not solar**: This is Amendment No. 4 to the Standard Generation Interconnection Agreement for 23INR0079 (Chillingham Storage LLC), signed Oct 31, 2024. Not a solar amendment.
- Renames Chillingham Solar LLC to Chillingham Storage LLC on storage IA
- Updates storage equipment: 45 Sungrow SC4000UD-MV-US @ 4 MVA, 180 MVA gross, 155.171 MW / 153.93 MW
- Signed by Benjamin Lindermeier, VP Development (both LLCs)
- The `unverified_` prefix was correct — it was not verifiable to solar INR 23INR0070

No solar Amendment No. 4 on disk; the Amended & Restated (35077-2251) supersedes all prior amendments and is the controlling document.

---

### D2 / D3 — pending:
- Run gmaps.py for site delivery pin
- cdse.py chip at [31.006, -97.262]
- Read remaining sources: engie-na PPA html, bellcounty solar list, ch313 HTML, 35077-2252 (storage A&R, optional)
- ch313.py resolve 23INR0070 for acres/applicant
