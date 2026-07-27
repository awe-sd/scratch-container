# Dossier template — every deep-scan run writes dossier.md in exactly this shape

Rules (stage-5 of PLAYBOOK.md):
- ≤ ~60 lines of content. Bullets over paragraphs. Most decision-relevant facts first.
- EVERY claim carries an inline link: local artifact (`[IA](sources/<file>.pdf)`) or URL.
  An unlinked claim is an unsupported claim.
- No methodology narration (log.md), no restating the identity packet, no hedging filler.
  One honest "limits" section at the end instead of hedges sprinkled through.
- Tables for: ownership chain, contractual schedule, imagery timeline.
- The one-page brief.html is generated from findings.json — the dossier is the analyst-depth
  layer; findings.json must agree with it exactly.

---

# Dossier — <Project> (<INR>)

Researched <date> · site <lat>, <lon> · verdict **<real_active|real_early|paper|unclear>**

## 1. Verdict

- **<verdict>** — <one line of the single most decisive evidence, linked>
- Construction: **<stage>**, first activity <date> ([frame](imagery/…))
- Site: <lat>, <lon> — <method>, <confidence> ([map](https://google.com/maps/@lat,lon,5000m/data=!3m1!1e3))
- COD: reported <date> → independent **<YYYY-Qq>**, drift risk **<low|med|high>** (<why, 5 words>)

## 2. Site identification

- Derivation: <method + 1 line> ([artifact](…))
- **Stated project area: <N> acres** per <abatement/IA/CAD doc> ([artifact](…)) —
  imagery footprint consistent? <yes/no/unverified>
- Cross-checks (each linked): <pin / POI text / parcel / map doc / OSM> — agree within <x> km
- Not obtainable: <e.g. exact POI switch coords (CEII)>

## 3. Ownership & money

| Entity | Role | Evidence |
|---|---|---|
| <LLC> | SPV | [<doc>](sources/…) |
| <DevCo> | developer/owner | [<PR/filing>](…) |
| <EPC> | EPC | [<pin/PR>](…) |
| <offtaker> | PPA | [<article>](…) |

- Financing: <status + 1 line> ([source](…))

## 4. Land & county records

- Tenure: **<leased|purchased|unknown>** — <evidence 1 line> ([doc](sources/…))
- Abatements/agreements: <Ch312/313/JETI, ISD> ([app](sources/…)) — <key facts: acres, tracts, schedule>
- CAD: <parcels found / 0 hits + what that means>

## 5. Interconnection & contractual schedule

- POI per signed IA: <quote fragment> ([IA](sources/…), [Amend 1](sources/…))
- Equipment (if in IA exhibits): <inverters/MW etc.>

| IA document | Signed | Financial security posted |
|---|---|---|
| Original IA ([pdf](sources/…)) | <date> | $<amount> <LC/cash/…> |
| Amendment 1 ([pdf](sources/…)) | <date> | $<amount> — <changed? why> |

(Security sits IN this table, per document — amounts often rise with amendments; never
bury it in a footnote.)

| Milestone | Original IA <yr> | Amendment <yr> |
|---|---|---|
| In-Service | <date> | <date> |
| Trial Operation | <date> | <date> |
| Scheduled COD | <date> | <date> |

- Queue-history COD drift (from [timeline.md](timeline.md)): <n> changes, <first → latest>

## 6. Satellite timeline

| Date | Observation | Frame |
|---|---|---|
| <YYYY-MM> | <undisturbed / pad appears / grading n% / racking signal> | [png](imagery/…) |

- Verdict: **<stage>** — <1 line why, incl. what resolution cannot confirm>

## 7. COD assessment

- <3-5 bullets: contractual grounding, observed pace vs schedule, risk factors, independent estimate>

## 8. Could not determine

- <honest list>
