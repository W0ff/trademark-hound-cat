# Trademark Hound + Cat

## What This Is

Two Claude Code slash commands for trademark infringement monitoring. Trademark Cat generates ~100 confusion-risk variants of a protected mark; Trademark Hound searches the web for those variants, investigates each lead, scores threats using a weighted matrix, and produces a reviewable report with persistent safe-listing to eliminate false positives over time.

Designed for IP attorneys and paralegals who need to monitor client trademark portfolios periodically without manual web research.

## Core Value

Attorneys can run the full pipeline — from trademark intake to prioritized threat report — with zero manual Google searching, and the system gets smarter over time as false positives are flagged to a safe list.

## Requirements

### Validated

(None yet — ship to validate)

### Active

- [ ] Trademark Cat generates ~100 variants across 5 linguistic categories from a trademark + company context
- [ ] Trademark Cat produces a user-reviewable list and iterates on feedback before writing output
- [ ] Trademark Cat writes `variants-[TRADEMARK].txt` for use by the Hound
- [ ] Trademark Hound checks for existing variants file and routes to Cat if missing
- [ ] Trademark Hound generates and runs a Serper.dev Python script per trademark
- [ ] Trademark Hound performs agentic browsing to assess each search lead
- [ ] Trademark Hound scores each lead with a weighted threat matrix (8 factors)
- [ ] Trademark Hound writes a dated Markdown report with Medium/High risk entries only
- [ ] Trademark Hound loads and respects an existing safe list on every run
- [ ] Trademark Hound updates the safe list when a reviewed report is passed

### Out of Scope

- Automated USPTO / trademark database searches — legal databases require separate subscriptions
- Real-time monitoring / scheduled alerts — periodic manual invocation is the target workflow
- Mobile or web UI — CLI-first, attorneys run from terminal or Claude Code

## Context

- Users are IP attorneys and paralegals doing periodic brand monitoring for client portfolios
- Serper.dev is the chosen search API (user has existing API key + script skeleton)
- Negative Constraints (ignore lists) are derived per-trademark from company context to distinguish non-competing uses (e.g. "Delta Airlines" ≠ "Delta Dental")
- Safe list persists across runs as `safelist-[TRADEMARK].json`
- Reports are Markdown tables reviewed offline; user fills in THREAT? column and re-runs Hound to update safe list

## Constraints

- **API**: Serper.dev — user provides API key at script generation time
- **Runtime files**: stored in the workspace directory where skills are invoked, organized by trademark name
- **Search scope**: commercial uses only — news, wikis, commentary explicitly excluded
- **Report threshold**: only Medium (10–14) and High (≥15) scores surface in reports

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Claude Code slash commands as delivery format | Attorneys already use Claude Code; no separate tool install | — Pending |
| Serper.dev for SERP automation | User has existing script skeleton; clean JSON; no scraping fragility | — Pending |
| Weighted threat matrix (8 factors, 0–48 scale) over simple 1–10 | More defensible scoring for legal context; each factor has clear legal analogue | — Pending |
| Safe list as JSON file (not database) | Simple, portable, human-readable; no infrastructure required | — Pending |

---
*Last updated: 2026-04-03 after initialization*
