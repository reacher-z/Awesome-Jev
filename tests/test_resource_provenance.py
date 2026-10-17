"""Check evidence markers on actual curated resources in both languages."""

from pathlib import Path
import re
import shutil
import subprocess
import unittest


ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(shutil.which("node"), "Node is required for shared renderer checks")
class ResourceProvenanceTests(unittest.TestCase):
    def test_markers_name_publisher_and_evidence(self):
        script = r'''
import assert from "node:assert/strict";
import {resources, translations} from "./site/catalog.mjs";
import {renderResource} from "./site/resource-view.mjs";
const marker = markup => markup.match(/class="evidence-marker"><span class="evidence-glyph" data-source="([a-z]+)" aria-hidden="true"><\/span>([^<]+)</)?.slice(1);
const cases = [
  ["https://github.com/bufbuild/protoc-gen-jev", "community", "Community · screened", "社区 · 已筛查"],
  ["https://github.com/evan-py-chen/jev-survey", "community", "Community · screened", "社区 · 已筛查"],
  ["https://github.com/earino/zero-shot-complaint-benchmark", "community", "Community · screened", "社区 · 已筛查"],
  ["https://github.com/typesafe-ai/typesafe-sdk-python", "official", "Official · author-reported", "官方 · 作者报告"],
  ["https://github.com/typesafe-ai/WorkflowEvals", "official", "Official · author-reported", "官方 · 作者报告"],
  ["https://huggingface.co/collections/typesafeAI/workflowevals", "official", "Official · author-reported", "官方 · 作者报告"],
  ["https://huggingface.co/Cloudflare/clef", "community", "Community · author-reported", "社区 · 作者报告"],
  ["https://proceedings.mlr.press/v70/guo17a.html", "background", "Background · author-reported", "背景文献 · 作者报告"],
];
for (const [url, source, en, zh] of cases) {
  const resource = resources.find(row => row.url === url);
  assert.ok(resource, `Missing regression resource: ${url}`);
  for (const [language, expected] of [["en", en], ["zh", zh]]) {
    assert.deepEqual(marker(renderResource(resource, language, translations)), [source, expected], `${language}: ${url}`);
  }
}
for (const resource of resources) {
  const expected = resource.category === "Papers" ? ["preprint", "Preprint · author-reported"] : undefined;
  const found = marker(renderResource(resource, "en", translations));
  assert.ok(found, `No evidence marker: ${resource.url}`);
  if (expected) assert.deepEqual(found, expected, resource.url);
}
'''
        result = subprocess.run(["node", "--input-type=module", "-e", script],
                                cwd=ROOT, text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_homepage_legend_explains_every_marker_and_links_to_the_method(self):
        method = "https://github.com/reacher-z/Awesome-Jev/blob/main/docs/source-audit.md#evidence-markers"
        self.assertIn("\n## Evidence markers\n", (ROOT / "docs/source-audit.md").read_text(encoding="utf-8"))
        words = {"site/index.html": ["Official", "Preprint", "Community", "Background", "author-reported", "screened", "reproduced"],
                 "site/zh/index.html": ["官方", "预印本", "社区", "背景文献", "作者报告", "已筛查", "已复现"]}
        for page, expected in words.items():
            with self.subTest(page=page):
                html = (ROOT / page).read_text(encoding="utf-8")
                legends = re.findall(r'<p class="evidence-legend">(.*?)</p>', html)
                self.assertEqual(len(legends), 1)
                self.assertIn(f'href="{method}"', legends[0])
                text = re.sub(r"<[^>]+>", " ", legends[0])
                for word in expected:
                    self.assertIn(word, text)
                for source in ("official", "preprint", "community", "background"):
                    self.assertIn(f'data-source="{source}"', legends[0])


if __name__ == "__main__":
    unittest.main()
