"""The legacy ecosystem collector grades index files by what it fetched; it never grants editorial review."""

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

SPACE_ROOT = ecosystem.SPACE_URL + "/raw/crafted-revision/"
# Crafted files whose content contradicts the evidence the collector used to hard-code:
# no benchmarks, no scoring weights, no entrants.
DOCUMENTS = {
    "https://huggingface.co/api/spaces/" + ecosystem.SPACE: json.dumps({"sha": "crafted-revision"}),
    SPACE_ROOT + "README.md": "---\nmodels:\n---\n# Index\n",
    SPACE_ROOT + "news.html": "<p>No links.</p>",
    SPACE_ROOT + "data/index.json": json.dumps({"models": [], "suite": {"label": "Crafted 0.0", "panel": 0, "jev_version": "0"}}),
    SPACE_ROOT + "data/methodology.json": json.dumps({"benchmarks": [], "reproduce": {"github": "https://github.com/fixture-org/harness"}}),
    SPACE_ROOT + "data/vision.json": "{}",
    SPACE_ROOT + "data/v03.json": "{}",
}
HARD_CODED = ("37 public benchmarks", "0.3.2 scoring correction", "0.2/0.5/0.3", "0.5/0.5",
              "separates trained models", "Inspected community tracker source")


def fetch(url):
    return DOCUMENTS[url].encode(), url, "text/plain"


def unavailable(seed):
    return dict(seed, retrieved_at="2026-10-17T00:00:00+00:00", verification_level="metadata_only", status="unavailable"), []


class LegacyIndexGradeTests(unittest.TestCase):
    def collect(self, prior=()):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "ecosystem-sources.jsonl"
            if prior:
                output.write_text("".join(json.dumps(row) + "\n" for row in prior), encoding="utf-8", newline="\n")
            printed = io.StringIO()
            argv = ["collect_ecosystem.py", "--output", str(output), "--max-depth", "0", "--workers", "1"]
            with patch.object(sys, "argv", argv), patch.object(ecosystem, "fetch", fetch), \
                    patch.object(ecosystem, "audit", unavailable), contextlib.redirect_stdout(printed):
                ecosystem.main()
            ledger = [json.loads(line) for line in output.read_text(encoding="utf-8").splitlines()]
        index_files = {row["title"].removeprefix("Jev Decision Index — "): row for row in ledger
                       if row["topic"] == "community-evaluation-index"}
        self.assertEqual(sorted(index_files), ["README.md", "data/index.json", "data/methodology.json",
                                               "data/v03.json", "data/vision.json", "news.html"])
        return index_files, json.loads(printed.getvalue().splitlines()[-1])

    def test_index_files_are_content_screened_not_editorially_reviewed(self):
        index_files, summary = self.collect()
        for name, row in index_files.items():
            with self.subTest(file=name):
                self.assertEqual(row["verification_level"], "content_screened")
                self.assertIn("not editorial review", row["checked_via"])
        self.assertNotIn("editorial_reviewed", summary["verification_levels"])

    def test_evidence_describes_the_fetched_content(self):
        index_files, _ = self.collect()
        for name, row in index_files.items():
            for claim in HARD_CODED:
                with self.subTest(file=name, claim=claim):
                    self.assertNotIn(claim, row["evidence"])
        self.assertIn("0 entrant records", index_files["data/index.json"]["evidence"])
        self.assertIn("0 benchmark entries", index_files["data/methodology.json"]["evidence"])
        self.assertIn("0 links", index_files["news.html"]["evidence"])

    def test_rerun_keeps_an_editorial_review_of_unchanged_content(self):
        # docs/maintenance.md: a rebuild keeps a documented review while the
        # URL, revision and fetched bytes still match, as the scheduled scan does.
        def reviewed(name, url, content):
            return {"url": url, "title": "Jev Decision Index — " + name, "topic": "community-evaluation-index",
                    "relation": "direct", "verification_level": "editorial_reviewed", "status": "screened",
                    "retrieved_at": "2026-10-16T00:00:00+00:00", "checked_via": "Fixture maintainer review.",
                    "retrieved_url": SPACE_ROOT + name, "resolved_revision": "crafted-revision",
                    "content_sha256": hashlib.sha256(content.encode()).hexdigest(), "content_bytes": len(content),
                    "evidence": "Fixture reviewed evidence for " + name + ".", "review_scope": "Fixture review scope.",
                    "relevance": "Fixture relevance.", "discovered_from": [ecosystem.SPACE_URL]}
        blob = ecosystem.SPACE_URL + "/blob/crafted-revision/"
        unchanged = reviewed("README.md", ecosystem.SPACE_URL, DOCUMENTS[SPACE_ROOT + "README.md"])
        changed = reviewed("data/index.json", blob + "data/index.json", "earlier reviewed bytes")
        other_revision = dict(reviewed("data/v03.json", blob + "data/v03.json", DOCUMENTS[SPACE_ROOT + "data/v03.json"]),
                              resolved_revision="earlier-revision")
        index_files, summary = self.collect([unchanged, changed, other_revision])
        self.assertEqual(index_files["README.md"], unchanged)
        for name in ("data/index.json", "data/v03.json"):
            with self.subTest(file=name):
                self.assertEqual(index_files[name]["verification_level"], "content_screened")
                self.assertIn("not editorial review", index_files[name]["checked_via"])
                self.assertNotIn("review_scope", index_files[name])
        self.assertEqual(summary["verification_levels"]["editorial_reviewed"], 1)
        self.assertEqual(summary["verification_levels"]["content_screened"], 5)


if __name__ == "__main__":
    unittest.main()
