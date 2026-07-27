# Triage log — Bufflehead BESS (24INR0274)

## T1 start

**queue_history.py output:** 53 snapshots, 7 COD changes.

**Milestone summary:**
- Screening complete: 2022-06-02
- FIS approved: 2026-02-27 (very recent — took ~4 years)
- IA signed: 2024-04-10
- Meets 6.9(1) and all 6.9: 2026-04-27 (recent)
- No construction start/end, no energization/sync/commercial operation

**COD drift (7 changes):**
- Original: 2024-04-01 → slipped repeatedly → current: 2027-02-15
- Total slip: ~3 years from original target
- Last two: 2027-03-30 (held 1 month), then 2027-02-15 (current, held since 2025-07-01)

**Capacity changes:**
- Started 201.2 MW, dropped to 100.8 MW (2023-11), bounced to 200 MW (2024-07), 
  then settled down to current 150.48 MW (2026-04)
- Significant resizing suggests project has been restructured

**Assessment:** Project is real and advanced — IA signed Apr 2024, FIS approved Feb 2026,
meets all 6.9 criteria as of Apr 2026. COD slipped ~3 years but milestones are largely
complete. The 2027-02-15 COD is plausible given the milestone completion pace.

## T2 start

**gmaps.py places:** HTTP 429 on both attempts (rate-limited). No pins found.
pins_found = 0

## T3 start

**Web sweep results:**
- Original developer: Black Mountain Energy Storage (BMES), Austin TX; founded by Rhett Bennett
- Current owner/developer: Boxcar Energy Storage, LLC (transferred from BMES)
- Interconnection counterparty: Oncor Electric Delivery Company LLC
- Location cited: City of Wylie, Collin County, TX
- No construction/permitting announcements found
- No dedicated project page or press release found
- "Bufflehead BESS LLC" search: no TX SOS filing details surfaced (would need SOSDirect)
- Third search for Boxcar+Collin County: no results

**Developer note:** BMES transferred to Boxcar Energy Storage. No news of financing close or construction start.

news_found = false (no project-specific PR or news article)

## T4 start

**PUCT Interchange direct access:** Blocked (HTTP 402) — portal requires session/auth.
**IA search via DDG:** Found — PUCT docket 35077
- Document: "First Amendment to the Standard Generation Interconnection Agreement"
- Parties: Oncor Electric Delivery Company LLC & Black Mountain Energy Storage II (Bufflehead BESS) (24INR0274)
- Filed: 2024-07-24
- Filed by: Thomas J. Yamin, P.E.
- Rule: Substantive Rule 25.195(h)
- Note: "First Amendment" implies original IA exists; amendment filed ~3 months after IA signed (2024-04-10)
**PDF download attempt:** Blocked (HTTP 402). Milestone schedule not retrieved.
**Second DDG query for schedule details:** CAPTCHA block.

ia_found = true (confirmed by docket reference, content CEII-status unknown)

## T5 start

**Ch. 313 search:** Comptroller Ch.313 page has no searchable database for abatements;
direct query attempts blocked/CAPTCHA. No Ch. 313 agreement found for Bufflehead/BMES/Boxcar in Collin County.
**JETI registry:** gov.texas.gov/business/page/jeti returned 404.
**Note:** Post-2022 projects are ineligible for Ch.313 (program expired). JETI is the successor;
this project filed Feb 2022, right at the boundary — JETI miss is plausible/expected.

abatement_found = false (normal for this vintage)

## T6 start

**Site candidate:** POI = "2475 Lavon Switch 138kV" near Lavon TX (Collin County).
From T3: City of Wylie cited. Lavon, TX coords ~33.028, -96.434 (Nominatim).
**Imagery attempt:** cdse.py chips at 2026-06-01 and 2024-01-15 → HTTP 401 Unauthorized.
CDSE credentials not available in this session.
construction_visible = false (no imagery retrieved)

## T7 start

triage_findings.json and triage.md written. Turns used: ~28. Run complete.
