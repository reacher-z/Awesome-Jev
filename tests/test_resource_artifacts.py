"""Artifact chips name their kind and paper, and the homepage "Has code" count matches the catalog."""

from pathlib import Path
import shutil
import subprocess
import unittest


ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(shutil.which("node"), "Node is required for shared renderer checks")
class ResourceArtifactTests(unittest.TestCase):
    def test_chips_render_every_artifact_link_with_an_accessible_name(self):
        script = r'''
import assert from "node:assert/strict";
import {readFileSync} from "node:fs";
import {resources, translations} from "./site/catalog.mjs";
import {renderResource, artifactLinks, hasCode} from "./site/resource-view.mjs";
const decode = text => text.replace(/&amp;/g, "&").replace(/&quot;/g, '"').replace(/&#39;/g, "'").replace(/&lt;/g, "<").replace(/&gt;/g, ">");
for (const resource of resources.filter(row => row.artifacts)) {
  for (const language of ["en", "zh"]) {
    const markup = renderResource(resource, language, translations);
    const chips = [...markup.matchAll(/<a class="artifact-chip" href="([^"]+)"[^>]*aria-label="([^"]+)">.*?<\/svg>([^<]+)<\/a>/g)];
    assert.deepEqual(chips.map(chip => decode(chip[1])), artifactLinks(resource).map(link => link.url), `${language}: ${resource.title}`);
    for (const [, , name, label] of chips) {
      assert.ok(decode(name).includes(decode(label)) && decode(name).includes(resource.title), `${language}: chip name "${name}"`);
    }
    assert.equal(markup.includes("artifact-unverified"), Boolean(resource.artifacts.unverified), `${language}: ${resource.title}`);
  }
}
const paper = resources.find(row => row.artifacts?.unverified === "code");
assert.ok(paper, "the README marks one paper's code as not verified");
assert.match(renderResource(paper, "en", translations), /Code not verified/);
assert.match(renderResource(paper, "zh", translations), /代码未核验/);
assert.ok(!hasCode(paper), "unverified code does not count as available code");
const count = resources.filter(hasCode).length;
for (const page of ["site/index.html", "site/zh/index.html"]) {
  const html = readFileSync(page, "utf8");
  assert.match(html, new RegExp(`id="code-filter" />.*?<span class="filter-count" aria-hidden="true">${count}</span>`), page);
}
'''
        result = subprocess.run(["node", "--input-type=module", "-e", script],
                                cwd=ROOT, text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
