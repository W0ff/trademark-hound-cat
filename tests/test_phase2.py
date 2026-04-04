#!/usr/bin/env python3
"""
Phase 2 test suite — Trademark Hound Core
Run: python3 tests/test_phase2.py

Tests verify structural correctness of:
  - .claude/commands/trademark-hound.md (HND-01 through HND-12)

HND-06 is covered by test_phase1.py::TestHoundLeadsTemplate::test_py02_delay_seconds — not repeated here.

These are contract tests, not behavioral tests. They confirm the artifact
contains the required content — not that Claude executes it correctly (that
requires human validation during acceptance testing).
"""
import unittest
from pathlib import Path

ROOT = Path(__file__).parent.parent


class TestTrademarkHoundCommand(unittest.TestCase):
    """HND-01 through HND-12: Structural checks on .claude/commands/trademark-hound.md"""

    HOUND_CMD = ROOT / ".claude" / "commands" / "trademark-hound.md"

    def _read(self):
        self.assertTrue(self.HOUND_CMD.exists(), f"Missing: {self.HOUND_CMD}")
        return self.HOUND_CMD.read_text(encoding="utf-8")

    def test_hnd01_file_exists(self):
        """HND-01: Command file exists at .claude/commands/trademark-hound.md"""
        self.assertTrue(self.HOUND_CMD.exists(), f"Missing: {self.HOUND_CMD}")

    def test_hnd01_arguments_intake(self):
        """HND-01: Command parses inline args via $ARGUMENTS"""
        content = self._read()
        self.assertIn("$ARGUMENTS", content,
            "Command must reference $ARGUMENTS to accept inline trademark name and context")

    def test_hnd02_safelist_load(self):
        """HND-02: Command references safelist file naming pattern"""
        content = self._read()
        self.assertIn("safelist-", content,
            "Command must reference the safelist-[TRADEMARK].json file naming pattern")

    def test_hnd03_missing_variants_halt(self):
        """HND-03: Command halts and routes to /trademark-cat when variants file missing"""
        content = self._read()
        self.assertIn("/trademark-cat", content,
            "Command must route user to /trademark-cat when variants file is missing")
        self.assertIn("variants-", content,
            "Command must reference variants-[TRADEMARK].txt file naming pattern")

    def test_hnd04_serp_script_reuse(self):
        """HND-04: Command references per-trademark SERP script name"""
        content = self._read()
        self.assertIn("hound-SERP-", content,
            "Command must reference hound-SERP-[TRADEMARK].py naming pattern")

    def test_hnd04_token_substitution(self):
        """HND-04: Command documents the [INSERT API KEY] placeholder token"""
        content = self._read()
        self.assertIn("[INSERT API KEY]", content,
            "Command must document the [INSERT API KEY] placeholder token used in template substitution")

    def test_hnd05_bash_execution(self):
        """HND-05: Command executes SERP script via Bash tool"""
        content = self._read()
        self.assertIn("python3", content,
            "Command must invoke Bash tool to run python3 for the SERP script")
        self.assertIn("hound_leads-", content,
            "Command must reference hound_leads-[TRADEMARK].json output file")

    def test_hnd07_safelist_filtering(self):
        """HND-07: Safelist filtering step present"""
        content_lower = self._read().lower()
        self.assertTrue(
            "filter" in content_lower or "exclude" in content_lower or "discard" in content_lower,
            "Command must include a safelist filtering step (filter/exclude/discard)"
        )

    def test_hnd08_webfetch_investigation(self):
        """HND-08: Agentic browsing via WebFetch with commerciality assessment"""
        content = self._read()
        self.assertIn("WebFetch", content,
            "Command must explicitly name the WebFetch tool for agentic lead investigation")
        self.assertTrue(
            "Commerciality" in content or "COMMERCIALITY" in content,
            "Command must name Commerciality as an assessment dimension"
        )

    def test_hnd09_informational_exclusion(self):
        """HND-09: Known exclusion domain (wikipedia) listed"""
        content = self._read()
        self.assertIn("wikipedia", content.lower(),
            "Command must list wikipedia as a known informational exclusion domain")

    def test_hnd10_eight_factor_matrix(self):
        """HND-10: Scoring table contains required factor names"""
        content = self._read()
        for factor in ["Mark Criticality", "Similarity", "Geography"]:
            self.assertIn(factor, content,
                f"Command scoring matrix must include factor: {factor}")

    def test_hnd11_risk_tiers(self):
        """HND-11: Risk tier labels and High threshold present"""
        content = self._read()
        self.assertIn("High", content,
            "Command must define High risk tier")
        self.assertIn("Medium", content,
            "Command must define Medium risk tier")
        self.assertIn("Low", content,
            "Command must define Low risk tier")
        self.assertTrue(
            "15" in content or ">= 15" in content or "≥ 15" in content,
            "Command must document High tier threshold (15 or >= 15 or ≥ 15)"
        )

    def test_hnd12_low_risk_dropped(self):
        """HND-12: Low-scoring leads dropped/excluded from output"""
        content_lower = self._read().lower()
        self.assertTrue(
            "low" in content_lower and (
                "drop" in content_lower or
                "exclude" in content_lower or
                "below" in content_lower
            ),
            "Command must state that Low-tier leads are dropped/excluded/below threshold"
        )

    def test_hnd_scored_output_file(self):
        """HND-10/11/12: Intermediate scored output file referenced"""
        content = self._read()
        self.assertIn("hound_scored-", content,
            "Command must reference hound_scored-[TRADEMARK].json intermediate output file")


if __name__ == "__main__":
    unittest.main(verbosity=2)
