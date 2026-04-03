# Phase 2: Trademark Hound Core - Research

**Researched:** 2026-04-03
**Domain:** Claude Code slash command authoring, Python SERP script instantiation, agentic WebFetch browsing, JSON safelist filtering, weighted threat scoring
**Confidence:** HIGH — core patterns established by Phase 1; Phase 2 extends the same delivery format with additional in-command agentic logic

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| HND-01 | User can invoke `/trademark-hound` and be prompted for trademark name and company context | Same `$ARGUMENTS` + interactive fallback pattern as `/trademark-cat`; confirmed working in Phase 1 |
| HND-02 | Hound checks for existing `safelist-[TRADEMARK].json` and loads it if present | `pathlib.Path.exists()` + `json.load()` — stdlib; safelist is read-only in this phase |
| HND-03 | Hound detects missing `variants-[TRADEMARK].txt` and routes user to run `/trademark-cat` first | `pathlib.Path.exists()` check with halt-and-message pattern |
| HND-04 | Hound checks for existing `hound-SERP-[TRADEMARK].py`; generates one from template if absent | Two-token substitution: read template, `.replace("[INSERT API KEY]", key)`, `.replace("[INSERT VARIANTS FILE]", path)`, write generated script |
| HND-05 | Hound executes the generated Python script and it produces `hound_leads-[TRADEMARK].json` | `Bash` tool execution of `python3 hound-SERP-[TRADEMARK].py`; output file path is deterministic |
| HND-06 | SERP script implements rate limiting and progress reporting | Already baked into `hound_leads_template.py` — inherited by generated script; no new code needed |
| HND-07 | After SERP execution, leads whose URLs appear in the safelist are filtered out | Set of URLs from safelist JSON; filter `hound_leads` list by `lead["url"] not in safelist_urls` |
| HND-08 | Hound visits each lead URL via WebFetch; assesses commerciality, trademark usage, market overlap | Direct WebFetch tool calls per URL; assessment is LLM reasoning in the command instructions |
| HND-09 | News articles, Wikipedia, dictionaries, informational content excluded before scoring | Rule-based URL and content triage: domain patterns + content signal checks in instructions |
| HND-10 | Each lead scored using 8-factor weighted threat matrix with evidence citation per factor | Scoring table locked in REQUIREMENTS.md; implemented as structured LLM output per lead |
| HND-11 | Risk tiers applied: High ≥ 15, Medium 10–14, Low < 10 | Arithmetic check; tiers applied after 8-factor total is computed |
| HND-12 | Leads scoring below 10 (Low) excluded from further surfacing | Filter step after scoring; Low leads are dropped silently (not passed to Phase 3 report) |
</phase_requirements>

---

## Summary

Phase 2 builds on the same Claude Code slash command delivery format established in Phase 1. The deliverable is `.claude/commands/trademark-hound.md` — a command file whose instructions guide Claude through a multi-step pipeline: intake, file checking, API key collection, SERP script generation, script execution, safelist filtering, agentic browsing, and threat scoring. Phase 3 will consume the scored leads to produce the dated Markdown report; Phase 2's terminal output is a filtered, scored set of leads ready for report generation.

The most architecturally distinctive aspect of Phase 2 is that it is a multi-tool Claude Code session: the Hound command instructs Claude to use `Bash` (to execute the Python SERP script), `WebFetch` (to visit each lead URL), and `Write` (to generate the per-trademark SERP script). All three tools are available to Claude in Claude Code sessions by default. There is no separate runtime or agent framework — the command file is the controller.

The 8-factor scoring matrix is implemented as structured LLM reasoning guided by the command instructions. Each factor has a defined scale and weight (locked in REQUIREMENTS.md). The instructions must specify the output format precisely — a per-lead score block with factor values, weights, factor totals, grand total, and evidence citations — so that Phase 3 can consume it deterministically. The key design decision is whether scored leads are accumulated in-memory in Claude's context window or written to an intermediate JSON file. Writing an intermediate `hound_scored-[TRADEMARK].json` file is the safer choice: it makes the phase restartable and gives Phase 3 a stable input contract.

**Primary recommendation:** Implement Hound as `.claude/commands/trademark-hound.md` following the same structural pattern as `trademark-cat.md`. Use an intermediate `hound_scored-[TRADEMARK].json` output file to pass scored leads to Phase 3. Do not try to hold all leads in context — the lead set can be 100s of entries after SERP expansion.

---

## Standard Stack

### Core

| Library / Format | Version | Purpose | Why Standard |
|-----------------|---------|---------|--------------|
| `.claude/commands/trademark-hound.md` | current | Claude Code slash command delivery | Same pattern as Phase 1; locked format; no separate install |
| `pathlib.Path` | stdlib | File existence checks, path construction | Used in Phase 1 tests; cross-OS safe; no deps |
| `json` | stdlib | Load safelist, load leads JSON, write scored output | Already used in template; zero dependencies |
| `WebFetch` (Claude tool) | built-in | Agentic lead URL investigation | Only available browsing mechanism within Claude Code sessions |
| `Bash` (Claude tool) | built-in | Execute `python3 hound-SERP-[TRADEMARK].py` | Required to run the SERP script from within the command session |
| `Write` (Claude tool) | built-in | Generate per-trademark SERP script from template | Same tool pattern used by Cat to write variants file |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `os.path` / `pathlib` | stdlib | Template file reading, script generation path | Path construction for `hound-SERP-[TRADEMARK].py` output |
| `str.replace()` | built-in | Substitute two placeholder tokens in template | Simple string substitution; no regex needed for exact tokens |
| `set()` | built-in | O(1) URL membership test against safelist | Safelist may have hundreds of URLs; set lookup is faster than list |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| `.claude/commands/` format | `.claude/skills/` format | Skills format supports bundled supporting files; commands format is simpler and already proven in Phase 1. Phase 1 research noted Phase 2 could revisit this. Verdict: commands format is sufficient — Hound has no supporting files that need bundling. |
| In-memory lead accumulation | `hound_scored-[TRADEMARK].json` intermediate file | Context window accumulation risks: (1) LLM context window pressure with 100+ leads, (2) unrecoverable state if session interrupted. Intermediate file is restartable and gives Phase 3 a clean input contract. |
| LLM-only content triage | URL blocklist regex | URL pattern matching (`.wikipedia.org`, `news.`, `.bbc.co.uk`) is fast, predictable, and not subject to LLM hallucination. Use URL triage first, then content-signal triage on remaining URLs. |

**Installation:**
```bash
# No new dependencies for Phase 2. Python stdlib + requests (already required for SERP template).
# Verify Phase 1 artifacts are present before starting Phase 2:
python3 tests/test_phase1.py
```

---

## Architecture Patterns

### File Layout

```
[project root]/
├── .claude/
│   └── commands/
│       ├── trademark-cat.md          # Phase 1 — exists
│       └── trademark-hound.md        # Phase 2 — new
├── hound_leads_template.py           # Phase 1 — exists; read-only in Phase 2
│
[workspace — where attorney invokes /trademark-hound]/
├── variants-[TRADEMARK].txt          # Phase 1 output — Hound reads this
├── safelist-[TRADEMARK].json         # Phase 2 loads (read-only); Phase 3 writes
├── hound-SERP-[TRADEMARK].py         # Phase 2 generates from template; reused if exists
├── hound_leads-[TRADEMARK].json      # Phase 2 SERP output — generated by python script
└── hound_scored-[TRADEMARK].json     # Phase 2 output — scored leads for Phase 3
```

### Pattern 1: Multi-Step Command File with Tool Sequencing

**What:** The command instructions explicitly sequence the pipeline steps, telling Claude which tool to use at each step and what to do with the output.

**When to use:** When a slash command requires multiple Claude Code tools (Bash, WebFetch, Write) called in a defined order with conditional branching.

**Pattern in command instructions:**
```markdown
## Step 1: Check Prerequisites

Use the Read tool to check whether `variants-[sanitized_name].txt` exists in the current directory.
If the file does NOT exist, output:
> "No variants file found for [TRADEMARK]. Please run `/trademark-cat [TRADEMARK]` first to generate the variants list."
Then stop. Do not proceed.

## Step 2: Load Safelist

Check whether `safelist-[sanitized_name].json` exists.
If it does, read it and load the list of safe URLs. Store them as a set for lookup.
If it does not exist, continue with an empty safelist.
Report: "Safelist loaded: [N] entries" (or "No safelist found — starting fresh")

## Step 3: Generate or Reuse SERP Script
...
```

**Why this pattern works:** Claude Code's command files are system prompts. Step-numbered sections with explicit tool directives work better than prose paragraphs — they mirror how multi-step workflows are naturally structured and reduce ambiguity about when to use which tool.

### Pattern 2: Two-Token SERP Script Generation

**What:** Hound reads `hound_leads_template.py`, substitutes both placeholder tokens, and writes the result as `hound-SERP-[TRADEMARK].py`. The API key is solicited from the attorney at runtime; it is never stored in any tracked file.

**When to use:** Any time a per-trademark instantiation of the template is needed.

**Token substitution in command instructions:**
```markdown
## Step 3: Generate SERP Script

Check whether `hound-SERP-[sanitized_name].py` exists.

If it EXISTS:
  Use it as-is. Proceed to Step 4.

If it does NOT exist:
  Ask the attorney: "What is your Serper.dev API key?"
  Wait for the key. Do not proceed until the key is provided.

  Read the file `hound_leads_template.py` from the project root.
  Replace the literal string `[INSERT API KEY]` with the attorney's API key.
  Replace the literal string `[INSERT VARIANTS FILE]` with `variants-[sanitized_name].txt`.
  Write the result to `hound-SERP-[sanitized_name].py`.

  Output: "SERP script generated: hound-SERP-[sanitized_name].py"
```

**Security note:** The API key appears in the generated `hound-SERP-[TRADEMARK].py` file. This file should not be committed to version control. The command instructions should note this: "Note: `hound-SERP-[TRADEMARK].py` contains your API key and should not be committed to git."

### Pattern 3: Bash Tool Script Execution with Output Capture

**What:** Hound executes the generated Python SERP script using the Bash tool and monitors its output for errors.

**Command instruction pattern:**
```markdown
## Step 4: Run SERP Search

Execute using the Bash tool:
  python3 hound-SERP-[sanitized_name].py

This will print progress as it runs: "[1/N] Searching: [variant]" for each variant.
When complete, it will report how many results were written to `hound_leads-[sanitized_name].json`.

If the script exits with an error (non-zero exit code, or "ERROR" in output):
  Report the error to the attorney and stop.
  Common errors: invalid API key, network timeout, variants file not found.

After successful completion, read `hound_leads-[sanitized_name].json` to get the raw leads.
Report: "SERP search complete. [N] leads found across [M] variants."
```

**Key detail:** The SERP script can take several minutes for 100+ variants with 0.5s delay. The command instructions should set this expectation explicitly: "This will take approximately [N × 0.5] seconds."

### Pattern 4: Safelist Filtering

**What:** Before investigation, filter the raw leads list to exclude any URL already in the safelist.

**Command instruction pattern:**
```markdown
## Step 5: Apply Safelist Filter

For each lead in `hound_leads-[sanitized_name].json`:
  If the lead's `url` field matches any URL in the loaded safelist, discard it silently.

Report: "[N] leads after safelist filtering ([M] leads excluded by safelist)"
Proceed with only the filtered leads.
```

**Implementation note:** URL matching should be exact (string equality). No fuzzy matching, no subdomain normalization. This keeps the filter deterministic and auditable — the safelist contains exactly what the attorney approved.

### Pattern 5: Informational Content Exclusion (URL + Content Triage)

**What:** Before scoring, exclude leads that are news articles, Wikipedia pages, dictionaries, or purely informational content. Two-stage: URL pattern first, then content signal check via WebFetch.

**Stage 1 — URL pattern triage (fast, no fetch needed):**
```markdown
Exclude without fetching if the URL matches any of these patterns:
- Contains: wikipedia.org, wikimedia.org, wiktionary.org
- Contains: dictionary.com, merriam-webster.com, vocabulary.com
- Domain starts with: news., en.wikipedia
- Contains: /news/, /article/, /blog/ (unless the site is a brand site — use judgment)
- Top-level news domains: bbc.co.uk, reuters.com, apnews.com, nytimes.com, wsj.com, theguardian.com
```

**Stage 2 — Content signal triage (fetch required for ambiguous URLs):**
```markdown
For each remaining lead, fetch the URL using WebFetch.
If the fetched content primarily contains:
  - News article bylines (Author, Published date, news header nav)
  - Encyclopedia-style neutral descriptions with no commercial intent
  - Dictionary/reference format (Definition:, Etymology:, Synonyms:)
  → Exclude this lead. Log: "Excluded [URL]: informational content"

If the content shows commercial signals (prices, Buy/Shop/Cart, brand identity, contact sales):
  → Keep for investigation.
```

**Why two stages:** URL-pattern exclusion handles the bulk of obvious informational URLs without spending a WebFetch call. The content-signal stage handles edge cases (e.g., a brand that runs a blog under `/blog/` but is still primarily commercial).

### Pattern 6: Agentic Lead Investigation (Three Dimensions)

**What:** For each commercial lead that passes triage, Hound assesses three dimensions using the already-fetched content.

**Assessment framework in command instructions:**
```markdown
For each commercial lead, assess the following using the page content:

1. COMMERCIALITY — Is this a for-profit entity selling goods or services?
   Evidence to look for: prices, Buy/Shop/Cart buttons, service descriptions, subscription offers
   If clearly non-commercial (nonprofit with no commercial arm): flag and skip scoring

2. TRADEMARK USAGE — Is the searched variant used as a brand identifier (source designator)?
   Evidence: variant appears in site title, logo alt text, domain name, product name, or as the company name
   Distinguish: variant used as a brand name vs. mentioned only in passing text

3. MARKET OVERLAP — Does the entity target a similar audience to the protected mark?
   Use the goods/services context from the variants file `# Context:` line as the comparison baseline
   Evidence: product category, customer descriptions, pricing tier, industry language
```

**Output structure per lead:**
```
Lead: [URL]
Variant matched: [variant name]
Title: [page title]

COMMERCIALITY: [Yes/No/Partial] — [one sentence evidence]
TRADEMARK USAGE: [Yes/No/Partial] — [one sentence evidence]
MARKET OVERLAP: [Yes/No/Partial] — [one sentence evidence]

→ PROCEED TO SCORING / EXCLUDE ([reason if excluded])
```

### Pattern 7: 8-Factor Weighted Threat Scoring

**What:** Each lead that passes investigation receives a score from the 8-factor matrix. Evidence citations are required per factor.

**Scoring table (locked in REQUIREMENTS.md):**

| Factor | Scale | Weight | Max contribution |
|--------|-------|--------|-----------------|
| Mark Criticality | 0–3 | ×3 | 9 |
| Similarity (sight/sound/meaning) | 0–4 | ×3 | 12 |
| Goods/Services & Channels Overlap | 0–3 | ×3 | 9 |
| Geography Priority | 0–3 | ×2 | 6 |
| Evidence of Confusion/Association | 0–2 | ×2 | 4 |
| Rights Posture (ours vs. theirs) | 0–2 | ×2 | 4 |
| Counterparty Profile | 0–2 | ×1 | 2 |
| Enforcement Cost vs. Budget | 0–2 | ×1 | 2 |

**Maximum possible score:** 48. Risk tiers: High ≥ 15, Medium 10–14, Low < 10.

**Required output format per scored lead (command instructions must specify this exactly):**
```markdown
## [Entity Name] — [URL]
Variant: [variant]

| Factor | Score | Weight | Subtotal | Evidence |
|--------|-------|--------|----------|---------|
| Mark Criticality | [0-3] | ×3 | [n] | [one sentence] |
| Similarity | [0-4] | ×3 | [n] | [one sentence] |
| Goods/Services Overlap | [0-3] | ×3 | [n] | [one sentence] |
| Geography Priority | [0-3] | ×2 | [n] | [one sentence] |
| Confusion Evidence | [0-2] | ×2 | [n] | [one sentence] |
| Rights Posture | [0-2] | ×2 | [n] | [one sentence] |
| Counterparty Profile | [0-2] | ×1 | [n] | [one sentence] |
| Enforcement Cost | [0-2] | ×1 | [n] | [one sentence] |

**Total: [N] — [High/Medium/Low]**
```

**Intermediate JSON structure for `hound_scored-[TRADEMARK].json`:**
```json
[
  {
    "url": "https://example.com",
    "variant": "AcmeTech",
    "title": "AcmeTech Software — Project Solutions",
    "entity_name": "AcmeTech Inc.",
    "industry": "Project Management Software",
    "factors": {
      "mark_criticality": {"score": 3, "weight": 3, "evidence": "..."},
      "similarity": {"score": 3, "weight": 3, "evidence": "..."},
      "goods_services_overlap": {"score": 3, "weight": 3, "evidence": "..."},
      "geography_priority": {"score": 2, "weight": 2, "evidence": "..."},
      "confusion_evidence": {"score": 1, "weight": 2, "evidence": "..."},
      "rights_posture": {"score": 1, "weight": 2, "evidence": "..."},
      "counterparty_profile": {"score": 1, "weight": 1, "evidence": "..."},
      "enforcement_cost": {"score": 1, "weight": 1, "evidence": "..."}
    },
    "total_score": 30,
    "risk_tier": "High"
  }
]
```

Only Medium (score 10–14) and High (score ≥ 15) leads are written to `hound_scored-[TRADEMARK].json`. Low leads (< 10) are silently dropped.

### Anti-Patterns to Avoid

- **Generating the SERP script on every run:** Always check for `hound-SERP-[TRADEMARK].py` first. If it exists, reuse it. Regenerating prompts for the API key unnecessarily and overwrites any manual tweaks the attorney may have made to `DELAY_SECONDS`.
- **Storing the API key in the command file or any tracked file:** The key is entered interactively per session and embedded only in the generated `hound-SERP-[TRADEMARK].py` (which should be gitignored).
- **Fuzzy URL matching against safelist:** Exact string equality only. Fuzzy matching introduces false exclusions (e.g., a different product page on the same domain as a safelisted page).
- **Attempting to score leads in a single LLM pass across all leads:** Score one lead at a time. A single "score all these leads" prompt with 100+ URLs will hallucinate or truncate. The command instructions must loop explicitly.
- **Dropping the context from the variants file:** The `# Context:` first line of `variants-[TRADEMARK].txt` is the goods/services baseline for Market Overlap assessment. Hound must read and retain this line when loading variants.
- **Treating all sub-10 leads as discarded silently without any acknowledgement:** The command should report final counts: "N leads scored — High: X, Medium: Y, Low: Z (dropped)."

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| SERP execution | Shell subprocess wrapper or async runner | `Bash` tool calling `python3 hound-SERP-[TRADEMARK].py` | The template already handles all SERP logic; Bash tool is the correct execution surface inside Claude Code |
| URL content fetching | Custom HTTP client | `WebFetch` tool | Built into Claude Code; handles redirects, timeouts, content extraction; no code to write |
| Template instantiation | Jinja2 or templating library | `str.replace("[INSERT API KEY]", key)` | Two exact-token substitutions; any templating library is overkill |
| Safelist URL lookup | Database, inverted index | `set(url for entry in safelist)` with `url in safelist_set` | O(1) membership test; safelist will never exceed thousands of entries |
| Factor score arithmetic | Custom scoring engine | Explicit multiplication table in the scoring format | LLM does arithmetic in the output format; scores are verified by reading the table, not by running code |

**Key insight:** Phase 2's complexity is operational, not algorithmic. The hard problems are LLM instruction clarity (correct sequencing of multi-tool steps, precise scoring format) and session flow design (how to handle interruptions, re-runs, partial completions). There is no algorithmic problem that warrants a custom library.

---

## Common Pitfalls

### Pitfall 1: Context Window Pressure from 100+ Lead URLs
**What goes wrong:** Hound loads 100+ SERP results, fetches each URL, and the accumulated context exceeds what the model can process reliably, causing hallucinations or truncation in later leads.
**Why it happens:** Each WebFetch call returns several hundred to several thousand tokens of page content. At 100 leads × ~2K tokens/page = ~200K tokens just for page content, plus conversation history.
**How to avoid:** (1) Apply safelist filtering and informational exclusion aggressively before investigation — this can eliminate 30–50% of leads. (2) Process leads one at a time and discard fetched content from context after scoring that lead. (3) Write scored leads to `hound_scored-[TRADEMARK].json` incrementally — if the session runs long, it can be resumed. The command instructions should explicitly say: "After scoring each lead and writing it to the output file, you may release its fetched content from your working memory."
**Warning signs:** Scoring quality degrades noticeably for leads late in the list; earlier leads get High scores while later leads with similar profiles get Low scores.

### Pitfall 2: API Key Inadvertently Logged or Stored
**What goes wrong:** The attorney's Serper.dev API key appears in Claude's response text, in a summary message, or in the conversation history in an exposed way.
**Why it happens:** Command instructions that say "show me the generated script before writing" will display the key in the chat.
**How to avoid:** Command instructions should say: "Do NOT display the generated script content in your response. Write it directly with the Write tool. Confirm only: 'SERP script written to hound-SERP-[name].py.'"
**Warning signs:** The API key appears in visible chat output.

### Pitfall 3: Goods/Services Context Lost Between Steps
**What goes wrong:** When assessing Market Overlap (HND-08), Hound does not know what market the protected mark is in — so it cannot determine if the lead's market overlaps.
**Why it happens:** The `# Context:` line in `variants-[TRADEMARK].txt` is only read when loading variants for SERP execution. By the time the investigation step runs, that context may not be referenced.
**How to avoid:** When Hound loads `variants-[TRADEMARK].txt`, it must explicitly extract and retain the `# Context:` line value. Command instructions: "Read the first line. If it starts with `# Context:`, store the goods/services description (everything after `# Context: `) as `protected_mark_context`. You will use this when assessing Market Overlap for every lead."

### Pitfall 4: SERP Script Re-Generation Overwrites Manual Tweaks
**What goes wrong:** Attorney adjusts `DELAY_SECONDS` in `hound-SERP-ACME.py` to 1.0 seconds. Next run, Hound regenerates the script and resets it to 0.5 seconds.
**Why it happens:** Hound generates a new script on every run rather than checking for an existing one.
**How to avoid:** Always check for `hound-SERP-[TRADEMARK].py` first. If it exists, use it. Only generate if it is absent. This is a locked requirement: HND-04 says "checks for an existing... if absent, generates one."

### Pitfall 5: Informational URL Exclusion Too Aggressive
**What goes wrong:** A competitor with a product called "Acme" has an About page at `/about/acme-story.html`. The path contains "story" and Hound excludes it as informational.
**Why it happens:** Path-based exclusion rules (e.g., exclude URLs containing `/blog/`, `/article/`) are too broad.
**How to avoid:** Apply domain-level exclusion for known information sites (Wikipedia, Reuters, etc.), not path-level exclusion. For ambiguous URLs, fetch the content and apply content-signal triage. Do not exclude based on path segments alone.

### Pitfall 6: Scoring Without Evidence Forces Hallucination
**What goes wrong:** The command instructs Claude to score a lead but does not require evidence per factor, so Claude generates plausible-sounding but unverified scores.
**Why it happens:** Without the evidence-citation requirement, the scoring step becomes a pure LLM reasoning task with no grounding. The WebFetch content is available but unused.
**How to avoid:** Command instructions must require evidence per factor: "For each factor, cite specific text, numbers, or observations from the fetched page content. Do not infer — quote or paraphrase directly."

### Pitfall 7: Phase 2 / Phase 3 Boundary Confusion
**What goes wrong:** The planner tries to implement report generation (HND-13 through HND-16) in the same command file and same plans as Phase 2, blurring the boundary.
**Why it happens:** It feels natural to finish the pipeline in one phase.
**How to avoid:** Phase 2 ends with `hound_scored-[TRADEMARK].json` containing only Medium and High leads. Phase 3 reads that file to generate the report. The output file is the explicit handoff contract. Phase 2 plans should NOT include any report writing logic.

---

## Code Examples

Verified patterns from Phase 1 and locked contracts:

### Variants File Loading with Context Extraction
```python
# Hound reads variants-[TRADEMARK].txt and extracts # Context: line
protected_mark_context = None
variants = []
with open("variants-acme.txt", encoding="utf-8") as f:
    for line in f:
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("# Context:"):
            protected_mark_context = stripped[len("# Context:"):].strip()
            continue
        if stripped.startswith("#"):
            continue
        variant_name = stripped.split("#")[0].strip()
        if variant_name:
            variants.append(variant_name)
# Result: protected_mark_context = "software for project management"
#         variants = ["Ackme", "AcmeTech", ...]
```

### Two-Token Template Substitution
```python
# Read template, substitute both tokens, write generated script
template = open("hound_leads_template.py", encoding="utf-8").read()
script = template.replace("[INSERT API KEY]", api_key)
script = script.replace("[INSERT VARIANTS FILE]", "variants-acme.txt")
with open("hound-SERP-acme.py", "w", encoding="utf-8") as f:
    f.write(script)
# Verify both tokens were actually replaced (guard against partial substitution)
assert "[INSERT API KEY]" not in script
assert "[INSERT VARIANTS FILE]" not in script
```

### Safelist URL Set Construction
```python
# Load safelist-[TRADEMARK].json into a set for O(1) lookup
import json
from pathlib import Path

safelist_path = Path("safelist-acme.json")
safelist_urls = set()
if safelist_path.exists():
    with open(safelist_path, encoding="utf-8") as f:
        safelist_data = json.load(f)
    # safelist-[TRADEMARK].json is a list of objects with a "url" key (Phase 3 format)
    # or a plain list of URL strings — handle both defensively
    for entry in safelist_data:
        if isinstance(entry, dict):
            safelist_urls.add(entry.get("url", ""))
        elif isinstance(entry, str):
            safelist_urls.add(entry)
```

### Lead Filtering Against Safelist
```python
# Load raw leads, filter against safelist
with open("hound_leads-acme.json", encoding="utf-8") as f:
    all_leads = json.load(f)  # list of {variant, title, url, snippet, position}

filtered_leads = [lead for lead in all_leads if lead["url"] not in safelist_urls]
excluded_count = len(all_leads) - len(filtered_leads)
# Report: f"{excluded_count} leads excluded by safelist; {len(filtered_leads)} leads to investigate"
```

### Informational URL Pattern Triage
```python
# URL-based triage: exclude known information domains without fetching
INFORMATIONAL_DOMAINS = {
    "wikipedia.org", "wikimedia.org", "wiktionary.org",
    "dictionary.com", "merriam-webster.com", "vocabulary.com",
    "britannica.com", "bbc.co.uk", "reuters.com", "apnews.com",
    "nytimes.com", "wsj.com", "theguardian.com", "bloomberg.com",
}

def is_informational_by_url(url):
    from urllib.parse import urlparse
    hostname = urlparse(url).hostname or ""
    return any(hostname == d or hostname.endswith("." + d)
               for d in INFORMATIONAL_DOMAINS)
```

### Hound Scored JSON Output Structure (Phase 3 contract)
```json
[
  {
    "url": "https://acmetech.io",
    "variant": "AcmeTech",
    "title": "AcmeTech — Project Management for Teams",
    "entity_name": "AcmeTech Inc.",
    "industry": "Project Management Software",
    "factors": {
      "mark_criticality":      {"score": 3, "weight": 3, "subtotal": 9,  "evidence": "Mark is in active commercial use as primary identifier on home page"},
      "similarity":            {"score": 3, "weight": 3, "subtotal": 9,  "evidence": "AcmeTech is phonetically identical to ACME + generic suffix; logo uses same stylized A"},
      "goods_services_overlap":{"score": 3, "weight": 3, "subtotal": 9,  "evidence": "Site describes project management software targeting teams — identical to protected mark context"},
      "geography_priority":    {"score": 2, "weight": 2, "subtotal": 4,  "evidence": "US-focused pricing, .io domain with US team bios"},
      "confusion_evidence":    {"score": 0, "weight": 2, "subtotal": 0,  "evidence": "No direct confusion evidence found on page"},
      "rights_posture":        {"score": 1, "weight": 2, "subtotal": 2,  "evidence": "No ® or ™ visible; no trademark notice in footer"},
      "counterparty_profile":  {"score": 1, "weight": 1, "subtotal": 1,  "evidence": "Small startup, ~15 employees per About page"},
      "enforcement_cost":      {"score": 1, "weight": 1, "subtotal": 1,  "evidence": "Small entity, likely low enforcement cost"}
    },
    "total_score": 35,
    "risk_tier": "High"
  }
]
```

---

## State of the Art

| Old Approach | Current Approach | Impact for Phase 2 |
|--------------|------------------|--------------------|
| `.claude/commands/` as simple one-shot prompt | Multi-step command with explicit tool sequencing (Bash, WebFetch, Write in sequence) | Phase 2 requires all three tools; command instructions must explicitly direct tool use at each step |
| Manual SERP results triage | Automated safelist filter + informational exclusion before investigation | Reduces investigation load by 30–50%; only commercial, new leads reach WebFetch stage |
| Ad hoc threat notes | Structured 8-factor matrix with evidence citations, written to JSON | Produces machine-readable intermediate output that Phase 3 can consume without parsing unstructured text |

**Open item from STATE.md (resolved):**
- `context: fork` availability in current Claude Code release: irrelevant for Phase 2 — Hound runs sequentially in a single session, not in parallel sub-agents. No forking needed.

---

## Open Questions

1. **Safelist JSON format — what does Phase 3 write?**
   - What we know: Phase 2 loads `safelist-[TRADEMARK].json` as read-only. Phase 3 writes it.
   - What's unclear: The exact schema Phase 3 will use (list of URL strings vs. list of objects with `url` + `entity_name` + `date_added`).
   - Recommendation: Phase 2's safelist loading should handle both a plain list of strings AND a list of objects with a `url` key defensively (see Code Examples above). This future-proofs Phase 2 regardless of what Phase 3 decides.

2. **Intermediate scored output filename convention**
   - What we know: Phase 1 established `hound_leads-[TRADEMARK].json` as the raw SERP output filename. Phase 2 needs a scored output.
   - What's unclear: No filename was specified for the scored intermediate file in REQUIREMENTS.md (Phase 2 requirements end at HND-12 which drops Low leads; HND-13 begins the report in Phase 3).
   - Recommendation: Use `hound_scored-[TRADEMARK].json` as the scored intermediate. This follows the established `hound_*-[TRADEMARK].json` naming convention and is clearly distinct from the raw `hound_leads` file.

3. **WebFetch failure handling for lead URLs**
   - What we know: WebFetch is the only available browsing tool in Claude Code.
   - What's unclear: What should Hound do when WebFetch returns an error (404, 403, timeout, DNS failure) for a lead URL?
   - Recommendation: On WebFetch failure, log the error and skip the lead: "Could not fetch [URL]: [error]. Skipping." Do not score a lead that cannot be investigated — scoring without content would produce unsupported evidence citations, which violates the evidentiary requirement of HND-10.

---

## Validation Architecture

> `nyquist_validation` is `true` in `.planning/config.json` — this section is required.

### Test Framework

| Property | Value |
|----------|-------|
| Framework | Python stdlib `unittest` (established in Phase 1) |
| Config file | None — run directly |
| Quick run command | `python3 tests/test_phase1.py && python3 tests/test_phase2.py` |
| Full suite command | `python3 tests/test_phase1.py && python3 tests/test_phase2.py` |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| HND-01 | `trademark-hound.md` exists at correct path | smoke | `python3 tests/test_phase2.py::TestHoundCommand::test_hnd01_file_exists` | ❌ Wave 0 |
| HND-02 | Command documents safelist loading with missing-file fallback | unit | `python3 tests/test_phase2.py::TestHoundCommand::test_hnd02_safelist_load` | ❌ Wave 0 |
| HND-03 | Command documents variants file check with halt instruction | unit | `python3 tests/test_phase2.py::TestHoundCommand::test_hnd03_variants_check` | ❌ Wave 0 |
| HND-04 | Command documents template existence check and two-token substitution | unit | `python3 tests/test_phase2.py::TestHoundCommand::test_hnd04_script_generation` | ❌ Wave 0 |
| HND-05 | Command documents Bash tool execution of SERP script | unit | `python3 tests/test_phase2.py::TestHoundCommand::test_hnd05_bash_execution` | ❌ Wave 0 |
| HND-06 | Rate limiting and progress output inherited from template (already satisfied by PY-02) | unit | `python3 tests/test_phase1.py::TestHoundLeadsTemplate::test_py02_delay_seconds` | ✅ Phase 1 |
| HND-07 | Command documents safelist URL filtering step | unit | `python3 tests/test_phase2.py::TestHoundCommand::test_hnd07_safelist_filter` | ❌ Wave 0 |
| HND-08 | Command documents three-dimension investigation (commerciality, trademark usage, market overlap) | unit | `python3 tests/test_phase2.py::TestHoundCommand::test_hnd08_investigation_dimensions` | ❌ Wave 0 |
| HND-09 | Command documents informational content exclusion (Wikipedia, news, etc.) | unit | `python3 tests/test_phase2.py::TestHoundCommand::test_hnd09_informational_exclusion` | ❌ Wave 0 |
| HND-10 | Command documents all 8 scoring factors and evidence citation requirement | unit | `python3 tests/test_phase2.py::TestHoundCommand::test_hnd10_eight_factors` | ❌ Wave 0 |
| HND-11 | Command documents risk tiers: High ≥ 15, Medium 10–14, Low < 10 | unit | `python3 tests/test_phase2.py::TestHoundCommand::test_hnd11_risk_tiers` | ❌ Wave 0 |
| HND-12 | Command documents Low-lead exclusion from output | unit | `python3 tests/test_phase2.py::TestHoundCommand::test_hnd12_low_exclusion` | ❌ Wave 0 |

### Sampling Rate
- **Per task commit:** `python3 tests/test_phase2.py 2>&1 | tail -3`
- **Per wave merge:** `python3 tests/test_phase1.py && python3 tests/test_phase2.py`
- **Phase gate:** Both test suites green before `/gsd:verify-work`

### Wave 0 Gaps

- [ ] `tests/test_phase2.py` — contract tests for `.claude/commands/trademark-hound.md` covering HND-01 through HND-12; follows the same `unittest` + `assertIn` structural-check pattern as `tests/test_phase1.py`; no external dependencies

*(HND-06 / rate limiting: already covered by `test_phase1.py::test_py02_delay_seconds` — no new test needed)*

---

## Sources

### Primary (HIGH confidence)
- `/Users/woff/Trademark Hound:Cat/.planning/phases/01-trademark-cat-contracts/01-RESEARCH.md` — Claude Code commands format, Python stdlib patterns, Serper.dev API call structure, Phase 1 established patterns
- `/Users/woff/Trademark Hound:Cat/.planning/phases/01-trademark-cat-contracts/01-VERIFICATION.md` — Phase 1 artifacts confirmed working; behavioral contract verified
- `/Users/woff/Trademark Hound:Cat/.claude/commands/trademark-cat.md` — authoritative reference implementation of command file format (149 lines; all 14 tests pass)
- `/Users/woff/Trademark Hound:Cat/hound_leads_template.py` — authoritative SERP template; token format locked
- `/Users/woff/Trademark Hound:Cat/.planning/REQUIREMENTS.md` — HND-01 through HND-12 requirement definitions; 8-factor scoring matrix
- `/Users/woff/Trademark Hound:Cat/.planning/phases/01-trademark-cat-contracts/01-CONTEXT.md` — all Phase 1 locked decisions; file contract formats

### Secondary (MEDIUM confidence)
- `/Users/woff/Trademark Hound:Cat/variants-cocoa-puffs.txt` — live example of variants file format including `# Context:` line; confirms inline annotation format
- `/Users/woff/Trademark Hound:Cat/.planning/STATE.md` — accumulated project decisions; confirmed `context: fork` concern is not applicable to Phase 2

### Tertiary (LOW confidence)
- Context window capacity estimate (200K tokens for 100 leads × 2K tokens/page) — back-of-envelope from training data; should be monitored empirically during Phase 2 execution

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — same delivery format as Phase 1; all tools (Bash, WebFetch, Write) are built-in Claude Code tools with established usage
- Architecture: HIGH — pipeline steps are fully specified in REQUIREMENTS.md; intermediate file contract is a natural extension of Phase 1 naming conventions
- Pitfalls: HIGH (context window pressure, token substitution guard, goods/services context loss) — derived from direct analysis of Phase 2 requirements; MEDIUM (informational exclusion edge cases) — based on reasoning about URL pattern coverage
- Validation architecture: HIGH — same test framework and structural-check pattern as Phase 1; specific test method names are speculative until `test_phase2.py` is written in Wave 0

**Research date:** 2026-04-03
**Valid until:** 2026-05-03 (stable domain — Claude Code commands format, Python stdlib, Serper.dev API are not fast-moving)
