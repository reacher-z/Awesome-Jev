"""Exercise the shipped browser loader with controlled network outcomes, offline."""

from pathlib import Path
import shutil
import subprocess
import unittest


ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(shutil.which("node"), "Node is required for browser loader checks")
class CorpusLoadingTests(unittest.TestCase):
    def test_failure_requires_manual_retry_and_concurrent_clicks_share_one_request(self):
        script = r'''
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import vm from "node:vm";
import { translations } from "./site/catalog.mjs";
import { englishLang } from "./site/resource-view.mjs";

// Run the actual app with a small DOM substitute. No requests leave this process.
const source = readFileSync("site/app.js", "utf8")
  .replace(/^import .*;\n/gm, "");
const flush = () => new Promise(resolve => setImmediate(resolve));

function harness(language, firstFailure) {
  const nodes = new Map();
  let document;
  function node(selector) {
    if (!nodes.has(selector)) nodes.set(selector, {
      value: "", textContent: "", innerHTML: "", hidden: false,
      disabled: false, open: false, dataset: {}, handlers: {},
      addEventListener(type, fn) { (this.handlers[type] ??= []).push(fn); },
      emit(type) { return Promise.all((this.handlers[type] ?? []).map(fn => fn({}))); },
      focus() { document.activeElement = this; },
      setAttribute() {},
    });
    return nodes.get(selector);
  }
  document = {
    documentElement: {lang: language, classList: {add() {}}},
    activeElement: {tagName: "BODY", isContentEditable: false},
    querySelector: node,
    querySelectorAll: () => [],
    addEventListener() {},
  };
  const observers = [];
  class Observer {
    constructor(callback) { this.callback = callback; observers.push(this); }
    observe() {}
    disconnect() {}
  }
  let attempts = 0;
  let finishRetry;
  const fetch = async () => {
    attempts++;
    if (attempts === 1) {
      if (firstFailure === "network") throw new TypeError("Offline");
      if (firstFailure === "http") return {ok: false};
      return {ok: true, json: async () => { throw new SyntaxError("Invalid JSON"); }};
    }
    return new Promise(resolve => { finishRetry = resolve; });
  };
  const context = vm.createContext({
    resources: [], translations, renderResource: () => "", englishLang, document,
    window: {IntersectionObserver: Observer, location: {search: "", pathname: "/", hash: ""}},
    IntersectionObserver: Observer, fetch, URL, URLSearchParams, setTimeout, clearTimeout,
  });
  vm.runInContext(source, context);
  return {
    node, document, observers, attempts: () => attempts,
    finish: payload => finishRetry({ok: true, json: async () => payload}),
  };
}

for (const language of ["en", "zh"]) {
  for (const failure of ["network", "http", "json"]) {
    const app = harness(language, failure);
    assert.equal(app.attempts(), 0, "Initial rendering must preserve deferred loading");
    app.observers[0].callback([{isIntersecting: true}]);
    await flush();
    assert.equal(app.attempts(), 1);
    assert.equal(app.node("#corpus-status").textContent, translations[language].corpusLoadFailed);
    assert.equal(app.node("#corpus-recovery").hidden, false);
    assert.equal(app.node("#corpus-retry").disabled, false);

    // Reopening and another visibility event cannot silently retry the failure.
    app.node(".corpus-disclosure").open = true;
    await app.node(".corpus-disclosure").emit("toggle");
    app.observers[0].callback([{isIntersecting: true}]);
    await flush();
    assert.equal(app.attempts(), 1, "Retries require an explicit user action");

    const retryButton = app.node("#corpus-retry");
    retryButton.focus();
    const firstClick = retryButton.emit("click");
    const duplicateClick = retryButton.emit("click");
    assert.equal(app.attempts(), 2, "Rapid duplicate requests must share one fetch");
    assert.equal(retryButton.disabled, true);
    assert.equal(app.node("#corpus-recovery").hidden, false);
    assert.equal(app.node("#corpus-status").textContent, translations[language].corpusLoading);
    app.finish({counts: {checked_sources: 1, metadata_only: 0}, sources: [
      {title: "Recovered source", url: "https://example.org/paper", description: "Available after retry"},
    ]});
    await Promise.all([firstClick, duplicateClick]);
    assert.equal(app.node("#corpus-recovery").hidden, true);
    assert.equal(app.node("#corpus-status").textContent, translations[language].corpusResults(1, 1));
    assert.match(app.node("#corpus-list").innerHTML, /Recovered source/);
    // English titles and untranslated descriptions on Chinese pages carry lang="en".
    assert.equal(/<a [^>]*lang="en"[^>]*>Recovered source</.test(app.node("#corpus-list").innerHTML), language === "zh");
    assert.equal(app.node("#corpus-list").innerHTML.includes('<p lang="en">Available after retry</p>'), language === "zh");
    assert.equal(app.document.activeElement, app.node("#corpus-search"), "Focus must not remain in a hidden recovery panel");
    await app.node(".corpus-disclosure").emit("toggle");
    await retryButton.emit("click");
    assert.equal(app.attempts(), 2, "A successful response is cached for the page session");
  }
}
console.log("Passed network/HTTP/JSON failure recovery, manual-only retry, single flight, success cache, focus and EN/ZH states.");
'''
        result = subprocess.run(
            ["node", "--input-type=module"], input=script, text=True,
            cwd=ROOT, capture_output=True, timeout=20,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
