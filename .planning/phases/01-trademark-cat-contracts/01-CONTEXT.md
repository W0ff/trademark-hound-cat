# Phase 1: Trademark Cat + Contracts - Context

**Gathered:** 2026-04-03
**Status:** Ready for planning

<domain>
## Phase Boundary

Build the `/trademark-cat` Claude Code skill: intake a trademark + company context, generate ~100 confusion-risk variants across 5 linguistic categories, run an interactive attorney-approval feedback loop, then write `variants-[TRADEMARK].txt` and `hound_leads_template.py`. This phase settles all file contracts (variants file format, Python template structure) that Phase 2's Trademark Hound depends on. No Hound logic in this phase.

</domain>

<decisions>
## Implementation Decisions

### Variant Display Format
- Grouped list with section headers: `# Category Name (N)` — count included in each header
- Variant names only during the review loop — no inline confusion axis or rationale
- Summary line before each iteration's list: `Total: N variants | Phonetic: X | Compound: Y | Semantic: Z | Conceptual: W | Hybrid: V`
- Full list shown after every revision (not a "what changed" diff)

### Feedback & Approval UX
- Attorney gives feedback in free-form natural language — no structured command syntax to learn
- Approval gate: attorney types "approved" or "looks good" (Cat watches for approval intent)
- Cat prompts explicitly after presenting each list: explains how to give feedback OR approve
- No automatic approval — file is never written without explicit attorney sign-off

### Variants File Format (variants-[TRADEMARK].txt)
- Plain text, one variant per line
- `# Category` section headers separating the five groups
- First line: goods/services context as a plain text comment: `# Context: [goods/services description]`
- Confusion axis + rationale stored inline per variant as a comment: `Choco Puffs  # phonetic: vowel swap, sounds near-identical when spoken`
- Annotations are in the file for Hound and attorney records — NOT shown during the review loop

### Python Template (hound_leads_template.py)
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

</decisions>

<specifics>
## Specific Ideas

- Invocation example from requirements: `/trademark-cat ACME "software for project management"` — supports inline args
- Review loop feel: attorney should feel in control, like editing a list with an AI assistant, not waiting for a black box
- The five categories from requirements: (1) Phonetic & Orthographic, (2) Compound Suffix-State, (3) Semantic Synonyms, (4) Conceptual Variants, (5) Additional Phonetics/Hybrids

</specifics>

<code_context>
## Existing Code Insights

### Reusable Assets
- None — this is the first phase of a new project. All patterns established here.

### Established Patterns
- Claude Code skill delivery: `.claude/commands/[name].md` files
- File naming convention: `[type]-[TRADEMARK-lowercase].ext` (variants, hound_leads, safelist, reports)

### Integration Points
- `variants-[TRADEMARK].txt` is the contract between Cat (Phase 1) and Hound (Phase 2) — format must be stable
- `hound_leads_template.py` is consumed by Hound in Phase 2 to generate per-trademark search scripts

</code_context>

<deferred>
## Deferred Ideas

- None — discussion stayed within Phase 1 scope

</deferred>

---

*Phase: 01-trademark-cat-contracts*
*Context gathered: 2026-04-03*
