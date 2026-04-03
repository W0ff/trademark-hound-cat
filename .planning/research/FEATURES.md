# Feature Research

**Domain:** AI-assisted trademark monitoring (Claude Code slash commands for IP attorneys)
**Researched:** 2026-04-03
**Confidence:** MEDIUM — professional tool features from vendor sites (MEDIUM); legal standard factors from authoritative sources (HIGH); AI agent patterns from practitioner articles (MEDIUM)

---

## Feature Landscape

### Table Stakes (Users Expect These)

These are features IP attorneys assume any serious trademark monitoring tool has. Missing them signals the tool is not production-ready for legal work.

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Variant generation across similarity dimensions | Every watch service generates phonetic, visual, and conceptual variants — these map to the three EUIPO/TTAB confusion axes | MEDIUM | Must cover: phonetic (sound-alikes), visual (letter swaps, spacing), conceptual (translations, synonyms), character (homoglyphs, accent substitution), typosquatting (missing/doubled letters). This is Trademark Cat's core job. |
| Configurable context / goods-and-services scope | Professional tools filter by goods class; attorneys need to exclude non-competing uses (e.g. Delta Airlines vs Delta Dental) | LOW | Already in PROJECT.md as "negative constraints." Must be an explicit input, not optional. |
| Threat scoring tied to legally recognized factors | Attorneys recognize the DuPont 13-factor test; a score that maps to legal factors is defensible in memos | HIGH | The 8-factor weighted matrix in PROJECT.md is correct. Factors should map to: mark similarity, goods/services similarity, trade channel overlap, consumer sophistication, fame of prior mark, actual/anecdotal confusion evidence, commercial use indicator, geographic scope. |
| Only commercially relevant hits surface | Attorneys need to distinguish infringing commercial use from news, academic, or commentary uses | MEDIUM | PROJECT.md already calls out "commercial uses only." The browsing/investigation step must enforce this; results filtered to commerce-indicating signals (e-commerce listings, business websites, app stores). |
| Exportable/reviewable report | Monitoring results need to be reviewed and stored in a client file; Markdown or PDF are acceptable | LOW | Dated Markdown report with a structured table is correct. Must include: URL, mark variant found, score breakdown, risk tier (Medium/High), and blank THREAT? column for attorney review. |
| Persistent false-positive exclusion | All professional tools offer some form of known-safe list to suppress repeat noise | LOW | safelist-[TRADEMARK].json is the right approach. Must be auto-loaded on every run; must be updated when an attorney marks THREAT? = NO. |
| Idempotent re-run behavior | Attorneys run monitoring on the same marks repeatedly; the tool must not re-alert on already-dismissed findings | LOW | Dependent on safe list feature. Each run loads safe list before scoring; matching entries are silently dropped. |
| Clear provenance per finding | Attorneys need a URL + visit date for each finding to attach to client files or enforcement letters | LOW | Browsing step must capture: URL, page title, visit timestamp, and a brief description of the infringing use. |

### Differentiators (Competitive Advantage)

Features where an AI-assisted Claude Code tool can beat both manual attorney work and expensive SaaS subscriptions.

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| Iterative variant refinement before committing to search | Attorneys can push back on generated variants before a costly search run — no SaaS tool offers a conversational refinement loop | LOW | Trademark Cat's "user-reviewable list + iteration" step is the key differentiator. Paid tools generate variants silently. |
| Inline rationale per variant | Explaining *why* each variant is a confusion risk educates the attorney and builds trust — no competing tool does this in a conversational format | LOW | Cat should annotate each variant with the confusion axis (phonetic/visual/conceptual/typo/transliteration) and a one-sentence reason. |
| Weighted scoring with visible factor breakdown | Paid tools give opaque risk scores; a transparent per-factor breakdown lets attorneys audit the reasoning and use it in enforcement memos | MEDIUM | Hound must show score as a sum of factor sub-scores, not just a total. "Visual similarity: 8/8, Goods overlap: 6/8..." is more useful than "Score: 38." |
| Automatic pipeline routing (Cat → Hound) | Hound detects missing variants file and invokes Cat automatically — eliminates workflow friction for non-technical users | LOW | Already in PROJECT.md. Simple file-existence check; route to Cat with context carried forward. |
| Safe list as human-readable JSON | SaaS tools lock exclusions inside their platform; a portable JSON file travels with the client matter and survives tool changes | LOW | safelist-[TRADEMARK].json can be checked into a client matter repo, emailed, or handed to another attorney. |
| Generates a Serper search script per trademark | Abstracting the SERP call into a generated Python script makes the search reproducible and auditable | MEDIUM | The generated script is evidence of the search methodology — useful if thoroughness is challenged. Date-stamp the script and include it in the client file. |
| Agentic browsing for evidence quality | Manual monitoring requires an attorney to visit each URL and take notes; Hound visits each lead and extracts commercial-use indicators automatically | HIGH | This is the highest-value automation step. Browsing must extract: business name, goods/services described, apparent jurisdiction, and any direct use of the variant in commerce. |
| Per-run dated reports | Monitoring is a continuous duty; dated reports create an audit trail showing the mark was actively policed | LOW | Filename: `report-[TRADEMARK]-[YYYY-MM-DD].md`. Each run creates a new file; no overwriting. |

### Anti-Features (Commonly Requested, Often Problematic)

Features to deliberately exclude from v1 (and likely v2).

| Feature | Why Requested | Why Problematic | Alternative |
|---------|---------------|-----------------|-------------|
| USPTO / trademark database search | Attorneys want official registry coverage | Requires paid API access (TSDR, CompuMark, Corsearch); out of scope per PROJECT.md; creates false confidence that web monitoring = clearance search | Clearly state in output header: "This report covers web/commercial use only. Registry clearance requires separate USPTO/international database search." |
| Automated cease-and-desist generation | Attorneys want the full enforcement workflow in one tool | Cease-and-desist letters require legal judgment about whether to enforce, on what claims, and with what demands — automating this creates malpractice risk. Also a different problem domain. | Hound report is designed to feed a C&D workflow, not replace it. Medium/High entries include all evidence fields an attorney needs to draft the letter manually. |
| Real-time / scheduled monitoring | Clients want continuous protection | Requires always-on infrastructure (cron, webhooks, server) incompatible with the Claude Code slash command model; adds operational complexity with no skill revenue model | Periodic invocation (monthly, quarterly) is the correct pattern for the attorney workflow. The dated report format supports "last monitored" documentation. |
| Social media monitoring | Social infringement is common | Requires platform-specific APIs (Meta, X, TikTok) or scraping; terms-of-service issues; separate product surface | Serper web search will surface social pages that rank publicly. Deep social scanning is a separate tool category (Red Points, BrandShield). |
| Logo / image similarity detection | Brand infringement often involves logo copies | Requires image embedding models and visual search infrastructure; entirely separate from text-variant monitoring | Logo monitoring is out of scope for v1. The tool focuses on word marks. Document this limitation clearly in output headers. |
| Automatic safe-list population | Reduce manual review burden | Automated safe-listing removes attorney judgment from a legal decision — what counts as non-threatening is a legal call, not a pattern-match call | Keep safe-list population manual (attorney marks THREAT? = NO in the report table, then re-runs Hound to commit). |
| Multi-trademark batch mode | Portfolio monitoring at scale | Adds queue management, progress tracking, and partial-failure handling complexity; the v1 pipeline needs to be solid on a single mark first | Run the pipeline once per trademark. A shell loop (`for mark in marks.txt`) is sufficient for power users. |
| Web UI or dashboard | Non-terminal users want a GUI | Requires a web server, auth, data persistence layer — entirely different product. The value prop is CLI-native in Claude Code. | Markdown reports are the UI. They open in any editor, render in GitHub, and can be shared by email. |

---

## Feature Dependencies

```
[Trademark Cat: variant generation]
    └──produces──> [variants-[TRADEMARK].txt]
                       └──required by──> [Trademark Hound: search execution]
                                             └──produces──> [search results / leads]
                                                                └──required by──> [Hound: agentic browsing]
                                                                                      └──produces──> [scored findings]
                                                                                                         └──required by──> [Hound: report generation]

[safelist-[TRADEMARK].json]
    └──loaded by──> [Hound: report generation] (filters scored findings before output)
    └──updated by──> [Hound: safe list update pass] (requires reviewed report as input)

[Hound: agentic browsing] ──depends on──> [context: goods/services scope]
    (needed to judge commercial relevance during browsing)

[Hound: threat scoring] ──depends on──> [context: goods/services scope]
    (Factor 2: goods/services similarity requires knowing what the protected mark covers)

[Cat: variant iteration] ──enhances──> [Hound: search quality]
    (More precise variants = fewer irrelevant leads = faster browsing pass)
```

### Dependency Notes

- **Cat must run before Hound.** Hound checks for `variants-[TRADEMARK].txt` and auto-routes to Cat if missing. This is a hard dependency, not a preference.
- **Goods/services context must be captured at Cat intake.** Both Cat (for variant relevance) and Hound (for scoring factors 2 and 3) need this. Capture once at Cat invocation; write it into the variants file header so Hound can read it without re-prompting.
- **Safe list load must precede scoring.** If Hound scores first and filters second, the score table in the report will be inconsistent with what was suppressed. Load safe list at the start of the browsing pass and skip those URLs entirely.
- **Safe list update is a separate Hound invocation.** The update pass reads the reviewed report (attorney has filled in THREAT? column), extracts NO entries, and appends to safelist JSON. This should not happen automatically at the end of the search pass — the attorney needs to review first.
- **Report generation requires agentic browsing output.** The report cannot be written from raw SERP results alone; browsing evidence is what makes the scoring defensible. Do not short-circuit the browsing step even for low-candidate runs.

---

## MVP Definition

### Launch With (v1)

- [ ] **Trademark Cat: variant generation across 5 categories** — Core differentiator; without this, Hound has no input. Categories: phonetic, visual/orthographic, conceptual/semantic, character-level (homoglyphs, accents), typosquatting.
- [ ] **Trademark Cat: iterative review loop** — Distinguishing feature vs silent variant generation in SaaS tools. Attorney approves or requests changes before variants file is written.
- [ ] **Trademark Cat: writes variants file with context header** — Structured output that Hound can parse; includes goods/services scope used during generation.
- [ ] **Trademark Hound: variants file detection and Cat routing** — Pipeline integrity; prevents Hound from running blind.
- [ ] **Trademark Hound: Serper.dev search script generation and execution** — Core search mechanism; generates dated, reproducible Python script per trademark.
- [ ] **Trademark Hound: agentic browsing with commercial-use filtering** — Highest-value automation; converts raw SERP hits into scored, evidenced leads.
- [ ] **Trademark Hound: 8-factor weighted threat scoring with visible breakdown** — Legal defensibility; each factor visible in output, not just total score.
- [ ] **Trademark Hound: Medium/High-only dated Markdown report** — Actionable output format for attorney review; includes THREAT? column.
- [ ] **Trademark Hound: safe list load on every run** — Table-stakes false-positive suppression; must work from first run.
- [ ] **Trademark Hound: safe list update pass from reviewed report** — Closes the feedback loop; makes the tool smarter per client matter over time.

### Add After Validation (v1.x)

- [ ] **Variant count tuning** — Allow attorney to specify "aggressive" vs "conservative" variant set size. Trigger: attorneys find 100 variants too many or too few for their monitoring cadence.
- [ ] **Score threshold configuration** — Allow changing the Medium/High cutoffs (default 10/15). Trigger: attorneys find too many or too few results surfacing.
- [ ] **Report diffing between runs** — Highlight new findings vs findings present in previous run. Trigger: attorneys doing monthly monitoring want to see "what's new" not the full list.
- [ ] **Structured evidence export (JSON/CSV)** — Machine-readable output for attorneys who pipe findings into their case management system. Trigger: adoption by larger firms with existing IP management tools.

### Future Consideration (v2+)

- [ ] **Batch portfolio mode** — Run the full pipeline across a client's trademark portfolio from a portfolio manifest file. Defer until v1 pipeline is stable and attorneys have validated the single-mark workflow.
- [ ] **USPTO registry watch integration** — Monitor new trademark applications for confusingly similar marks. Defer due to API cost and the distinct use case from web/commercial monitoring.
- [ ] **Domain registration monitoring** — Watch for new domain registrations using variants (requires domain WHOIS or registration-feed API). Defer; distinct data source and subscription model.
- [ ] **Enforcement action tracking** — Track which findings were escalated to C&D, resolved, or still open. Defer; requires persistent state beyond flat files and is a practice management feature, not a monitoring feature.

---

## Feature Prioritization Matrix

| Feature | User Value | Implementation Cost | Priority |
|---------|------------|---------------------|----------|
| Variant generation (Cat) | HIGH | MEDIUM | P1 |
| Iterative variant review (Cat) | HIGH | LOW | P1 |
| Agentic browsing with commercial filter (Hound) | HIGH | HIGH | P1 |
| Threat scoring with factor breakdown (Hound) | HIGH | MEDIUM | P1 |
| Dated Markdown report, Medium/High only (Hound) | HIGH | LOW | P1 |
| Safe list load + update (Hound) | HIGH | LOW | P1 |
| Pipeline auto-routing Cat → Hound | MEDIUM | LOW | P1 |
| Goods/services context capture and propagation | HIGH | LOW | P1 |
| Variant count / threshold tuning | MEDIUM | LOW | P2 |
| Report diff between runs | MEDIUM | MEDIUM | P2 |
| Structured JSON/CSV export | LOW | LOW | P2 |
| Batch portfolio mode | HIGH | HIGH | P3 |
| USPTO registry watch | HIGH | HIGH | P3 |
| Domain registration monitoring | MEDIUM | HIGH | P3 |

**Priority key:**
- P1: Must have for launch
- P2: Should have, add when possible
- P3: Nice to have, future consideration

---

## Competitor Feature Analysis

| Feature | Corsearch / TrademarkNow | Clarivate CompuMark | Trademark Hound + Cat |
|---------|--------------------------|---------------------|-----------------------|
| Variant generation | Silent, automated | Silent, automated | Conversational, iterative, attorney-approved |
| Variant rationale | None | None | Per-variant annotation with confusion axis |
| Search scope | Trademark registries (primary), some web | Trademark registries (primary) | Web / commercial use (primary), no registry |
| Threat scoring | AI score, opaque | AI score, opaque | 8-factor weighted matrix, per-factor visible breakdown |
| False-positive handling | Platform-internal exclusion list | Platform-internal exclusion list | Portable JSON safe list, travels with client matter |
| Report format | Platform dashboard, PDF export | Platform dashboard, PDF export | Dated Markdown, offline reviewable, attorney fills THREAT? column |
| Agentic browsing | None (human review team) | None (human review team) | Automated agentic browsing per lead |
| Cost model | Enterprise SaaS ($$$) | Enterprise SaaS ($$$) | Serper.dev API cost only (~$0.001/search) |
| Jurisdictional coverage | 200+ registry jurisdictions | Major jurisdictions | Global web (limited to what Serper indexes) |
| Logo / image monitoring | Yes (LogoWatch) | Yes (design mark analysis) | No — word marks only |
| Social media monitoring | Some (brand protection tier) | Limited | No — excludes social-only platforms |
| Scheduling / alerting | Yes (continuous watch) | Yes (continuous watch) | No — periodic manual invocation only |

---

## Sources

- [Corsearch trademark solutions and TrademarkNow](https://corsearch.com/trademark-solutions) — MEDIUM confidence (vendor marketing)
- [Top 10 Trademark Monitoring Tools comparison](https://www.devopsschool.com/blog/top-10-trademark-monitoring-tools-features-pros-cons-comparison/) — MEDIUM confidence (third-party review)
- [20 Best Trademark Monitoring Software 2026](https://thecmo.com/tools/best-trademark-monitoring-software/) — MEDIUM confidence (third-party review, gated)
- [Clarivate Trademark Watching](https://clarivate.com/intellectual-property/brand-ip-solutions/trademark-watching/) — MEDIUM confidence (vendor)
- [Questel Trademark Watch](https://www.questel.com/trademark/trademark-design-and-domain-services/trademark-watch/) — MEDIUM confidence (vendor)
- [DuPont factors for likelihood of confusion](https://www.erikpelton.com/what-are-the-dupont-factors-in-a-trademark-confusion-analysis-2/) — HIGH confidence (established legal standard, widely documented)
- [AI Agents for IP Lawyers — Datagrid](https://datagrid.com/blog/unlocking-trademark-monitoring-ai-agents-for-ip-lawyers) — MEDIUM confidence (practitioner article)
- [Alt Legal: Monitoring Trademarks](https://www.altlegal.com/blog/monitoring-trademarks/) — MEDIUM confidence (IP management vendor)
- [Similar Trademark Detection via Semantic, Phonetic and Visual Similarity — ACM SIGIR](https://dl.acm.org/doi/abs/10.1145/3404835.3463038) — HIGH confidence (peer-reviewed research)

---

*Feature research for: AI-assisted trademark monitoring (Trademark Hound + Cat)*
*Researched: 2026-04-03*
