"""Legacy research-collector regressions: never replace the ledger with nothing, no network."""

import contextlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from scripts import collect_research as collect

ROOT = Path(__file__).resolve().parents[1]
LEDGER = '{"id": "arxiv:2609.00001", "title": "Existing accepted record"}\n'
ABSTRACT = ("We study confidence calibration of neural classifiers and report how predicted "
            "probabilities match observed accuracy across many benchmark tasks, comparing "
            "temperature scaling with other post hoc methods under a fixed evaluation protocol.")


def run_main(*argv):
    """Return the SystemExit code; a string code is printed to stderr with exit status 1."""
    with patch.object(sys, "argv", ["collect_research.py", *argv]), \
            contextlib.redirect_stdout(io.StringIO()):
        try:
            collect.main()
        except SystemExit as exit_:
            return exit_.code
    return 0


class OfflineRescreenTests(unittest.TestCase):
    def test_offline_with_empty_cache_fails_and_keeps_ledger(self):
        with tempfile.TemporaryDirectory(prefix="awesome-jev-test-") as directory:
            root = Path(directory)
            cache, output = root / "cache", root / "research-sources.jsonl"
            cache.mkdir()
            output.write_text(LEDGER, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, "scripts/collect_research.py", "--offline", "--target", "0",
                 "--with-openalex", "--cache-dir", str(cache), "--output", str(output)],
                cwd=ROOT, capture_output=True, text=True, timeout=60,
            )
            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("no cached response", result.stderr)
            self.assertEqual(output.read_text(encoding="utf-8"), LEDGER)

    def test_zero_accepted_records_fail_and_keep_ledger(self):
        empty = lambda self, topic, query, provider=collect.PROVIDER: (topic, query, {"data": []})
        with tempfile.TemporaryDirectory(prefix="awesome-jev-test-") as directory, \
                patch.object(collect.Collector, "fetch", empty):
            root = Path(directory)
            output = root / "research-sources.jsonl"
            output.write_text(LEDGER, encoding="utf-8")
            code = run_main("--offline", "--cache-dir", str(root / "cache"), "--output", str(output))
            self.assertIsInstance(code, str)
            self.assertIn("no records qualified", code)
            self.assertEqual(output.read_text(encoding="utf-8"), LEDGER)

    def test_complete_cache_still_writes_screened_records(self):
        def cached(self, topic, query, provider=collect.PROVIDER):
            papers = []
            if query == collect.QUERIES["probability_calibration"][0]:
                papers = [{"paper": {"id": "2609.00002v1", "title": "Confidence calibration of neural classifiers",
                                     "summary": ABSTRACT, "authors": [{"name": "A. Author"}],
                                     "publishedAt": "2026-09-01"}}]
            return topic, query, {"data": papers, "retrieved_at": "2026-10-15T00:00:00+00:00",
                                  "http_status": 200, "retrieval_url": "https://example.org/" + query,
                                  "provider": provider}

        with tempfile.TemporaryDirectory(prefix="awesome-jev-test-") as directory, \
                patch.object(collect.Collector, "fetch", cached):
            root = Path(directory)
            output = root / "research-sources.jsonl"
            output.write_text(LEDGER, encoding="utf-8")
            self.assertEqual(run_main("--offline", "--cache-dir", str(root / "cache"), "--output", str(output)), 0)
            records = [json.loads(line) for line in output.read_text(encoding="utf-8").splitlines()]
            self.assertEqual([r["id"] for r in records], ["arxiv:2609.00002"])


def response(query, *papers):
    return ("probability_calibration", query, {
        "data": [{"paper": {"summary": ABSTRACT, "authors": [{"name": "A. Author"}],
                            "publishedAt": "2026-09-01", **paper}} for paper in papers],
        "retrieved_at": "2026-10-15T00:00:00+00:00", "http_status": 200,
        "retrieval_url": "https://example.org/search?q=" + query, "provider": collect.PROVIDER,
    })


class BuildRecordsTitleKeyTests(unittest.TestCase):
    def test_empty_and_non_latin_titles_keep_distinct_ids(self):
        records, audit = collect.build_records([response(
            "calibration",
            {"id": "2401.00001", "title": ""},
            {"id": "2401.00002", "title": "神经网络置信度校准"},
            {"id": "2401.00003", "title": "Калибровка уверенности"},
        )])
        self.assertEqual([r["id"] for r in records], ["arxiv:2401.00001", "arxiv:2401.00002", "arxiv:2401.00003"])
        self.assertNotIn("deduplicated_appearances", audit["counts"])
        self.assertEqual(audit["counts"]["distinct_screened_candidates"], 3)

    def test_long_non_latin_title_keys_keep_their_letters(self):
        self.assertEqual(collect.normalize_title("Калибровка уверенности, нейронных сетей!"), "калибровкауверенностинейронныхсетей")
        self.assertNotEqual(collect.normalize_title("Калибровка уверенности нейронных сетей"),
                            collect.normalize_title("Оценка неопределенности нейронных сетей"))

    def test_same_long_title_with_different_ids_still_merges(self):
        title = "Confidence Calibration of Neural Classifiers"
        records, audit = collect.build_records([
            response("calibration", {"id": "2401.00004v2", "title": title}),
            response("temperature scaling", {"id": "doi:10.1000/example", "_record_id": "doi:10.1000/example",
                                             "_canonical_url": "https://doi.org/10.1000/example",
                                             "title": title.upper() + "."}),
        ])
        self.assertEqual([r["id"] for r in records], ["arxiv:2401.00004"])
        self.assertEqual(records[0]["discovery_queries"], ["calibration", "temperature scaling"])
        self.assertEqual(audit["counts"]["deduplicated_appearances"], 1)

    def test_short_titles_still_merge_on_the_same_id(self):
        records, audit = collect.build_records([
            response("calibration", {"id": "2401.00005v1", "title": ""}),
            response("temperature scaling", {"id": "2401.00005v2", "title": ""}),
        ])
        self.assertEqual([r["id"] for r in records], ["arxiv:2401.00005"])
        self.assertEqual(records[0]["discovery_queries"], ["calibration", "temperature scaling"])
        self.assertEqual(audit["counts"]["deduplicated_appearances"], 1)


if __name__ == "__main__":
    unittest.main()
