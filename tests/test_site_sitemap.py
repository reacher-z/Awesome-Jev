"""The sitemap and each page head declare the same hreflang language cluster, and lastmod follows content."""

import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from urllib.parse import urlsplit
import xml.etree.ElementTree as ET

from test_site_discovery import BASE, BUILD_INPUTS, ROOT, CrawlPage

NS = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9", "xhtml": "http://www.w3.org/1999/xhtml"}


class SitemapAlternateTests(unittest.TestCase):
    def test_sitemap_alternates_match_each_page_alternate_links(self):
        tree = ET.fromstring((ROOT / "site/sitemap.xml").read_bytes())
        entries = tree.findall("sm:url", NS)
        self.assertTrue(entries)
        for entry in entries:
            location = entry.find("sm:loc", NS).text
            with self.subTest(location=location):
                listed = sorted((link.get("hreflang"), link.get("href")) for link in entry.findall("xhtml:link", NS)
                                if link.get("rel") == "alternate")
                path = ROOT / "site" / urlsplit(location).path.strip("/") / "index.html"
                declared = sorted(CrawlPage(path.read_text(encoding="utf-8")).alternates)
                self.assertEqual(listed, declared)
                self.assertIn(("x-default", dict(declared).get("en")), listed)
                self.assertTrue(dict(listed)["en"].startswith(BASE + "/"))


def lastmods(root):
    tree = ET.fromstring((root / "site/sitemap.xml").read_bytes())
    return {urlsplit(entry.find("sm:loc", NS).text).path: entry.find("sm:lastmod", NS).text
            for entry in tree.findall("sm:url", NS)}


@unittest.skipUnless(shutil.which("node"), "Node is required to build the site")
class SitemapLastmodTests(unittest.TestCase):
    def build(self, root):
        result = subprocess.run([shutil.which("node"), "scripts/build_site.mjs"], cwd=root,
                                capture_output=True, text=True, encoding="utf-8", timeout=45)
        self.assertEqual(result.returncode, 0, result.stderr)
        return lastmods(root)

    def edit(self, path, change):
        data = json.loads(path.read_text(encoding="utf-8"))
        change(data)
        path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8", newline="\n")
        return data

    def test_directory_lastmod_follows_the_newest_entry_it_renders(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for name in BUILD_INPUTS:
                destination = root / name
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / name, destination)
            before = self.build(root)
            # A revised topic and a newly retrieved addition, without touching the curated contentDate.
            topics = self.edit(root / "data/research-topics.json",
                               lambda data: data["topics"][0].update(updated="2099-01-02"))
            self.edit(root / "data/expansion-progress-2026-10-16.json",
                      lambda data: data["additions"][0].update(retrieved_at="2099-01-03T04:05:06+00:00"))
            after = self.build(root)
            edited_topic = "topics/" + topics["topics"][0]["slug"] + "/"
            expected = dict(before)
            for language in ("/", "/zh/"):
                expected.update({language + "topics/": "2099-01-02", language + edited_topic: "2099-01-02",
                                 language + "discoveries/": "2099-01-03"})
            self.assertEqual(after, expected)
            for language in ("", "zh"):
                page = (root / "site" / language / "discoveries/index.html").read_text(encoding="utf-8")
                self.assertTrue('<time datetime="2099-01-03">2099-01-03</time> · <a href="/data/expansion-progress.json">' in page,
                                f"/{language}/discoveries/ does not show the newest retrieval date")

if __name__ == "__main__":
    unittest.main()
