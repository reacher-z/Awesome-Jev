"""Generated pages keep a heading outline that never skips a level."""

from html.parser import HTMLParser
import re
import unittest

from test_site_discovery import ROOT, ROUTES


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

    def test_paper_directories_label_their_card_list_with_the_paper_count(self):
        for route, label in (("/papers/", "Selected papers"), ("/zh/papers/", "精选论文")):
            with self.subTest(route=route):
                outline = HeadingOutline((ROOT / "site" / route.strip("/") / "index.html").read_text(encoding="utf-8"))
                cards = outline.levels.count(3)
                self.assertGreater(cards, 0)
                self.assertEqual(outline.levels, [1, 2] + [3] * cards)
                self.assertEqual(outline.texts[1], f"{label} ({cards})")


if __name__ == "__main__":
    unittest.main()
