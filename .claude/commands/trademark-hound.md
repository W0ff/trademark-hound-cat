---
description: "Investigate trademark infringement leads. Runs SERP search across variants, filters against safelist, investigates each lead via WebFetch, and scores using the 8-factor weighted threat matrix. Use after /trademark-cat has generated a variants file."
---

## Intake

Parse `$ARGUMENTS` to extract:
1. The trademark name (first token or first quoted string)
2. The goods/services description (optional — second quoted string or everything after first token)

If `$ARGUMENTS` is empty or contains only a trademark name with no goods/services description, ask:

> "What goods or services does [TRADEMARK] cover? For example: 'software for project management' or 'retail clothing stores'."

Do not proceed until you have BOTH the trademark name AND a goods/services description.

Sanitize the trademark name for filenames: replace spaces with hyphens, convert to lowercase, remove any characters that are not letters, numbers, or hyphens. Store as `sanitized_name`.

---

## Step 1: Check Prerequisites (variants file)

Use the Read tool to check whether `variants-[sanitized_name].txt` exists in the current directory.

If the file does NOT exist, output exactly:
> "No variants file found for [TRADEMARK]. Please run `/trademark-cat [TRADEMARK]` first to generate the variants list."
Then stop. Do not proceed.

If it exists, read it and extract:
- The `# Context:` line (first line starting with "# Context:"): store the goods/services description as `protected_mark_context` (everything after "# Context: "). If no Context line is found, use the goods/services description provided at intake.
- The variant names: for each non-empty line, skip lines starting with "#", then strip inline annotation (everything from " #" onward). Collect the clean variant names.

Report: "Variants loaded: [N] variants for [TRADEMARK] | Context: [protected_mark_context]"

---

## Step 2: Load Safelist

Check whether `safelist-[sanitized_name].json` exists.

If it does:
  Read the file. Parse as JSON. Extract the list of safe URLs.
  Store as a set: safelist_urls = set of all URL strings in the JSON array.
  Report: "Safelist loaded: [N] entries"

If it does not exist:
  Set safelist_urls = empty set.
  Report: "No safelist found — starting fresh"

---

## Step 3: Generate or Reuse SERP Script

Check whether `hound-SERP-[sanitized_name].py` exists.

If it EXISTS:
  Report: "SERP script found: hound-SERP-[sanitized_name].py — reusing existing script."
  Proceed to Step 4.

If it does NOT exist:
  Ask the attorney:
  > "What is your Serper.dev API key? (It will be written to hound-SERP-[sanitized_name].py and should not be committed to git.)"
  Wait for the key. Do not proceed until it is provided.

  Read the file `hound_leads_template.py` from the project root using the Read tool.
  Replace the literal string `[INSERT API KEY]` with the attorney's API key.
  Replace the literal string `[INSERT VARIANTS FILE]` with `variants-[sanitized_name].txt`.
  Write the result to `hound-SERP-[sanitized_name].py` using the Write tool.

  Do NOT display the generated script content in your response.
  Report: "SERP script generated: hound-SERP-[sanitized_name].py"
  Note to attorney: "Note: hound-SERP-[sanitized_name].py contains your API key — do not commit it to git."

---

## Step 4: Run SERP Search

Execute using the Bash tool:
  python3 hound-SERP-[sanitized_name].py

This script will print progress as it runs: "[1/N] Searching: [variant]" for each variant.
With ~100 variants and 0.5s delay, expect approximately 50–60 seconds of runtime.
When complete, the script reports how many results were written to `hound_leads-[sanitized_name].json`.

If the script exits with a non-zero exit code or "ERROR" appears in output:
  Report the error message to the attorney and stop.
  Common causes: invalid API key, network timeout, variants file not found.

After successful completion, read `hound_leads-[sanitized_name].json`.
Report: "SERP search complete. [N] raw leads found across [M] variants."

---

## Step 5: Apply Safelist Filter

For each lead in the raw leads list:
  If the lead's `url` field is an exact string match for any URL in safelist_urls: discard silently.
  Otherwise: keep for investigation.

Use exact string equality only. Do not normalize URLs, strip query strings, or do subdomain matching.

Report: "[N] leads after safelist filtering ([M] leads excluded by safelist)"

---

## Step 6: Informational Content Exclusion

Before spending WebFetch calls, apply two-stage triage.

**Stage 1 — URL domain triage (no fetch needed):**
Exclude a lead without fetching if its URL contains any of these domains:
  wikipedia.org, wikimedia.org, wiktionary.org
  dictionary.com, merriam-webster.com, vocabulary.com
  bbc.co.uk, reuters.com, apnews.com, nytimes.com, wsj.com, theguardian.com, cnn.com, npr.org

Apply domain-level exclusion only. Do NOT exclude based on URL path segments like /blog/ or /article/ — a brand site may have a blog and still be a commercial competitor.

Log each excluded URL: "Excluded [URL]: known informational domain"

**Stage 2 — Content signal triage (for ambiguous URLs):**
For each remaining lead, fetch the URL using the WebFetch tool.
If the fetched content primarily shows:
  - News article structure (bylines, publication date in news format, news navigation)
  - Encyclopedia-style neutral description with no commercial intent
  - Dictionary/reference format (Definition:, Etymology:, Synonyms: sections)
→ Exclude this lead. Log: "Excluded [URL]: informational content signal"

If the content shows commercial signals (prices, Buy/Shop/Cart buttons, service descriptions, brand identity, contact forms):
→ Keep for investigation in Step 7.

Report: "[N] leads after informational exclusion ([M] excluded in Stage 1, [P] excluded in Stage 2)"

---

## Step 7: Agentic Investigation and 8-Factor Threat Scoring

Process each remaining commercial lead ONE AT A TIME. Do not batch.

For each lead, using the WebFetch content already retrieved in Step 6 (or fetch now if not yet fetched):

**Assessment (three dimensions):**

1. COMMERCIALITY — Is this a for-profit entity selling goods or services?
   Evidence: prices, Buy/Shop/Cart buttons, service descriptions, subscription offers
   If clearly non-commercial (nonprofit with no commercial arm): skip scoring. Log: "Excluded [URL]: non-commercial entity"

2. TRADEMARK USAGE — Is the searched variant used as a brand identifier (source designator)?
   Evidence: variant appears in site title, logo alt text, domain name, product name, or as the company name
   Distinguish: variant used as a brand name vs. merely mentioned in passing

3. MARKET OVERLAP — Does the entity target a similar audience to the protected mark?
   Use `protected_mark_context` (extracted in Step 1) as the comparison baseline.
   Evidence: product category, customer descriptions, pricing tier, industry language

If both COMMERCIALITY and TRADEMARK USAGE are No: exclude. Log: "Excluded [URL]: no commercial trademark usage"

**8-Factor Scoring (for leads that pass assessment):**

Score using this table. For each factor, cite specific text from the fetched page content. Do not infer — quote or paraphrase directly from the page.

| Factor | Scale | Weight |
|--------|-------|--------|
| Mark Criticality | 0–3 | ×3 |
| Similarity (sight/sound/meaning) | 0–4 | ×3 |
| Goods/Services & Channels Overlap | 0–3 | ×3 |
| Geography Priority | 0–3 | ×2 |
| Evidence of Confusion/Association | 0–2 | ×2 |
| Rights Posture (ours vs. theirs) | 0–2 | ×2 |
| Counterparty Profile | 0–2 | ×1 |
| Enforcement Cost vs. Budget | 0–2 | ×1 |

Display the score block for each lead:

```
## [Entity Name] — [URL]
Variant: [variant name]

| Factor | Score | Weight | Subtotal | Evidence |
|--------|-------|--------|----------|---------|
| Mark Criticality | [0-3] | ×3 | [n] | [one sentence from page] |
| Similarity | [0-4] | ×3 | [n] | [one sentence from page] |
| Goods/Services Overlap | [0-3] | ×3 | [n] | [one sentence from page] |
| Geography Priority | [0-3] | ×2 | [n] | [one sentence from page] |
| Confusion Evidence | [0-2] | ×2 | [n] | [one sentence from page] |
| Rights Posture | [0-2] | ×2 | [n] | [one sentence from page] |
| Counterparty Profile | [0-2] | ×1 | [n] | [one sentence from page] |
| Enforcement Cost | [0-2] | ×1 | [n] | [one sentence from page] |

**Total: [N] — [High/Medium/Low]**
```

**Risk tier assignment:**
  Total ≥ 15 → High
  Total 10–14 → Medium
  Total < 10 → Low (drop — do not write to output)

**After scoring each lead:**
- If Low (< 10): log "Dropped [URL]: Low risk (score [N])" — do not include in output file
- If Medium or High: write the lead immediately to `hound_scored-[sanitized_name].json` (append to array)
- After writing, release the fetched page content from your working memory before processing the next lead

**Writing hound_scored-[TRADEMARK].json:**
Accumulate Medium and High leads. After all leads are processed, write the complete array to `hound_scored-[sanitized_name].json` using the Write tool.

Each entry must follow this JSON structure:
```json
{
  "url": "https://...",
  "variant": "VariantName",
  "title": "Page title",
  "entity_name": "Company or entity name",
  "industry": "Industry description",
  "factors": {
    "mark_criticality": {"score": N, "weight": 3, "evidence": "..."},
    "similarity": {"score": N, "weight": 3, "evidence": "..."},
    "goods_services_overlap": {"score": N, "weight": 3, "evidence": "..."},
    "geography_priority": {"score": N, "weight": 2, "evidence": "..."},
    "confusion_evidence": {"score": N, "weight": 2, "evidence": "..."},
    "rights_posture": {"score": N, "weight": 2, "evidence": "..."},
    "counterparty_profile": {"score": N, "weight": 1, "evidence": "..."},
    "enforcement_cost": {"score": N, "weight": 1, "evidence": "..."}
  },
  "total_score": N,
  "risk_tier": "High"
}
```

Report after all leads are processed:
> "[N] leads scored — High: [X], Medium: [Y], Low: [Z] (dropped)
> Scored leads written to: hound_scored-[sanitized_name].json"

This completes the Trademark Hound investigation phase. Run `/trademark-hound` again with a reviewed report path to update the safelist (Phase 3).

---

CRITICAL: Do NOT write any report file in this command. Report generation (HOUND_REPORT_[TRADEMARK]_[DATE].md) is handled separately. This command's terminal output is hound_scored-[sanitized_name].json.
