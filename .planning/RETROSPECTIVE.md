# Retrospective: Trademark Hound + Cat

## Milestone: v1.0 — MVP

**Shipped:** 2026-04-04
**Phases:** 3 | **Plans:** 10 | **Commits:** 35

### What Was Built

- `/trademark-cat` — interactive variant generation across 5 linguistic categories with per-mark directory and context file
- `hound_leads_template.py` — Serper.dev SERP script with rate limiting, progress output, correct per-mark output path
- `/trademark-hound` — full SERP → triage → batch approval → parallel fetch → 8-factor scoring pipeline with re-invocation safelist ingestion
- `/trademark-report` — markdown and CSV report with Attorney Review Table (THREAT? column), disclaimer, and interactive safelist update
- Per-mark directory structure with `context-[trademark].md` for persistent criticality/geography preferences
- `.gitignore` protecting API keys and large lead dump files

### What Worked

- **TDD with Nyquist**: Writing RED contract tests before implementation caught structural issues early (HND-17 re-invocation section requirement was clarified by the test before the code existed)
- **Stage 1.5 batch approval gate**: The single biggest UX improvement — collapsed 39 individual prompts into one review table. Discovered during actual pipeline run, immediately implemented
- **Composable commands**: Keeping hound (JSON output) and report (separate command) cleanly separated made re-running reports trivial and kept each command focused
- **Atomic file writes**: `.tmp` → `mv` pattern used consistently throughout; no corruption issues in any test run
- **GSD wave-based execution**: Parallel agent waves for research, planning, and testing significantly compressed the build timeline

### What Was Inefficient

- **Preferences-in-safelist detour**: Added criticality/geography to safelist JSON schema, then immediately refactored to context file — one extra round-trip that could have been avoided with clearer upfront architecture
- **Double `[mark_dir]/` bug**: Sed substitution during path refactor produced `[mark_dir]/[mark_dir]/hound_scored-...` at two locations — caught and fixed but added friction
- **Score display template typo**: `Attorney-rated [N]/5` persisted unnoticed until final cleanup — minor but indicates the score block template wasn't tested against the actual scoring range
- **No `.gitignore` until milestone end**: API key files existed in the repo for the entire build; adding this on day 1 would have been safer

### Patterns Established

- **Per-mark directory structure**: All mark files under `[sanitized_name]/` — clean workspace, multiple marks in parallel, no filename collisions
- **context-[trademark].md**: Persistent per-mark metadata separate from the safelist (which is purely exclusion URLs)
- **Re-invocation pattern**: Single command (`/trademark-hound [mark] [report]`) handles both modes via second-argument detection — clean UX, no separate safelist command needed
- **Skill frontmatter `allowed_tools`**: Declaring tools in frontmatter eliminates per-call permission prompts — essential for production use

### Key Lessons

- Design the directory structure before writing any file paths — the mid-build refactor was avoidable
- Test the score display table against the actual scale before shipping — small inconsistencies (0–3 vs 0–5) erode attorney trust in the output
- Add `.gitignore` on day 1 for any project with API keys
- The batch approval gate was user-discovered during a real pipeline run — building a "minimum viable" pipeline first and observing real usage identified the right UX improvement

### Cost Observations

- Build completed in 2 days across multiple sessions
- Notable: Claude Code's parallel agent waves (for research and content triage) made the otherwise-serial pipeline practical at scale (10 parallel fetch batches)

---

## Cross-Milestone Trends

| Milestone | Phases | Plans | Timeline | Key Pattern |
|-----------|--------|-------|----------|-------------|
| v1.0 MVP | 3 | 10 | 2 days | TDD + wave execution + composable commands |
