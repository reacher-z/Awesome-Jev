"""The homepage's image alt text and wordmark label follow the page language."""

from html.parser import HTMLParser
import re
import unittest

from test_site_discovery import ROOT

CJK = re.compile(r"[㐀-鿿]")
ENGLISH_ALT = "AwesomeJev — an independent field guide to typed decision models. Research, models, tools, and evidence."


class HomeLabels(HTMLParser):
    def __init__(self, source):
        super().__init__(convert_charrefs=True)
        self.image_alts = {}
        self.wordmark = None
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        name = attrs.get("property") or attrs.get("name")
        if tag == "meta" and name in {"og:image:alt", "twitter:image:alt"}:
            self.image_alts[name] = attrs.get("content", "")
        if tag == "a" and "wordmark" in attrs.get("class", "").split():
            self.wordmark = attrs.get("aria-label")


class HomepageLabelLanguageTests(unittest.TestCase):
    def labels(self, route):
        return HomeLabels((ROOT / "site" / route).read_text(encoding="utf-8"))

    def test_chinese_homepage_has_chinese_image_alt_and_wordmark_label(self):
        page = self.labels("zh/index.html")
        self.assertEqual(set(page.image_alts), {"og:image:alt", "twitter:image:alt"})
        for name, alt in page.image_alts.items():
            with self.subTest(meta=name):
                self.assertRegex(alt, CJK)
                self.assertNotIn("field guide", alt)
        self.assertEqual(len(set(page.image_alts.values())), 1)
        self.assertEqual(page.wordmark, "AwesomeJev 首页")

    def test_english_homepage_keeps_english_labels(self):
        page = self.labels("index.html")
        self.assertEqual(page.image_alts, {"og:image:alt": ENGLISH_ALT, "twitter:image:alt": ENGLISH_ALT})
        self.assertEqual(page.wordmark, "AwesomeJev home")


if __name__ == "__main__":
    unittest.main()
