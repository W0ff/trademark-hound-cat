# Pitfalls Research

**Domain:** Claude Code slash command skills for trademark monitoring — SERP automation, AI-assisted legal/IP analysis, persistent JSON state
**Researched:** 2026-04-03
**Confidence:** HIGH (critical pitfalls), MEDIUM (phase mapping), LOW (scale-specific thresholds)

---

## Critical Pitfalls

### Pitfall 1: Skill Prompt Gives Inconsistent Variant Output Across Runs

**What goes wrong:**
Trademark Cat produces 100 variants in one session and 60 in the next because the prompt specifies categories without locking counts, examples, or format. Each Claude invocation treats instructions as guidelines unless counts and structure are enforced explicitly. The downstream Hound then silently works with an undersized variant set without knowing the target was 100.

**Why it happens:**
Slash command authors treat system prompts as descriptions rather than contracts. Vague instructions like "generate about 100 variants across 5 categories" allow Claude to satisfy the instruction loosely. Without an explicit validation step (count check + category coverage check) before writing output, drift goes undetected.

**How to avoid:**
- Specify exact counts per category (e.g., "20 per category, 5 categories = 100 total") not approximations.
- Include a self-check step in the prompt: "Before writing the file, count your variants. If any category has fewer than 18 or more than 22, regenerate that category."
- Validate the output file programmatically after creation (line count, category header presence) and surface errors to the user before proceeding.

**Warning signs:**
- `variants-[TRADEMARK].txt` files vary noticeably in line count between runs on the same mark.
- Hound reports seem thin — fewer leads than expected.
- Users describe Cat as "sometimes thorough, sometimes not."

**Phase to address:**
Trademark Cat build phase — validation logic is a first-class requirement, not a polish step.

---

### Pitfall 2: Serper.dev Rate Limiting Silently Truncates Search Results

**What goes wrong:**
The Hound generates and runs a Python script that fires ~100 search queries (one per variant). At Serper's free/starter tier this can hit the per-minute or daily cap. The Python script gets 429 errors, silently swallows them or logs them nowhere the skill can see, and the Hound reports on a fraction of the variant set. The attorney receives a report that looks complete but has large blind spots.

**Why it happens:**
Serper.dev's free tier enforces per-second QPS limits. Naive generated scripts fire all requests in a tight loop. The Hound skill has no visibility into what the script wrote to stderr vs. stdout. Without explicit error-surface logic in the generated script, failures are invisible at the skill layer.

**How to avoid:**
- Generated Python scripts must include a per-request delay (minimum 0.5s between calls) and exponential backoff on 429.
- Script must write a summary line at the end: `COMPLETED: X of Y queries succeeded, Z failed.`
- The Hound skill prompt must instruct Claude to read that summary line and halt with an error if Z > 0 rather than proceeding to analysis on partial data.
- Cache results to disk immediately after each successful query so a rate-limited run can be resumed rather than restarted.

**Warning signs:**
- Hound reports consistently have fewer than (variants × typical-hits) leads.
- Search results suspiciously round numbers (exactly 50 hits, not 47 or 63).
- Report generation is faster than expected for the variant count.

**Phase to address:**
Trademark Hound SERP automation phase — the generated script template is where this is fixed, not the skill prompt.

---

### Pitfall 3: AI Threat Scoring Hallucinates Company Details During Agentic Browsing

**What goes wrong:**
The Hound visits each lead URL and scores it using 8 factors. When a page loads slowly, blocks bots, or has thin content, Claude fills gaps from training data — inventing company size, industry, geographic scope, or product overlap that isn't on the page. The score reflects hallucinated context, not actual evidence, and may produce HIGH or LOW scores that are completely wrong.

**Why it happens:**
Agentic browsing tools are subject to the same hallucination pressures as any LLM task: when evidence is absent, the model interpolates. Post-mortems on legal RAG systems (Stanford, 2024) found that one-third of confabulations traced to unreviewed content being accepted without provenance checks. The scoring prompt gives Claude 8 factors to fill — if even 2-3 lack page evidence, the model will estimate.

**How to avoid:**
- The scoring prompt must require evidence citation for each scored factor: "For each factor, quote the specific text from the page that justifies this score. If you cannot find direct evidence, assign 0 for that factor — do not estimate."
- Add a confidence field per factor: `evidence_found: yes/no`. Aggregate `no` count and flag entries where 3+ factors lacked evidence.
- Treat bot-blocked or inaccessible pages as "insufficient data" rather than scoring them — surface them separately for manual review.

**Warning signs:**
- Scored entries cite specific facts (employee count, revenue, target market) not present in the report excerpt.
- Multiple entries from the same domain score inconsistently across runs.
- Threat scores cluster at extremes (many 0s and many HIGH) with little middle range.

**Phase to address:**
Threat scoring design phase — build the evidence-citation requirement into the scoring template before implementing the 8-factor matrix.

---

### Pitfall 4: Safe List Corruption from Partial JSON Writes

**What goes wrong:**
`safelist-[TRADEMARK].json` is written by the Hound when processing a reviewed report. If the write is interrupted mid-operation (timeout, Claude session kill, disk error), the file is left in a truncated or syntactically invalid state. On the next run, the Hound attempts to load the safe list, JSON parsing fails, and either the entire run aborts or — worse — the safe list is silently treated as empty, causing all previously cleared false positives to resurface and flood the new report.

**Why it happens:**
Direct JSON file writes are not atomic. `open(file, 'w')` followed by `json.dump()` creates a race window where the file exists but is incomplete. This is a known and documented failure mode in Node.js (nodejs/help issue #2346) and Python alike. Generated scripts rarely include write-safety logic.

**How to avoid:**
- Always write to a temp file first (`safelist-[TRADEMARK].json.tmp`), then `os.rename()` / `os.replace()` to the final path — rename is atomic on all major OS/filesystem combinations.
- On load, catch JSON parse errors explicitly. If the main file is corrupt and a `.tmp` file exists (indicating a failed previous write), attempt to load the `.tmp` as recovery. Never silently fall back to an empty safe list — surface the error to the user.
- Include a schema validation step after loading: verify the expected structure before trusting the contents.

**Warning signs:**
- A previously reviewed trademark suddenly has hundreds of leads in a new report (safe list not being applied).
- JSON parse errors in Hound output.
- `.tmp` files left over in the workspace directory.

**Phase to address:**
Safe list persistence phase — atomic write pattern is a day-one requirement, not a hardening step.

---

### Pitfall 5: Legal Liability Boundary Violation — Tool Output Framed as Legal Advice

**What goes wrong:**
The Hound report uses language like "this constitutes infringement" or "HIGH threat" without qualification. An attorney shows this to a client, the client acts on it without further review, and the matter ends in a dispute. Alternatively, a paralegal without bar admission uses the tool autonomously and their use is characterized as unauthorized practice of law (UPL). The tool developer's liability exposure depends entirely on how outputs are framed.

**Why it happens:**
Report templates optimize for clarity and action, which naturally produces assertive language. Developers in this space underestimate that disclaimers in terms-of-service shift, not eliminate, liability — and that "designed to cross the attorney-client line" has been used as a product liability theory (Nippon Life v. OpenAI, Stanford Law 2026). The UPL analysis also applies to the tool's design intent, not just end-user behavior.

**How to avoid:**
- Report output must use consistent hedging language throughout: "potential threat requiring attorney review," not "infringement confirmed."
- Include a prominent header in every generated report: "This report is a research aid for licensed IP attorneys. All findings require professional legal judgment before action. No attorney-client relationship is created by this tool."
- The scoring matrix documentation must describe factors in terms of likelihood indicators, not legal conclusions.
- Design the workflow explicitly as attorney-supervised: the "THREAT?" column the attorney fills in is not cosmetic — it is the documented gate between AI output and legal action.

**Warning signs:**
- Report language contains declarative statements about infringement rather than risk indicators.
- Users describe the tool as "making the decision for them."
- The workflow is being used by non-attorney staff as the final step, not a research input.

**Phase to address:**
Report template design phase and throughout — language review is required at every output point in both Cat and Hound.

---

### Pitfall 6: Negative Constraint (Ignore List) Logic Too Broad or Too Narrow

**What goes wrong:**
The Hound uses company context to exclude non-competing uses (e.g., "Delta Airlines" context should exclude "Delta Dental" results). If the ignore list is built too broadly (any result mentioning "delta" in healthcare), legitimate healthcare-sector infringers are missed. If too narrow, the attorney reviews hundreds of irrelevant dental/airline results that clog the report and erode trust in the tool.

**Why it happens:**
Ignore list terms are generated from company context at search time, not manually curated. LLMs tend to over-generate safe-seeming exclusions when asked for "non-competing uses." The logic is applied as a keyword filter on search result snippets, which is a poor proxy for industry determination — a dental company can have "airline" in its marketing copy.

**How to avoid:**
- Generate ignore terms at the industry/sector level, not keyword level: "healthcare dental services sector" not "dental."
- Apply ignore logic to inferred industry of the result (requires brief classification step) rather than raw keyword matching in snippet text.
- Make the ignore list visible in the report header so attorneys can spot over-exclusion: "The following sectors were excluded from analysis: [list]. Flag any incorrect exclusion."
- Do not apply ignore logic at the search query stage (which would suppress retrieval entirely) — apply it only at the scoring stage so suppressed leads remain auditable.

**Warning signs:**
- Reports for marks in cross-sector industries (Delta, Mercury, Arrow) are suspiciously clean.
- Attorneys report that known competitors are not appearing in results.
- Ignore list terms include generic words that appear in many industries.

**Phase to address:**
Variant generation and scoring phase — ignore logic design precedes both Cat and Hound implementation.

---

### Pitfall 7: Skill Prompt Length Causes Context Budget Problems at Scale

**What goes wrong:**
The Hound skill prompt includes the threat matrix, scoring rubric, report format, safe list logic, and error handling in a single large command file. When the Hound runs against a trademark with a large variant set (100 variants × 10 results each = 1,000 leads), the accumulated search results fill the context window before the analysis phase begins. Claude either truncates analysis silently or hits a hard limit and aborts.

**Why it happens:**
Claude Code dynamically trims skill descriptions when context budget is tight (scales at 1% of context window, fallback 8,000 chars). But the problem here is not description length — it is the raw data volume injected by agentic browsing. 1,000 web page snippets, each 200-400 tokens, can consume 200K-400K tokens before any analysis happens.

**How to avoid:**
- Process variants in batches, not all-at-once. The generated Python script writes results to a JSONL file; the Hound reads and scores in batches of 20-30 results.
- Use `context: fork` (subagent isolation) for the browsing/scoring phase so the main context sees only aggregated results, not raw page content.
- Apply search result pre-filtering (snippet-level score ≥ threshold before full page visit) to cut the set before expensive agentic browsing.
- Set a per-run hard cap (e.g., browse top 50 leads by snippet relevance) and surface the cap explicitly in the report.

**Warning signs:**
- Hound runs abort partway through analysis on large trademarks.
- Reports contain fewer scored entries than search results retrieved.
- Session context indicators show high utilization before scoring begins.

**Phase to address:**
Hound architecture design phase — batching and subagent isolation are structural decisions that cannot be easily retrofitted.

---

## Technical Debt Patterns

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|----------------|-----------------|
| Skip atomic writes for safe list | Simpler generated code | Corrupt safe list on interrupted write; all false positives resurface | Never — atomic write is two extra lines |
| Single monolithic Hound prompt | Easier to write and read | Context exhaustion on large trademark portfolios; brittle to prompt order changes | MVP only if trademark portfolio is small (< 20 variants) |
| Keyword-based ignore list | Fast to generate | Over-excludes legitimate threats in cross-sector marks | Never for marks with cross-sector exposure |
| No rate limiting in SERP script | Faster first run | Silent data gaps on all subsequent runs; unreliable reports | Never — rate limiting is table stakes |
| Assertive language in reports | Cleaner report UX | Legal liability exposure; reduces attorney critical review | Never — hedging is a legal safety requirement |
| No evidence citation in scoring | Simpler scoring prompt | Undetectable hallucinated scores; wrong prioritization | Never for legal-use outputs |

---

## Integration Gotchas

| Integration | Common Mistake | Correct Approach |
|-------------|----------------|------------------|
| Serper.dev | Fire all variant queries in parallel without rate limiting | Sequential with 0.5s delay + exponential backoff on 429; batch into groups of 10 |
| Serper.dev | Not caching results to disk before processing | Write each result to JSONL immediately; processing is separate from retrieval |
| Serper.dev | API key hardcoded in generated script | Pass as environment variable `SERPER_API_KEY`; never write it into generated files |
| Agentic browsing | Treating inaccessible pages as scoreable | Classify as `status: blocked` and route to manual review section, not threat scoring |
| JSON safe list | `json.load()` without try/except | Explicit parse error handling with recovery path and user-visible error message |
| JSON safe list | Appending to in-memory list and writing once at end | Write incrementally or accept that session abort = full data loss; document the tradeoff |

---

## Performance Traps

| Trap | Symptoms | Prevention | When It Breaks |
|------|----------|------------|----------------|
| Sequential agentic page visits with no timeout | Run takes 2+ hours; Claude Code session times out | Set per-page visit timeout (10s); skip and flag pages that exceed it | At ~50+ leads per run |
| No pre-filtering before full page visits | Trivial results (Wikipedia, news articles) are visited and scored | Apply snippet-level relevance score before dispatching agentic browse | At any scale — wastes tokens immediately |
| Loading full page HTML into context | Context fills with navigation menus, footers, cookie banners | Extract main content only (main text, title, meta description) before injecting into scoring context | At any scale |
| Regenerating all variants when adding context | Re-running Cat on an existing mark to add context destroys the original file | Append/merge mode: Cat checks for existing file and adds to it rather than replacing | First time an attorney wants to refine context |

---

## Security Mistakes

| Mistake | Risk | Prevention |
|---------|------|------------|
| API key in generated Python script | Key exposed in workspace file, git history, or shared report directory | `SERPER_API_KEY` env var; generated scripts reference `os.environ.get()` only |
| Storing safe list in report directory alongside reports | Reports shared with clients could expose safe list (business intelligence: what the attorney has decided is not a threat) | Separate safe list storage from report storage; document the distinction |
| No input validation on trademark name in file paths | Trademark names with `/`, `:`, or `..` create path traversal in generated filenames | Sanitize trademark names to `[a-zA-Z0-9_-]` before using in filenames |
| Generated Python script runs arbitrary shell commands | Prompt injection via variant content could cause script to include malicious search strings | Variants are passed as data (JSON array), not interpolated into shell commands |

---

## UX Pitfalls

| Pitfall | User Impact | Better Approach |
|---------|-------------|-----------------|
| No progress indicator during 100-query SERP run | Attorney abandons thinking it stalled | Print per-query progress: `[23/100] Searching: "Trademrk Hund"...` |
| Report requires knowing which column to fill in | Paralegals fill wrong column or skip the feedback step entirely | Report includes inline instructions: "Fill THREAT? with YES/NO for each row, then re-run `/trademark-hound [MARK] --update-safelist`" |
| Cat feedback loop exits immediately if user says "looks good" | No validation that all 5 categories are actually present | Cat counts categories and entries before accepting approval |
| No run summary at end of Hound | Attorney doesn't know if run was complete | Final output: "Run complete. Searched 100 variants, visited 47 leads, scored 23 Medium/High. 3 pages were inaccessible and flagged for manual review." |
| Safe list silently applies without telling user what it filtered | Attorney doesn't know 40 known-safe results were suppressed | Report header: "Safe list applied: 43 results suppressed. [Show suppressed]" |

---

## "Looks Done But Isn't" Checklist

- [ ] **Trademark Cat:** Generates output file — verify count per category (not just total count) and that all 5 linguistic categories are present with distinct entries.
- [ ] **Trademark Hound SERP script:** Runs without error — verify the summary line shows X of Y queries succeeded; a clean exit code with 40/100 successes is a silent failure.
- [ ] **Threat scoring:** Scores are assigned to all leads — verify each entry has evidence citations for each factor; zero-evidence scores are hallucination, not analysis.
- [ ] **Safe list update:** "Safe list updated" message appears — verify the file was written atomically (no `.tmp` left over) and that the entry count increased.
- [ ] **Report format:** Report renders in Markdown — verify the THREAT? column is blank (not pre-filled) and that the re-run instruction is present.
- [ ] **Ignore list:** Non-competing uses excluded — verify one known competitor IS in the results (proves exclusion logic isn't over-broad).
- [ ] **Legal disclaimer:** Report has a disclaimer section — verify it appears in every generated report, not just the first run.

---

## Recovery Strategies

| Pitfall | Recovery Cost | Recovery Steps |
|---------|---------------|----------------|
| Corrupt safe list | MEDIUM | Restore from last clean report (re-derive entries from THREAT?=NO rows); document timestamp of last known-good state |
| Rate-limited SERP run with no cache | HIGH | Restart with delays; no data recovery possible without cached JSONL |
| Rate-limited SERP run with cache | LOW | Re-run scoring step only against cached JSONL; skip retrieval |
| Hallucinated threat scores discovered post-report | HIGH | Re-run scoring with evidence-citation prompt on the affected entries; compare delta; issue amended report |
| Over-broad ignore list excludes real competitor | MEDIUM | Re-run Hound with revised ignore terms; diff new report against original to surface newly visible leads |
| Context exhaustion mid-analysis | MEDIUM | Break variant set into two runs (A-M, N-Z); merge reports manually; or implement batching before next run |

---

## Pitfall-to-Phase Mapping

| Pitfall | Prevention Phase | Verification |
|---------|------------------|--------------|
| Inconsistent Cat variant output | Cat build — validation logic | Run Cat 3 times on same input; verify output count within ±2 per category |
| SERP rate limiting silent truncation | Hound SERP script template | Run against a 100-variant set and verify summary line reports 100/100 |
| Hallucinated threat scores | Scoring prompt design | Score 5 test leads; verify every factor has a quoted evidence string |
| Safe list JSON corruption | Safe list persistence (Hound build) | Kill session mid-write; verify next run detects corruption and surfaces error rather than proceeding empty |
| Legal liability language | Report template design | Review every output surface for declarative infringement language before any attorney use |
| Ignore list over-exclusion | Variant + scoring design | Run against a known cross-sector mark; verify known competitor appears in output |
| Context exhaustion at scale | Hound architecture design | Simulate 100-variant run; verify context utilization at scoring phase start is below 40% |
| API key exposure | SERP script template (day one) | Grep generated scripts for literal API key strings; should be zero matches |

---

## Sources

- [Serper.dev official docs](https://serper.dev/) — rate limiting and pricing
- [Understanding API Rate Limits — SerpHouse](https://www.serphouse.com/blog/api-rate-limits-explained-for-developers/) — retry/backoff patterns
- [SERP API Pricing Index 2026 — SearchCans](https://www.searchcans.com/blog/serp-api-pricing-index-2026/) — tier caps
- [Claude Code Best Practices — official docs](https://code.claude.ai/docs/en/best-practices) — context management, subagents
- [Claude Code Skills — official docs](https://code.claude.ai/docs/en/skills) — context isolation with `context: fork`
- [Claude Skills: The Controllability Problem — paddo.dev](https://paddo.dev/blog/claude-skills-controllability-problem/) — prompt consistency issues
- [Context Window in Claude Code — MindStudio](https://www.mindstudio.ai/blog/context-window-claude-code-manage-consistent-results) — exhaustion patterns
- [JSON corruption from concurrent writes — nodejs/help #2346](https://github.com/nodejs/help/issues/2346) — atomic write necessity
- [lowdb concurrent write issue #333](https://github.com/typicode/lowdb/issues/333) — JSON state corruption real-world case
- [AI Hallucinations in Court — Sterne Kessler 2025 review](https://www.sternekessler.com/news-insights/insights/ai-ip-year-in-reviewai-hallucinations-in-court-filings-and-orders-a-2025-review-of-sanctions-across-the-courts-and-rule-proposals/) — legal AI hallucination rates
- [Hallucination-Free? Legal RAG reliability — Stanford DHo](https://dho.stanford.edu/wp-content/uploads/Legal_RAG_Hallucinations.pdf) — 1/3 confabulation rate from unreviewed pages
- [Is AI for Legal Services UPL? — ByDesignLaw](https://www.bydesignlaw.com/ai-for-legal-services-is-it-unauthorized-practice-of-law-upl) — UPL analysis
- [Designed to Cross — Stanford CodeX](https://law.stanford.edu/2026/03/07/designed-to-cross-why-nippon-life-v-openai-is-a-product-liability-case/) — product liability theory for AI legal tools
- [AI Hallucinations in Web Agents — arXiv 2504.01382](https://arxiv.org/html/2504.01382v4) — agentic browsing reliability assessment

---
*Pitfalls research for: Trademark Hound + Cat — Claude Code slash command skills for trademark monitoring*
*Researched: 2026-04-03*
