"""Keep the curated paper metadata exported to papers.json uniform."""

from pathlib import Path
import shutil
import subprocess
import unittest


ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(shutil.which("node"), "Node is required to load the site catalog")
class PaperMetadataTests(unittest.TestCase):
    def test_every_paper_records_its_first_submission_date(self):
        script = r'''
import assert from "node:assert/strict";
import {resources} from "./site/catalog.mjs";
const papers = resources.filter(row => row.category === "Papers");
assert.ok(papers.length > 0);
for (const paper of papers) {
  const version = paper.url.match(/arxiv\.org\/abs\/\d{4}\.\d{4,5}(v\d+)$/)?.[1];
  assert.ok(version, `Unversioned arXiv URL: ${paper.url}`);
  assert.match(paper.first_submitted ?? "", /^\d{4}-\d{2}-\d{2}$/, `Missing first_submitted: ${paper.url}`);
  if (version === "v1") assert.equal(paper.first_submitted, paper.date, `A v1 link was first submitted on its listed date: ${paper.url}`);
  else assert.ok(paper.first_submitted <= paper.date, `Revision dated before its first submission: ${paper.url}`);
}
'''
        result = subprocess.run(["node", "--input-type=module", "-e", script],
                                cwd=ROOT, text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
