---
phase: 2
slug: trademark-hound-core
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-04-03
---

# Phase 2 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | Python stdlib `unittest` (established in Phase 1) |
| **Config file** | None — run directly |
| **Quick run command** | `python3 tests/test_phase2.py 2>&1 \| tail -3` |
| **Full suite command** | `python3 tests/test_phase1.py && python3 tests/test_phase2.py` |
| **Estimated runtime** | ~2 seconds |

---

## Sampling Rate

- **After every task commit:** `python3 tests/test_phase2.py 2>&1 | tail -3`
- **After every plan wave:** `python3 tests/test_phase1.py && python3 tests/test_phase2.py`
- **Before `/gsd:verify-work`:** Both test suites must be green
- **Max feedback latency:** 5 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 2-01-01 | 02-01 | 1 | HND-01–12 | unit | `python3 tests/test_phase2.py 2>&1 \| tail -3` | ❌ W0 | ⬜ pending |
| 2-02-01 | 02-02 | 2 | HND-01,02,03,04,05,06,07,08,09,10,11,12 | unit | `python3 tests/test_phase2.py 2>&1` | ❌ W0 | ⬜ pending |
| 2-02-02 | 02-02 | 2 | HND-01–12 | human-verify | `/trademark-hound` end-to-end walkthrough | N/A | ⬜ pending |

*HND-06 is already covered by `tests/test_phase1.py::TestHoundLeadsTemplate::test_py02_delay_seconds` — no new test needed.*

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_phase2.py` — contract tests for `.claude/commands/trademark-hound.md` covering HND-01 through HND-12 (minus HND-06 already in Phase 1 suite); same `unittest` + `assertIn` structural-check pattern as `tests/test_phase1.py`; no external dependencies

*Existing infrastructure: `tests/test_phase1.py` continues to run and must stay green throughout Phase 2.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Hound detects missing variants file and routes to /trademark-cat | HND-03 | LLM routing behavior; can't verify AI decision-making structurally | Invoke `/trademark-hound ACME` in a workspace with no `variants-acme.txt`; verify Hound instructs user to run `/trademark-cat` and halts |
| WebFetch investigation correctly excludes informational content | HND-09 | LLM judgment; exclusion decisions depend on page content analysis | Run full Hound on a test trademark; verify news articles, Wikipedia entries are absent from scored output |
| 8-factor scoring produces correct risk tiers with evidence citations | HND-10, HND-11 | LLM scoring quality; cannot verify evidence citation quality statically | Review `hound_scored-[TRADEMARK].json` — each factor must have non-empty evidence string; scores must map to correct tier (≥15 High, 10–14 Medium, <10 Low and excluded) |
| Safelist URLs are silently filtered before investigation | HND-07 | Runtime behavior with actual JSON file | Create a `safelist-[TRADEMARK].json` with known test URLs; run Hound; verify those URLs don't appear in scored output |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 5s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
