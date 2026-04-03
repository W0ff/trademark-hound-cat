#!/usr/bin/env python3
"""
Phase 1 test suite — Trademark Cat + Contracts
Run: python3 tests/test_phase1.py

Tests verify structural correctness of:
  - .claude/commands/trademark-cat.md (CAT-01 through CAT-08)
  - hound_leads_template.py (PY-01 through PY-03)

These are contract tests, not behavioral tests. They confirm the artifacts
contain the required content — not that Claude executes them correctly (that
requires human validation during acceptance testing).
"""
import os
import ast
import unittest
from pathlib import Path

ROOT = Path(__file__).parent.parent


class TestTrademarkCatCommand(unittest.TestCase):
    """CAT-01 through CAT-08: Structural checks on .claude/commands/trademark-cat.md"""

    CAT_CMD = ROOT / ".claude" / "commands" / "trademark-cat.md"

    def _read(self):
        self.assertTrue(self.CAT_CMD.exists(), f"Missing: {self.CAT_CMD}")
        return self.CAT_CMD.read_text(encoding="utf-8")

    def test_cat01_file_exists(self):
        """CAT-01: Command file exists at .claude/commands/trademark-cat.md"""
        self.assertTrue(self.CAT_CMD.exists(), f"Missing: {self.CAT_CMD}")

    def test_cat02_negative_constraints(self):
        """CAT-02: Negative Constraints / Ignore List section present"""
        content = self._read()
        self.assertIn("Negative Constraints", content,
            "Command must instruct Claude to derive a Negative Constraints (Ignore List)")

    def test_cat03_all_five_categories(self):
        """CAT-03: All 5 linguistic category names present"""
        content = self._read()
        categories = ["Phonetic", "Compound", "Semantic", "Conceptual", "Hybrid"]
        for cat in categories:
            self.assertIn(cat, content, f"Missing category in command: {cat}")

    def test_cat04_confusion_axis_annotation(self):
        """CAT-04: Confusion axis annotation format documented"""
        content = self._read()
        self.assertIn("confusion axis", content.lower(),
            "Command must document the confusion axis annotation format")

    def test_cat05_display_format_summary_line(self):
        """CAT-05: Summary line format (Total: N variants) present"""
        content = self._read()
        self.assertIn("Total:", content,
            "Command must specify the summary line format: 'Total: N variants | ...'")

    def test_cat06_approval_gate(self):
        """CAT-06: Approval gate language present"""
        content = self._read().lower()
        has_approval = "approved" in content or "looks good" in content
        self.assertTrue(has_approval,
            "Command must document the approval gate ('approved' or 'looks good')")

    def test_cat07_variants_file_format(self):
        """CAT-07: Variants file format documented (# Context: header)"""
        content = self._read()
        self.assertIn("# Context:", content,
            "Command must document the '# Context:' first-line format for the variants file")

    def test_cat08_file_confirmation(self):
        """CAT-08: File path confirmation message documented"""
        content = self._read().lower()
        has_confirm = "confirm" in content or "written to" in content
        self.assertTrue(has_confirm,
            "Command must instruct Claude to confirm the output file path after writing")


class TestHoundLeadsTemplate(unittest.TestCase):
    """PY-01 through PY-03: Structural checks on hound_leads_template.py"""

    TEMPLATE = ROOT / "hound_leads_template.py"

    def _read(self):
        self.assertTrue(self.TEMPLATE.exists(), f"Missing: {self.TEMPLATE}")
        return self.TEMPLATE.read_text(encoding="utf-8")

    def test_py01_file_exists_and_syntax(self):
        """PY-01: Template file exists and is valid Python syntax"""
        content = self._read()
        try:
            ast.parse(content)
        except SyntaxError as e:
            self.fail(f"hound_leads_template.py has syntax error: {e}")

    def test_py01_placeholder_tokens(self):
        """PY-01: Both exact placeholder tokens present"""
        content = self._read()
        self.assertIn("[INSERT API KEY]", content,
            "Template must contain exact placeholder: [INSERT API KEY]")
        self.assertIn("[INSERT VARIANTS FILE]", content,
            "Template must contain exact placeholder: [INSERT VARIANTS FILE]")

    def test_py02_delay_seconds(self):
        """PY-02: DELAY_SECONDS configurable constant present"""
        content = self._read()
        self.assertIn("DELAY_SECONDS", content,
            "Template must define DELAY_SECONDS constant for configurable rate limiting")

    def test_py02_progress_output(self):
        """PY-02: Progress print statement present"""
        content = self._read()
        self.assertIn("print(", content,
            "Template must include print() for progress output per variant")
        self.assertIn("flush=True", content,
            "Template progress print must use flush=True so output is not buffered")

    def test_py02_comment_line_skipping(self):
        """PY-02: Variants file comment-line skipping logic present"""
        content = self._read()
        self.assertIn("startswith(\"#\")", content,
            "Template must skip lines starting with '#' when loading variants file")

    def test_py03_output_fields(self):
        """PY-03: All 5 required JSON output fields present"""
        content = self._read()
        for field in ["variant", "title", "url", "snippet", "position"]:
            self.assertIn(f'"{field}"', content,
                f"Template output record must include field: {field}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
