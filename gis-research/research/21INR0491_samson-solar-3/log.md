# Research Log — Samson Solar 3 (21INR0491)

Started: 2026-07-19

## Identity packet
- Project: Samson Solar 3
- INR: 21INR0491
- LLC: Samson Solar 3, LLC (to verify)
- County: Lamar, Texas
- Capacity: 250.0 MW Solar PV
- POI: "tap both 345kV 1685 FarmersVl - 1695 Moses ckts"
- CDR Zone: NORTH
- Reported COD: 2026-09-30 (claim to verify)

---

## Stage 1 — LLC → parent chain


### 2026-07-19 — Stage 1 search results

**LLC confirmed:** Samson Solar Energy III LLC (not "Samson Solar 3, LLC")
**Developer:** Invenergy (One South Wacker Drive, Suite 1500, Chicago, IL 60606)
**Co-owner (Dec 2025):** WEC Infrastructure / WEC Energy Group (80% stake)
- Source: infrasure.ai, constructionreviewonline.com, samsonsolarenergycenter.com
- Chain: Samson Solar Energy III LLC → Invenergy LLC (developer/manager) + WEC Infrastructure (80% owner)

**Phase context:** Phase 3 of 5-phase 1,310 MW complex (Franklin, Lamar, Red River Counties TX)
- Phase 1 (250 MW, 21INR0221): operating since May 2022, WEC 80% acquired Feb 2023
- Phase 2 (200 MW, 21INR0490): operating late 2024/2025
- Phase 3 (250 MW, 21INR0491): projected COD 2026-09-30 (this project)
- Phases 4 & 5 (300+310 MW): future
- Source: constructionreviewonline.com Feb 2026, monarchprivate.com Sep 2024 (Monarch tax equity for Phase 2)

**ERCOT GIS June 2026 (per subagent reading local xlsx):**
- IA Signed: 2020-08-27
- Approved for Energization: 2021-06-30
- Approved for Synchronization: 2021-10-26  ← ANOMALY: sync approval 5 yrs before COD
- Projected COD: 2026-09-30
- Construction start/end: blank

**!!ANOMALY!!** `approvedForSynchronization = 2021-10-26` normally indicates ~online per data model.
Yet projected COD is 2026-09-30. Either: (a) data confusion between phases, (b) this unit did partial sync/test then paused, (c) milestone applies to a different unit sharing the INR. Requires verification via satellite + queue_history script.

**Note:** infrasure.ai mapped EIA 63883 to this LLC with only 78% confidence; agent flagged this as possibly confused with Phase 1. The approvedForSynchronization date (2021-10) aligns suspiciously with Phase 1 COD (May 2022) timeline.

**PUCT interchange:** 402 response (behind paywall); will try direct PUCT filing search.

### 2026-07-19 — queue_history output (timeline.md written)

**18 COD changes** over 78 monthly snapshots (2020-01 → 2026-06):
- Original COD: 2021-12-31 → drifted to current 2026-09-30 = ~5.75 year total slip
- Pattern: 3-6 month steps repeatedly since 2021
- Last slip: 2026-06-30 → 2026-09-30 (May 2026)

**Key milestone anomaly:**
- Approved for Energization: 2021-06-30
- Approved for Synchronization: 2021-10-26
- Commercial Operation Approved: NEVER (blank)
- Construction start/end: NEVER reported
These sync/energization approvals from 2021 with no subsequent COD across 4+ years is highly unusual.
May indicate Phase 1 milestone data bled into Phase 3 record, or partial commissioning that stalled.

**Stage 2 — County records:** Unable to run due to budget constraint. No CAD/PUCT/Ch313 searches completed.
**Stage 3 — Site pinpoint:** gmaps.py hit 429 rate limit; no Places pin obtained.
**Stage 4 — Satellite imagery:** Not run due to budget constraint.

### Negative evidence log
- PUCT interchange.puc.texas.gov: HTTP 402 (payment required for direct filing search)
- gmaps.py places: HTTP 429 (rate limited)
- TX Comptroller CPA search: redirect loop (interface requires browser JS)
- No CAD parcel search completed for Lamar County
- No Ch.313/JETI search completed
- No satellite imagery chips acquired
