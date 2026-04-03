---
phase: 1
slug: trademark-cat-contracts
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-04-03
---

# Phase 1 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | Python stdlib (`ast`, file checks, grep) — no external test framework needed for Phase 1 |
| **Config file** | `tests/test_phase1.py` — Wave 0 gap |
| **Quick run command** | `python3 -c "import ast; ast.parse(open('hound_leads_template.py').read()); print('Template syntax OK')"` |
| **Full suite command** | `python3 tests/test_phase1.py` |
| **Estimated runtime** | ~2 seconds |

---

## Sampling Rate

- **After every task commit:** Run quick syntax check + file existence check for the file just created
- **After every plan wave:** Run `python3 tests/test_phase1.py`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 5 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 1-01-01 | 01 | 1 | CAT-01 | smoke | `test -f .claude/commands/trademark-cat.md && echo PASS` | ❌ W0 | ⬜ pending |
| 1-01-02 | 01 | 1 | CAT-02 | unit | `grep -q "Negative Constraints" .claude/commands/trademark-cat.md && echo PASS` | ❌ W0 | ⬜ pending |
| 1-01-03 | 01 | 1 | CAT-03 | unit | `grep -c "Phonetic\|Compound\|Semantic\|Conceptual\|Hybrid" .claude/commands/trademark-cat.md` | ❌ W0 | ⬜ pending |
| 1-01-04 | 01 | 1 | CAT-04 | unit | `grep -q "confusion axis" .claude/commands/trademark-cat.md && echo PASS` | ❌ W0 | ⬜ pending |
| 1-01-05 | 01 | 1 | CAT-05 | unit | `grep -q "Total:" .claude/commands/trademark-cat.md && echo PASS` | ❌ W0 | ⬜ pending |
| 1-01-06 | 01 | 1 | CAT-06 | unit | `grep -qi "approved\|looks good" .claude/commands/trademark-cat.md && echo PASS` | ❌ W0 | ⬜ pending |
| 1-01-07 | 01 | 1 | CAT-07 | unit | `grep -q "# Context:" .claude/commands/trademark-cat.md && echo PASS` | ❌ W0 | ⬜ pending |
| 1-01-08 | 01 | 1 | CAT-08 | unit | `grep -q "confirm\|written to" .claude/commands/trademark-cat.md && echo PASS` | ❌ W0 | ⬜ pending |
| 1-02-01 | 02 | 2 | PY-01 | unit | `python3 tests/test_phase1.py TestTemplate.test_placeholders` | ❌ W0 | ⬜ pending |
| 1-02-02 | 02 | 2 | PY-02 | unit | `python3 tests/test_phase1.py TestTemplate.test_rate_limit_and_progress` | ❌ W0 | ⬜ pending |
| 1-02-03 | 02 | 2 | PY-03 | unit | `python3 tests/test_phase1.py TestTemplate.test_output_fields` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_phase1.py` — test stubs for CAT-01 through CAT-08 (file existence + grep checks) and PY-01 through PY-03 (template structure checks)
- [ ] `.claude/commands/` directory — must exist before trademark-cat.md can be written

*Note: No external test framework needed. All tests use Python stdlib (`ast`, `subprocess`, `os`, `unittest`).*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Trademark Cat generates ~100 variants across 5 categories from natural language context | CAT-03 | LLM output quality; count and category balance can't be deterministically verified | Invoke `/trademark-cat "Cocoa Puffs" "chocolate breakfast cereal"`, count variants per section, verify all 5 categories present with ~20 each |
| Feedback loop iterates correctly on natural language instructions | CAT-06 | Conversational AI behavior; iteration depends on LLM interpretation of free-form feedback | Give feedback like "add more phonetic variants", verify Cat regenerates and changes the list accordingly |
| Negative Constraints derived correctly from company context | CAT-02 | LLM reasoning quality | Invoke with a well-known brand (e.g. "Delta" + "airlines"), verify the ignore list excludes dental/plumbing/unrelated industries |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 5s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
