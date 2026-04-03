---
description: Generate ~100 confusion-risk trademark variants for attorney review. Use when preparing a trademark monitoring search or generating a variants file for /trademark-hound.
---

## Intake

Parse `$ARGUMENTS` to extract:
1. The trademark name (first token or first quoted string)
2. The goods/services description (second quoted string, or everything after the first token)

If `$ARGUMENTS` is empty or contains only a trademark name with no goods/services description, ask:

> "What goods or services does [TRADEMARK] cover? For example: 'software for project management' or 'retail clothing stores'."

Do not proceed until you have BOTH the trademark name AND a goods/services description.

Sanitize the trademark name for use in filenames: replace spaces with hyphens, convert to lowercase, remove any characters that are not letters, numbers, or hyphens. Store this as `sanitized_name` for all file output. Example: "OMEGA 3" → "omega-3", "Coca-Cola" → "coca-cola".

---

## Negative Constraints

From the goods/services description, derive a Negative Constraints (Ignore List): a list of non-competing industries that should be excluded from confusion analysis. For example, for "Delta" in "airlines," exclude dental, plumbing, carpentry, and financial services.

State these constraints clearly to yourself — do not present them to the attorney — before generating variants. Use them to filter out irrelevant semantic synonyms and conceptual variants that would not cause consumer confusion in the relevant market.

---

## Variant Generation

Generate ~100 variants across these 5 categories, targeting approximately 20 per category:

**Category 1 — Phonetic & Orthographic**
Sound-alike spellings, vowel swaps, consonant substitutions, homophones, alternate spellings, and letter transpositions.
Examples for ACME: Ackme, Akme, ACMEE, Aqme, Ackmee, Acmy, Axme

**Category 2 — Compound Suffix-State**
Adding or removing common suffixes (-Tech, -Corp, -Pro, -Hub, -AI, -Labs, -Soft, -Co, -Group, -Solutions, -Systems, -Digital, -Net, -Works) and geographic or state-based combinations.
Examples for ACME: AcmeTech, AcmeCorp, AcmePro, AcmeHub, AcmeAI, AcmeLabs, AcmeSoft, AcmeCo, AcmeGroup

**Category 3 — Semantic Synonyms**
Words with equivalent or near-equivalent meaning to the trademark. Apply the Negative Constraints here — exclude synonyms from non-competing industries.
Examples for ACME: Apex, Summit, Pinnacle, Zenith, Peak, Crest, Vertex, Crown

**Category 4 — Conceptual Variants**
Related concepts, translated meanings, associated ideas, and category associations that a consumer might confuse with the original mark.
Apply Negative Constraints here as well.
Examples for ACME: Topmost, Paramount, Premier, Optimal, Ultimate, MaxPoint

**Category 5 — Additional Phonetics/Hybrids**
Cross-category hybrids, phonetic transliterations, stylistic variations that combine approaches from multiple categories (e.g., phonetic + suffix, semantic + spelling variation).
Examples for ACME: Akme-Pro, Akmax, Acmax, Aqume, A.C.M.E., Acmex

---

After generating all variants, COUNT the variants per category. If any category has fewer than 15 variants, generate additional variants for that category before proceeding. Do not present the list until all 5 categories have at least 15 variants.

**Variant name rules:**
- Variant names MUST NOT contain the `#` character
- Variant names may only contain letters, numbers, hyphens, spaces, and common punctuation (periods, apostrophes, ampersands)
- Each variant should be distinct from every other variant in the list

**Internal annotations (not shown during review):**
For each variant, internally record:
- The confusion axis: one of `phonetic`, `visual`, `conceptual`, or `compound`
- A one-sentence rationale (e.g., "vowel swap; sounds near-identical when spoken aloud")

These annotations are NOT shown during the review loop. They are written to the variants file only after approval.

---

## Presentation and Approval Loop

Present the variants using EXACTLY this format:

```
---
Total: [N] variants | Phonetic: [X] | Compound: [Y] | Semantic: [Z] | Conceptual: [W] | Hybrid: [V]

# Phonetic & Orthographic ([X])
[variant 1]
[variant 2]
...

# Compound Suffix-State ([Y])
[variant 1]
...

# Semantic Synonyms ([Z])
...

# Conceptual Variants ([W])
...

# Additional Phonetics/Hybrids ([V])
...
---
```

Show variant NAMES ONLY in the list — no comments, no annotations, no rationale inline. The `# Category (N)` headers are shown; confusion axis annotations are NOT shown during review.

After presenting the list, tell the attorney:

> "Review this list. To give feedback — add variants, remove variants, rebalance categories, or anything else — just describe what you'd like changed in plain language. To approve and write the variants file, say 'approved' or 'looks good'."

**Watch for feedback intent:** Any instruction implying adding, removing, renaming, or rebalancing variants — "add more phonetics," "remove the ones with -Corp," "I want more food synonyms," "that category is thin," etc. If feedback is given:
1. Revise the list accordingly, maintaining the minimum 15 per category rule
2. Present the FULL revised list again from the top using the same format
3. Do not show a diff or partial list — always show the complete current list

**Watch for approval intent:** "approved," "looks good," "that's fine," "go ahead," "yes," "perfect," "ship it," or equivalent affirmation. If there is ANY ambiguity about whether the attorney is approving or giving feedback, ask:

> "Just to confirm — shall I write the approved variants file now?"

Do NOT write the file until approval is explicit. Repeat this loop until explicit approval is received.

---

## Writing the Variants File

After explicit attorney approval, construct the variants file content as follows.

**Line 1:** `# Context: [goods/services description exactly as given by attorney]`

Then for each category, write:
```
# [Category Name]
[variant name]  # [confusion axis]: [one-sentence rationale]
```

Full example:
```
# Context: software for project management
# Phonetic & Orthographic
Ackme  # phonetic: vowel shift; sounds near-identical when spoken aloud
A.C.M.E  # orthographic: punctuation insertion; phonetically identical
Acmee  # phonetic: doubled vowel; near-identical pronunciation
# Compound Suffix-State
AcmeTech  # compound: generic tech suffix; common in software branding
AcmePro  # compound: professional tier suffix; strong association with B2B software
```

Write the file to the current working directory as: `variants-[sanitized_name].txt`

Use the Write tool to create the file. After the Write tool confirms success, output exactly:

> "Variants file written to: variants-[sanitized_name].txt ([N] variants across 5 categories)"

Do not write the file before explicit approval. Do not write the file more than once per invocation.
