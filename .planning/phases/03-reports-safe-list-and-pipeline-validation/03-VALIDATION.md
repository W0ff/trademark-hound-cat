---
phase: 3
slug: reports-safe-list-and-pipeline-validation
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-04-04
---

# Phase 3 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | Python stdlib `unittest` (no install needed) |
| **Config file** | none — stdlib only |
| **Quick run command** | `python3 -m pytest tests/test_phase3.py -q` |
| **Full suite command** | `python3 -m pytest tests/ -q` |
| **Estimated runtime** | ~3 seconds |

---

## Sampling Rate

- **After every task commit:** Run `python3 -m pytest tests/test_phase3.py -q`
- **After every plan wave:** Run `python3 -m pytest tests/ -q`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 5 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 3-01-01 | 01 | 0 | HND-13 | unit stub | `python3 -m pytest tests/test_phase3.py::TestReportFormat -q` | ❌ W0 | ⬜ pending |
| 3-01-02 | 01 | 0 | HND-14 | unit stub | `python3 -m pytest tests/test_phase3.py::TestThreatColumn -q` | ❌ W0 | ⬜ pending |
| 3-01-03 | 01 | 0 | HND-15 | unit stub | `python3 -m pytest tests/test_phase3.py::TestDisclaimer -q` | ❌ W0 | ⬜ pending |
| 3-01-04 | 01 | 0 | HND-16 | unit stub | `python3 -m pytest tests/test_phase3.py::TestRunSummary -q` | ❌ W0 | ⬜ pending |
| 3-01-05 | 01 | 0 | HND-17 | unit stub | `python3 -m pytest tests/test_phase3.py::TestSafelistIngestion -q` | ❌ W0 | ⬜ pending |
| 3-01-06 | 01 | 0 | HND-18 | unit stub | `python3 -m pytest tests/test_phase3.py::TestAtomicWrite -q` | ❌ W0 | ⬜ pending |
| 3-02-01 | 02 | 1 | HND-13,14,15 | structural | `python3 -m pytest tests/test_phase3.py::TestReportFormat -q` | ✅ W0 | ⬜ pending |
| 3-02-02 | 02 | 1 | HND-16 | structural | `python3 -m pytest tests/test_phase3.py::TestRunSummary -q` | ✅ W0 | ⬜ pending |
| 3-02-03 | 02 | 1 | HND-17,18 | structural | `python3 -m pytest tests/test_phase3.py::TestSafelistIngestion -q` | ✅ W0 | ⬜ pending |
| 3-03-01 | 03 | 2 | HND-19 | manual + structural | `python3 -m pytest tests/ -q` | ✅ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_phase3.py` — failing stubs for HND-13 through HND-19
- [ ] Extend `tests/test_phase2.py` structural checks if relevant

*Existing `tests/test_phase1.py` and `tests/test_phase2.py` infrastructure covers shared fixtures.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Report renders correctly in a Markdown viewer | HND-13 | Visual layout can't be asserted programmatically | Open HOUND_REPORT_*.md in VS Code preview; confirm table alignment, section headings, and disclaimer block |
| CSV opens cleanly in Numbers/Excel | HND-13 | File association and column rendering | Open .csv output; confirm columns match spec, no merged rows |
| THREAT? column is blank in fresh reports | HND-14 | Structural test can only check column exists, not blank | Open fresh report; confirm THREAT? column has no pre-filled values |
| Safe list update run summary is human-readable | HND-18 | Output phrasing is subjective | Re-invoke hound with reviewed report; confirm message is clear and accurate |
| Full pipeline produces no orphaned files | HND-19 | Requires observing working directory across a full run | Run Cat → Hound → Report → Safelist update; confirm no *.tmp files remain |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 5s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
