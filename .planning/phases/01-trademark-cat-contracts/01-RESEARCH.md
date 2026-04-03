# Phase 1: Trademark Cat + Contracts - Research

**Researched:** 2026-04-03
**Domain:** Claude Code slash command skill authoring, Python SERP script templating, plain-text file contracts
**Confidence:** HIGH (core skill format and file contracts verified from official docs and prior project research)

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**Skill Delivery**
- Skill delivered as `.claude/commands/trademark-cat.md` (Claude Code slash command)

**Variant Display Format**
- Grouped list with section headers: `# Category Name (N)` — count included in each header
- Variant names only during the review loop — no inline confusion axis or rationale
- Summary line before each iteration's list: `Total: N variants | Phonetic: X | Compound: Y | Semantic: Z | Conceptual: W | Hybrid: V`
- Full list shown after every revision (not a "what changed" diff)

**Feedback & Approval UX**
- Attorney gives feedback in free-form natural language — no structured command syntax to learn
- Approval gate: attorney types "approved" or "looks good" (Cat watches for approval intent)
- Cat prompts explicitly after presenting each list: explains how to give feedback OR approve
- No automatic approval — file is never written without explicit attorney sign-off

**Variants File Format (variants-[TRADEMARK].txt)**
- Plain text, one variant per line
- `# Category` section headers separating the five groups
- First line: goods/services context as a plain text comment: `# Context: [goods/services description]`
- Confusion axis + rationale stored inline per variant as a comment: `Choco Puffs  # phonetic: vowel swap, sounds near-identical when spoken`
- Annotations are in the file for Hound and attorney records — NOT shown during the review loop

**Python Template (hound_leads_template.py)**
- Placeholder tokens exactly: `[INSERT API KEY]` and `[INSERT VARIANTS FILE]`
- Reads variants file skipping `#` comment lines
- Serper.dev exact-match search: wraps each variant in quotes `"variant"`
- Rate limiting: configurable `DELAY_SECONDS` (default 0.5s between requests)
- Progress output: prints each variant being searched to stdout
- Writes `hound_leads-[TRADEMARK].json` with fields per result: `variant`, `title`, `url`, `snippet`, `position`

### Claude's Discretion
- Exact wording of Cat's prompts and instructions to the attorney
- Number of variants per category (target ~20 per category, ~100 total — adjust if some categories are thin for a given mark)
- Whether to accept trademark + context as inline args or always prompt interactively (supporting both is fine)

### Deferred Ideas (OUT OF SCOPE)
- None — discussion stayed within Phase 1 scope
</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| CAT-01 | User can invoke `/trademark-cat` and be prompted for trademark name and company context | Slash command `$ARGUMENTS` pattern enables inline args; interactive prompt fallback is standard in command file instructions |
| CAT-02 | Trademark Cat derives a Negative Constraints (Ignore List) from company context | Implemented as LLM reasoning within the command instructions: "From the goods/services description, list industries that do not compete with this mark" |
| CAT-03 | Trademark Cat generates ~100 variants across 5 linguistic categories | Fully spec'd in CONTEXT.md: (1) Phonetic & Orthographic, (2) Compound Suffix-State, (3) Semantic Synonyms, (4) Conceptual Variants, (5) Additional Phonetics/Hybrids. ~20 per category. Self-check step required (see Pitfalls). |
| CAT-04 | Each variant annotated with confusion axis and one-sentence rationale | Stored as inline comments in the variants file (not displayed during review). Format locked: `Variant Name  # axis: rationale` |
| CAT-05 | Variants presented grouped by category for review | Locked display format: `# Category (N)` headers with summary line. Category headers with counts, names only during review. |
| CAT-06 | User can provide feedback and Cat iterates until user approves | Free-form feedback, explicit "approved" / "looks good" gate. Full list reshown after every revision. |
| CAT-07 | Approved variant list written to `variants-[TRADEMARK NAME].txt` | Format fully locked: `# Context:` first line, `# Category` section headers, one variant per line with inline `# axis: rationale` comment |
| CAT-08 | Trademark Cat confirms output file path upon completion | Simple output message after Write tool confirms file written |
| PY-01 | `hound_leads_template.py` exists with exact placeholder tokens | Locked tokens: `[INSERT API KEY]` and `[INSERT VARIANTS FILE]`. Standalone Python file at project root. |
| PY-02 | Template includes variant loading, Serper.dev search, rate limiting, progress output, JSON writing | All details locked in CONTEXT.md. `DELAY_SECONDS = 0.5` default, exact-match quoting, print-per-variant progress. |
| PY-03 | Generated JSON stores: `variant`, `title`, `url`, `snippet`, `position` | Exact field names locked. File named `hound_leads-[TRADEMARK].json`. |
</phase_requirements>

---

## Summary

Phase 1 delivers two artifacts: (1) a `.claude/commands/trademark-cat.md` slash command that Claude Code users invoke as `/trademark-cat`, and (2) a standalone `hound_leads_template.py` Python file in the project root. All format contracts for both artifacts are locked in CONTEXT.md — this research's job is to surface implementation mechanics and pitfalls, not re-litigate decisions.

The slash command is a Markdown file with optional YAML frontmatter. The body contains natural-language instructions that Claude follows when the command is invoked. Claude reads `$ARGUMENTS` to accept the trademark and context inline; if absent, it prompts interactively. The variant generation and approval loop are implemented entirely as instruction prose — no separate script files are needed for Cat in this phase. The Write tool is the only file-system tool Cat requires.

The Python template is a standalone script, not a Claude Code skill component. It is written directly to the project root during this phase as a static file. Phase 2 (Hound) will read this template and instantiate it per trademark. The template is purely a contract artifact in Phase 1 — it does not need to be executed during this phase, though it should be verifiable by running `python3 -c "import ast; ast.parse(open('hound_leads_template.py').read())"`.

**Primary recommendation:** Implement Cat as a single `.claude/commands/trademark-cat.md` command file. Implement the Python template as a static file at project root. Keep the command file focused and human-readable — it is the system prompt Claude follows verbatim.

---

## Critical Format Discrepancy: Commands vs. Skills

**This must be resolved before planning begins.**

CONTEXT.md locks delivery to `.claude/commands/trademark-cat.md`. Prior project research (STACK.md) states `.claude/skills/` supersedes `.claude/commands/` as of 2025 and supports frontmatter and supporting files. These are two different Claude Code delivery formats.

**Resolution:** Honor the CONTEXT.md locked decision. Use `.claude/commands/trademark-cat.md`. The commands format works for Trademark Cat because:
- Cat requires no supporting files in Phase 1 — just instructions and Write tool
- The commands format still supports `$ARGUMENTS` substitution
- Phase 2 research can revisit the format for Hound if skills format provides needed capabilities

The planner should create the command at `.claude/commands/trademark-cat.md`, not `.claude/skills/trademark-cat/SKILL.md`.

---

## Standard Stack

### Core

| Library / Format | Version | Purpose | Why Standard |
|-----------------|---------|---------|--------------|
| `.claude/commands/[name].md` | current | Claude Code slash command delivery | Locked decision; user's stated format |
| Python 3 | 3.13 (system) | `hound_leads_template.py` | Already installed; no setup needed |
| `requests` | `>=2.28` | Serper.dev HTTP calls in template | Best for synchronous one-shot API scripts; no async overhead |
| `json` | stdlib | JSON output serialization | Zero dependencies; `json.dumps(indent=2)` for human-readable output |
| `time` | stdlib | `time.sleep(DELAY_SECONDS)` rate limiting | No install; sufficient for configurable delay |
| Plain text (`.txt`) | — | `variants-[TRADEMARK].txt` file contract | Locked format; human-readable; no parsing library needed |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `pathlib` | stdlib | File path operations in template | Use `Path(VARIANTS_FILE).read_text()` over `open()` for cross-OS safety |
| `sys` | stdlib | Exit codes, error messages to stderr | `sys.stderr.write()` for errors; `sys.exit(1)` on failure |
| `re` | stdlib | Skip `#` comment lines in variants file | `line.strip().startswith('#')` is sufficient; re not strictly needed |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| `.claude/commands/` | `.claude/skills/` | Skills format offers frontmatter and supporting file bundling; commands format simpler for single-file instructions. Locked to commands for Phase 1. |
| `requests` | `httpx` | httpx async advantage is irrelevant for a sequential-per-variant script; requests is simpler |
| `time.sleep` | `asyncio.sleep` | asyncio adds complexity; template is synchronous by design |

**Installation:**
```bash
# One-time, only if requests is not already installed
pip3 install requests

# Verify Python syntax of template (no execution needed in Phase 1)
python3 -c "import ast; ast.parse(open('hound_leads_template.py').read())"
```

---

## Architecture Patterns

### File Layout

```
[project root]/
├── .claude/
│   └── commands/
│       └── trademark-cat.md      # Slash command: /trademark-cat
└── hound_leads_template.py       # Python template (project root, static file)

[workspace — where attorney invokes /trademark-cat]/
└── variants-[TRADEMARK].txt      # Written by Cat after attorney approval
```

Note: `hound_leads_template.py` lives at the project root, not inside `.claude/`. It is a workspace file, not a skill component. Phase 2 Hound will read it and instantiate per-trademark scripts.

### Pattern 1: Claude Code Command File Structure

**What:** A Markdown file at `.claude/commands/[name].md` that Claude Code registers as `/[name]`. When invoked, Claude reads the file as a system prompt and follows the instructions.

**`$ARGUMENTS` substitution:** Everything typed after `/trademark-cat` on the invocation line is substituted for `$ARGUMENTS` in the command body. Example: `/trademark-cat ACME "software for project management"` → `$ARGUMENTS` becomes `ACME "software for project management"`.

**Dual-mode intake pattern (inline args + interactive fallback):**
```markdown
## Intake

The attorney may invoke this command with inline arguments:
`/trademark-cat TRADEMARK "goods/services description"`

Parse `$ARGUMENTS` to extract:
1. The trademark name (first token)
2. The goods/services description (quoted string, or everything after the first token)

If `$ARGUMENTS` is empty or only contains the trademark name without a goods/services description,
ask the attorney: "What goods or services does [TRADEMARK] cover? (e.g., 'software for project management')"

Do not proceed until you have both the trademark name and a goods/services description.
```

### Pattern 2: Variant Generation with Self-Check

**What:** The command instructs Claude to generate variants across all 5 categories, then validate the output before presenting it to the attorney.

**Self-check pattern:**
```markdown
## Variant Generation

Generate ~100 variants across these 5 categories (target ~20 per category):
1. Phonetic & Orthographic — sound-alike spellings, vowel swaps, consonant substitutions
2. Compound Suffix-State — adding/removing common suffixes (-Tech, -Corp, -Pro, -Hub, -AI)
3. Semantic Synonyms — words with equivalent meaning to the mark
4. Conceptual Variants — related concepts, translated meanings, associated ideas
5. Additional Phonetics/Hybrids — cross-category hybrids, phonetic transliterations

After generating, count the variants per category. If any category has fewer than 15 variants,
generate additional variants for that category before presenting.
```

**Why self-check matters:** Without it, variant count drifts across runs (see Pitfall 1 in prior research). The self-check step prevents the attorney from approving an undersized set.

### Pattern 3: Interactive Approval Loop

**What:** Cat presents variants, prompts explicitly, waits for feedback or approval signal, revises if feedback given, re-presents full list.

**Loop structure in command instructions:**
```markdown
## Presentation and Approval Loop

Present the variants using this exact format:

---
Total: [N] variants | Phonetic: [X] | Compound: [Y] | Semantic: [Z] | Conceptual: [W] | Hybrid: [V]

# Phonetic & Orthographic ([X])
[variant 1]
[variant 2]
...

# Compound Suffix-State ([Y])
...
---

After presenting, tell the attorney:
"Review this list. To give feedback (add, remove, rebalance categories), just describe what you'd like changed.
To approve and write the variants file, say 'approved' or 'looks good'."

Watch for approval intent: "approved", "looks good", "that's fine", "go ahead", "yes", "perfect", etc.
Watch for feedback: any instruction that implies adding, removing, or changing variants.

If feedback is given: revise the list and present the full revised list again. Repeat.
If approval is detected: proceed to write the file. Do NOT write the file before approval.
```

### Pattern 4: Variants File Write

**What:** After approval, Cat constructs the file content with annotations (not shown during review) and writes it using the Write tool.

**File construction logic:**
```markdown
## Writing the Variants File

After attorney approves, construct `variants-[TRADEMARK].txt` as follows:

Line 1: # Context: [goods/services description as given by attorney]
Then for each category, write:
  # [Category Name]
  [variant name]  # [confusion axis]: [one-sentence rationale]
  ...

Example:
# Context: software for project management
# Phonetic & Orthographic
Ackme  # phonetic: vowel shift; sounds near-identical when spoken aloud
A.C.M.E  # orthographic: punctuation insertion; visually distinct but phonetically identical
...

Write the file to the current working directory as: variants-[TRADEMARK-lowercase].txt
After writing, confirm: "Variants file written to: variants-[trademark].txt ([N] variants across 5 categories)"
```

Note: Per CONTEXT.md, the `# axis: rationale` annotations are written to file but NOT shown to the attorney during the review loop. They are for Hound and records.

### Pattern 5: Python Template Structure

**What:** A static Python script with two exact placeholder tokens. Phase 2 Hound will copy and substitute them.

**Template skeleton:**
```python
#!/usr/bin/env python3
"""
hound_leads_template.py — Serper.dev search template for Trademark Hound
Placeholders substituted by /trademark-hound at run time:
  [INSERT API KEY]      → Serper.dev API key
  [INSERT VARIANTS FILE] → path to variants-[TRADEMARK].txt
"""
import json
import time
import sys
import requests

API_KEY = "[INSERT API KEY]"
VARIANTS_FILE = "[INSERT VARIANTS FILE]"
DELAY_SECONDS = 0.5  # configurable: seconds between Serper.dev requests

def load_variants(path):
    """Read variants file, skip # comment lines and blank lines."""
    variants = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            stripped = line.strip()
            if stripped and not stripped.startswith("#"):
                # Strip inline comment (everything after the first #)
                variant_name = stripped.split("#")[0].strip()
                if variant_name:
                    variants.append(variant_name)
    return variants

def search_variant(variant, api_key):
    """Run exact-match Serper.dev search for a single variant."""
    url = "https://google.serper.dev/search"
    headers = {
        "X-API-KEY": api_key,
        "Content-Type": "application/json",
    }
    payload = {"q": f'"{variant}"', "num": 10}
    response = requests.post(url, headers=headers, json=payload, timeout=15)
    response.raise_for_status()
    return response.json().get("organic", [])

def main():
    variants = load_variants(VARIANTS_FILE)
    total = len(variants)
    all_results = []

    for i, variant in enumerate(variants, 1):
        print(f"[{i}/{total}] Searching: {variant}", flush=True)
        try:
            results = search_variant(variant, API_KEY)
            for r in results:
                all_results.append({
                    "variant": variant,
                    "title": r.get("title", ""),
                    "url": r.get("link", ""),
                    "snippet": r.get("snippet", ""),
                    "position": r.get("position", 0),
                })
        except requests.HTTPError as e:
            print(f"  ERROR: {e}", file=sys.stderr, flush=True)
        if i < total:
            time.sleep(DELAY_SECONDS)

    # Derive output filename from variants file path
    import os
    base = os.path.splitext(os.path.basename(VARIANTS_FILE))[0]
    trademark = base.replace("variants-", "")
    output_file = f"hound_leads-{trademark}.json"

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)

    print(f"\nDone. {len(all_results)} results written to {output_file}", flush=True)

if __name__ == "__main__":
    main()
```

**Key implementation notes for the template:**
- Inline comments stripped from each line before treating as variant name: `variant_name = stripped.split("#")[0].strip()`
- Exact-match quoting: each variant wrapped in double quotes in the query: `f'"{variant}"'`
- Output filename derived from input variants file: `variants-ACME.txt` → `hound_leads-ACME.json`
- JSON fields exactly as locked: `variant`, `title`, `url`, `snippet`, `position`
- `url` maps from Serper's `link` field (Serper uses `link`, not `url`)
- Print flush=True on progress lines so output appears immediately (not buffered)

### Anti-Patterns to Avoid

- **Showing annotations during the review loop:** The `# axis: rationale` comment is for the file only. During review, show variant names only, grouped under category headers. Never show the annotation to the attorney during iteration.
- **Writing the file before explicit approval:** The approval gate is non-negotiable. Cat must positively detect approval intent. Absence of feedback is not approval.
- **Inline API key in the Python template:** `[INSERT API KEY]` stays as a literal placeholder string in the template. Hound substitutes it at script-generation time. The template itself is committed to the repo and must contain no real credentials.
- **Storing `hound_leads_template.py` inside `.claude/`:** It is a workspace contract file, not a skill component. It lives at project root.
- **Using `.split("#")[0]` on lines with URLs:** This pattern is safe for the variants file format because URLs appear only inside `# comment` sections and never as standalone line content. All standalone lines are variant names.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Comment stripping from variants file | Custom parser | `line.split("#")[0].strip()` — one line | The format is trivially simple: variant name, optional `# comment`. No parser needed. |
| Approval detection in feedback loop | Keyword matcher or structured command | Claude's natural language comprehension | Cat instructions tell Claude to watch for approval intent. No code needed — this is an LLM task. |
| HTTP requests to Serper.dev | urllib raw calls | `requests.post()` with `raise_for_status()` | Requests handles auth headers, JSON encoding, timeout, and error surfaces cleanly in 5 lines. |
| Rate limiting | Token bucket or leaky bucket algorithm | `time.sleep(DELAY_SECONDS)` | Simple sleep is sufficient for a sequential CLI script. No concurrency means no need for a rate limiter. |
| Output filename derivation | Config file or argument | `base.replace("variants-", "")` string operation | The file naming convention `variants-[TM].txt` → `hound_leads-[TM].json` is deterministic. |

**Key insight:** Phase 1 contains no algorithmic complexity. All complexity is linguistic (variant generation quality) and instructional (how precisely Cat's command file guides Claude's behavior). The implementation decisions are about prompt engineering, not code design.

---

## Common Pitfalls

### Pitfall 1: Variant Count Drift Across Runs
**What goes wrong:** `/trademark-cat ACME "software"` generates 103 variants one session and 61 the next because the prompt says "about 100."
**Why it happens:** LLMs treat approximate counts as guidelines unless a validation gate exists.
**How to avoid:** Specify exact target counts per category (20 per category = 100 total). Add a self-check instruction: "Count variants per category. If any category has fewer than 15, generate more before presenting."
**Warning signs:** Variants files vary significantly in line count between runs on the same mark.

### Pitfall 2: Annotation Comments Leaking into Review Display
**What goes wrong:** The attorney sees `ACME-Soft  # phonetic: consonant swap` during the review loop instead of just `ACME-Soft`.
**Why it happens:** The command instructions conflate the display format (names only) with the file format (names + comments). If instructions are ambiguous, Claude includes the comments.
**How to avoid:** State explicitly in the command instructions: "During the review loop, display variant names ONLY — no comments or rationale. Comments are written to the file only."

### Pitfall 3: Approval Gate Bypassed by Ambiguous Response
**What goes wrong:** Attorney types "fine, continue" or "whatever" and Cat writes the file, but the attorney was expressing mild satisfaction, not giving explicit approval.
**Why it happens:** The approval detection instructions are too broad ("watch for positive responses").
**How to avoid:** Require explicit approval signals. Instruct Cat: "Only write the file when the attorney uses an explicit approval phrase. If unsure, ask: 'Just to confirm — shall I write the approved variants file?'"

### Pitfall 4: Trademark Name Used Raw in Filename
**What goes wrong:** Attorney invokes `/trademark-cat "OMEGA 3" "nutritional supplements"` and Cat tries to write `variants-OMEGA 3.txt` — filename with a space.
**Why it happens:** The trademark name is used directly in the filename without sanitization.
**How to avoid:** In the command instructions, specify: "Sanitize the trademark name for use in filenames: replace spaces with hyphens, remove any characters that are not letters, numbers, or hyphens. Use the sanitized name for all filenames."

### Pitfall 5: Template Placeholder Tokens Partially Substituted
**What goes wrong:** In Phase 2, Hound generates a script from the template but only substitutes `[INSERT API KEY]`, leaving `[INSERT VARIANTS FILE]` as a literal string in the executed script.
**Why it happens:** The placeholder tokens are long strings; easy to miss one in string substitution. Also easy for someone editing the template to accidentally change the token text.
**How to avoid:** The exact token strings are locked (`[INSERT API KEY]` and `[INSERT VARIANTS FILE]`). Document them clearly in the template's docstring. In Phase 1, verify both tokens appear in the written file using a simple grep check.

### Pitfall 6: Inline Comment Split Breaks on Variant Names Containing `#`
**What goes wrong:** A variant like `C#Sharp` (using `#` as part of the name) gets truncated to `C` by the comment-stripping logic.
**Why it happens:** `line.split("#")[0]` treats any `#` in the variant name as a comment start.
**How to avoid:** Variant names should not contain `#`. Instruct Cat: "Variant names may only contain letters, numbers, hyphens, spaces, and common punctuation. Do not use `#` in variant names."

---

## Code Examples

Verified patterns from official/locked sources:

### Variants File Format (locked in CONTEXT.md)
```text
# Context: software for project management
# Phonetic & Orthographic
Ackme  # phonetic: vowel shift; sounds near-identical when spoken aloud
A.C.M.E  # orthographic: punctuation insertion; identical phonetically
...
# Compound Suffix-State
AcmeTech  # compound: common tech-industry suffix
AcmeHub  # compound: common platform suffix
...
```

### Comment Line Skipping in Python Template
```python
# Strips both pure comment lines AND inline variant comments
for line in f:
    stripped = line.strip()
    if stripped and not stripped.startswith("#"):
        variant_name = stripped.split("#")[0].strip()
        if variant_name:
            variants.append(variant_name)
```

### Exact-Match Serper.dev Query
```python
# Wraps variant in quotes for exact-match search
payload = {"q": f'"{variant}"', "num": 10}
response = requests.post(
    "https://google.serper.dev/search",
    headers={"X-API-KEY": api_key, "Content-Type": "application/json"},
    json=payload,
    timeout=15
)
response.raise_for_status()
results = response.json().get("organic", [])
```

### JSON Output Record Structure (locked field names)
```python
all_results.append({
    "variant": variant,        # the search term used
    "title": r.get("title", ""),
    "url": r.get("link", ""),  # Serper returns "link", we store as "url"
    "snippet": r.get("snippet", ""),
    "position": r.get("position", 0),
})
```

### Progress Output (flush required)
```python
print(f"[{i}/{total}] Searching: {variant}", flush=True)
```

### Command File Frontmatter Pattern
```yaml
---
description: Generate ~100 confusion-risk trademark variants for attorney review. Use when: preparing a trademark monitoring search, need to generate a reviewed variants file for /trademark-hound.
---
```

Note: The `commands` format supports optional frontmatter with `description`. This controls what appears when the attorney runs `/help` or browses available commands. The `allowed-tools` and `disable-model-invocation` frontmatter fields are properties of the `skills` format, not the `commands` format.

---

## State of the Art

| Old Approach | Current Approach | Impact for Phase 1 |
|--------------|------------------|--------------------|
| `.claude/commands/` only delivery | `.claude/skills/` with frontmatter + supporting files | Phase 1 uses `commands/` per locked decision. Skills format is available for Phase 2 if Hound needs bundled scripts. |
| Hardcoded delay in SERP scripts | Configurable `DELAY_SECONDS` constant | Template uses `DELAY_SECONDS = 0.5` at top of file so Phase 2 can expose this as a parameter |
| Serper.dev `link` field | Universally called `url` in consuming code | The mapping `r.get("link", "")` → stored as `"url"` is deliberate to normalize the field name for downstream consumers |

**Key open question from STATE.md (resolved for Phase 1):**
- Goods/services context propagation format: locked as plain text `# Context: [description]` on line 1 of variants file. Not JSON frontmatter. Phase 1 establishes this as the contract.
- Serper.dev QPS cap: 0.5s delay is conservative and correct for Phase 1. Phase 2 should verify current tier limits at implementation time.

---

## Validation Architecture

> `nyquist_validation` is `true` in `.planning/config.json` — this section is required.

### Test Framework

| Property | Value |
|----------|-------|
| Framework | None detected — this is a new project with no existing test infrastructure |
| Config file | None — see Wave 0 |
| Quick run command | `python3 -c "import ast; ast.parse(open('hound_leads_template.py').read()); print('OK')"` |
| Full suite command | `python3 tests/test_phase1.py` (Wave 0 gap) |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| CAT-01 | Command file exists at correct path and registers as `/trademark-cat` | smoke | `test -f .claude/commands/trademark-cat.md && echo PASS` | ❌ Wave 0 |
| CAT-02 | Negative constraints section present in command instructions | unit | `grep -q "Negative Constraints" .claude/commands/trademark-cat.md && echo PASS` | ❌ Wave 0 |
| CAT-03 | All 5 category names present in command instructions | unit | `grep -c "Phonetic\|Compound\|Semantic\|Conceptual\|Hybrid" .claude/commands/trademark-cat.md` | ❌ Wave 0 |
| CAT-04 | Annotation comment format documented in command instructions | unit | `grep -q "confusion axis" .claude/commands/trademark-cat.md && echo PASS` | ❌ Wave 0 |
| CAT-05 | Display format (category headers + summary line) documented in command | unit | `grep -q "Total:" .claude/commands/trademark-cat.md && echo PASS` | ❌ Wave 0 |
| CAT-06 | Approval gate language present in command instructions | unit | `grep -qi "approved\|looks good" .claude/commands/trademark-cat.md && echo PASS` | ❌ Wave 0 |
| CAT-07 | Variants file format documented in command (Context header + Category headers) | unit | `grep -q "# Context:" .claude/commands/trademark-cat.md && echo PASS` | ❌ Wave 0 |
| CAT-08 | File path confirmation documented in command instructions | unit | `grep -q "confirm\|written to" .claude/commands/trademark-cat.md && echo PASS` | ❌ Wave 0 |
| PY-01 | Template file exists and contains both placeholder tokens | unit | `python3 tests/test_template.py::test_placeholders` | ❌ Wave 0 |
| PY-02 | Template includes rate limiting (DELAY_SECONDS) and progress print | unit | `python3 tests/test_template.py::test_rate_limit_and_progress` | ❌ Wave 0 |
| PY-03 | Template output JSON has all 5 required fields | unit | `python3 tests/test_template.py::test_output_fields` | ❌ Wave 0 |

### Sampling Rate
- **Per task commit:** `python3 -c "import ast; ast.parse(open('hound_leads_template.py').read()); print('Template syntax OK')"` + file existence checks
- **Per wave merge:** `python3 tests/test_phase1.py` (full suite)
- **Phase gate:** All tests green before `/gsd:verify-work`

### Wave 0 Gaps

- [ ] `tests/test_phase1.py` — test runner covering PY-01, PY-02, PY-03 with mock HTTP (no real Serper key needed)
- [ ] `tests/test_template.py` — unit tests: placeholder token presence, `load_variants()` comment-stripping behavior, output field names
- [ ] No framework install needed — stdlib `unittest` is sufficient; no pytest or external test runner required

**Note on CAT-* tests:** Most CAT-* validations are structural checks on the command file itself (presence of specific text). These run in under 1 second using shell grep or Python `in` checks. They verify the contract is documented, not that Claude executes it correctly (which requires human validation during acceptance testing).

---

## Sources

### Primary (HIGH confidence)
- `.planning/research/STACK.md` — Claude Code commands/skills format, Python patterns, Serper.dev API call structure (verified 2026-04-03 from official Claude Code docs)
- `.planning/research/ARCHITECTURE.md` — file-contract hand-off pattern, project structure (verified 2026-04-03)
- `.planning/phases/01-trademark-cat-contracts/01-CONTEXT.md` — all locked format decisions (authoritative: user decisions)
- `.planning/REQUIREMENTS.md` — CAT-01 through PY-03 requirement definitions

### Secondary (MEDIUM confidence)
- `.planning/research/PITFALLS.md` — variant count drift, annotation display leak, approval gate patterns (verified against prior research)
- `.planning/research/FEATURES.md` — feature completeness analysis, anti-features
- Serper.dev API: `https://google.serper.dev/search` endpoint, `X-API-KEY` header, `organic[].link` field (MEDIUM — community-verified pattern, consistent across multiple sources in prior research)

### Tertiary (LOW confidence)
- Claude Code `commands/` frontmatter `description` field — observed pattern; not explicitly verified against current official docs for the `commands/` (non-skills) format specifically

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — Python stdlib patterns are trivially verifiable; format decisions are locked
- Architecture: HIGH — Two-artifact structure (command file + Python template) is unambiguous from requirements
- Pitfalls: HIGH (critical ones) / MEDIUM (edge cases like trademark names with `#`) — from prior verified research
- Validation architecture: MEDIUM — test structure is straightforward; specific test commands rely on file paths not yet created

**Research date:** 2026-04-03
**Valid until:** 2026-05-03 (stable domain — Claude Code commands format and Python stdlib are not fast-moving)
