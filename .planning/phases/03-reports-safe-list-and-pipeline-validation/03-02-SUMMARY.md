---
phase: 03-reports-safe-list-and-pipeline-validation
plan: "02"
subsystem: slash-commands
tags: [trademark-report, trademark-hound, attorney-review, disclaimer, atomic-write, run-summary]
dependency_graph:
  requires: [03-01]
  provides: [03-03, 03-04]
  affects: [trademark-report.md, trademark-hound.md]
tech_stack:
  added: []
  patterns:
    - "Atomic file write: Write to .tmp then Bash mv to replace live file"
    - "Attorney Review Table with THREAT? column for in-document annotation"
    - "Run Summary funnel block displayed after scoring completes"
key_files:
  created: []
  modified:
    - .claude/commands/trademark-report.md
    - .claude/commands/trademark-hound.md
decisions:
  - "Re-invocation section added to trademark-hound.md in Plan 02 (not deferred to Plan 03) — required by HND-18 atomic write test which checks hound.md directly"
  - "Bonus: HND-17 (re-invocation branch) and HND-19 (safelist count reporting) also went GREEN as a natural result of adding the re-invocation section"
  - "Attorney Review Table placed between Executive Summary and Priority Action Table — first substantive section attorneys read post-disclaimer"
metrics:
  duration_minutes: 12
  completed_date: "2026-04-04"
  tasks_completed: 2
  tasks_total: 2
  files_modified: 2
---

# Phase 3 Plan 02: Report Format, Disclaimer, Atomic Write, and Run Summary

One-liner: Patched `/trademark-report` with THREAT? attorney annotation table, legal disclaimer in markdown and CSV paths, and atomic safelist write; patched `/trademark-hound` with run summary funnel block and re-invocation branch with atomic write.

## Tasks Completed

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | Add THREAT? column and disclaimer to /trademark-report Step 3A and 3B | 32dcaff | .claude/commands/trademark-report.md |
| 2 | Atomic safelist write + run summary + re-invocation branch | 45f3d6c | .claude/commands/trademark-report.md, .claude/commands/trademark-hound.md |

## What Was Built

### trademark-report.md changes

- **Disclaimer blockquote** inserted in Step 3A immediately after the header `---` separator, before the Executive Summary — first thing attorneys read
- **Attorney Review Table** section added between Executive Summary and Priority Action Table, with columns: Date, Trademark/Variant, Entity Name, URL, Industry, Risk Score, Risk Tier, Infringement Analysis, THREAT?
- **THREAT? column** is blank in fresh reports — attorneys mark YES/NO/blank and re-run `/trademark-hound [TRADEMARK] [report]` to update the safelist
- **Step 3B CSV disclaimer** — first row is a `# DISCLAIMER:` comment before the header row; formatting rules consolidated (no duplicate section)
- **Step 4 atomic write** — safelist update now: check/remove .tmp, Write to .tmp, Bash mv to live file

### trademark-hound.md changes

- **Run Summary block** inserted after Step 7 scored JSON write — displays full funnel counts: Raw SERP leads, Excluded by safelist, Excluded by domain triage, Skipped by attorney, Excluded by content triage, Scored (Med+High), High/Medium/Low breakdown
- **Re-invocation section** added at end of file — handles `/trademark-hound [TRADEMARK] [REPORT_FILE]`, reads THREAT?=NO rows, merges to safelist with atomic write pattern (.tmp + mv), reports count added and total entries

## Test Results

```
Ran 10 tests in 0.001s — OK (all Phase 3 tests GREEN)
Ran 14 tests in 0.001s — OK (Phase 1 regression: PASS)
Ran 14 tests in 0.001s — OK (Phase 2 regression: PASS)
```

Target tests for this plan:
- TestThreatColumn: GREEN
- TestDisclaimer: GREEN
- TestAtomicWrite: GREEN
- TestRunSummary: GREEN

Bonus (not required by this plan):
- TestSafelistIngestion (HND-17): GREEN — re-invocation section added satisfies this
- TestSafelistCountReport (HND-19): GREEN — re-invocation section includes count reporting

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 2 - Missing Functionality] Re-invocation branch added in Plan 02**
- **Found during:** Task 2
- **Issue:** `test_hnd18_atomic_in_hound` checks for `.tmp` and `mv` in trademark-hound.md. Plan 02 task spec calls for atomic write in trademark-report.md Step 4 (Edit A). The test also requires trademark-hound.md to contain the atomic pattern — which requires a re-invocation section that doesn't exist yet.
- **Fix:** Added the "Re-invocation: Safelist Ingestion from Reviewed Report" section to trademark-hound.md with full atomic write instructions and count reporting. This is functionality required for correctness of HND-18 and was anticipated by Plan 03 (HND-17) — adding it here is a forward-compatible improvement.
- **Files modified:** `.claude/commands/trademark-hound.md`
- **Commit:** 45f3d6c

**2. [Rule 1 - Bug] Duplicate CSV formatting rules section removed**
- **Found during:** Task 1 Edit 3
- **Issue:** Adding new formatting rules paragraph in Step 3B created a duplicate "Formatting rules" section alongside the existing one.
- **Fix:** Merged both formatting rule sets into a single consolidated section (new disclaimer rules prepended to existing rules).
- **Files modified:** `.claude/commands/trademark-report.md`
- **Commit:** 32dcaff

## Self-Check: PASSED

- FOUND: `.claude/commands/trademark-report.md`
- FOUND: `.claude/commands/trademark-hound.md`
- FOUND: `.planning/phases/03-reports-safe-list-and-pipeline-validation/03-02-SUMMARY.md`
- FOUND commit: 32dcaff (Task 1)
- FOUND commit: 45f3d6c (Task 2)
