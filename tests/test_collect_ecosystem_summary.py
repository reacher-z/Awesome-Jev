"""A full ecosystem collection must not commit a count summary that later scans leave stale."""

import contextlib
import hashlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

from scripts import collect_ecosystem as ecosystem

ROOT = Path(__file__).resolve().parents[1]
SPACE_ROOT = ecosystem.SPACE_URL + "/raw/fixture-revision/"
DOCUMENTS = {
    "https://huggingface.co/api/spaces/" + ecosystem.SPACE: json.dumps({"sha": "fixture-revision"}),
    SPACE_ROOT + "README.md": "---\nmodels:\n- fixture-org/jev-fixture\n---\n# Index\n",
    SPACE_ROOT + "news.html": "<p>No links.</p>",
    SPACE_ROOT + "data/index.json": json.dumps({"models": [], "suite": {"label": "Fixture 1.0", "panel": 1, "jev_version": "1"}}),
    SPACE_ROOT + "data/methodology.json": json.dumps({"reproduce": {"github": "https://github.com/fixture-org/harness"}}),
    SPACE_ROOT + "data/vision.json": "{}",
    SPACE_ROOT + "data/v03.json": "{}",
}


def fetch(url):
    return DOCUMENTS[url].encode(), url, "text/plain"


def audit(seed):
    body = ("Jev fixture " + seed["url"]).encode()
    return dict(seed, retrieved_at="2026-10-17T00:00:00+00:00", verification_level="content_screened", status="screened",
                content_sha256=hashlib.sha256(body).hexdigest(), matched_topics=["Jev"]), []


class EcosystemSummaryTests(unittest.TestCase):
    def test_committed_summary_is_not_kept(self):
        self.assertFalse((ROOT / "data/ecosystem-sources.summary.json").exists(),
                         "Counts belong in the generated, checked data/source-counts.json")

    def test_full_collection_prints_summary_without_writing_it(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "data/ecosystem-sources.jsonl"
            printed = io.StringIO()
            argv = ["collect_ecosystem.py", "--output", str(output), "--max-depth", "0", "--workers", "1"]
            with patch.object(sys, "argv", argv), patch.object(ecosystem, "fetch", fetch), \
                    patch.object(ecosystem, "audit", audit), contextlib.redirect_stdout(printed):
                ecosystem.main()
            ledger = [json.loads(line) for line in output.read_text(encoding="utf-8").splitlines()]
            summary = json.loads(printed.getvalue().splitlines()[-1])
            self.assertEqual(summary["records"], len(ledger))
            self.assertTrue(output.with_suffix(".excluded.jsonl").exists())
            self.assertEqual(sorted(path.name for path in output.parent.iterdir()),
                             ["ecosystem-sources.excluded.jsonl", "ecosystem-sources.jsonl"])


if __name__ == "__main__":
    unittest.main()
