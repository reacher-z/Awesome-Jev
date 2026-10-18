"""A source is either accepted or excluded by the screen, never both."""

import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts import refresh_sources as refresh
from scripts import validate

ROOT = Path(__file__).resolve().parents[1]


def row(url, **fields):
    return {"url": url, "title": "Fixture", "verification_level": "content_screened", **fields}


def read_ledger(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


class LedgerOverlapValidationTests(unittest.TestCase):
    def overlap_errors(self, accepted_rows, excluded_rows):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            accepted = {root / "data/ecosystem-sources.jsonl": accepted_rows}
            excluded = {root / "data/ecosystem-sources.excluded.jsonl": excluded_rows}
            with patch.object(validate, "ROOT", root), patch.object(validate, "errors", []):
                validate.check_ledger_overlap(accepted, excluded)
                return list(validate.errors)

    def test_source_in_accepted_and_excluded_ledgers_fails(self):
        errors = self.overlap_errors([row("https://github.com/owner/project")],
                                     [row("https://github.com/owner/project", verification_level="metadata_only")])
        self.assertEqual(len(errors), 1)
        self.assertIn("data/ecosystem-sources.excluded.jsonl", errors[0])
        self.assertIn("https://github.com/owner/project", errors[0])

    def test_url_aliases_and_github_case_are_the_same_source(self):
        accepted = [row("https://github.com/Owner/Project")]
        for alias in ("https://www.github.com/owner/project/", "https://github.com/owner/project.git",
                      "https://github.com/OWNER/project/blob/main/README.md"):
            with self.subTest(alias=alias):
                self.assertEqual(len(self.overlap_errors(accepted, [row(alias)])), 1)

    def test_distinct_sources_pass(self):
        self.assertEqual(self.overlap_errors([row("https://github.com/owner/project")],
                                             [row("https://github.com/owner/project-two"),
                                              row("https://huggingface.co/owner/project")]), [])

    def test_committed_ledgers_do_not_overlap(self):
        accepted = {ROOT / "data" / name: read_ledger(ROOT / "data" / name)
                    for name in ("ecosystem-sources.jsonl", "research-sources.jsonl")}
        excluded = {path: read_ledger(path) for path in sorted((ROOT / "data").glob("*.excluded.jsonl"))}
        with patch.object(validate, "errors", []):
            validate.check_ledger_overlap(accepted, excluded)
            self.assertEqual(validate.errors, [])


class ScanPrunesPromotedExclusionsTests(unittest.TestCase):
    def test_scan_removes_exclusion_rows_for_accepted_sources_only(self):
        rows = [row("https://github.com/owner/promoted", exclusion_reason="Not established."),
                row("https://github.com/owner/still-excluded", exclusion_reason="Not established.")]
        excluded = refresh.Ledger(rows, [json.dumps(item) + "\n" for item in rows])
        pruned, promoted = refresh.prune_promoted_exclusions(excluded, [row("https://github.com/Owner/Promoted")])
        self.assertEqual(promoted, ["https://github.com/owner/promoted"])
        self.assertEqual(pruned.rows, rows[1:])
        self.assertEqual(pruned.lines, excluded.lines[1:])

    def test_scan_without_promotions_leaves_exclusion_ledger_unchanged(self):
        rows = [row("https://github.com/owner/still-excluded")]
        excluded = refresh.Ledger(rows, [json.dumps(rows[0]) + "\n"])
        pruned, promoted = refresh.prune_promoted_exclusions(excluded, [row("https://github.com/owner/other")])
        self.assertEqual((pruned, promoted), (excluded, []))


if __name__ == "__main__":
    unittest.main()
