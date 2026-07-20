# Triage log — 27INR0049 Darkwood Solar

**Date:** 2026-07-19
**Triage started**

---

T1 start
**T1 result:** 32 snapshots (2023-11-01 → 2026-06-01). Milestones: Screening complete 2023-09-01, FIS approved 2025-07-29, IA signed 2025-11-05. No construction start/end or energization milestones. COD drift: 1 change — 2027-01-30 → 2027-09-20 (slipped ~8 months, noted at 2025-07-01 snapshot). Capacity stable at 150.76 MW since 2024-01-01. **Strong queue progression: IA signed is a material milestone.**

T2 start
**T2 result:** gmaps.py returned HTTP 429 on both attempts (rate-limited). No pins found. Pins: 0.

T3 start
**T3 result:** Developer confirmed as **Mustang Creek Solar, LLC** (Austin TX); operating entity Mustang Creek Solar I, LLC (EIA Form 860). "Darkwood Solar LLC" not found as registered entity. Companion BESS (150.5 MW) at same site. **Construction signal:** Facebook group post states construction started on Evan Ranch (Comanche Co.). PUCT IA filing found (Oncor, Nov 2025, case ~35077). Location: near CR 328/343 between Proctor and HWY 36. Notes saved to sources/web_sweep_notes.md.

T4 start
**T4 result:** PUCT Interchange portal returned HTTP 402 on all attempts (auth/payment wall). Could not download IA PDF. **IA existence confirmed via T3 web sweep** (Oncor filed Standard Generation IA, Nov 2025, case ~35077) — IA is real, just not downloadable here. Milestone schedule exhibit not retrieved.

T5 start
**T5 result:** TX Comptroller Ch.313 page did not surface searchable data (portal redirects/generic page). DDG search for JETI/abatement hit CAPTCHA. No Ch.313 or JETI abatement found for Darkwood Solar / Mustang Creek Solar in Comanche County. **Normal for post-2022 project** (Ch.313 expired; JETI is newer and not yet widely filed). Not a negative signal.

T6 start
**T6 result:** Site candidate: ~31.97°N, 98.47°W (near Proctor TX, CR 328/343 area, Evan Ranch — low confidence, inferred from community posts). Contact sheet (2 frames): 2024-06-15 baseline shows Proctor Lake vicinity, green farmland/pasture, no solar infrastructure visible. 2026-06-15 chip is all-black (no valid Sentinel-2 composite available — likely data gap or heavy cloud cover at this date/location). **No construction visible in imagery.** Coordinate estimate may be offset (centered near Proctor Lake, not confirmed Evan Ranch parcel). Construction signal from Facebook text only, not confirmed by imagery.

T7 start
**T7 result:** triage_findings.json + triage.md written. Turns used: ~22. STOP.
