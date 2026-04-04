# Phase 3: Reports, Safe List, and Pipeline Validation — Research

**Researched:** 2026-04-04
**Domain:** Claude Code slash command authoring, atomic file I/O, Markdown report contracts, safe list feedback loops, end-to-end pipeline validation
**Confidence:** HIGH

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| HND-13 | Write `HOUND_REPORT_[TRADEMARK]_[YYYY-MM-DD].md` with Medium and High entries only | Already partially built in `/trademark-report` — gaps identified below |
| HND-14 | Report table columns: Date, Trademark/Variant, Entity Name, URL, Industry, Risk Score, Risk Tier, Infringement Analysis, THREAT? | Current `/trademark-report` uses a different table schema — the THREAT? column and flat table format are missing |
| HND-15 | Disclaimer header: report is for attorney review only, does not constitute legal advice | Missing from current `/trademark-report` output — the disclaimer is absent from HOUND_REPORT_TESTMARK_2026-04-04.md |
| HND-16 | Run summary to user: total leads found, safelist-filtered, investigated, High/Medium/Low counts, report file path | Missing from `/trademark-hound` — hound outputs a final count but not this structured summary |
| HND-17 | Re-invocation with reviewed report path reads THREAT? column, adds "NO" entries to safelist | Not yet implemented — /trademark-hound has no reviewed-report-path intake branch |
| HND-18 | Atomic safelist write (write to temp, then rename) | Not yet implemented — /trademark-report writes safelist directly |
| HND-19 | Report how many entries added to safelist and total now excluded | Partially in /trademark-report Step 4, but needs to propagate to /trademark-hound's HND-17 branch |
</phase_requirements>

---

## Summary

Phase 3 closes the pipeline loop. The critical finding from reviewing the existing artifacts is that `/trademark-report` was built during Phase 2 verification and it satisfies the report *generation* workflow (executive summary, scored lead cards, interactive safelist update step), but it does not fully satisfy the HND-13 through HND-19 requirements as written. Specifically: the report schema in the REQUIREMENTS.md specifies a flat table with a THREAT? column (the attorney marks YES/NO inline in the Markdown), but the current `/trademark-report` command generates a rich narrative format with lead cards and no THREAT? column. The safelist update in `/trademark-report` is also done at report-generation time via interactive prompts, not via the re-invocation pattern described in HND-17 (passing a reviewed report path to `/trademark-hound`). The atomic write requirement (HND-18) is also unmet — current safelist writes go direct.

The core planning question for this phase is: **which implementation model to adopt?** The REQUIREMENTS.md describes a two-step attorney workflow: (1) generate report with blank THREAT? column, (2) attorney fills in YES/NO in the file, (3) re-run `/trademark-hound [TRADEMARK] [report-path]` to ingest those annotations. The existing `/trademark-report` adopts a different model: interactive prompts during report generation where the attorney dismisses leads by number. Both approaches work; they differ in when and how attorney judgment is captured. The planner must decide which model to honor — or whether to reconcile them.

The pipeline validation requirement means verifying that the five-phase sequence (Cat → Hound → Report → Safelist Update → Re-run Hound with safelist loaded) produces consistent, non-corrupted, orphan-free files. This is primarily a human walkthrough, not an automated test — the same pattern used for Phase 2's Plan 02-03 walkthrough. Contract tests (structural checks on the command files) can cover the new requirements in `tests/test_phase3.py`.

**Primary recommendation:** Add a THREAT? column and disclaimer to the report format in `/trademark-report`, implement the re-invocation safelist-ingestion branch in `/trademark-hound`, upgrade safelist writes to use atomic temp-file-rename, and run an end-to-end walkthrough. The existing interactive dismiss flow in `/trademark-report` can coexist as a fast path.

---

## What Is Already Built (Phase 2 Early Delivery)

This is the most important finding for planning. Audit what exists vs. what the requirements say.

### Requirement-by-Requirement Status

| Req | Requirement Text | Built? | Where | Gap |
|-----|-----------------|--------|-------|-----|
| HND-13 | Write `HOUND_REPORT_[TRADEMARK]_[YYYY-MM-DD].md` with Medium/High only | YES (partial) | `/trademark-report` Step 3A | File naming matches. Content matches. But report format differs from HND-14 flat table spec. |
| HND-14 | Columns: Date, Trademark/Variant, Entity Name, URL, Industry, Risk Score, Risk Tier, Infringement Analysis, THREAT? | NO | `/trademark-report` | Current report has Priority Action Table + Lead Cards — no flat table with THREAT? column. The THREAT? column for attorney inline annotation is absent. |
| HND-15 | Disclaimer: attorney review only, not legal advice | NO | — | No disclaimer present in `HOUND_REPORT_TESTMARK_2026-04-04.md`. The Methodology Notes section at the bottom says nothing about legal advice. |
| HND-16 | Run summary: totals found, filtered, investigated, High/Medium/Low counts, report path | NO | `/trademark-hound` | Hound outputs scores but no structured "run summary" block at the end. `/trademark-report` reports `loaded N scored leads` but not the full pipeline funnel. |
| HND-17 | Re-invoke `/trademark-hound` with reviewed report path → read THREAT? column → add "NO" entries to safelist | NO | — | `/trademark-hound` has no second-mode intake. The current safelist update lives in `/trademark-report` via interactive prompts, not THREAT? column parsing. |
| HND-18 | Atomic safelist write (temp file then rename) | NO | — | `/trademark-report` Step 4 writes directly with the Write tool. No temp-file-then-rename pattern. |
| HND-19 | Report count of entries added and total excluded from future runs | PARTIAL | `/trademark-report` Step 4 | Step 4 reports count after interactive update. Missing from the HND-17 branch (doesn't exist yet). |

### What the Existing `/trademark-report` Actually Does

- Generates `HOUND_REPORT_[TRADEMARK]_[DATE].md` or `.csv` (HND-13 filename pattern: YES)
- Has an executive summary, priority action table, and scored lead cards (rich narrative format)
- Has an interactive Step 4: attorney lists lead numbers/names to add to safelist
- Writes safelist directly (no atomic write)
- Reports count of safelist additions
- Does NOT have a THREAT? column (HND-14 flat table format)
- Does NOT have a legal disclaimer (HND-15)
- Does NOT produce the run summary funnel described in HND-16

---

## Architecture Patterns

### The Two Safelist Update Models

There are two distinct design approaches for HND-17. The planner must choose one or reconcile both.

**Model A — Inline THREAT? column (what HND-17 specifies):**
1. Report is generated with a blank THREAT? column
2. Attorney opens the `.md` file, edits the column to YES/NO/MONITOR for each entry
3. Attorney re-runs `/trademark-hound TESTMARK HOUND_REPORT_TESTMARK_2026-04-04.md`
4. Hound parses the markdown table, finds rows where THREAT? = "NO", adds those URLs to safelist atomically
5. Hound reports count of additions and new total

**Model B — Interactive dismiss during report generation (what `/trademark-report` currently does):**
1. Report is generated and displayed
2. Immediately after, attorney is prompted: "List leads to dismiss (by number or name)"
3. Attorney types dismissals, safelist is updated immediately
4. No re-invocation of `/trademark-hound` needed

**Recommendation:** Implement Model A as the primary pattern (to satisfy HND-17 as written) AND keep Model B's interactive dismiss in `/trademark-report` as a fast-path alternative. Model A is superior for asynchronous attorney review (they can review overnight, then commit), and the THREAT? column serves as a durable audit trail in the report file itself. The two models coexist naturally.

### Atomic Safelist Write Pattern (HND-18)

Claude Code slash commands can instruct Claude to use Bash for atomic writes. The shell-idiomatic pattern:

```bash
# Write to temp file, then rename atomically
python3 -c "import json, sys; data = json.load(open('safelist-testmark.json')); data.append('https://new-url.com'); open('safelist-testmark.json.tmp', 'w').write(json.dumps(data, indent=2))"
mv safelist-testmark.json.tmp safelist-testmark.json
```

Or equivalently, instruct Claude to: write to `safelist-[TRADEMARK].json.tmp`, then `mv` (rename) to `safelist-[TRADEMARK].json`. The rename is atomic at the filesystem level on macOS (POSIX rename semantics). This prevents a half-written file if Claude is interrupted mid-write.

**Implementation in a slash command:** The command text should say "Write to `safelist-[sanitized_name].json.tmp` using the Write tool, then use the Bash tool to run `mv safelist-[sanitized_name].json.tmp safelist-[sanitized_name].json`."

**Cleanup:** If the tmp file exists when the command starts (orphaned from a prior interrupted run), log a warning and delete it before starting.

### Markdown THREAT? Column Parsing

For HND-17, `/trademark-hound` must parse a Markdown table with a THREAT? column. The parsing requirement is simple: find rows where the last column value is `NO` (case-insensitive, trimmed). The URL is in the URL column.

The slash command can instruct Claude to:
1. Read the reviewed report file
2. Locate the table with a THREAT? header
3. For each row where THREAT? = "NO", extract the URL column value
4. Add those URLs to the safelist

This is LLM-native parsing — Claude handles Markdown tables well and no regex or script is needed.

**Edge cases to document:**
- THREAT? column is blank (attorney hasn't reviewed yet) → skip entry, do not add to safelist
- THREAT? = "YES" → keep for enforcement tracking, do not add to safelist
- THREAT? = "NO" → add URL to safelist (suppress future scans)
- Duplicate URLs already in safelist → skip silently, do not double-count
- Report file not found → halt with clear error

### Run Summary Format (HND-16)

The run summary belongs at the END of `/trademark-hound` after `hound_scored-[TRADEMARK].json` is written. Current Hound already outputs intermediate counts (leads found, safelist filtered, etc.). Phase 3 adds a structured terminal summary block:

```
=== Trademark Hound Run Summary ===
Trademark: TESTMARK
Run date: 2026-04-04

  Raw SERP leads:          564
  Excluded by safelist:     12
  After domain triage:      52
  Skipped by attorney:       5
  After content triage:     14
  Investigated & scored:    14

  Risk distribution:
    High (≥ 15):            13
    Medium (10–14):          1
    Low (< 10, dropped):    N/A (already filtered)

Report: Run /trademark-report TESTMARK to generate the report.
```

This summary does NOT write the report itself — report generation remains the responsibility of `/trademark-report`. Hound simply surfaces the funnel and instructs the attorney to run `/trademark-report` next.

**Note:** The actual Low count is harder to track because Hound drops Low leads during scoring. HND-16 says "High/Medium/Low counts" — the Low count can be reported as the difference between investigated and (High + Medium). Or the command can track a running low_count counter during scoring. The latter is cleaner.

### Disclaimer Pattern (HND-15)

The disclaimer must appear in the report file. Based on the requirements ("for attorney review only and does not constitute legal advice"), the standard placement is:

```markdown
> **DISCLAIMER:** This report is prepared for attorney review and internal use only. It does not constitute legal advice, an opinion of counsel, or a legal conclusion. All findings require independent legal evaluation before any action is taken.
```

Location options:
- Immediately after the report header (before Executive Summary) — HIGH visibility, attorney sees it first
- As a footer (after Methodology Notes) — common legal doc convention

**Recommendation:** Place it between the report header block and the Executive Summary, using a Markdown blockquote (`>`). This matches legal document conventions where disclaimers precede substantive content. The `/trademark-report` command's Step 3A template must be updated to include this block.

### Report Table Schema Reconciliation (HND-14)

The REQUIREMENTS.md specifies a flat table with these columns:
```
Date | Trademark/Variant | Entity Name | URL | Industry | Risk Score | Risk Tier | Infringement Analysis | THREAT?
```

The current `/trademark-report` generates:
- A Priority Action Table (Priority | Entity | Mark Used | Score | Tier | Recommended Action)
- Full Lead Cards with factor-level detail

**Reconciliation approach:** Add the HND-14 flat table as a new section in the markdown report, positioned between the Executive Summary and the Priority Action Table (or replacing the Priority Action Table). Call it "Attorney Review Table" to distinguish it from the priority action view. The THREAT? column is blank in fresh reports (dashes or empty strings).

The Lead Cards can remain as a secondary section — they provide the evidence detail that supports attorney decisions. The flat table is the attorney's working document; the Lead Cards are the supporting analysis.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead |
|---------|-------------|-------------|
| Atomic file writes | Custom Python write-and-swap logic | `Write` tool to `.tmp` filename, then `Bash` tool `mv` (POSIX rename) |
| Markdown table parsing | Regex-based table parser | LLM-native: instruct Claude to read the table and identify THREAT?=NO rows |
| JSON deduplication | Set-diff logic | Instruct Claude: "add URL only if not already in the array" — LLM handles this |
| Report file format validation | Schema validator | Structural contract tests in `tests/test_phase3.py` (same pattern as Phases 1–2) |

**Key insight:** In Claude Code slash commands, Claude IS the parser/processor. Complex parsing tasks that would require scripts in other contexts are handled naturally by the LLM following the command's instructions.

---

## Common Pitfalls

### Pitfall 1: THREAT? Column Left Blank = Unreviewed, Not "Yes"
**What goes wrong:** If attorney runs `/trademark-hound TESTMARK report.md` before filling in any THREAT? values, a naive implementation might ingest all blank entries as "not a threat."
**How to avoid:** The command must explicitly state: "Only process rows where THREAT? is exactly 'NO' (case-insensitive). Blank entries, dashes, and question marks mean unreviewed — skip them."
**Warning signs:** Safelist grows unexpectedly after first report generation before attorney review.

### Pitfall 2: Safelist Grows Without Bound
**What goes wrong:** Each re-run of the safelist update command appends more URLs. If the attorney accidentally passes the same report twice, duplicates accumulate.
**How to avoid:** Deduplicate before writing. The merge step must check `if url not in current_safelist` before adding.
**Warning signs:** Safelist entry count jumps by the full report entry count on second invocation.

### Pitfall 3: Orphaned `.tmp` Files After Interrupted Atomic Write
**What goes wrong:** Atomic write creates `safelist-[TRADEMARK].json.tmp`. If Claude is interrupted before the `mv`, the `.tmp` file is orphaned. On the next run, the command reads the real safelist file (which is intact), but the `.tmp` sits alongside it indefinitely.
**How to avoid:** At the start of the safelist update step, check for `safelist-[sanitized_name].json.tmp` and remove it if found before starting the write cycle.
**Warning signs:** `.tmp` files appearing in the workspace.

### Pitfall 4: Report Written But HND-16 Summary Missing
**What goes wrong:** `/trademark-hound` completes, writes `hound_scored-*.json`, then says "run `/trademark-report`" — but never surfaces the funnel counts. The attorney has no summary without reading the scored JSON.
**How to avoid:** The run summary block is written by `/trademark-hound` to the conversation, not to a file. It reads the intermediate counts tracked during Steps 4–7 and formats them into the summary table before the final instruction to run `/trademark-report`.
**Warning signs:** HND-16 tested and found to produce no summary output.

### Pitfall 5: Second-Mode Intake in `/trademark-hound` Confuses the Normal Flow
**What goes wrong:** Adding a "reviewed report path" intake branch to `/trademark-hound` that fires when the first argument looks like a file path could accidentally trigger on trademark names that look like paths.
**How to avoid:** Make the second-mode explicit. Check if a second argument is provided AND it matches `HOUND_REPORT_*.md` pattern OR the file exists with that exact name. Do not try to auto-detect from the first argument — require the attorney to be explicit about which report to ingest.
**Warning signs:** Normal `/trademark-hound ACME` invocations triggering the safelist update branch.

### Pitfall 6: Disclaimer Missing From CSV Format
**What goes wrong:** HND-15 says "report includes a disclaimer." The current `/trademark-report` offers both markdown and CSV formats. A disclaimer row or header comment should appear in the CSV too, but is easy to forget.
**How to avoid:** Add disclaimer handling to Step 3B (CSV) as well — include a first-row comment or prepend the disclaimer as a comment line. CSV format typically allows `#` comment lines or a dedicated metadata row.

---

## Code Examples

### Atomic Safelist Write (Bash pattern for slash command instruction)

```bash
# Write updated safelist to temp file
# (Claude uses Write tool to write safelist-testmark.json.tmp with the merged array)
# Then atomically replace:
mv safelist-testmark.json.tmp safelist-testmark.json
```

Source: POSIX rename(2) semantics — atomic on macOS/Linux for same-filesystem moves.

### THREAT? Column Parsing Logic (slash command prose instruction)

```
For each row in the Attorney Review Table:
  - Locate the THREAT? column value
  - Trim whitespace and compare case-insensitively
  - If value == "NO": collect the URL from that row's URL column
  - If value == "YES", blank, "-", or any other value: skip the row
```

This is an LLM instruction pattern, not code — Claude executes it natively when reading the report file.

### Run Summary Block (target output format for HND-16)

```
=== Trademark Hound Run Summary ===
Trademark: [TRADEMARK]
Run date: [YYYY-MM-DD]

  Raw SERP leads:          [N]
  Excluded by safelist:    [M]
  Remaining after domain triage: [P]
  Skipped by attorney:     [Q]
  After content triage:   [R]
  Scored leads:            [S]

  High (≥ 15):             [X]
  Medium (10–14):          [Y]
  Low (< 10, dropped):     [Z]

Next step: Run `/trademark-report [TRADEMARK]` to generate the attorney report.
```

---

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | Python stdlib `unittest` (established in Phases 1–2) |
| Config file | None — run directly |
| Quick run command | `python3 tests/test_phase3.py 2>&1 \| tail -3` |
| Full suite command | `python3 tests/test_phase1.py && python3 tests/test_phase2.py && python3 tests/test_phase3.py` |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| HND-13 | `HOUND_REPORT_` filename pattern in `/trademark-report` | unit | `python3 tests/test_phase3.py 2>&1 \| tail -3` | ❌ Wave 0 |
| HND-14 | THREAT? column present in `/trademark-report` Step 3A template | unit | `python3 tests/test_phase3.py 2>&1 \| tail -3` | ❌ Wave 0 |
| HND-15 | Disclaimer text present in `/trademark-report` Step 3A template | unit | `python3 tests/test_phase3.py 2>&1 \| tail -3` | ❌ Wave 0 |
| HND-16 | Run summary block present in `/trademark-hound` | unit | `python3 tests/test_phase3.py 2>&1 \| tail -3` | ❌ Wave 0 |
| HND-17 | Re-invocation branch present in `/trademark-hound` intake | unit | `python3 tests/test_phase3.py 2>&1 \| tail -3` | ❌ Wave 0 |
| HND-18 | `.tmp` + `mv` atomic pattern in safelist update steps | unit | `python3 tests/test_phase3.py 2>&1 \| tail -3` | ❌ Wave 0 |
| HND-19 | Safelist count reporting present after update step | unit | `python3 tests/test_phase3.py 2>&1 \| tail -3` | ❌ Wave 0 |
| End-to-end | Full Cat → Hound → Report → Safelist → Re-run pipeline | human-verify | Manual walkthrough | N/A |

### Sampling Rate

- **Per task commit:** `python3 tests/test_phase3.py 2>&1 | tail -3`
- **Per wave merge:** `python3 tests/test_phase1.py && python3 tests/test_phase2.py && python3 tests/test_phase3.py`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps

- [ ] `tests/test_phase3.py` — contract tests for `/trademark-report` (HND-13, HND-14, HND-15, HND-19) and `/trademark-hound` additions (HND-16, HND-17, HND-18); same `unittest` + `assertIn` structural-check pattern as prior phases; no external dependencies

---

## Standard Stack

This phase is entirely within the existing slash command stack. No new libraries needed.

### Core

| Artifact | Purpose | Pattern |
|----------|---------|---------|
| `.claude/commands/trademark-report.md` | Report generation (modify in place) | Update Step 3A template to add THREAT? column, disclaimer, and note about HND-17 re-invocation |
| `.claude/commands/trademark-hound.md` | Pipeline intake + safelist update (modify in place) | Add second-mode intake branch for reviewed report path; add run summary block at end of Step 7 |
| `tests/test_phase3.py` | Contract tests for new requirements | New file, same pattern as `tests/test_phase2.py` |

### No New Dependencies

- Atomic write: POSIX `mv` via Bash tool (already available)
- Markdown parsing: LLM-native (no script needed)
- JSON merge: LLM-native (instruct Claude to deduplicate)
- Test framework: `python3 unittest` (already established)

---

## State of the Art

| Old Approach | Current Approach | Impact for Phase 3 |
|--------------|------------------|-------------------|
| `/trademark-report` built as standalone Phase 3 command | Already exists from Phase 2 | Phase 3 is modifications to existing command, not new command authoring |
| Safelist updated via interactive prompts at report time | Must also support THREAT? column re-ingestion (HND-17) | Two coexisting update paths; both valid |
| No disclaimer in report | HND-15 requires disclaimer | Single-line addition to report template |
| Direct safelist write | HND-18 requires atomic write | Upgrade to `.tmp` + `mv` pattern in both update paths |

---

## Open Questions

1. **Which report format satisfies HND-14?**
   - What we know: HND-14 specifies a flat table (Date | Trademark/Variant | Entity | URL | Industry | Score | Tier | Infringement Analysis | THREAT?). The current report has rich lead cards instead.
   - What's unclear: Does the planner want to replace the Priority Action Table with the HND-14 flat table, add it as a second table, or restructure entirely?
   - Recommendation: Add the HND-14 flat table as a new "Attorney Review Table" section. Keep the Lead Cards as supporting detail. This preserves the existing report's value while satisfying the requirement.

2. **Where does the run summary (HND-16) live — in `/trademark-hound` or `/trademark-report`?**
   - What we know: HND-16 says "Trademark Hound displays a summary." The ROADMAP says this is a Hound-side output.
   - What's unclear: `/trademark-hound` doesn't currently track Low count (it drops Lows during scoring without counting them). The summary may need a Low counter added to the scoring loop.
   - Recommendation: Add the summary to the END of `/trademark-hound`'s Step 7 output. Track low_count during scoring. The Low count = investigated - (high_count + medium_count).

3. **What happens if attorney reviews only some rows in the THREAT? column?**
   - What we know: HND-17 says "adds all entries marked NO." Blank entries should be skipped.
   - What's unclear: Should the re-invocation warn if some rows are still blank (unreviewed)?
   - Recommendation: After processing, report "X entries marked NO (added to safelist), Y entries marked YES (retained for enforcement), Z entries still blank (not reviewed, skipped)." This gives the attorney a complete accounting.

---

## Sources

### Primary (HIGH confidence)
- Direct read of `.claude/commands/trademark-report.md` — full command text, all steps, exact schema
- Direct read of `.claude/commands/trademark-hound.md` — full pipeline, existing output format
- Direct read of `HOUND_REPORT_TESTMARK_2026-04-04.md` — actual output, confirmed disclaimer absent
- Direct read of `safelist-testmark.json` — 17 entries, direct-write format (no atomic write)
- Direct read of `tests/test_phase2.py` — confirms `assertIn`/`unittest` pattern for contract tests
- Direct read of `.planning/REQUIREMENTS.md` — HND-13 through HND-19 verbatim

### Secondary (MEDIUM confidence)
- POSIX rename(2) semantics: atomic on same-filesystem mv on macOS/Linux — well-established system programming fact

### Tertiary (LOW confidence)
- None — all findings are from direct artifact inspection

---

## Metadata

**Confidence breakdown:**
- Gap analysis (what's built vs. what's required): HIGH — based on direct file reads of both the requirements and the existing artifacts
- Architecture patterns (atomic write, THREAT? parsing): HIGH — standard patterns with no ambiguity
- Test framework approach: HIGH — continuing established Phase 1/2 pattern
- Planning decisions (which model for HND-17): MEDIUM — the right answer depends on planner judgment about report schema; both options are technically straightforward

**Research date:** 2026-04-04
**Valid until:** N/A — this is a single-milestone project; findings reflect current artifact state
