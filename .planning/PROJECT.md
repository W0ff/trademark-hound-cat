# Trademark Hound + Cat

## What This Is

Three Claude Code slash commands delivering a complete attorney-grade trademark monitoring pipeline. `/trademark-cat` generates ~100 confusion-risk variants of a protected mark across 5 linguistic categories with an interactive approval loop. `/trademark-hound` searches the web for those variants using Serper.dev, applies a batch attorney approval gate, investigates each lead via parallel WebFetch, scores threats on a weighted 8-factor matrix, and writes a JSON output for downstream reporting. `/trademark-report` renders scored leads as a markdown or CSV report with an Attorney Review Table (THREAT? column) and an interactive safelist update step. All per-mark files are organized in a named subdirectory with a persistent context file for criticality and geography preferences.

Designed for IP attorneys and paralegals who need to monitor client trademark portfolios periodically without manual web research.

## Core Value

Attorneys can run the full pipeline — from trademark intake to prioritized threat report — with zero manual Google searching, and the system gets smarter over time as false positives are flagged to a safe list.

## Requirements

### Validated

- ✓ Trademark Cat generates ~100 variants across 5 linguistic categories from a trademark + company context — v1.0
- ✓ Trademark Cat produces a user-reviewable list and iterates on feedback before writing output — v1.0
- ✓ Trademark Cat writes `[mark]/variants-[TRADEMARK].txt` for use by the Hound — v1.0
- ✓ Trademark Hound checks for existing variants file and routes to Cat if missing — v1.0
- ✓ Trademark Hound generates and runs a Serper.dev Python script per trademark — v1.0
- ✓ Trademark Hound applies batch attorney URL approval gate before any WebFetch calls — v1.0
- ✓ Trademark Hound performs agentic browsing to assess each search lead — v1.0
- ✓ Trademark Hound scores each lead with a weighted threat matrix (8 factors, max 48) — v1.0
- ✓ Trademark Hound writes a dated JSON output with Medium/High risk entries only — v1.0
- ✓ Trademark Hound loads and respects an existing safe list on every run — v1.0
- ✓ Trademark Hound updates the safe list when a reviewed report is passed (re-invocation mode) — v1.0
- ✓ Trademark Report generates markdown or CSV with THREAT? column, disclaimer, and safelist update step — v1.0
- ✓ Per-mark directory structure with context file (criticality, geography, skip_confirmation) — v1.0

### Active

(No active requirements — see v2 requirements in REQUIREMENTS archive for next milestone candidates)

### Out of Scope

- Automated USPTO / trademark database searches — legal databases require separate subscriptions
- Real-time monitoring / scheduled alerts — periodic manual invocation is the target workflow
- Mobile or web UI — CLI-first, attorneys run from terminal or Claude Code
- Automated C&D generation — unauthorized practice of law risk; attorneys draft all correspondence
- Multi-user / shared safe list — file-based model is per-matter; sharing requires infrastructure

## Context

- Users are IP attorneys and paralegals doing periodic brand monitoring for client portfolios
- Serper.dev is the chosen search API (user provides API key at script generation time)
- All mark files organized under `[sanitized_name]/` subdirectory (e.g., `testmark/`, `flowstate/`)
- `context-[trademark].md` stores goods/services, criticality (0–3), geography, and skip_confirmation flag
- Safe list persists across runs as `[mark]/safelist-[TRADEMARK].json` (flat JSON array of URLs)
- Reports reviewed offline; user fills THREAT? column, re-runs Hound to update safelist
- Tested with: testmark ("testing software"), flowstate, cocoa-puffs

**Current codebase:** ~1,100 lines across 4 primary files (3 skill .md files + SERP template)
**Tech stack:** Claude Code slash commands (LLM instruction files), Python 3, Serper.dev API
**v1.0 shipped:** 2026-04-04 | 3 phases, 10 plans, 35 commits

## Constraints

- **API**: Serper.dev — user provides API key at script generation time; key stored in per-mark SERP script (gitignored)
- **Runtime files**: organized in per-mark subdirectory within the workspace where skills are invoked
- **Search scope**: commercial uses only — news, wikis, commentary explicitly excluded
- **Report threshold**: only Medium (10–14) and High (≥15) scores surface in reports

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Claude Code slash commands as delivery format | Attorneys already use Claude Code; no separate tool install | ✓ Good — zero friction for users |
| Serper.dev for SERP automation | User has existing script skeleton; clean JSON; no scraping fragility | ✓ Good — 564 leads from 100 variants per run |
| Weighted threat matrix (8 factors, 0–48 scale) over simple 1–10 | More defensible scoring for legal context; each factor has clear legal analogue | ✓ Good — attorneys find scores intuitive |
| Safe list as flat JSON array (not database) | Simple, portable, human-readable; no infrastructure required | ✓ Good — atomic write prevents corruption |
| Stage 1.5 batch URL approval gate | Eliminates 39 individual prompts per run; attorney sees all URLs at once | ✓ Good — single "proceed" reply triggers all fetches |
| /trademark-report as separate command | Hound writes JSON → Report reads it — composable and re-runnable without re-searching | ✓ Good — clean separation of concerns |
| Per-mark directory structure | Multiple marks supported without filename collisions; workspace stays clean | ✓ Good — intuitive organization |
| context-[trademark].md over safelist preferences | Clean separation: safelist = exclusion URLs, context = mark metadata | ✓ Good — schema clarity |

---
*Last updated: 2026-04-04 after v1.0 milestone*
