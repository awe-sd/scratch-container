# ERCOT LLWG/LFLTF large-load vintage series -- meeting inventory & notes

Point-in-time ("vintage") aggregate MW series built from ERCOT Large Load
Working Group (LLWG) meeting materials and its predecessor, the Large
Flexible Load Task Force (LFLTF). Companion CSV:
`data/derived/llwg_vintages.csv`. Raw source files cached under
`data/raw/llwg/<meeting_date>/`.

Purpose (per sdalvi): a point-in-time large-load prior with **no hindsight**
-- for each snapshot date, what ERCOT itself reported the queue/approved/
energized aggregates to be, as understood at roughly that time, not what we
know today with the benefit of later corrections.

## What this body is, in two parts

- **LFLTF** (Large Flexible Load Task Force) -- chartered ~May 25, 2022
  (`LFLTF_Charter_TAC_Approved 052522`, first agenda materials Apr 14, 2022).
  Archived at `https://www.ercot.com/committees/inactive/lfltf` (year
  sub-pages `/2022`, `/2023`, `/2024`).
- **LLWG** (Large Load Working Group) -- replaced LFLTF; charter TAC-approved
  Apr 23, 2025; first meeting May 16, 2025. Live committee page:
  `https://www.ercot.com/committees/tac/llwg` (year sub-page `/2025`; 2026
  meetings listed on the main page).

## Coverage achieved

- **Span:** 2022-04-26 through 2026-06-19 (~4.2 years), 35 distinct snapshot
  dates, 201 rows in the CSV.
- **Meetings found (calendar inventory):** 52 LFLTF/LLWG calendar entries
  identified from Apr 2022 through Jun 2026 (matches the per-year table
  below; a couple of the 2023 entries are "RESCHEDULED" stub rows that likely
  duplicate a nearby held-meeting date rather than being fully distinct
  events, so the true count of distinct meetings is a little lower). All
  were checked for a queue-status/aggregate deck by fetching each meeting's
  calendar page and listing its posted files.
- **Meetings with an aggregate MW deck actually extracted (own materials
  read in full):** 9 -- 2022-08-22, 2022-09-26, 2023-01-23, 2023-07-24
  (posted late), 2024-01-25, 2024-04-01, 2024-09-06, 2026-06-19, plus a
  partial (use-type only) read of 2025-08-14.
- **Additional snapshot dates recovered without opening that meeting's own
  deck**, via multi-month trailing-history charts embedded in a *later*
  meeting's own deck (this is the mechanism sdalvi described -- "aggregate
  vintages ... if you go back in time"): 25 more dates, spanning 2022-05
  through 2026-05, sourced from the Jan-2024, Apr-2024, Sep-2024, and
  Jun-2026 decks' own retrospective "Past N Months" charts.
- **Known real gaps (no data found for these windows despite checking):**
  - 2022-11 / 2022-Dec-onward gap between the Sep-26-2022 and Oct-28-2022
    snapshots is fine (both covered), but no meeting was held in Nov 2022
    (cancelled) or Dec 2022 at all.
  - **May-2025 through Jul-2025** (3 months): no source found. All 7 of the
    2025 LLWG meetings' own posted materials were checked; none carried a
    standalone queue-status/report deck. The Jun-2026 deck's own trailing
    chart only reaches back 11 months, to 2025-08 -- it does not cover
    May-Jul 2025. This is a genuine, unresolved gap.
  - **`energized` stage is fully covered for 2025-08 through 2026-06** (added
    after the first pass, from the Jun-2026 deck's slides 8 and 9, which were
    initially missed) -- both an all-time-style non-simultaneous peak and a
    simultaneous peak, each on a MONTHLY (not all-time-cumulative) definition
    for this era; see discontinuity note 8 below.
  - 2023 has two ambiguous month-only labels (`Aug-23`, and a `Sep-23` that
    could be either the Sep 6 or Sep 25, 2023 meeting) where the retrospective
    chart didn't print an exact day and no meeting's own deck was opened to
    disambiguate -- see per-row notes in the CSV.

## Meeting inventory (checked = fetched that meeting's calendar page and
listed its posted files; extracted = a numeric MW aggregate went into the CSV)

| Year | Meetings checked | Had an aggregate-MW deck | Extracted (own deck read) |
|------|------------------|--------------------------|----------------------------|
| 2022 (LFLTF) | 12 (2 cancelled) | Aug 22, Sep 26, ~Oct 24 (deck found, not opened) | Aug 22, Sep 26 |
| 2023 (LFLTF) | 14 (2 cancelled, 2 rescheduled) | Jan 23, Feb 17, Mar 20, Apr 12, May 31, Sep 6, Sep 25, Oct 23, Dec 11, + a late-posted "Jul 2023" deck (all found; most not individually opened) | Jan 23, Jul-2023 (late-posted) |
| 2024 (LFLTF) | 13 (8 cancelled) | Apr 1, May 6, Jun 3, Jul 8, Sep 6 (all found; some not individually opened) | Apr 1, Sep 6 |
| 2025 (LLWG) | 7 | none found under any obvious filename | none (Aug 14 gave a use-type-only supplement, different metric) |
| 2026 (LLWG, through Jun) | 6 | Jan 22, Feb 19, Mar 13, Apr 24, May 21 (deck found under `<Month>-LLWG-Report` naming, not individually opened), Jun 19 | Jun 19 |

Full per-meeting detail (URL, files found, extracted True/False + reason) is
long; the CSV's `notes` column carries the per-row provenance. Ask if a
plain meeting-by-meeting table is wanted as a separate file.

### Meetings explicitly checked and found to have NO aggregate MW content
(agenda covered other topics only -- e.g. VRT studies, NPRR/NOGRR comments,
ride-through assessments, Batch Zero process mechanics): 2022-04-14,
2022-05-18, 2022-05-24, 2022-06-15, 2022-06-24, 2022-06-29, 2022-07-25,
2025-05-16, 2025-07-11, 2025-09-19, 2025-10-24 (opened `OCT_LLWG_LLI_Process.pptx`
directly and confirmed process-only), 2025-11-20, 2025-12-11.

## Definition / methodology changes over time (IMPORTANT -- read before using this series)

ERCOT re-based the queue taxonomy and/or scope **repeatedly**. Three of the
changes below are stated explicitly by ERCOT in the meeting decks themselves
(quoted); one is an inference by this agent (flagged as such). Do not treat
the series as one continuous, homogeneous definition.

**BIGGEST LEVEL DISCONTINUITY IN THE WHOLE SERIES -- read this one first.**
Total tracked queue goes from **56,954 MW (2024-09-06)** to **189,328 MW
(2025-08-14)**, a **+232%** jump across the unsourced 2025 gap (see coverage
note above) -- more than 3x larger, proportionally, than the +73% Feb->Mar
2026 jump flagged as item 6 below. This sits exactly across (a) the
LFLTF->LLWG re-charter (Apr 2025) and (b) the inferred taxonomy rename
(item 5 below), and there is a real risk that some/most of this jump is
scope or definitional rather than actual queue growth. **Do not read the
gap between these two dates as organic demand growth without first getting
one real 2025 data point to anchor it** -- none was found in this pass.

1. **Sep 26, 2022 -- chart methodology changed, ERCOT's own words:**
   "The methodology for this chart differs from what was presented at the
   August meeting. This chart better accounts for staged energization
   schedules [and] MWs limited by the interim process that have a defined
   exit strategy." Categories went from a 6-bucket scheme (Received by
   ERCOT / Under Review / MW Above Interim Planning Limit / Met Planning /
   Approved to Energize / Operational) to a 4-bucket scheme (In Service /
   Deferred / In Study / Planned). *(This affects the by-in-service-year
   cumulative table only, which is intentionally excluded from the CSV --
   see "What's excluded" below -- but signals the tracking system itself was
   unstable in 2022.)*

2. **Jan 23, 2023 -- second re-basing, ERCOT's own words:** "The migration to
   the new Jira-based system has required some changes to the methodology
   behind the charts... The Deferred MW category has been removed." New
   4-bucket scheme introduced: Approved to Energize / Met Planning / In
   Study / Planned -- renamed again by mid-2023 to Approved to Energize /
   Planning Studies Approved / Under ERCOT Review / No Studies Submitted,
   which then held stable through Sep 2024.

3. **Jan 2024 -- retroactive reclassification correction, ERCOT's own words**
   (stated in the Jan-2024, Apr-2024, and Sep-2024 decks alike): "In January
   2024 ERCOT identified several projects that had been previously
   misclassified in this chart. This error was corrected, resulting in a
   higher 2023 total of approved load than was previously reported. The
   overall size of the queue was not impacted by this error." This means
   the 2023 `approved_to_energize` / `in_study` (Planning Studies Approved)
   figures for dates **before** Jan 2024 in this CSV are the **corrected**
   (restated) values, not what was actually shown live at those 2023
   meetings -- a real hindsight contamination risk for anyone using this as
   a strict "what was known then" series. The `other` (total queue) figures
   were not affected per ERCOT's own statement.

4. **Jul 2024 -- queue horizon expanded, ERCOT's own words:** "In July 2024
   ERCOT expanded the queue to include projects with projected in-service
   dates of 2028. Previously, projects without an in-service date were
   assigned a default ISD of 12/31/2027. Those projects were reassigned a
   default ISD of 12/31/2028." This affects the by-in-service-year table
   (excluded from the CSV) and coincides with part of the Jun-2024 ->
   Jul-2024 total-queue jump (43,683 -> 47,879 MW).

5. **Between Sep 2024 and Aug 2025 (exact date unknown -- inside the data
   gap) -- taxonomy renamed again, THIS ONE IS INFERRED, NOT CONFIRMED BY
   ERCOT TEXT.** The 2022-2024 generation's `Planning Studies Approved`
   bucket is, by this agent's inference from bucket ordering and relative
   size, likely split into two finer successor buckets in the 2025-2026
   LLWG decks: `Section 9.4 Requirements Only` and `Section 9.4/9.5
   Requirements Met`. No ERCOT text explicitly equating these was found (the
   Jun-2026 deck defines the new categories in isolation, referencing
   Planning Guide Sections 9.4/9.5 and the Mar-2022 interim process, but
   never says "this replaces Planning Studies Approved"). **Treat this
   generation-3 vs generation-2 mapping as a hypothesis, not a fact.**
   *Independent validation of the within-chart bucket assignment* (separate
   from the generation-3-vs-2 mapping question above): the Jun-2026 deck's
   own "Notes on Content" slide states "The decrease in 9.4/9.5 approved
   load between May and June ... is a result of the removal of duplicate
   tickets." The CSV's `Section 9.4/9.5 Requirements Met` value does
   decrease May->Jun 2026 (37,149 -> 37,085) while `Section 9.4 Requirements
   Only` rises (9,237 -> 11,803), consistent with that text -- it would
   contradict if the two bar segments had been transposed during image
   reading. This is the one segment assignment in the CSV with an
   independent textual check; the rest of the 2026 figures are vision-read
   only and unchecked beyond the standalone+colocated=total arithmetic
   validation (passed for all 29 checkable rows).

6. **March 2026 -- unexplained total-queue discontinuity, NOT flagged by
   ERCOT anywhere found.** Total tracked queue jumps from 241,748 MW
   (2026-02) to 418,998 MW (2026-03), +73% in one month, driven almost
   entirely by the Standalone component (213,105 -> 372,459). The Jun-2026
   deck's own "Notes on Content" slide only describes a *smaller*,
   *later* (May->Jun 2026) LLIS ticket clean-up ahead of "Batch Zero" and
   does not mention anything from March. **No explanation for the March
   jump was found in any material checked.** Flag this row before using it
   in any model; it may be a scope/definition change, a one-time bulk
   ticket import, or something else entirely -- NEEDS_CONTEXT if it matters
   to the load-forecast work.

7. **"Approved to Energize" vs "energized" is not one number.** Every
   generation of the deck distinguishes the *capacity* that has cleared
   ERCOT's Approval-to-Energize gate (which includes MW **not yet observed
   operational**) from the *observed* consumption of that pool (a genuinely
   "already energized" figure). This CSV keeps them as separate `stage`
   values (`approved_to_energize` vs `energized`) -- do not sum them, the
   `energized` figure is a subset of `approved_to_energize`, already counted
   once.

8. **`energized` definition itself shifts mid-series.** The 2023-2024 rows
   (`... (ALL-TIME, of Approved-to-Energize pool)`) are an **all-time**
   cumulative peak -- "the sum of the maximum value for each individual load
   regardless of when that maximum occurred," per that era's own slide text
   -- and are monotonically non-decreasing by construction (1,814 in Jan-2023
   up to 3,282 in Sep-2024). The 2025-08 through 2026-06 rows
   (`... (MONTHLY, of Approved-to-Energize pool)`) are instead a **monthly**
   peak that resets each month and is genuinely non-monotonic (e.g.
   non-simultaneous: 4,227 in 2025-10 down to 4,011 in 2025-12), per the
   Jun-2026 slide 8 text ("...monthly peak consumption of 3900 MW in June
   2026 which is a slight decrease since May"). **Do not concatenate these
   two eras as one continuous `energized` series** -- there both is a
   coverage gap (2024-10 through 2025-07) and a definition change across it.

## Whole-series sanity check (read before this feeds any model)

The `other`-stage total-queue figures top out at **466,497 MW** (2026-06) --
roughly **5x ERCOT's system-wide peak demand**. That is unremarkable for a
cumulative *interconnection request* queue (which by ERCOT's own definitions
includes speculative, duplicate, and never-built projects, some later
cancelled) but would be an absurd *load* level. **The `other`/total-queue
rows in this CSV are request-queue volume, not expected or realized load,
and must not be used as a load-growth level or prior on their own.** The
`energized` stage (observed peak consumption) is the only series in this
CSV that reflects load actually being served, and even that is a small,
LZ_WEST-and-datacenter-skewed subset of the full queue (see zone-split
caveat below). `approved_to_energize` and `in_study` sit conceptually
between the two -- capacity that has cleared a gate but may or may not ever
be built out.

## What's excluded from the CSV on purpose

Every generation of deck also carries a **by-in-service-year cumulative
table/chart** (e.g. "Current Large Load Interconnection Queue," columns
2022...2027/2028, rows = stage) -- this is ERCOT's forward *plan* as
understood at that meeting (which MW is expected to reach which stage by
which future year), a fundamentally different axis from "what was the
queue as of this meeting date." Including both axes in one CSV would risk
double-counting or silent mixing. This second axis was **not** transcribed
into the CSV; it exists in every downloaded raw file if wanted later as a
separate "forward-plan vintages" table.

## Caveats

- **`stage='in_study'` is a misnomer for what it actually contains.** Every
  `in_study`-tagged row in this CSV (`Planning Studies Approved`, `Section
  9.4 Requirements Only`, `Section 9.4/9.5 Requirements Met`) is a bucket of
  projects whose studies are **already complete/approved** -- i.e. "past
  submission, pre-Approval-to-Energize" -- not projects currently
  mid-review. The verbatim `stage_label` always carries ERCOT's true
  wording, so no information is lost, but don't filter on `stage='in_study'`
  expecting "actively being studied right now."
- **Standalone vs Co-Located** MW splits are a project-type cut of the
  *same* total, not a region -- kept as separate `other`-stage rows
  (`region='ERCOT'`) rather than misusing the `region` column.
- **Region/zone splits exist for only 2 dates** (2024-01-25, 2024-09-06:
  LZ_WEST vs "other load zones" = LZ_NORTH+LZ_SOUTH+LZ_HOUSTON), both for
  the `approved_to_energize` stage only. No zonal cut was found anywhere
  else in the materials checked.
- **Month-only labels:** many retrospective chart x-axes print only
  `Mon-YY` (no day). Where this happens, `meeting_date` in the CSV is set to
  that month's actual LFLTF/LLWG meeting date (from the calendar inventory)
  as the best available proxy -- flagged per-row in `notes`. Two 2023 rows
  (`Aug-23`, `Sep-23`) are genuinely ambiguous (no meeting that exact month,
  or two meetings that month) and use a placeholder day; see notes.
- **PDF page-rendering tool (`pdftoppm`) is not installed** in this
  container, so the `pages=` parameter on the Read tool fails for PDFs;
  reading the whole PDF (no `pages` arg) works fine and is what was used
  throughout.
- **2022-04-26's own deck** (`InterimLargeLoadInterconnectionProcess_
  AggregateData_04262022.pptx`, cached on disk) has its charts as pasted
  PNG images, not extractable as text/data -- not opened as an image given
  the number it would show (17,376 MW) was already recoverable from three
  later decks' retrospective charts. Same is true of the March/April/May
  2026 individual `-LLWG-Report.pptx` decks and the June 2026 one's own
  bar charts (`image9.png`, `image12.png` under
  `data/raw/llwg/2026-06-19/_unzip/ppt/media/`) -- those two WERE opened as
  images since they were the only source for the entire 2025-08 through
  2026-06 span.
- **Anonymous HTTPS to ercot.com worked throughout** with a standard
  browser User-Agent via both `curl` and the WebFetch tool -- no blocking
  encountered, no NEEDS_CONTEXT required on the access side.

## Reproducing / extending this series

- Meeting calendar pages: `https://www.ercot.com/calendar/<MMDDYYYY>-LLWG-Meeting`
  (2025+) or `-LFLTF-Meeting` (2022-2024); committee archive index:
  `https://www.ercot.com/committees/tac/llwg` (current) and
  `https://www.ercot.com/committees/inactive/lfltf` (+ `/2022`, `/2023`,
  `/2024` sub-pages).
  The WebFetch tool tends to summarize/truncate a calendar page's file list
  to a handful of "Key Documents" -- fetching the same URL with `curl -sL`
  plus a browser User-Agent and grepping for `files/docs/` in the raw HTML
  returns the complete, untruncated list and is far cheaper.
- pptx text extraction helper written for this task:
  `scripts/extract_pptx_text.py <deck.pptx>` -- unzips and dumps per-slide
  text by joining `<a:t>` runs in slide order (no `python-pptx` dependency).
  Does **not** recover chart data when a slide's chart is a pasted image
  (common in 2026-era decks) -- those need the Read tool pointed at the
  underlying `ppt/media/imageN.png` (find the mapping via that slide's
  `_rels/slideN.xml.rels`).
