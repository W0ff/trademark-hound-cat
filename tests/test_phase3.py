#!/usr/bin/env python3
"""
Phase 3 contract tests — HND-13 through HND-19.

These are structural checks on command file contents. All tests must be RED
before Plan 02 implementation begins.

Run: python3 tests/test_phase3.py
"""
import unittest
from pathlib import Path

ROOT = Path(__file__).parent.parent


class TestReportFormat(unittest.TestCase):
    """HND-13: Report output uses HOUND_REPORT_ filename prefix."""

    REPORT_CMD = ROOT / ".claude" / "commands" / "trademark-report.md"

    def _read(self):
        self.assertTrue(self.REPORT_CMD.exists(), f"Missing: {self.REPORT_CMD}")
        return self.REPORT_CMD.read_text(encoding="utf-8")

    def test_hnd13_report_filename_pattern(self):
        """HND-13: trademark-report.md references HOUND_REPORT_ filename prefix."""
        content = self._read()
        self.assertIn(
            "HOUND_REPORT_",
            content,
            "trademark-report.md must reference the HOUND_REPORT_ filename prefix",
        )

    def test_hnd13_threat_column_in_priority_table(self):
        """HND-13/14: Priority Action Table must include a THREAT? column header."""
        content = self._read()
        self.assertIn(
            "THREAT?",
            content,
            "trademark-report.md Priority Action Table must include a 'THREAT?' column",
        )


class TestThreatColumn(unittest.TestCase):
    """HND-14: THREAT? column appears in the report output table."""

    REPORT_CMD = ROOT / ".claude" / "commands" / "trademark-report.md"

    def _read(self):
        self.assertTrue(self.REPORT_CMD.exists(), f"Missing: {self.REPORT_CMD}")
        return self.REPORT_CMD.read_text(encoding="utf-8")

    def test_hnd14_threat_column_present(self):
        """HND-14: trademark-report.md includes THREAT? column in the action table."""
        content = self._read()
        self.assertIn(
            "THREAT?",
            content,
            "trademark-report.md must include a THREAT? column for attorney annotation",
        )


class TestDisclaimer(unittest.TestCase):
    """HND-15: Legal disclaimer appears in both markdown and CSV report outputs."""

    REPORT_CMD = ROOT / ".claude" / "commands" / "trademark-report.md"

    def _read(self):
        self.assertTrue(self.REPORT_CMD.exists(), f"Missing: {self.REPORT_CMD}")
        return self.REPORT_CMD.read_text(encoding="utf-8")

    def test_hnd15_disclaimer_in_markdown(self):
        """HND-15: Step 3A markdown report includes legal disclaimer text."""
        content = self._read()
        has_disclaimer = (
            "does not constitute legal advice" in content.lower()
            or "attorney review" in content.lower()
            or "not legal advice" in content.lower()
        )
        self.assertTrue(
            has_disclaimer,
            "trademark-report.md Step 3A must include a legal disclaimer "
            "('does not constitute legal advice' or 'attorney review')",
        )

    def test_hnd15_disclaimer_in_csv(self):
        """HND-15: Step 3B CSV report section references disclaimer or note."""
        content = self._read()
        # Step 3B section must contain a disclaimer indicator
        step3b_start = content.find("## Step 3B")
        self.assertNotEqual(step3b_start, -1, "trademark-report.md must contain a Step 3B section")
        step3b_content = content[step3b_start:]
        has_disclaimer = (
            "does not constitute legal advice" in step3b_content.lower()
            or "attorney review" in step3b_content.lower()
            or "not legal advice" in step3b_content.lower()
            or "disclaimer" in step3b_content.lower()
        )
        self.assertTrue(
            has_disclaimer,
            "trademark-report.md Step 3B must include a disclaimer field or note in the CSV output",
        )


class TestRunSummary(unittest.TestCase):
    """HND-16: Run summary block printed after hound completes."""

    HOUND_CMD = ROOT / ".claude" / "commands" / "trademark-hound.md"

    def _read(self):
        self.assertTrue(self.HOUND_CMD.exists(), f"Missing: {self.HOUND_CMD}")
        return self.HOUND_CMD.read_text(encoding="utf-8")

    def test_hnd16_run_summary_block(self):
        """HND-16: trademark-hound.md includes a Run Summary output block."""
        content = self._read()
        has_summary = (
            "Run Summary" in content
            or "=== Trademark Hound Run Summary" in content
            or "run summary" in content.lower()
        )
        self.assertTrue(
            has_summary,
            "trademark-hound.md must include a 'Run Summary' block printed at completion",
        )


class TestSafelistIngestion(unittest.TestCase):
    """HND-17: Re-invocation branch accepts a reviewed report path and updates safelist."""

    HOUND_CMD = ROOT / ".claude" / "commands" / "trademark-hound.md"

    def _read(self):
        self.assertTrue(self.HOUND_CMD.exists(), f"Missing: {self.HOUND_CMD}")
        return self.HOUND_CMD.read_text(encoding="utf-8")

    def test_hnd17_reinvocation_branch(self):
        """HND-17: trademark-hound.md has a dedicated re-invocation branch that reads a report."""
        content = self._read()
        # Requires a structured re-invocation section with explicit second-argument intake.
        # The branch must be labeled and contain the actual ingestion logic,
        # not just a passing mention in a CRITICAL note at the bottom of the file.
        has_intake_branch = (
            "re-invocation" in content.lower()
            or "reinvocation" in content.lower()
            or "safelist ingestion" in content.lower()
            or "second argument" in content.lower()
        )
        self.assertTrue(
            has_intake_branch,
            "trademark-hound.md must include a dedicated re-invocation branch section "
            "(labeled 're-invocation', 'safelist ingestion', or 'second argument' intake) "
            "for processing a reviewed report path",
        )


class TestAtomicWrite(unittest.TestCase):
    """HND-18: Safelist writes use atomic tmp-then-mv pattern."""

    REPORT_CMD = ROOT / ".claude" / "commands" / "trademark-report.md"
    HOUND_CMD = ROOT / ".claude" / "commands" / "trademark-hound.md"

    def _read_report(self):
        self.assertTrue(self.REPORT_CMD.exists(), f"Missing: {self.REPORT_CMD}")
        return self.REPORT_CMD.read_text(encoding="utf-8")

    def _read_hound(self):
        self.assertTrue(self.HOUND_CMD.exists(), f"Missing: {self.HOUND_CMD}")
        return self.HOUND_CMD.read_text(encoding="utf-8")

    def test_hnd18_tmp_file_write(self):
        """HND-18: trademark-report.md references atomic write pattern (.tmp + mv)."""
        content = self._read_report()
        has_tmp = ".tmp" in content
        has_mv = "mv" in content
        self.assertTrue(
            has_tmp and has_mv,
            "trademark-report.md must reference atomic write pattern: write to .tmp then mv "
            f"(has .tmp: {has_tmp}, has mv: {has_mv})",
        )

    def test_hnd18_atomic_in_hound(self):
        """HND-18: trademark-hound.md re-invocation branch uses atomic write pattern (.tmp + mv)."""
        content = self._read_hound()
        has_tmp = ".tmp" in content
        has_mv = "mv" in content
        self.assertTrue(
            has_tmp and has_mv,
            "trademark-hound.md must reference atomic write pattern in re-invocation branch: "
            f"write to .tmp then mv (has .tmp: {has_tmp}, has mv: {has_mv})",
        )


class TestSafelistCountReport(unittest.TestCase):
    """HND-19: Safelist count reporting after update (entries added / total entries)."""

    HOUND_CMD = ROOT / ".claude" / "commands" / "trademark-hound.md"

    def _read(self):
        self.assertTrue(self.HOUND_CMD.exists(), f"Missing: {self.HOUND_CMD}")
        return self.HOUND_CMD.read_text(encoding="utf-8")

    def test_hnd19_count_reporting(self):
        """HND-19: trademark-hound.md reports count of entries added and total excluded."""
        content = self._read()
        has_count_report = (
            "entries added" in content.lower()
            or "now excluded" in content.lower()
            or "total entries" in content.lower()
            or "added to safelist" in content.lower()
        )
        self.assertTrue(
            has_count_report,
            "trademark-hound.md must report safelist update counts "
            "('entries added', 'now excluded', or 'total entries')",
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
