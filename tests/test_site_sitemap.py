"""The sitemap and each page head declare the same hreflang language cluster."""

from pathlib import Path
import unittest
from urllib.parse import urlsplit
import xml.etree.ElementTree as ET

from test_site_discovery import BASE, ROOT, CrawlPage

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


if __name__ == "__main__":
    unittest.main()
