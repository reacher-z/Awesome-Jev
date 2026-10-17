"""Social metadata is shared by every page, with image alt text and labels in the page language."""

from html.parser import HTMLParser
import re
import struct
import unittest

from test_site_discovery import ROOT, ROUTES, CrawlPage

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



class HeadMeta(HTMLParser):
    def __init__(self, source):
        super().__init__(convert_charrefs=True)
        self.meta = {}
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        name = attrs.get("property") or attrs.get("name")
        if tag == "meta" and name:
            self.meta.setdefault(name, []).append(attrs.get("content", ""))


class SharedSocialMetadataTests(unittest.TestCase):
    def test_every_page_has_the_same_social_card_in_its_language(self):
        width, height = struct.unpack(">II", (ROOT / "site/assets/social.png").read_bytes()[16:24])
        for route in ROUTES:
            with self.subTest(route=route):
                zh = route.startswith("/zh/")
                meta = HeadMeta((ROOT / "site" / route.strip("/") / "index.html").read_text(encoding="utf-8")).meta
                image = "https://awesomejev.github.io/assets/social.png"
                expected = {
                    "og:image": [image], "og:image:type": ["image/png"],
                    "og:image:width": [str(width)], "og:image:height": [str(height)],
                    "twitter:card": ["summary_large_image"], "twitter:image": [image],
                    "og:locale": ["zh_CN" if zh else "en_US"], "og:locale:alternate": ["en_US" if zh else "zh_CN"],
                }
                self.assertEqual({key: meta.get(key) for key in expected}, expected)
                alts = meta["og:image:alt"] + meta["twitter:image:alt"]
                self.assertEqual(len(alts), 2)
                self.assertEqual(len(set(alts)), 1)
                if zh:
                    self.assertRegex(alts[0], CJK)
                else:
                    self.assertEqual(alts[0], ENGLISH_ALT)

    def test_article_pages_state_the_dates_in_their_structured_data(self):
        for route in ROUTES:
            source = (ROOT / "site" / route.strip("/") / "index.html").read_text(encoding="utf-8")
            meta = HeadMeta(source).meta
            if meta["og:type"] != ["article"]:
                self.assertNotIn("article:modified_time", meta, route)
                continue
            with self.subTest(route=route):
                graph = CrawlPage(source).structured[0]["@graph"]
                article = next(node["mainEntity"] for node in graph if node.get("@id", "").endswith("#page"))
                self.assertEqual(article["@type"], "Article")
                self.assertEqual(meta["article:modified_time"], [article["dateModified"]])
                self.assertEqual(meta.get("article:published_time"), [article["datePublished"]] if "datePublished" in article else None)
                self.assertEqual(article["image"]["url"], meta["og:image"][0])
                if "/topics/" in route:
                    self.assertIn("article:published_time", meta)

if __name__ == "__main__":
    unittest.main()
