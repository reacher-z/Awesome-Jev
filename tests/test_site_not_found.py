"""The generated 404 page routes readers back to both languages without being indexed."""

import re
import unittest
from urllib.parse import urlsplit

from test_site_discovery import BASE, ROOT, CrawlPage


class NotFoundPageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = (ROOT / "site/404.html").read_text(encoding="utf-8")
        cls.page = CrawlPage(cls.source)

    def test_not_found_page_is_noindex_without_canonical_alternates_or_structured_data(self):
        self.assertTrue(any("noindex" in re.split(r"[,\s]+", value.lower()) for value in self.page.robots))
        self.assertEqual(self.page.canonicals, [])
        self.assertEqual(self.page.alternates, [])
        self.assertEqual(self.page.structured, [])
        self.assertNotIn("/404.html", (ROOT / "site/sitemap.xml").read_text())

    def test_not_found_page_links_back_to_both_languages_with_root_absolute_urls(self):
        self.assertTrue({"/", "/zh/", "/topics/", "/zh/topics/", "/sitemap.xml"}.issubset(self.page.links))
        self.assertRegex("".join(self.page.body_text), r"[\u4e00-\u9fff]", "The page must also address Chinese readers")
        self.assertEqual(len(self.page.headings), 1)
        # GitHub Pages serves this file at any depth, so relative URLs would break.
        urls = self.page.links + self.page.stylesheets + re.findall(r'<link\b[^>]*\bhref="([^"]+)"', self.source)
        for url in urls:
            with self.subTest(url=url):
                parsed = urlsplit(url)
                self.assertTrue(parsed.scheme in {"http", "https"} or url.startswith(("/", "#")), url)
                if not parsed.scheme and url.startswith("/"):
                    target = ROOT / "site" / parsed.path.lstrip("/")
                    self.assertTrue((target / "index.html" if parsed.path.endswith("/") else target).is_file(), url)
        self.assertTrue(all(not url.startswith(BASE + "/404") for url in urls))


if __name__ == "__main__":
    unittest.main()
