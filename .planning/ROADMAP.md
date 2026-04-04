# Roadmap: Trademark Hound + Cat

## Overview

Two Claude Code slash commands delivering an attorney-grade trademark monitoring pipeline. Phase 1 builds the `/trademark-cat` skill — variant generation with an interactive approval loop — plus the Python SERP template and shared file contracts. Phase 2 builds the `/trademark-hound` search and investigation pipeline: SERP script execution, agentic browsing, and 8-factor threat scoring. Phase 3 completes the loop: dated Markdown reports with attorney-review columns, safe list update flow, and end-to-end pipeline validation.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [x] **Phase 1: Trademark Cat + Contracts** - Interactive variant generation skill, Python SERP template, and all shared file schemas (completed 2026-04-03)
- [ ] **Phase 2: Trademark Hound Core** - Intake, SERP search execution, agentic browsing, and 8-factor threat scoring
- [ ] **Phase 3: Reports, Safe List, and Pipeline Validation** - Dated Markdown report generation, safe list update flow, and end-to-end validation

## Phase Details

### Phase 1: Trademark Cat + Contracts
**Goal**: Attorneys can generate a reviewed, approved variant list for any trademark and the file contracts that connect Cat to Hound are settled and tested
**Depends on**: Nothing (first phase)
**Requirements**: CAT-01, CAT-02, CAT-03, CAT-04, CAT-05, CAT-06, CAT-07, CAT-08, PY-01, PY-02, PY-03
**Success Criteria** (what must be TRUE):
  1. User can invoke `/trademark-cat ACME "software for project management"` and receive a grouped list of ~100 variants across 5 linguistic categories, each annotated with confusion axis and rationale
  2. User can push back on the variant list (add, remove, rebalance categories) and Trademark Cat iterates until the user explicitly approves
  3. Approved variants are written to `variants-[TRADEMARK].txt` in the workspace with `# Category` section headers and a goods/services context header line
  4. `hound_leads_template.py` exists with `[INSERT API KEY]` and `[INSERT VARIANTS FILE]` placeholders, implements rate limiting with progress output, and writes a correctly structured `hound_leads-[TRADEMARK].json`
  5. Trademark Cat confirms the output file path upon completion
**Plans**: 3 plans

Plans:
- [ ] 01-01-PLAN.md — Test scaffold and .claude/commands/ directory setup (Wave 1)
- [ ] 01-02-PLAN.md — /trademark-cat slash command with approval loop (Wave 2)
- [ ] 01-03-PLAN.md — hound_leads_template.py Python SERP template (Wave 2)

### Phase 2: Trademark Hound Core
**Goal**: Attorneys can run `/trademark-hound` and receive a filtered, scored set of investigated leads ready for report generation
**Depends on**: Phase 1
**Requirements**: HND-01, HND-02, HND-03, HND-04, HND-05, HND-06, HND-07, HND-08, HND-09, HND-10, HND-11, HND-12
**Success Criteria** (what must be TRUE):
  1. User can invoke `/trademark-hound ACME` and the skill detects a missing variants file, tells the user to run `/trademark-cat` first, and halts cleanly
  2. Trademark Hound generates a per-trademark `hound-SERP-[TRADEMARK].py` from the template (or reuses an existing one), executes it, and produces `hound_leads-[TRADEMARK].json` with progress output per variant query
  3. All leads whose URLs appear in the loaded `safelist-[TRADEMARK].json` are silently excluded before investigation begins
  4. Each remaining lead is visited via WebFetch; news articles, Wikipedia, and informational content are excluded; commercial leads are assessed on commerciality, trademark usage, and market overlap
  5. Each assessed lead receives a score from the 8-factor weighted threat matrix with evidence citations per factor; leads below 10 (Low) are dropped and not surfaced further
**Plans**: 3 plans

Plans:
- [ ] 02-01-PLAN.md — RED test scaffold for /trademark-hound (tests/test_phase2.py) (Wave 1)
- [ ] 02-02-PLAN.md — /trademark-hound slash command: full pipeline from intake to hound_scored JSON (Wave 2)
- [ ] 02-03-PLAN.md — Human verification checkpoint: end-to-end pipeline walkthrough (Wave 3)

### Phase 3: Reports, Safe List, and Pipeline Validation
**Goal**: The full pipeline produces a dated, attorney-ready Markdown report and the safe list feedback loop closes correctly, allowing prior false positives to be suppressed on future runs
**Depends on**: Phase 2
**Requirements**: HND-13, HND-14, HND-15, HND-16, HND-17, HND-18, HND-19
**Success Criteria** (what must be TRUE):
  1. Trademark Hound writes `HOUND_REPORT_[TRADEMARK]_[YYYY-MM-DD].md` containing only Medium (10-14) and High (>=15) risk entries, with columns: Date, Trademark/Variant, Entity Name, URL, Industry, Risk Score, Risk Tier, Infringement Analysis, THREAT? — the THREAT? column is blank in fresh reports
  2. Report includes a disclaimer header stating the report is for attorney review only and does not constitute legal advice
  3. Trademark Hound displays a run summary to the user: total leads found, leads filtered by safe list, leads investigated, High/Medium/Low counts, and report file path
  4. When Trademark Hound is re-invoked with a reviewed report path, it reads the THREAT? column and atomically writes all "NO" entries to `safelist-[TRADEMARK].json`, then reports how many entries were added and how many are now excluded from future runs
  5. Running the full pipeline end-to-end (Cat to Hound to report to safe list update) produces consistent, non-corrupted output files with no orphaned tmp files
**Plans**: TBD

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 2 → 3

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Trademark Cat + Contracts | 3/3 | Complete    | 2026-04-03 |
| 2. Trademark Hound Core | 2/3 | In Progress|  |
| 3. Reports, Safe List, and Pipeline Validation | 0/TBD | Not started | - |
