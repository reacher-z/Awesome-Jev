"""Generated pages keep a heading outline that never skips a level."""

from html.parser import HTMLParser
import re
import unittest

from test_site_discovery import ROOT, ROUTES, TOPIC_SLUGS, CrawlPage


class HeadingOutline(HTMLParser):
    def __init__(self, source):
        super().__init__(convert_charrefs=True)
        self.levels = []
        self.texts = []
        self._text = None
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        if re.fullmatch(r"h[1-6]", tag):
            self.levels.append(int(tag[1]))
            self._text = []

    def handle_endtag(self, tag):
        if re.fullmatch(r"h[1-6]", tag) and self._text is not None:
            self.texts.append(re.sub(r"\s+", " ", "".join(self._text)).strip())
            self._text = None

    def handle_data(self, value):
        if self._text is not None:
            self._text.append(value)


class HeadingOrderTests(unittest.TestCase):
    def test_no_generated_page_skips_a_heading_level(self):
        for route in ROUTES:
            with self.subTest(route=route):
                outline = HeadingOutline((ROOT / "site" / route.strip("/") / "index.html").read_text(encoding="utf-8"))
                self.assertEqual(outline.levels[:1], [1])
                for previous, current in zip(outline.levels, outline.levels[1:]):
                    self.assertLessEqual(current, previous + 1, f"h{previous} is followed by h{current}")

    def test_paper_directories_label_their_table_with_the_paper_count(self):
        for route, label in (("/papers/", "Selected papers"), ("/zh/papers/", "精选论文")):
            with self.subTest(route=route):
                source = (ROOT / "site" / route.strip("/") / "index.html").read_text(encoding="utf-8")
                outline = HeadingOutline(source)
                rows = len(CrawlPage(source).cards)
                self.assertGreater(rows, 0)
                # The table's heading, then the heading of the related-topic links that end the page.
                self.assertEqual(outline.levels, [1, 2, 2])
                self.assertEqual(outline.texts[1], f"{label} ({rows})")

    def test_topic_link_lists_are_named_by_a_visible_heading(self):
        sections = {"guide": ("Related research topics", "相关研究专题"), "papers": ("Related research topics", "相关研究专题")}
        sections.update({f"topics/{slug}": ("Continue reading", "继续阅读") for slug in TOPIC_SLUGS})
        for prefix, language in (("/", 0), ("/zh/", 1)):
            for section, headings in sections.items():
                route = f"{prefix}{section}/"
                with self.subTest(route=route):
                    source = (ROOT / "site" / route.strip("/") / "index.html").read_text(encoding="utf-8")
                    match = re.search(r'<h2 id="related-topics">([^<]+)</h2><nav class="document-toc" aria-labelledby="related-topics"><ul>(.*?)</ul></nav>', source)
                    self.assertIsNotNone(match, "The topic links need a visible heading that names the list")
                    self.assertEqual(match.group(1), headings[language])
                    self.assertIn(f'href="{prefix}topics/', match.group(2))


if __name__ == "__main__":
    unittest.main()
