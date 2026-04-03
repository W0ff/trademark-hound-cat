---
phase: 01-trademark-cat-contracts
plan: "03"
subsystem: tooling

tags: [python, serper-dev, serp, template, requests]

# Dependency graph
requires:
  - phase: 01-trademark-cat-contracts
    provides: "tests/test_phase1.py: PY-01–PY-03 contract tests for hound_leads_template.py"
provides:
  - "hound_leads_template.py: Serper.dev SERP search template for Phase 2 Hound instantiation — reads variants-[TRADEMARK].txt, outputs hound_leads-[TRADEMARK].json"
affects:
  - 02-trademark-hound

# Tech tracking
tech-stack:
  added:
    - requests (used in template; not installed by this plan — runtime dependency for Hound)
  patterns:
    - "Template file with placeholder tokens ([INSERT API KEY], [INSERT VARIANTS FILE]) substituted at instantiation time by Phase 2 Hound"
    - "Variants file parsing: skip pure # lines, split on first # to strip inline annotation, strip whitespace"
    - "Serper.dev exact-match search: q field wrapped in double quotes, X-API-KEY header auth, organic[].link mapped to url"
    - "Rate limiting via DELAY_SECONDS constant (0.5s default) with flush=True for unbuffered progress output"

key-files:
  created:
    - hound_leads_template.py
  modified: []

key-decisions:
  - "Output field 'url' maps from Serper's 'link' field — intentional normalization for downstream consumers"
  - "DELAY_SECONDS = 0.5 as conservative default; Serper QPS cap to be verified at Phase 2 run time"
  - "Filename derived from variants file path: strip variants- prefix from basename → hound_leads-[TRADEMARK].json"

patterns-established:
  - "Two-token substitution pattern: template committed to repo with literal placeholders; Hound copies and replaces before execution"
  - "Inline annotation stripping: split('#')[0].strip() handles 'VariantName  # comment' format from variants file"

requirements-completed:
  - PY-01
  - PY-02
  - PY-03

# Metrics
duration: 3min
completed: 2026-04-03
---

# Phase 01 Plan 03: Hound Leads Template Summary

**Serper.dev SERP search template (hound_leads_template.py) with two-token substitution contract, comment-stripping variant loader, and JSON output — settling the Cat-to-Hound file interface**

## Performance

- **Duration:** ~3 min
- **Started:** 2026-04-03T21:25:20Z
- **Completed:** 2026-04-03T21:28:00Z
- **Tasks:** 1 of 1
- **Files modified:** 1

## Accomplishments

- `hound_leads_template.py` created at project root with both placeholder tokens (`[INSERT API KEY]`, `[INSERT VARIANTS FILE]`) as literal strings
- `load_variants()` correctly skips `#`-only lines and strips inline `# annotation` comments from variant lines
- Rate-limited search loop with `DELAY_SECONDS = 0.5` and `flush=True` on all progress prints for unbuffered output
- Output JSON fields (`variant`, `title`, `url`, `snippet`, `position`) with `link`→`url` normalization from Serper response
- All 6 `TestHoundLeadsTemplate` tests green (PY-01: file exists + syntax + placeholders; PY-02: DELAY_SECONDS + flush + comment-skipping; PY-03: all 5 output fields)

## Task Commits

Each task was committed atomically:

1. **Task 1: Write hound_leads_template.py** - `259d286` (feat)

**Plan metadata:** *(docs commit follows)*

## Files Created/Modified

- `hound_leads_template.py` — 102-line Serper.dev SERP search template; two placeholder tokens for Phase 2 Hound substitution; reads variants file, outputs hound_leads-[TRADEMARK].json

## Decisions Made

- `url` field in output mapped from Serper's `link` field — intentional normalization so downstream consumers use a stable field name regardless of Serper API changes
- `DELAY_SECONDS = 0.5` set as conservative default; actual Serper QPS cap should be verified at Phase 2 execution time
- Output filename derived from variants file path (`variants-acme.txt` → `hound_leads-acme.json`) to keep per-trademark artifacts consistently named

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required. Serper.dev API key is a Phase 2 concern (provided by user at Hound instantiation time).

## Next Phase Readiness

- Phase 1 complete: all three file contracts settled
  - `tests/test_phase1.py` — contract test suite (Plan 01)
  - `.claude/commands/trademark-cat.md` — Cat slash command (Plan 02)
  - `hound_leads_template.py` — Hound search template (Plan 03)
- Phase 2 Hound can copy `hound_leads_template.py`, substitute the two tokens, and execute the resulting per-trademark script
- Variants file format (`variants-[TRADEMARK].txt`) produced by `/trademark-cat` is fully specified and template parsing is validated

---
*Phase: 01-trademark-cat-contracts*
*Completed: 2026-04-03*
