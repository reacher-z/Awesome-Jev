"""Legacy research-collector regressions: never replace the ledger with nothing, no network."""

import contextlib
import io
import json
import os
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


@unittest.skipUnless(hasattr(os, "getuid"), "POSIX ownership and permission bits")
class CacheTests(unittest.TestCase):
    class Response(io.BytesIO):
        status = 200

    BODY = json.dumps([{"paper": {"id": "2609.00004v1", "title": "Confidence calibration of neural classifiers",
                                  "summary": ABSTRACT, "authors": [{"name": "A. Author"}],
                                  "publishedAt": "2026-09-01"}}]).encode()

    def setUp(self):
        directory = tempfile.TemporaryDirectory(prefix="awesome-jev-test-")
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        self.calls = 0

    def urlopen(self, request, timeout=None):
        self.calls += 1
        return self.Response(self.BODY)

    def offline_urlopen(self, request, timeout=None):
        raise AssertionError("an offline run must not make network requests")

    def test_online_fetch_refreshes_an_existing_cached_response(self):
        cache = self.root / "cache"
        with patch.object(collect.urllib.request, "urlopen", self.urlopen):
            collect.Collector(cache, 1).fetch("probability_calibration", "calibration")
            [cached] = cache.glob("*.json")
            cached.write_text(json.dumps({"data": [], "retrieved_at": "2020-01-01T00:00:00+00:00"}))
            collector = collect.Collector(cache, 1)
            _, _, wrapper = collector.fetch("probability_calibration", "calibration")
        self.assertEqual(self.calls, 2)
        self.assertNotEqual(wrapper["retrieved_at"], "2020-01-01T00:00:00+00:00")
        self.assertEqual(len(wrapper["data"]), 1)
        self.assertEqual(json.loads(cached.read_text())["retrieved_at"], wrapper["retrieved_at"])
        self.assertEqual(collector.cached_queries, 0)

    def test_offline_fetch_reads_and_counts_the_cache(self):
        cache = self.root / "cache"
        with patch.object(collect.urllib.request, "urlopen", self.urlopen):
            _, _, online = collect.Collector(cache, 1).fetch("probability_calibration", "calibration")
        with patch.object(collect.urllib.request, "urlopen", self.offline_urlopen):
            collector = collect.Collector(cache, 1, offline=True)
            _, _, offline = collector.fetch("probability_calibration", "calibration")
        self.assertEqual(offline["retrieved_at"], online["retrieved_at"])
        self.assertEqual(collector.cached_queries, 1)

    def test_audit_reports_queries_answered_from_the_cache(self):
        def audit(*argv, urlopen):
            out = io.StringIO()
            with patch.object(sys, "argv", ["collect_research.py", *argv]), contextlib.redirect_stdout(out), \
                    patch.dict(collect.QUERIES, {"probability_calibration": ["calibration"]}, clear=True), \
                    patch.object(collect.urllib.request, "urlopen", urlopen):
                collect.main()
            return json.loads("{" + out.getvalue().split("\n{", 1)[1])

        argv = ("--cache-dir", str(self.root / "cache"), "--output", str(self.root / "research-sources.jsonl"))
        self.assertEqual(audit(*argv, urlopen=self.urlopen)["cached_queries"], 0)
        self.assertEqual(audit("--offline", *argv, urlopen=self.offline_urlopen)["cached_queries"], 1)

    def test_default_cache_dir_is_per_user(self):
        with patch.dict(os.environ, {"XDG_CACHE_HOME": str(self.root / "xdg")}):
            self.assertEqual(collect.default_cache_dir(), self.root / "xdg" / "awesome-jev" / "research-api")
        with patch.dict(os.environ, {"HOME": str(self.root / "home")}):
            os.environ.pop("XDG_CACHE_HOME", None)
            self.assertEqual(collect.default_cache_dir(), self.root / "home" / ".cache" / "awesome-jev" / "research-api")

    def test_new_cache_dir_is_private(self):
        cache = self.root / "parent" / "cache"
        collect.Collector(cache, 1)
        self.assertEqual(cache.stat().st_mode & 0o777, 0o700)

    def test_shared_or_foreign_cache_dir_is_refused(self):
        shared = self.root / "shared"
        shared.mkdir()
        shared.chmod(0o777)
        with self.assertRaisesRegex(PermissionError, "writable by other users"):
            collect.Collector(shared, 1)
        foreign = self.root / "foreign"
        foreign.mkdir(mode=0o700)
        with patch.object(os, "getuid", return_value=os.getuid() + 1), \
                self.assertRaisesRegex(PermissionError, "owned by another user"):
            collect.Collector(foreign, 1)


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
