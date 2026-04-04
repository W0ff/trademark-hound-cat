---
phase: 03-reports-safe-list-and-pipeline-validation
plan: 01
subsystem: testing
tags: [unittest, tdd, red-green, contract-tests, structural-checks]

# Dependency graph
requires:
  - phase: 02-trademark-hound-core
    provides: trademark-hound.md and trademark-report.md command files being tested
provides:
  - RED contract test scaffold in tests/test_phase3.py covering HND-13 through HND-19
  - Verification gate for all Phase 3 implementation plans
affects:
  - 03-02-PLAN.md (must turn these tests GREEN)
  - 03-03-PLAN.md (must also pass the full test suite)

# Tech tracking
tech-stack:
  added: []
  patterns: [stdlib-unittest-structural-checks, path-based-file-content-assertions, per-requirement-test-class]

key-files:
  created: [tests/test_phase3.py]
  modified: []

key-decisions:
  - "test_hnd13_report_filename_pattern passes GREEN (HOUND_REPORT_ already in trademark-report.md) — this is intentional; the test is a non-regression guard, not a RED gate"
  - "HND-17 re-invocation test requires explicit section label — loosely worded passing mention in CRITICAL note does not satisfy contract"
  - "HND-18 atomic write tested in both command files independently (report writes safelist, hound re-invocation branch writes safelist)"

patterns-established:
  - "Per-requirement test class: one class per HND requirement with _read() helper asserting file existence"
  - "ROOT = Path(__file__).parent.parent anchor for all path resolution"
  - "assertIn over exact string literals — no regex, no complex parsing"

requirements-completed: [HND-13, HND-14, HND-15, HND-16, HND-17, HND-18, HND-19]

# Metrics
duration: 2min
completed: 2026-04-04
---

# Phase 3 Plan 01: Phase 3 RED Test Scaffold Summary

**stdlib unittest RED contract scaffold with 7 test classes (10 tests) asserting absent HND-13 through HND-19 features in trademark-report.md and trademark-hound.md**

## Performance

- **Duration:** 2 min
- **Started:** 2026-04-04T19:37:55Z
- **Completed:** 2026-04-04T19:39:50Z
- **Tasks:** 1
- **Files modified:** 1

## Accomplishments

- Created `tests/test_phase3.py` with 7 test classes covering all Phase 3 requirements
- 9 of 10 tests fail RED — all unimplemented features correctly undetected
- 1 test passes (filename pattern sanity check — non-regression guard, already satisfied by existing command file)
- No external dependencies — stdlib `unittest` only, consistent with test_phase2.py pattern

## Task Commits

Each task was committed atomically:

1. **Task 1: Write RED test scaffold for all Phase 3 requirements** - `6a061e5` (test)

**Plan metadata:** (docs commit follows)

## Files Created/Modified

- `tests/test_phase3.py` — 7 test classes, 10 tests, covers HND-13 through HND-19

## Decisions Made

- `test_hnd13_report_filename_pattern` passes GREEN: `HOUND_REPORT_` already exists in trademark-report.md. Kept as a non-regression guard (Plan 02 must not remove the filename pattern). This does not violate the RED gate purpose because the test class `TestReportFormat` as a whole has one RED test.
- HND-17 re-invocation test checks for section labels (`re-invocation`, `reinvocation`, `safelist ingestion`, `second argument`) — the existing passing mention "reviewed report path" in the CRITICAL footer note is deliberately not matched, ensuring a proper labeled section must be added in Plan 02.
- HND-18 tested in both command files: `trademark-report.md` (Step 4 safelist write) and `trademark-hound.md` (re-invocation branch safelist write).

## Deviations from Plan

None — plan executed exactly as written. The one test that passes (`test_hnd13_report_filename_pattern`) is per the plan's behavior spec (`assertIn "HOUND_REPORT_"`) and the current command file already satisfies it; overall test run still outputs `FAILED (failures=9)` satisfying the `done` criterion.

## Issues Encountered

- Initial `test_hnd17_reinvocation_branch` passed unexpectedly because the existing trademark-hound.md footer contains the phrase "reviewed report path". Tightened assertion to require a dedicated labeled section (re-invocation / safelist ingestion / second argument), which correctly fails RED.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- RED test scaffold is in place; Plan 02 must turn all 9 failing tests GREEN
- Tests cover: THREAT? column (HND-14), legal disclaimer in markdown + CSV (HND-15), run summary block (HND-16), re-invocation branch with labeled section (HND-17), atomic .tmp + mv write in both commands (HND-18), count reporting (HND-19)
- Run with: `python3 tests/test_phase3.py`

## Self-Check: PASSED

- FOUND: tests/test_phase3.py
- FOUND: .planning/phases/03-reports-safe-list-and-pipeline-validation/03-01-SUMMARY.md
- FOUND: commit 6a061e5
- Test output: `FAILED (failures=9)` — all 9 unimplemented requirement tests RED

---
*Phase: 03-reports-safe-list-and-pipeline-validation*
*Completed: 2026-04-04*
