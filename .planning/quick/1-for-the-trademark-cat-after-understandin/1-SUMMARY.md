---
phase: quick
plan: 1
subsystem: trademark-cat
tags: [variant-generation, attorney-ux, confirmation-step]
key-files:
  modified:
    - .claude/commands/trademark-cat.md
decisions:
  - "Default variant count set to 100; attorney may override at runtime before generation begins"
  - "Minimum-per-category threshold made dynamic: floor(confirmed_variant_count / 5 * 0.75)"
metrics:
  duration: "< 5 minutes"
  completed: "2026-04-05"
  tasks: 1
  files_modified: 1
---

# Quick Task 1: Variant Count Confirmation Step — Summary

**One-liner:** Attorney-confirmed variant count prompt inserted between Negative Constraints and Variant Generation, replacing all hard-coded ~100 references with `confirmed_variant_count`.

## What Was Changed

### File: `.claude/commands/trademark-cat.md`

**New section inserted (lines 82–95):** `## Variant Count Confirmation`

The section fires after Negative Constraints derivation and before Variant Generation. It prompts the attorney with a single message offering the default of 100 variants (~20 per category) or any custom number. Response parsing handles plain integers, "default", non-numeric affirmations, and ambiguous replies (one clarifying follow-up allowed). The resolved value is stored as `confirmed_variant_count`.

**Exact line range of new section:** lines 82–95

**Variant Generation section updates (same file):**

| Original (hard-coded) | Updated (dynamic) |
|---|---|
| `Generate ~100 variants across these 5 categories, targeting approximately 20 per category:` | `Generate \`confirmed_variant_count\` variants across these 5 categories, targeting approximately \`confirmed_variant_count / 5\` per category (round to nearest integer):` |
| `If any category has fewer than 15 variants, generate additional variants for that category before proceeding.` | `If any category has fewer than \`floor(confirmed_variant_count / 5 * 0.75)\` variants, generate additional variants for that category before proceeding. (For the default of 100, this threshold is 15.)` |
| `Total: [N] variants` header description (implicit static N) | Added note: `(N should equal confirmed_variant_count)` |

## Verification Results

- `grep -c "confirmed_variant_count"` → **6** (threshold: >= 4) — PASS
- `grep "~100"` in Variant Generation section → **0** (only appears in frontmatter description, not as an instruction) — PASS
- Section order: Intake → Negative Constraints → **Variant Count Confirmation** → Variant Generation → Presentation and Approval Loop → Writing the Variants File — PASS

## Deviations from Plan

None — plan executed exactly as written.

## Self-Check: PASSED

- `.claude/commands/trademark-cat.md` modified and committed (e7ad54f)
- New section present at line 82
- `confirmed_variant_count` appears 6 times (set once, referenced in generation target, threshold formula, threshold example, presentation note, and generation count line)
