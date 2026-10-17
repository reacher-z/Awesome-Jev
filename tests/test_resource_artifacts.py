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

    def test_code_toggle_only_narrows_categories_with_artifact_records(self):
        script = r'''
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import vm from "node:vm";
import { resources, translations } from "./site/catalog.mjs";
import { englishLang, renderResource, hasCode } from "./site/resource-view.mjs";

// Run the shipped homepage script against the real catalog with a small DOM substitute.
const source = readFileSync("site/app.js", "utf8").replace(/^import .*;\n/gm, "");
const nodes = new Map();
const node = selector => {
  if (!nodes.has(selector)) nodes.set(selector, {
    value: "", textContent: "", innerHTML: "", hidden: false, checked: false, disabled: false,
    dataset: {}, handlers: {},
    addEventListener(type, fn) { (this.handlers[type] ??= []).push(fn); },
    emit(type) { (this.handlers[type] ?? []).forEach(fn => fn({})); },
    focus() {}, setAttribute() {},
  });
  return nodes.get(selector);
};
const document = {
  documentElement: {lang: "en", classList: {add() {}}},
  querySelector: node, querySelectorAll: () => [], addEventListener() {},
};
class Observer { observe() {} disconnect() {} }
const context = vm.createContext({
  resources, translations, renderResource, englishLang, hasCode, document,
  window: {IntersectionObserver: Observer, location: {search: "", pathname: "/", hash: ""}},
  IntersectionObserver: Observer, URL, URLSearchParams, setTimeout, clearTimeout,
});
vm.runInContext(source, context);
const toggle = node("#code-filter");
const shown = () => (node("#resource-list").innerHTML.match(/<article class="resource-row"/g) ?? []).length;

// Only papers carry artifact records, which is what the "Papers with code" label promises.
assert.ok(resources.filter(row => row.artifacts).every(row => row.category === "Papers"),
  'Rename the "Papers with code" toggle when another category gains artifact records');
assert.equal(translations.en.filterHasCode, "Papers with code");
assert.equal(translations.zh.filterHasCode, "有代码的论文");

for (const category of ["All", ...new Set(resources.map(row => row.category))]) {
  const rows = resources.filter(row => category === "All" || row.category === category);
  context.selectFilter(category);
  toggle.checked = true;
  toggle.emit("change");
  if (rows.some(row => row.artifacts)) {
    assert.equal(toggle.disabled, false, category);
    assert.equal(shown(), rows.filter(hasCode).length, category);
    assert.ok(shown() > 0, category);
  } else {
    // Ticking the toggle in Tools or Models once emptied the list; now it does not apply there.
    assert.equal(toggle.disabled, true, category);
    assert.equal(toggle.checked, false, category);
    assert.equal(shown(), rows.length, category);
  }
}
'''
        result = subprocess.run(["node", "--input-type=module", "-e", script],
                                cwd=ROOT, text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
