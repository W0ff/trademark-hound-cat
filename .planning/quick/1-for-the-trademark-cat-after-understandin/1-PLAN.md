---
phase: quick
plan: 1
type: execute
wave: 1
depends_on: []
files_modified:
  - .claude/commands/trademark-cat.md
autonomous: true
requirements: []
must_haves:
  truths:
    - "After intake and context are gathered, the agent asks the attorney how many variants to generate before generating any"
    - "The attorney can accept the default (100) or specify a different number"
    - "All downstream variant generation uses the attorney-confirmed count, not the hard-coded ~100"
  artifacts:
    - path: ".claude/commands/trademark-cat.md"
      provides: "Updated trademark-cat command with variant count confirmation step"
  key_links:
    - from: "Intake / context file"
      to: "Variant Generation section"
      via: "New check-in step that sets confirmed_variant_count"
---

<objective>
Add a user check-in step to trademark-cat.md that fires after the mark context is confirmed and before variant generation begins. The agent should ask the attorney whether they want the default ~100 variants or a different number. The confirmed count then drives the per-category targets for the entire generation run.

Purpose: Attorneys working on high-stakes marks may want more variants; for quick triage searches they may want fewer. The agent currently hard-codes ~100 with no way to adjust except after-the-fact feedback.
Output: Updated .claude/commands/trademark-cat.md with a variant count confirmation prompt inserted between the Negative Constraints derivation and the Variant Generation section.
</objective>

<execution_context>
@/Users/woff/.claude/get-shit-done/workflows/execute-plan.md
@/Users/woff/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/PROJECT.md
@.planning/STATE.md
@.claude/commands/trademark-cat.md
</context>

<tasks>

<task type="auto">
  <name>Task 1: Insert variant count confirmation step into trademark-cat.md</name>
  <files>.claude/commands/trademark-cat.md</files>
  <action>
Read the full current content of `.claude/commands/trademark-cat.md`.

Insert a new section titled `## Variant Count Confirmation` between the `## Negative Constraints` section and the `## Variant Generation` section. The section should read as follows (use this exact wording):

---

## Variant Count Confirmation

After deriving negative constraints, ask the attorney:

> "How many variants would you like generated? The default is **100** (approximately 20 per category). You can specify any number — for example, '50' for a lighter search or '150' for broader coverage. Just reply with a number or press Enter / say 'default' to use 100."

Wait for a response. Parse the response:
- If the attorney replies with a plain integer (e.g. "75", "150"), set `confirmed_variant_count` to that integer.
- If the attorney replies "default", presses Enter, or gives any non-numeric affirmation (e.g. "100 is fine", "go ahead", "sounds good"), set `confirmed_variant_count` to 100.
- If the response is ambiguous, ask once: "Just to confirm — how many total variants would you like? (default is 100)"

Store `confirmed_variant_count`. This value drives the Variant Generation section below.

---

Then update the `## Variant Generation` section to replace all hard-coded references to "~100" and "approximately 20 per category" with dynamic references to `confirmed_variant_count`:

- Change the opening sentence from:
  "Generate ~100 variants across these 5 categories, targeting approximately 20 per category:"
  to:
  "Generate `confirmed_variant_count` variants across these 5 categories, targeting approximately `confirmed_variant_count / 5` per category (round to nearest integer):"

- Change the minimum-per-category enforcement sentence from:
  "If any category has fewer than 15 variants, generate additional variants for that category before proceeding."
  to:
  "If any category has fewer than `floor(confirmed_variant_count / 5 * 0.75)` variants, generate additional variants for that category before proceeding. (For the default of 100, this threshold is 15.)"

- Update the presentation format header line to reflect the confirmed count:
  Change the static "Total: [N] variants" line description to note that N should equal confirmed_variant_count.

Use the Write tool to save the updated file. Do not change any other section of the command file.
  </action>
  <verify>
    <automated>grep -n "Variant Count Confirmation" "/Users/woff/Trademark Hound:Cat/.claude/commands/trademark-cat.md" && grep -n "confirmed_variant_count" "/Users/woff/Trademark Hound:Cat/.claude/commands/trademark-cat.md" | wc -l</automated>
  </verify>
  <done>
The file contains a "## Variant Count Confirmation" section. The string "confirmed_variant_count" appears at least 4 times (set in the new section, used in Variant Generation opening, used in minimum threshold, used in presentation). The "~100" hard-code in the Variant Generation opening sentence is replaced with the dynamic reference.
  </done>
</task>

</tasks>

<verification>
After the task completes:
1. grep -c "confirmed_variant_count" ".claude/commands/trademark-cat.md" — should return >= 4
2. grep "~100" ".claude/commands/trademark-cat.md" — should return nothing (or only in the new section's example text, not as an instruction)
3. The section order in the file must be: Intake → Negative Constraints → Variant Count Confirmation → Variant Generation → Presentation and Approval Loop → Writing the Variants File
</verification>

<success_criteria>
- trademark-cat.md contains a new check-in step between Negative Constraints and Variant Generation
- The attorney is prompted for a count before any variants are generated
- The confirmed count drives per-category targets and the minimum enforcement threshold
- No other sections of the command are altered
</success_criteria>

<output>
After completion, create `.planning/quick/1-for-the-trademark-cat-after-understandin/1-SUMMARY.md` with a brief summary of what was changed and the exact line range of the new section.
</output>
