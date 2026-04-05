# Trademark Hound + Cat

**AI-powered trademark monitoring that catches what manual searches miss.**

## Why This Exists

Every brand owner faces the same problem: monitoring your trademarks for infringement is tedious and expensive. Traditional monitoring catches exact matches and obvious typos. It misses the phonetic near-misses, the semantic cousins, the compound-suffix clones that erode your brand equity while flying under the radar.

Trademark Hound + Cat close that gap. 

Trademark Cat -  thinks the way an infringer names a product — sound-alikes, concept riffs, suffix swaps to generate intelligent variants that define your threat area you need to search. 

Trademark Hound — then hunts every variant across the open web, scores each find against a weighted threat matrix that is tuned to your products, goods and services, and delivers a prioritized report ready for action.

**For attorneys:** This is a repeatable, evidence-grounded investigation pipeline. Every threat score cites page content directly. Attorney-supplied values (mark criticality, geography) are locked in and never overridden. The eight-factor matrix maps to the likelihood-of-confusion factors you already use. You review and approve at every gate — nothing fires without your sign-off.

**For brand and marketing teams:** This is the early-warning system your brand deserves. Instead of discovering copycats after they've gained traction, you surface them while they're still small and actionable. Run it monthly, run it before a launch, run it when a competitor pivots into your space. Three commands, one report, zero guesswork about what to prioritize.

The pipeline runs inside [Claude Code](https://claude.ai/claude-code) — three commands, each handing off a file to the next. No dashboards to learn, no subscription tiers, no waiting for a vendor to return results.

---

## Pipeline Overview

```
/trademark-cat [MARK]
      │
      │  variants-[mark].txt
      ▼
/trademark-hound [MARK]
      │
      │  hound_scored-[mark].json
      ▼
/trademark-report [MARK]
      │
      ▼
HOUND_REPORT_[MARK]_[DATE].md  (or .csv)
```

Each command hands off a file to the next. You can re-run any stage independently.

---

## Prerequisites

| Requirement | Details |
|---|---|
| [Claude Code](https://claude.ai/claude-code) | The AI coding assistant this pipeline runs inside |
| [Serper.dev](https://serper.dev) API key | Used by `/trademark-hound` for SERP searches. A free tier is available. |
| Python 3.8+ | Required to execute the generated SERP script |
| `requests` library | `pip install requests` |

---

## Quick Start

```bash
# Step 1 — Generate variants
/trademark-cat Datablox

# Step 2 — Search and score
/trademark-hound Datablox

# Step 3 — Generate report
/trademark-report Datablox
```

All outputs are written to a mark directory created automatically (`datablox/` in this example).

---

## Command Reference

### `/trademark-cat`

**The variant brainstorm you'd need a room full of linguists to do manually.**

A single mark can be infringed dozens of ways: swap a vowel, bolt on a suffix, translate the concept into a synonym, combine two of those tricks at once. Trademark Cat generates up to 100+ confusion-risk variants across five linguistic categories — phonetic, orthographic, compound, semantic, and hybrid — then puts every one in front of you for review before a single search is run. Think of it as the creative brief for the investigation that follows.

**Usage**
```
/trademark-cat [MARK]
/trademark-cat [MARK] "goods and services description"
```

**What it does**

1. **Context intake** — Prompts for the mark's goods/services description, mark criticality (0–3), and key geographies. Stores this in `[mark]/context-[mark].md` for reuse on subsequent runs. If a context file already exists, it is loaded automatically.

2. **Negative constraint derivation** — Identifies non-competing industries that should be excluded from variant generation. For example, for a data infrastructure mark, the agent internally excludes variants from construction, food service, and automotive — industries where consumer confusion is implausible.

3. **Variant count confirmation** — Asks how many variants to generate. The default is **100** (~20 per category). Any integer is accepted; say "default" or press Enter to use 100.

4. **Variant generation** — Generates variants across five categories:

   | Category | Description | Example variants for *Datablox* |
   |---|---|---|
   | Phonetic & Orthographic | Sound-alike spellings, vowel swaps, consonant substitutions, homophones | Datablocks, Datablox, Dātablox, Datablock, Databl0x |
   | Compound Suffix-State | Adding or removing common brand suffixes (-Tech, -AI, -Hub, -Labs, -Pro, -Corp) | DatabloxAI, DatabloxLabs, DatabloxHQ, DatabloxCloud |
   | Semantic Synonyms | Words with equivalent or near-equivalent meaning | DataBricks, InfoBlox, DataVault, DataCube, ByteBlox |
   | Conceptual Variants | Related concepts, translated meanings, associated ideas | DataFoundation, InfoArchitect, DataNode, DataStack |
   | Phonetics/Hybrids | Cross-category combinations of the above | Datablox-Pro, D8ablox, DataBlox.io, Datab10x |

5. **Review loop** — Presents the full variant list for attorney review. Feedback is applied iteratively (add, remove, rebalance) until the attorney explicitly approves. No file is written until approval is given.

6. **File output** — Writes `[mark]/variants-[mark].txt` with each variant annotated by confusion axis and rationale.

**Output file format**
```
# Context: cloud data infrastructure software
# Phonetic & Orthographic
Datablocks  # phonetic: final /ks/ identical; near-identical when spoken
Dātablox    # orthographic: diacritic insertion; visually similar
...
# Compound Suffix-State
DatabloxAI  # compound: AI suffix; strong association with B2B data tooling
DatabloxHub # compound: hub suffix; marketplace/ecosystem brand pattern
...
```

**Generated files**
```
[mark]/
  context-[mark].md        ← mark context (goods/services, criticality, geography)
  variants-[mark].txt      ← approved variant list with annotations
```

---

### `/trademark-hound`

**The investigator that never gets tired, never skips a lead, and cites its sources.**

Trademark Hound takes every variant Cat generated and hunts it across the open web — hundreds of search queries, thousands of raw results. Then it gets ruthless: known-safe URLs are dropped, non-commercial noise is filtered, and every surviving lead is fetched, read, and scored against an eight-factor weighted threat matrix grounded in actual page content. What comes back isn't a wall of links — it's a shortlist of scored, evidence-backed commercial threats ranked by how urgently they need your attention.

**Usage**
```
/trademark-hound [MARK]
```

**Prerequisites** — `/trademark-cat [MARK]` must have been run first to produce `variants-[mark].txt`.

**What it does**

**Stage 1 — SERP Search**

On first run, prompts for your Serper.dev API key and generates a Python search script at `[mark]/hound-SERP-[mark].py`. This script:

- Searches the **literal mark** first (top 50 results) before processing any variants
- Searches each variant with an exact-match query (`"Datablox"`)
- Returns up to 10 organic results per variant
- Runs with a 0.5-second delay between requests
- Writes all raw results to `[mark]/hound_leads-[mark].json`

With ~100 variants, expect approximately 60 seconds of runtime.

**Stage 2 — Safelist Filter**

Loads `[mark]/safelist-[mark].json` (if it exists) and discards any leads whose URL was previously dismissed. Safelisted URLs are silently excluded from all future runs.

**Stage 3 — Domain Triage**

Automatically excludes leads from ~120 known non-commercial domains without fetching them. Excluded categories include encyclopedias, news outlets, social media, business directories, academic databases, patent/trademark registries, app stores, code hosting platforms, and other noise sources. Domain exclusion applies at the hostname level only — brand sites with a `/blog/` path are not excluded.

**Stage 4 — Attorney Approval Gate**

Before fetching any page content, presents all surviving leads as a numbered table:

```
14 URLs cleared domain triage. Review before fetching:

 #  | URL                                  | Variant
----|--------------------------------------|----------
 1  | https://datablox.io/                 | DatabloxIO
 2  | https://somecompany.com/datablox     | Datablox
...
```

Reply `proceed` to continue, or list numbers to skip (e.g. `3, 7`).

**Stage 5 — Content Signal Triage**

Fetches the approved URLs in parallel batches of 10. Each URL is classified as one of: `commercial`, `developer-docs`, `academic`, `government`, `informational`, `crypto/finance`, or `error/inaccessible`. Only `commercial` results carrying plausible goods/services overlap proceed to scoring. All others are logged and discarded.

**Stage 6 — 8-Factor Threat Scoring**

Each surviving commercial lead is scored against eight factors. Attorney-supplied values (mark criticality and geography) are taken directly from the context file and are never inferred.

| Factor | Scale | Weight | Max |
|---|---|---|---|
| Mark Criticality | 0–3 | ×3 | 9 |
| Similarity (sight/sound/meaning) | 0–4 | ×3 | 12 |
| Goods/Services & Channels Overlap | 0–3 | ×3 | 9 |
| Geography Priority | 0–3 | ×2 | 6 |
| Evidence of Confusion/Association | 0–2 | ×2 | 4 |
| Rights Posture (ours vs. theirs) | 0–2 | ×2 | 4 |
| Counterparty Profile | 0–2 | ×1 | 2 |
| Enforcement Cost vs. Budget | 0–2 | ×1 | 2 |
| **Maximum total** | | | **48** |

**Risk tiers:**
- **High** — score ≥ 15
- **Medium** — score 10–14
- **Low** — score < 10 (not written to output)

Each factor score is grounded in a direct quote or paraphrase from the fetched page. No factor is inferred without supporting evidence.

**Run summary**

At completion, Trademark Hound prints a full pipeline summary:

```
=== Trademark Hound Run Summary ===
Trademark: DATABLOX
Run date: 2026-04-05

  Raw SERP leads:              312
  Excluded by safelist:          8
  Excluded by domain triage:   201
  Skipped by attorney:           4
  Excluded by content triage:   71
  Scored leads (Med + High):    28

  High (>= 15):                 21
  Medium (10-14):                7
  Low (< 10, dropped):          15

Next step: Run `/trademark-report DATABLOX` to generate the attorney report.
```

**Generated files**
```
[mark]/
  hound-SERP-[mark].py         ← generated SERP script (contains API key — do not commit)
  hound_leads-[mark].json      ← raw SERP results
  hound_scored-[mark].json     ← Medium and High scored leads
  safelist-[mark].json         ← URLs dismissed in prior runs (updated after /trademark-report)
```

> **API Key Security** — `hound-SERP-[mark].py` contains your Serper.dev API key in plaintext. Add `[mark]/hound-SERP-*.py` to `.gitignore` before committing.

**Safelist ingestion (re-invocation mode)**

After filling in the `THREAT?` column in a report, pass the report path as a second argument to update the safelist:

```
/trademark-hound Datablox datablox/HOUND_REPORT_DATABLOX_2026-04-05.md
```

Rows marked `NO` are added to `[mark]/safelist-[mark].json` and excluded from all future runs. Rows marked `YES` are retained. Blank rows are skipped.

---

### `/trademark-report`

**From raw scores to a report your team can act on — in seconds.**

Trademark Report takes the scored output from Hound and transforms it into a polished deliverable: an executive summary with the numbers that matter, a ranked action table with recommended next steps, and detailed lead cards with the full eight-factor breakdown. Choose markdown for narrative review or CSV for import into Excel, Google Sheets, or your matter management system. A built-in annotation workflow lets you mark each lead as a threat or dismiss it — and dismissed URLs are automatically safelisted so they never appear again.

**Usage**
```
/trademark-report [MARK]
```

**What it does**

1. Prompts for output format: **markdown** (full narrative report) or **csv** (spreadsheet-ready).
2. Loads `[mark]/hound_scored-[mark].json`.
3. Generates the report with all sections described below.
4. Offers an interactive safelist update step to dismiss leads without editing a file.

**Markdown report structure**

```
# Trademark Monitoring Report: DATABLOX
Generated: 2026-04-05
Mark context: cloud data infrastructure software
Prepared by: Trademark Hound

DISCLAIMER: For attorney review only. Does not constitute legal advice.

## Executive Summary
[metric table + 1–3 sentence narrative]

## Attorney Review Table
[sortable table: Date | Trademark/Variant | Entity | URL | Industry |
 Risk Score | Risk Tier | Infringement Analysis | THREAT?]

## Priority Action Table
[ranked table: Priority | Entity | Mark Used | Score | Tier | Recommended Action]

## Scored Lead Cards
[one detailed card per lead with full 8-factor breakdown]

## Methodology Notes
```

**Sample executive summary (hypothetical)**

> The scan surfaced 28 scored leads across the cloud data infrastructure space, with 21 rated High risk. The most urgent concern is DataBlox Systems Inc. (score 41): a direct-overlap cloud data platform operating under an identical mark with an active US trademark application. Three additional Priority C&D candidates operate in overlapping verticals with junior marks. Datablox.io and DatabloxAI present phonetically identical marks but appear to be parked domains, warranting monitoring rather than immediate action.

**Recommended action thresholds**

| Score range | Recommended action |
|---|---|
| ≥ 35 | Immediate C&D |
| 25–34 | Priority C&D |
| 15–24 | Monitor / Consider C&D |
| 10–14 | Monitor |

**CSV report**

The CSV format includes one row per lead with all eight factor scores, evidence text, and metadata columns — designed for import into Excel, Google Sheets, or matter management software.

**THREAT? column workflow**

The Attorney Review Table includes a blank `THREAT?` column for manual annotation:

- Mark `YES` to flag as an active infringement threat
- Mark `NO` to dismiss (adds URL to safelist automatically on re-ingestion)
- Leave blank if the lead requires further review

After annotating the report, run the safelist ingestion command to persist your decisions:

```
/trademark-hound Datablox datablox/HOUND_REPORT_DATABLOX_2026-04-05.md
```

**Generated files**
```
[mark]/
  HOUND_REPORT_[MARK]_[DATE].md   ← full narrative report (markdown format)
  HOUND_REPORT_[MARK]_[DATE].csv  ← spreadsheet report (csv format)
```

---

## File Reference

After running the full pipeline for a mark named `Datablox`, the mark directory contains:

```
datablox/
  context-datablox.md               ← mark context (created by /trademark-cat)
  variants-datablox.txt             ← approved variant list with annotations
  hound-SERP-datablox.py            ← SERP search script (contains API key)
  hound_leads-datablox.json         ← raw SERP results
  hound_scored-datablox.json        ← scored leads (Medium + High)
  safelist-datablox.json            ← dismissed URLs (excluded from future runs)
  HOUND_REPORT_DATABLOX_2026-04-05.md
```

---

## The Eight-Factor Threat Matrix

Scores are evidence-grounded — every factor score cites a direct quote or paraphrase from the investigated page. Attorney-supplied values (mark criticality and geography) are never overridden by the agent.

| Factor | What is assessed |
|---|---|
| **Mark Criticality** | How important is this mark to the protected business? Supplied by attorney (0–3). |
| **Similarity** | Sight, sound, and meaning comparison between the variant and the protected mark (0–4). |
| **Goods/Services Overlap** | How closely do the infringer's goods/services align with the protected mark's scope (0–3). |
| **Geography Priority** | Does the infringer operate in the attorney's declared priority geographies (0–3)? |
| **Confusion Evidence** | Is there observable evidence of actual consumer confusion or association (0–2)? |
| **Rights Posture** | Who likely holds senior rights — the protected mark or the infringer (0–2)? |
| **Counterparty Profile** | How large and well-resourced is the infringer? Smaller parties score higher (easier to resolve) (0–2). |
| **Enforcement Cost** | How expensive or complex would enforcement be (0–2)? Smaller/domestic parties score higher. |

**Maximum possible score: 48 points**

---

## Safelist Management

The safelist (`[mark]/safelist-[mark].json`) is a flat JSON array of URLs. Any URL in this file is silently excluded from all future `/trademark-hound` runs for that mark.

URLs are added to the safelist in two ways:
1. The interactive step at the end of `/trademark-report`
2. The safelist ingestion re-invocation: `/trademark-hound [MARK] [report-path]`

The safelist is never modified destructively — new entries are appended and the file is written atomically.

---

## Disclaimer

Reports generated by this pipeline are for attorney review and internal use only. They do not constitute legal advice, an opinion of counsel, or a legal conclusion. All findings require independent legal evaluation before any action is taken.
