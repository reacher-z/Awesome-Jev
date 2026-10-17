"""Ledger relation, topic, source type, status and timestamps use controlled values."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts import validate


ROOT = Path(__file__).resolve().parents[1]
ROW = {"url": "https://huggingface.co/example/jev-model", "title": "Fixture model", "topic": "decision-model-card",
       "relation": "direct", "source_type": "hf_model", "status": "screened",
       "retrieved_at": "2026-10-17T03:35:59.068352+00:00", "verification_level": "metadata_only",
       "relevance": "Synthetic vocabulary fixture."}


class LedgerVocabularyTests(unittest.TestCase):
    def check(self, *rows, raw_lines=()):
        with tempfile.TemporaryDirectory() as tmp, patch.object(validate, "errors", []):
            root = Path(tmp)
            path = root / "data/ecosystem-sources.jsonl"
            path.parent.mkdir()
            lines = [json.dumps({**ROW, **changes}, ensure_ascii=False) for changes in rows] + list(raw_lines)
            path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
            with patch.object(validate, "ROOT", root):
                validate.check_vocabulary(path)
            return list(validate.errors)

    def test_current_ledgers_use_the_vocabularies(self):
        with patch.object(validate, "errors", []):
            for path in sorted((ROOT / "data").glob("*.jsonl")):
                validate.check_vocabulary(path)
            self.assertEqual(validate.errors, [])

    def test_valid_values_and_optional_fields_pass(self):
        self.assertEqual(self.check({}, {"relation": "background", "topic": "probability_calibration",
                                         "source_type": "scholarly_work", "published_at": "2012"},
                                    {"status": "audit_error", "published_at": "2026-10-01"},
                                    {"published_at": "2026-10-01T12:00:00.000Z", "retrieved_at": "2026-10-16T00:00:00Z"},
                                    {"published_at": None}), [])
        row = dict(ROW)
        for key in ("source_type", "status"):
            row.pop(key)
        self.assertEqual(self.check(row), [])

    def test_issue_reproduction_typo_and_unparseable_timestamp_are_rejected(self):
        errors = self.check({}, {"relation": "drect", "retrieved_at": "last tuesday"})
        self.assertEqual(errors, ["data/ecosystem-sources.jsonl:2: unknown relation",
                                  "data/ecosystem-sources.jsonl:2: retrieved_at must be an ISO 8601 timestamp"])

    def test_off_vocabulary_audiojev_spellings_are_rejected(self):
        self.assertEqual(self.check({"topic": "model-card", "source_type": "model_card"}),
                         ["data/ecosystem-sources.jsonl:1: unknown topic",
                          "data/ecosystem-sources.jsonl:1: unknown source_type"])

    def test_unknown_or_non_string_values_are_rejected(self):
        for key, value in (("status", "Screened"), ("status", ["screened"]), ("relation", None),
                           ("topic", {"name": "decision-model-card"}), ("source_type", 3)):
            with self.subTest(key=key, value=value):
                self.assertEqual(self.check({key: value}), [f"data/ecosystem-sources.jsonl:1: unknown {key}"])

    def test_published_at_must_be_a_year_date_or_timestamp(self):
        for value in ("26", "2026-13-01", "October 2026", 2026):
            with self.subTest(value=value):
                self.assertEqual(self.check({"published_at": value}), [
                    "data/ecosystem-sources.jsonl:1: published_at must be a year or an ISO 8601 date or timestamp"])

    def test_blank_and_malformed_lines_are_left_to_the_ledger_check(self):
        errors = self.check({}, raw_lines=("", "{not json", "[1]", json.dumps({**ROW, "relation": "drect"})))
        self.assertEqual(errors, ["data/ecosystem-sources.jsonl:5: unknown relation"])

    def test_main_flow_checks_every_ledger(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(validate, "errors", []):
            root = Path(tmp)
            (root / "data").mkdir()
            for name, changes in (("ecosystem-sources.jsonl", {"topic": "model-card"}),
                                  ("ecosystem-sources.excluded.jsonl", {"relation": "drect"})):
                (root / "data" / name).write_text(json.dumps({**ROW, **changes}) + "\n", encoding="utf-8", newline="\n")
            with patch.object(validate, "ROOT", root), patch.object(validate, "check_index"), \
                    patch("builtins.print"):
                self.assertEqual(validate.main(), 1)
            self.assertIn("data/ecosystem-sources.jsonl:1: unknown topic", validate.errors)
            self.assertIn("data/ecosystem-sources.excluded.jsonl:1: unknown relation", validate.errors)


if __name__ == "__main__":
    unittest.main()
