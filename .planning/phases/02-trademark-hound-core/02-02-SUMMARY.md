---
phase: 02-trademark-hound-core
plan: "02"
subsystem: cli
tags: [claude-code, slash-command, serp, webfetch, threat-scoring, safelist, json]

# Dependency graph
requires:
  - phase: 02-01
    provides: RED contract tests for trademark-hound.md (test_phase2.py)
  - phase: 01-02
    provides: trademark-cat.md structural pattern (YAML frontmatter, $ARGUMENTS, numbered steps)
  - phase: 01-03
    provides: hound_leads_template.py with [INSERT API KEY] / [INSERT VARIANTS FILE] placeholders
provides:
  - .claude/commands/trademark-hound.md — full /trademark-hound slash command pipeline
  - hound_scored-[TRADEMARK].json output contract for Phase 3 report generation
affects: [03-report-generation]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Multi-step slash command with explicit tool directives (Read, Write, Bash, WebFetch)"
    - "Two-token substitution: read template → replace [INSERT API KEY] + [INSERT VARIANTS FILE] → write generated script"
    - "Two-stage informational exclusion: URL domain triage (no fetch) then content-signal triage (with fetch)"
    - "8-factor weighted threat matrix with per-factor evidence citation from fetched page content"
    - "Incremental scored output: accumulate Medium/High leads then write hound_scored-[TRADEMARK].json atomically"

key-files:
  created:
    - .claude/commands/trademark-hound.md
  modified: []

key-decisions:
  - "Command ends at hound_scored-[TRADEMARK].json — no HOUND_REPORT written in Phase 2 (clean phase boundary)"
  - "Domain-level exclusion only for informational sites — no path-segment exclusion (/blog/, /article/) to avoid false positives on brand sites"
  - "Score one lead at a time (not batched) with explicit working-memory release instruction between leads"
  - "Exact string equality for safelist URL matching — no fuzzy matching, no subdomain inference"

patterns-established:
  - "Pattern: Per-trademark generated scripts (hound-SERP-[TRADEMARK].py) checked for existence before regeneration — avoid overwriting API keys"
  - "Pattern: API key requested interactively only when script absent, never stored except in generated file"
  - "Pattern: Low-tier leads (< 10) dropped silently, not written to output file"

requirements-completed: [HND-01, HND-02, HND-03, HND-04, HND-05, HND-07, HND-08, HND-09, HND-10, HND-11, HND-12]

# Metrics
duration: 2min
completed: 2026-04-04
---

# Phase 2 Plan 02: Trademark Hound Core Summary

**7-step /trademark-hound slash command with SERP script generation, safelist filtering, WebFetch agentic investigation, and 8-factor weighted threat scoring outputting hound_scored-[TRADEMARK].json**

## Performance

- **Duration:** ~2 min
- **Started:** 2026-04-04T02:26:25Z
- **Completed:** 2026-04-04T02:27:47Z
- **Tasks:** 2
- **Files modified:** 1

## Accomplishments
- Wrote `.claude/commands/trademark-hound.md` — complete 7-step pipeline command (236 lines)
- Turned test_phase2.py from 14 FAIL to 14 OK in a single write (no iteration needed)
- Both test suites (test_phase1.py + test_phase2.py) confirmed GREEN: 28/28 tests passing

## Task Commits

Each task was committed atomically:

1. **Task 1: Write .claude/commands/trademark-hound.md** - `9ca7299` (feat)
2. **Task 2: Verify full dual-suite passes GREEN** - (no file changes; verification only)

**Plan metadata:** (docs commit follows)

## Files Created/Modified
- `.claude/commands/trademark-hound.md` — Full /trademark-hound slash command: intake, prerequisites check, safelist load, SERP script generation/reuse, SERP execution, safelist filter, informational exclusion (2-stage), 8-factor threat scoring, hound_scored output

## Decisions Made
- Command ends at hound_scored-[TRADEMARK].json, no HOUND_REPORT written — clean Phase 2/3 boundary
- Domain-level exclusion only for informational sites (no /blog/ path exclusion) to avoid false positives on commercial brand sites with blogs
- One lead at a time scoring with explicit working-memory release instruction to manage context window pressure
- Exact string equality for safelist URL matching — no normalization, no subdomain inference

## Deviations from Plan

None - plan executed exactly as written. Command written in a single pass, all 14 tests GREEN immediately.

## Issues Encountered
None.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- hound_scored-[TRADEMARK].json output contract is locked and documented in the command
- Phase 3 (report generation) can consume hound_scored-[TRADEMARK].json to write HOUND_REPORT_[TRADEMARK]_[DATE].md
- Remaining HND requirements for Phase 3: HND-13, HND-14, HND-15, HND-16, HND-17, HND-18, HND-19
- HND-06 is already covered by test_phase1.py::test_py02_delay_seconds (baked into template)

---
*Phase: 02-trademark-hound-core*
*Completed: 2026-04-04*
