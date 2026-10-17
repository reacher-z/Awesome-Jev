"""The homepage's first paint already matches what app.js renders, so start-up shifts nothing."""

from pathlib import Path
import shutil
import subprocess
import unittest


ROOT = Path(__file__).resolve().parents[1]
HOMEPAGES = ("site/index.html", "site/zh/index.html")
JS_CLASS = '<script>document.documentElement.classList.add("js")</script>'


class InitialRenderTests(unittest.TestCase):
    def test_script_only_controls_are_revealed_before_first_paint(self):
        # A class set by the deferred module would reveal the controls after the rows had painted.
        for page in HOMEPAGES:
            head = (ROOT / page).read_text(encoding="utf-8").split("</head>", 1)[0]
            self.assertTrue(JS_CLASS in head, f"{page} must set the js class in <head>")
            self.assertLess(head.index(JS_CLASS), head.index('<link rel="stylesheet"'), page)

    @unittest.skipUnless(shutil.which("node"), "Node is required to run app.js")
    def test_app_keeps_the_generated_rows_and_filter_buttons(self):
        script = r'''
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import vm from "node:vm";
import { resources, translations } from "./site/catalog.mjs";
import * as view from "./site/resource-view.mjs";

const source = readFileSync("site/app.js", "utf8").replace(/^import .*;\n/gm, "");
for (const [language, page] of [["en", "site/index.html"], ["zh", "site/zh/index.html"]]) {
  const html = readFileSync(page, "utf8");
  const generated = Object.fromEntries([...html.matchAll(/<button\b[^>]*data-filter="([^"]+)"[^>]*>([\s\S]*?)<\/button>/g)]
    .map(([, filter, content]) => [filter, content]));
  assert.ok(Object.keys(generated).length > 1, "Expected generated filter buttons");
  const nodes = new Map();
  const node = selector => {
    if (!nodes.has(selector)) nodes.set(selector, {
      value: "", textContent: "", innerHTML: "generated rows", hidden: false, checked: false, disabled: false,
      dataset: {}, addEventListener() {}, focus() {}, setAttribute() {},
    });
    return nodes.get(selector);
  };
  const buttons = Object.entries(generated).map(([filter, content]) => ({
    dataset: {filter}, innerHTML: content, classList: {toggle() {}}, setAttribute() {},
    addEventListener(type, fn) { this.click = fn; },
  }));
  const document = {
    documentElement: {lang: language === "zh" ? "zh-CN" : "en", classList: {add() {}}},
    activeElement: {tagName: "BODY"},
    querySelector: node,
    querySelectorAll: selector => (selector === "[data-filter]" ? buttons : []),
    addEventListener() {},
  };
  vm.runInContext(source, vm.createContext({
    ...view, resources, translations, document, URL, URLSearchParams, setTimeout, clearTimeout,
    window: {location: {search: "", pathname: "/", hash: ""}}, fetch: () => new Promise(() => {}),
  }));
  for (const button of buttons) {
    assert.equal(button.innerHTML, generated[button.dataset.filter], `${language} ${button.dataset.filter} button changed at start-up`);
  }
  assert.equal(node("#resource-list").innerHTML, "generated rows", `${language}: start-up must keep the generated rows`);
  buttons.find(button => button.dataset.filter === "Papers").click();
  assert.notEqual(node("#resource-list").innerHTML, "generated rows", "Filtering renders rows");
  buttons.find(button => button.dataset.filter === "All").click();
  assert.equal(node("#resource-list").innerHTML, resources.map(row => view.renderResource(row, language, translations)).join(""));
}
console.log("Start-up keeps the generated rows and filter buttons in EN and ZH.");
'''
        result = subprocess.run(
            ["node", "--input-type=module"], input=script, text=True,
            cwd=ROOT, capture_output=True, timeout=30,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
