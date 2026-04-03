# Project Research Summary

**Project:** Trademark Hound + Cat
**Domain:** Claude Code skills for AI-assisted trademark monitoring (IP attorneys)
**Researched:** 2026-04-03
**Confidence:** HIGH

## Executive Summary

Trademark Hound + Cat is a two-skill Claude Code pipeline designed for IP attorneys to monitor trademark infringement on the web. The established approach in this domain — used by enterprise tools like Corsearch and CompuMark — is to generate phonetic, visual, and conceptual variants of a mark, search the web for those variants, investigate commercial hits, and score them against legally recognized confusion factors. The key recommendation from research is to implement this as two decoupled Claude Code skills connected by a plain-text file contract: Trademark Cat for iterative attorney-approved variant generation, and Trademark Hound for the full investigation pipeline. The significant competitive differentiator over SaaS alternatives is the conversational variant-review loop and a transparent per-factor scoring breakdown, neither of which incumbent tools offer.

The recommended stack is deliberately minimal: Claude Code skills format (`.claude/skills/`), Python 3 with `requests` for Serper.dev API calls, `pathlib`/`json` stdlib for all state management, and Markdown for attorney-facing reports. No npm, no database, no server. The native Claude WebFetch and WebSearch tools handle agentic browsing with zero install overhead. This stack has been verified against official Claude Code documentation and is appropriate for a periodic CLI tool used by individual attorneys — not a continuous SaaS product.

The primary risks are all implementation-level, not architectural: the AI scoring step can hallucinate company details when page content is thin (mitigated by mandatory evidence citation per factor), the Serper.dev SERP script can silently fail on rate limits (mitigated by per-query progress reporting and backoff), and report language can inadvertently cross the unauthorized-practice-of-law line (mitigated by consistent hedging language and a mandatory attorney-review gate). None of these risks are novel — all have documented prevention patterns. The safe list JSON corruption risk is the only one that can silently destroy prior work; atomic writes are the prevention and must be treated as a day-one requirement.

---

## Key Findings

### Recommended Stack

The project requires no novel technology decisions. Claude Code skills format (`.claude/skills/[name]/SKILL.md`) is the correct delivery mechanism — it supersedes the legacy `.claude/commands/` format, supports frontmatter, bundled supporting files, and `$ARGUMENTS` substitution. Python 3.13 (already installed) with `requests` handles Serper.dev API calls; all other dependencies are stdlib. Claude's native WebFetch/WebSearch tools replace Playwright or Firecrawl entirely, saving substantial install overhead and working within Claude Code's permission model without additional configuration.

See full stack details: `.planning/research/STACK.md`

**Core technologies:**
- **Claude Code Skills** (`.claude/skills/`) — slash command delivery; use `disable-model-invocation: true` and `allowed-tools` frontmatter to control invocation and pre-approve tool permissions
- **Python 3 + `requests`** — Serper.dev API calls via generated script; single-shot synchronous calls make `requests` the correct choice over `httpx`
- **`pathlib` + `json` (stdlib)** — all state file I/O; atomic write pattern (write to `.tmp`, rename) is mandatory for safe list integrity
- **Native WebFetch/WebSearch** — agentic browsing without third-party dependencies; converts HTML to Markdown automatically
- **Markdown files** — attorney-facing report format; renders in any editor, Claude Code, and GitHub; no rendering infrastructure required

### Expected Features

See full feature analysis: `.planning/research/FEATURES.md`

**Must have (table stakes) — attorneys expect these from any professional tool:**
- Variant generation across 5 linguistic categories (phonetic, visual/orthographic, conceptual/semantic, character-level homoglyphs, typosquatting) — missing any category creates legal blind spots
- Goods-and-services context input at Cat invocation — required for both variant relevance and scoring factors 2 and 3 in Hound
- 8-factor weighted threat scoring tied to DuPont confusion factors — scores must be legally defensible, not opaque
- Commercial-use filtering in the browsing step — attorneys cannot act on news or academic mentions
- Dated Markdown report (Medium/High hits only) with blank THREAT? column for attorney review
- Persistent safe list (`safelist-[TRADEMARK].json`) loaded on every run — false-positive suppression is non-negotiable for repeat monitoring
- Idempotent re-run behavior — same mark, different dates, clean results

**Should have (competitive differentiators over SaaS tools):**
- Iterative variant review loop in Cat — attorneys can push back before a costly search runs; no SaaS tool offers conversational refinement
- Per-variant annotation with confusion axis (phonetic/visual/conceptual/typo) and one-sentence rationale — builds attorney trust and education
- Visible per-factor score breakdown in reports ("Visual similarity: 8/8, Goods overlap: 6/8") vs. opaque total score
- Automatic pipeline routing — Hound detects missing variants file and directs user to run Cat first
- Portable JSON safe list that travels with the client matter file (not locked inside a platform)
- Per-run dated reports creating an audit trail of active policing

**Defer to v2+:**
- USPTO registry watch integration (requires paid API, distinct use case)
- Domain registration monitoring (distinct data source and subscription model)
- Batch portfolio mode (run after v1 pipeline is validated on single-mark workflow)
- Report diffing between runs (useful, but requires stable v1 report format first)
- Variant count and threshold tuning (add once attorneys validate default settings)

**Anti-features (explicitly exclude from v1 and likely v2):**
- Automated cease-and-desist generation — creates malpractice liability
- Real-time/scheduled monitoring — incompatible with Claude Code skill model
- Auto-population of safe list — removes attorney judgment from a legal decision
- Web UI or dashboard — different product; Markdown is the UI

### Architecture Approach

The architecture is a two-skill file-contract pipeline. Trademark Cat writes `variants-[TRADEMARK].txt`; Trademark Hound reads it. This is the only interface between the skills — no direct invocation chaining, no shared memory. This decoupling is intentional: attorneys need to review and potentially edit variants before an expensive search run begins. Hound guards for the missing file and routes to Cat when absent. All runtime artifacts (variants, safe list, leads JSON, reports) land in the workspace directory where the skill is invoked.

See full architecture diagrams: `.planning/research/ARCHITECTURE.md`

**Major components:**
1. **Trademark Cat skill** — interactive variant generation with user approval loop; writes `variants-[TRADEMARK].txt` including goods/services context header
2. **variants-[TRADEMARK].txt** — the only interface between Cat and Hound; plain text, one variant per line, written once per review cycle
3. **Trademark Hound skill** — full investigation orchestration: guard, safelist load, Serper script generation + execution, SERP filter, agentic browsing, 8-factor scoring, report write
4. **Generated Python script (`search-[TRADEMARK].py`)** — disposable Serper.dev API caller; generated by Hound, executed via Bash tool, writes `leads-[TRADEMARK].json`; inspectable and re-runnable
5. **`leads-[TRADEMARK].json`** — intermediate state: raw SERP hits before safe-list filtering and scoring; preserved for re-scoring without re-querying
6. **`safelist-[TRADEMARK].json`** — persistent false-positive elimination; loaded at Hound startup, updated in a separate invocation after attorney review
7. **Report Markdown** — dated, attorney-facing output with blank THREAT? column and inline re-run instructions for safe list update

**Build order dictated by dependencies:**
1. Serper.dev Python script template (validates API mechanics)
2. Variants file format and safe list JSON schema (contracts before consumers)
3. Trademark Cat skill (writes the variants file)
4. Threat scoring matrix (8 factors, weightings — embedded in Hound SKILL.md)
5. Trademark Hound skill (search + filter + score + report)
6. Safe list update sub-flow (consumes the report format Hound produces)

### Critical Pitfalls

See full pitfall analysis: `.planning/research/PITFALLS.md`

1. **AI hallucination in threat scoring** — When pages load slowly, block bots, or have thin content, Claude fills scoring factors from training data rather than page evidence. Prevention: require a quoted evidence string per factor in the scoring prompt; assign 0 (not an estimate) when evidence is absent; route bot-blocked pages to manual review rather than scoring.

2. **Serper.dev rate limiting silently truncates results** — Naive scripts fire 100 queries in a tight loop, hit per-minute caps, and produce partial reports that look complete. Prevention: 0.5s delay between queries with exponential backoff on 429; script writes `COMPLETED: X of Y queries` summary line; Hound halts on Z > 0 failures rather than proceeding on partial data.

3. **Legal liability from assertive report language** — Stating "this constitutes infringement" creates UPL exposure and product liability risk. Prevention: every output surface uses hedging language ("potential threat requiring attorney review"); every report includes a mandatory disclaimer header; the THREAT? column the attorney fills in is the documented gate between AI output and legal action.

4. **Safe list JSON corruption** — Interrupted writes leave a truncated file; on next run, safe list silently loads as empty, flooding the report with previously-cleared false positives. Prevention: atomic write pattern (write to `.tmp`, rename) is mandatory from day one — it is two extra lines of code and there is no acceptable reason to skip it.

5. **Context exhaustion at scale** — 100 variants × 10 results each = 1,000 page snippets can fill the context window before scoring begins. Prevention: pre-filter leads at snippet level before dispatching agentic browse; set a hard per-run browse cap (50 leads); implement batching in the Hound architecture from the start — retrofitting is expensive.

---

## Implications for Roadmap

Based on research, the build sequence is dictated by hard file-contract dependencies. Cat must exist before Hound can be tested. The scoring matrix must be defined before Hound is authored. The safe list update flow depends on the report format Hound produces. Anti-patterns to avoid at every phase: monolithic skill design, API key hardcoding, direct Cat-to-Hound chaining, and assertive report language.

### Phase 1: Contracts and Foundations

**Rationale:** The variants file format and safe list JSON schema are the contracts between all downstream components. Building before consumers prevents rework. The Serper.dev script template validates API mechanics independently, before any skill complexity is added.
**Delivers:** Validated Serper.dev connectivity; settled file schemas; rate-limiting and atomic-write patterns baked in before any skill depends on them.
**Addresses:** Serper rate limiting pitfall, safe list corruption pitfall, API key security requirement.
**Avoids:** The pattern of discovering API gotchas mid-skill-build; schema-breaking changes after consumers are written.

### Phase 2: Trademark Cat Skill

**Rationale:** Cat is the prerequisite for Hound. It is also lower-risk (no external API calls, no legal scoring, no agentic browsing), making it the right place to establish skill structure, argument handling, and output formatting conventions.
**Delivers:** Working `/trademark-cat` slash command with 5-category variant generation, interactive approval loop, and `variants-[TRADEMARK].txt` output including goods/services context header.
**Addresses:** Variant generation (table stakes), iterative review loop (key differentiator), goods/services context capture (required by both Cat and Hound).
**Avoids:** Inconsistent variant output pitfall — validation logic (count per category, category coverage check, self-verification step) is built into Cat from the start, not added as a polish step.
**Research flag:** Standard patterns apply. No additional research needed for this phase.

### Phase 3: Trademark Hound Core Pipeline (Search + Filter)

**Rationale:** The search and filtering steps (script generation, execution, safe list load, lead filtering) are foundational to the report step. Building them as a validated unit first prevents discovering integration problems (rate limits, JSON parsing, safe list behavior) during the high-complexity scoring and browsing phase.
**Delivers:** Working Serper.dev search execution; raw `leads-[TRADEMARK].json` output; safe list load and URL filtering; progress reporting per query; graceful rate-limit detection.
**Addresses:** SERP rate limiting pitfall, safe list load requirement, pipeline guard (missing variants file detection).
**Avoids:** Silent data gaps from rate limiting; safe list being treated as empty on parse error.
**Research flag:** Standard patterns apply. Rate-limiting and backoff patterns are well-documented.

### Phase 4: Agentic Browsing and Threat Scoring

**Rationale:** This is the highest-complexity phase and the highest source of hallucination risk. It depends on Phase 3 providing clean filtered leads. The evidence-citation requirement and evidence-confidence field must be designed into the scoring prompt before any scoring code is written.
**Delivers:** Working agentic browsing with commercial-use filtering and per-page timeout; 8-factor weighted scoring with mandatory evidence citations; per-factor confidence indicators; bot-blocked page routing to manual review section.
**Addresses:** Agentic browsing (highest-value automation), 8-factor scoring with visible breakdown (key differentiator and table stakes), commercial-use filtering (table stakes).
**Avoids:** Hallucinated threat scores — evidence citation is a prompt-design requirement, not a polish step; context exhaustion — snippet-level pre-filtering and browse cap must be in place before this phase completes.
**Research flag:** This phase warrants deeper research during planning. Agentic browsing reliability, evidence-citation prompt patterns, and context window budgeting for large lead sets are niche enough to benefit from targeted phase research.

### Phase 5: Report Generation and Safe List Update Flow

**Rationale:** Report output depends on scored findings from Phase 4. Safe list update depends on the report format. Both require the legal-language review that must happen before any attorney-facing output is produced.
**Delivers:** Dated Markdown report (Medium/High only) with THREAT? column, inline re-run instructions, disclaimer header, safe list summary in report header; safe list update sub-flow triggered by `--update-safelist` argument.
**Addresses:** Report format (table stakes), persistent safe list update (closes feedback loop), legal liability language prevention, per-run audit trail.
**Avoids:** Assertive infringement language — every output surface reviewed for hedging compliance before this phase completes; safe list corruption — atomic write verified in Phase 1 is exercised here at scale.
**Research flag:** Legal disclaimer language review may benefit from brief targeted research to ensure hedging patterns match current UPL case law.

### Phase 6: Polish and End-to-End Validation

**Rationale:** After all components are individually working, validate the full pipeline against the "Looks Done But Isn't" checklist from PITFALLS.md. This phase catches integration gaps (e.g., goods/services context not propagating from Cat to Hound, ignore list over-exclusion silently hiding real competitors) that unit testing of individual phases misses.
**Delivers:** Validated end-to-end pipeline; run summary output from Hound; ignore list visible in report header; full checklist verification (variant count per category, query success rate, evidence citation completeness, atomic write verification, THREAT? column blank in fresh reports, legal disclaimer present).
**Addresses:** All "Looks Done But Isn't" checklist items; UX pitfalls (progress indicators, run summary, safe list suppression count in header).
**Research flag:** No additional research needed. Verification criteria are fully specified in PITFALLS.md.

### Phase Ordering Rationale

- **Contracts before consumers** (Phase 1 first): Safe list schema and variants file format are consumed by both skills. Changing these after skills are written requires rework in multiple places.
- **Cat before Hound** (Phase 2 before 3-5): Hound's guard depends on Cat's output format being settled. Testing Hound without a real Cat-produced variants file creates false confidence.
- **Search before scoring** (Phase 3 before 4): Discovering Serper rate-limit behavior mid-scoring-build creates confounded debugging. Validate the data pipeline cleanly first.
- **Scoring before reporting** (Phase 4 before 5): Report format is dictated by scoring output structure. Designing reporting before scoring is decided risks format rework.
- **Evidence citation is Phase 4, not Phase 6**: The hallucination risk is highest here and most expensive to retrofit. It must be a design requirement, not a hardening step.
- **Atomic writes are Phase 1, not Phase 5**: Safe list corruption can destroy prior work silently. This is a day-one requirement.

### Research Flags

Phases likely needing deeper research during planning:
- **Phase 4 (Agentic Browsing + Scoring):** Evidence-citation prompt design, agentic browsing reliability patterns, context window budgeting for 50-lead browse passes, and `context: fork` subagent isolation trade-offs are niche enough to benefit from targeted phase research before implementation.
- **Phase 5 (Report + Safe List Update):** Brief research on current UPL hedging language standards and AI legal tool disclaimer patterns is recommended before finalizing report template language.

Phases with standard patterns (skip research-phase):
- **Phase 1 (Contracts/Foundations):** Serper.dev API, atomic write pattern, and JSON schema design are well-documented.
- **Phase 2 (Trademark Cat):** Claude Code skill authoring and iterative conversation loop are covered by official documentation.
- **Phase 3 (Hound Core Pipeline):** Rate limiting, backoff, and safe list file I/O patterns are fully documented and verified.
- **Phase 6 (Validation):** Verification criteria are fully enumerated in PITFALLS.md — no additional research needed.

---

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | Claude Code skills format verified from official docs; Serper.dev POST pattern verified from multiple community sources; Python stdlib patterns are authoritative |
| Features | HIGH | DuPont 13-factor test is established legal standard (HIGH); competitor feature analysis from vendor marketing (MEDIUM); overall confidence HIGH because legal factors are the foundation |
| Architecture | HIGH | Official Claude Code docs verify skill structure, `${CLAUDE_SKILL_DIR}`, `$ARGUMENTS`, `context: fork`, and `allowed-tools` frontmatter; file-contract pattern is well-established |
| Pitfalls | HIGH (critical) / MEDIUM (phase mapping) | Critical pitfalls sourced from official docs, peer-reviewed legal AI research (Stanford DHo), and documented real-world cases; phase mapping estimates are reasonable but not empirically verified |

**Overall confidence:** HIGH

### Gaps to Address

- **Serper.dev rate limit thresholds at current tier pricing:** The per-minute QPS cap on starter/pro tiers changes with Serper's pricing model. Verify exact limits at implementation time; the 0.5s delay recommendation is conservative but the correct batch-size cap should be confirmed against current docs.
- **`context: fork` availability in current Claude Code release:** Architecture research references `context: fork` as the upgrade path for parallel browsing at scale. Verify this feature is available and stable in the current release before committing to it in Phase 4 architecture decisions.
- **Goods/services context propagation format:** FEATURES.md specifies that goods/services context must be written into the variants file header so Hound can read it without re-prompting. The exact format (plain text header line vs. JSON frontmatter in the text file) is not settled in research and needs a decision in Phase 1.
- **`--update-safelist` argument handling:** ARCHITECTURE.md specifies this as a separate Hound invocation mode. How Claude Code skills distinguish invocation modes from `$ARGUMENTS` (e.g., prefix detection vs. named flag) needs verification against current skill documentation before Phase 5 design.

---

## Sources

### Primary (HIGH confidence)
- [Claude Code Skills official documentation](https://code.claude.com/docs/en/slash-commands) — skill directory structure, frontmatter reference, `$ARGUMENTS`, `CLAUDE_SKILL_DIR`, `allowed-tools`, `disable-model-invocation`
- [Claude Code Skills official documentation](https://code.claude.ai/docs/en/skills) — `context: fork`, context isolation, context budget behavior
- [DuPont factors for likelihood of confusion](https://www.erikpelton.com/what-are-the-dupont-factors-in-a-trademark-confusion-analysis-2/) — legal basis for 8-factor scoring matrix
- [Hallucination-Free? Legal RAG reliability — Stanford DHo](https://dho.stanford.edu/wp-content/uploads/Legal_RAG_Hallucinations.pdf) — 1/3 confabulation rate from unreviewed content; basis for evidence-citation requirement
- [Python pathlib + JSON best practices](https://cr88.hashnode.dev/using-pythons-pathlib-to-work-with-json-files-why-and-how) — atomic write pattern, `Path.read_text`/`write_text` idioms
- [Similar Trademark Detection — ACM SIGIR](https://dl.acm.org/doi/abs/10.1145/3404835.3463038) — phonetic, visual, conceptual similarity axes (peer-reviewed)

### Secondary (MEDIUM confidence)
- [Serper.dev API — Python POST example](https://www.restack.io/p/serper-api-key-answer-python-search-engine-cat-ai) — endpoint URL, `X-API-KEY` header, `requests.post` pattern
- [Inside Claude Code Skills — mikhail.io](https://mikhail.io/2025/10/claude-code-skills/) — Python script bundling pattern, base path injection
- [Claude Skills: The Controllability Problem — paddo.dev](https://paddo.dev/blog/claude-skills-controllability-problem/) — prompt consistency issues and inconsistent output across runs
- [Context Window in Claude Code — MindStudio](https://www.mindstudio.ai/blog/context-window-claude-code-manage-consistent-results) — context exhaustion patterns
- [Corsearch trademark solutions](https://corsearch.com/trademark-solutions) — competitor feature baseline
- [Clarivate Trademark Watching](https://clarivate.com/intellectual-property/brand-ip-solutions/trademark-watching/) — competitor feature baseline
- [Is AI for Legal Services UPL? — ByDesignLaw](https://www.bydesignlaw.com/ai-for-legal-services-is-it-unauthorized-practice-of-law-upl) — UPL analysis for AI legal tools
- [Designed to Cross — Stanford CodeX](https://law.stanford.edu/2026/03/07/designed-to-cross-why-nippon-life-v-openai-is-a-product-liability-case/) — product liability theory for AI legal tools

### Tertiary (LOW confidence)
- [SERP API Pricing Index 2026 — SearchCans](https://www.searchcans.com/blog/serp-api-pricing-index-2026/) — tier caps (pricing changes; verify at implementation)
- [Top 10 Trademark Monitoring Tools — DevOps School](https://www.devopsschool.com/blog/top-10-trademark-monitoring-tools-features-pros-cons-comparison/) — competitor feature comparison (third-party review, may be outdated)

---
*Research completed: 2026-04-03*
*Ready for roadmap: yes*
