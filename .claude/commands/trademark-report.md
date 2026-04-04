---
description: "Generate a formatted trademark monitoring report from hound_scored-[TRADEMARK].json. Produces HOUND_REPORT_[TRADEMARK]_[DATE].md or .csv with executive summary, ranked action table, full scored lead cards, and an interactive safelist update step. Run after /trademark-hound completes."
allowed_tools: ["Read", "Write", "Bash"]
---

## Intake

Parse `$ARGUMENTS` to extract the trademark name (first token or first quoted string).

If `$ARGUMENTS` is empty, ask:
> "Which trademark should I report on? (e.g. `testmark`)"

Sanitize the trademark name for filenames: replace spaces with hyphens, convert to lowercase, remove any characters that are not letters, numbers, or hyphens. Store as `sanitized_name`.

Set `report_date` to today's date in YYYY-MM-DD format.

Ask the attorney:
> "Which format would you like?
> - **markdown** — full narrative report with executive summary, scored lead cards, and methodology notes (`HOUND_REPORT_[TRADEMARK]_[DATE].md`)
> - **csv** — one row per lead with all 8 factor scores and evidence columns, ready for spreadsheet import (`HOUND_REPORT_[TRADEMARK]_[DATE].csv`)"

Wait for the response. Accept any of: `markdown`, `md`, `csv`, `spreadsheet`, `excel`. Store as `output_format`.

Set `report_filename` to:
- If markdown: `HOUND_REPORT_[UPPERCASE TRADEMARK]_[report_date].md`
- If csv: `HOUND_REPORT_[UPPERCASE TRADEMARK]_[report_date].csv`

---

## Step 1: Load Scored Leads

Check whether `hound_scored-[sanitized_name].json` exists.

If it does NOT exist, output:
> "No scored leads file found for [TRADEMARK]. Please run `/trademark-hound [TRADEMARK]` first."
Then stop.

Read and parse the file. Store leads as `scored_leads`.

Also read `variants-[sanitized_name].txt` if it exists — extract the `# Context:` line and store as `protected_mark_context`. If not found, use "[goods/services not specified]".

Report:
> "Loaded [N] scored leads for [TRADEMARK] | Context: [protected_mark_context]"

---

## Step 2: Compute Summary Statistics

From `scored_leads`, compute:
- `count_high` = leads where risk_tier == "High"
- `count_medium` = leads where risk_tier == "Medium"
- `total` = count_high + count_medium
- `top_score` = highest total_score in the set
- `top_entity` = entity_name with the highest total_score

Assign recommended actions by score:

| Score range | Action label |
|-------------|-------------|
| ≥ 35 | Immediate C&D |
| 25–34 | Priority C&D |
| 15–24 | Monitor / Consider C&D |
| 10–14 | Monitor |

---

## Step 3A: Write Markdown Report

*Execute this step only if `output_format` is markdown.*

Construct the full report content and write it to `[report_filename]` using the Write tool.

The report must follow this exact structure:

```markdown
# Trademark Monitoring Report: [TRADEMARK]
**Generated:** [report_date]
**Mark context:** [protected_mark_context]
**Prepared by:** Trademark Hound

---

> **DISCLAIMER:** This report is prepared for attorney review and internal use only. It does not constitute legal advice, an opinion of counsel, or a legal conclusion. All findings require independent legal evaluation before any action is taken.

---

## Executive Summary

| Metric | Value |
|--------|-------|
| Total scored leads | [total] |
| High risk | [count_high] |
| Medium risk | [count_medium] |
| Highest threat score | [top_score] / 48 — [top_entity] |
| Report date | [report_date] |

[1–3 sentence narrative: what the scan found, the most urgent concern, and the overall risk posture.]

---

## Attorney Review Table

| Date | Trademark/Variant | Entity Name | URL | Industry | Risk Score | Risk Tier | Infringement Analysis | THREAT? |
|------|-------------------|-------------|-----|----------|------------|-----------|----------------------|---------|
[Sort leads by total_score descending. For each lead, output one row:]
| [report_date] | [variant] | [entity_name] | [url] | [industry] | [total_score] | [risk_tier] | [One sentence summary of the strongest infringement factor and evidence from the scoring.] | |

*THREAT? column: Attorney marks YES (enforce), NO (dismiss to safelist), or leave blank (needs further review). Run `/trademark-hound [TRADEMARK] [this-report-filename]` after filling in this column to update the safelist.*

---

## Priority Action Table

| Priority | Entity | Mark Used | Score | Tier | Recommended Action |
|----------|--------|-----------|-------|------|--------------------|
[Sort leads by total_score descending. For each lead, output one row:]
| [rank] | [entity_name] | [variant] | [total_score] | [risk_tier] | [action label from Step 2] |

---

## Scored Lead Cards

[For each lead sorted by total_score descending, output:]

### [rank]. [entity_name] — Score: [total_score] ([risk_tier])
**URL:** [url]
**Variant matched:** [variant]
**Industry:** [industry]
**Recommended action:** [action label]

| Factor | Score | Max | Weight | Subtotal | Evidence |
|--------|-------|-----|--------|----------|----------|
| Mark Criticality | [score] | 3 | ×3 | [subtotal] | [evidence] |
| Similarity | [score] | 4 | ×3 | [subtotal] | [evidence] |
| Goods/Services Overlap | [score] | 3 | ×3 | [subtotal] | [evidence] |
| Geography Priority | [score] | 3 | ×2 | [subtotal] | [evidence] |
| Confusion Evidence | [score] | 2 | ×2 | [subtotal] | [evidence] |
| Rights Posture | [score] | 2 | ×2 | [subtotal] | [evidence] |
| Counterparty Profile | [score] | 2 | ×1 | [subtotal] | [evidence] |
| Enforcement Cost | [score] | 2 | ×1 | [subtotal] | [evidence] |
| **TOTAL** | | | | **[total_score]** | |

---

[repeat for each lead]

---

## Methodology Notes

- **Variants searched:** ~100 phonetic, compound, semantic, conceptual, and hybrid variants generated by `/trademark-cat`
- **SERP source:** Serper.dev organic results, one search per variant
- **Triage pipeline:** Safelist filter → domain triage (~120 excluded domains) → attorney batch approval gate → parallel content-signal fetch → 8-factor scoring
- **Scoring max:** 48 points (Mark Criticality 9 + Similarity 12 + Goods/Services 9 + Geography 6 + Confusion 4 + Rights 4 + Counterparty 2 + Enforcement 2)
- **Risk tiers:** High ≥ 15 | Medium 10–14 | Low < 10 (not written to output)
- **Safelist:** URLs added to safelist are excluded from future scans automatically

---

*Generated by Trademark Hound · /trademark-cat + /trademark-hound + /trademark-report*
```

After writing, report:
> "Report written to: [report_filename]"

Then proceed to Step 4.

---

## Step 3B: Write CSV Report

*Execute this step only if `output_format` is csv.*

The first row of the CSV file must be a comment row: `# DISCLAIMER: For attorney review only. Does not constitute legal advice.` — prefix the hash-comment as the literal first line before the header row.

Write a CSV file to `[report_filename]` using the Write tool.

**Formatting rules:**
- First line: the disclaimer comment row starting with `#`.
- Second line: the column headers.
- Subsequent lines: one data row per lead, sorted by total_score descending.
- All text fields must be enclosed in double quotes.
- Double quotes within field values must be escaped as two double quotes (`""`).
- Numeric fields (scores) are unquoted integers.
- The `recommended_action` field uses the action label from Step 2.
- `report_date` and `protected_mark_context` repeat on every row.

**CSV columns (in this order):**

```
rank, entity_name, url, variant, industry, total_score, risk_tier, recommended_action,
mark_criticality_score, mark_criticality_evidence,
similarity_score, similarity_evidence,
goods_services_overlap_score, goods_services_overlap_evidence,
geography_priority_score, geography_priority_evidence,
confusion_evidence_score, confusion_evidence_evidence,
rights_posture_score, rights_posture_evidence,
counterparty_profile_score, counterparty_profile_evidence,
enforcement_cost_score, enforcement_cost_evidence,
report_date, protected_mark_context
```

After writing, report:
> "Report written to: [report_filename]"

Then proceed to Step 4.

---

## Step 4: Safelist Update (Interactive)

After the report is written, present this prompt to the attorney:

> "Review the scored leads above. To dismiss any leads from future scans (add to safelist), list their numbers or entity names (e.g. '4, 7' or 'Synopsys, CheckMark'). These will be added to `safelist-[sanitized_name].json`.
>
> Reply **'done'** to finish without adding to safelist, or list the leads to dismiss."

Wait for the attorney's reply.

**If 'done' or equivalent (skip, nothing, no):**
  Report: "Safelist unchanged. Report complete."
  Stop.

**If leads are listed:**
  Parse the input — accept numbers (matching rank in the Priority Action Table) or entity names (case-insensitive partial match).

  For each matched lead:
  - Add its `url` to the safelist
  - Log: "Added to safelist: [entity_name] — [url]"

  Read the current `safelist-[sanitized_name].json` (or start with empty array if not found).
  Merge new URLs (no duplicates).
  Write back to `safelist-[sanitized_name].json`.

  Report:
  > "Safelist updated: [N] URLs added. `safelist-[sanitized_name].json` now contains [M] total entries."

  Then stop.

---

CRITICAL: The report filename is `HOUND_REPORT_[UPPERCASE TRADEMARK]_[YYYY-MM-DD].md` or `.csv` depending on format chosen. Do not write a scored JSON file — that is hound's output, not this command's.
