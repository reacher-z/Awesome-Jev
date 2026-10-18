"""Generated pages keep their content inside landmarks, with the primary content in <main>."""

from html.parser import HTMLParser
import unittest

from test_site_discovery import ROOT, ROUTES

VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}
LANDMARKS = {"header", "nav", "main", "footer", "aside"}


class Landmarks(HTMLParser):
    def __init__(self, source):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.mains = 0
        self.outside = []        # visible text outside every landmark
        self.nested_asides = 0   # complementary landmarks inside <main>
        self.in_main = {}        # id or class -> whether that section sits inside <main>
        self.feed(source)

    def _inside(self, *tags):
        return any(tag in tags for tag, _ in self.stack)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "main":
            self.mains += 1
        if tag == "aside" and self._inside("main"):
            self.nested_asides += 1
        if tag == "section":
            key = attrs.get("id") or " ".join(attrs.get("class", "").split()[:1])
            if key:
                self.in_main[key] = self._inside("main")
        if tag not in VOID:
            self.stack.append((tag, attrs))

    def handle_startendtag(self, tag, attrs):
        if tag not in VOID:
            self.handle_starttag(tag, attrs)
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        for index in range(len(self.stack) - 1, -1, -1):
            if self.stack[index][0] == tag:
                del self.stack[index:]
                return

    def handle_data(self, value):
        text = value.strip()
        if not text or not self._inside("body") or self._inside("script", "noscript", *LANDMARKS):
            return
        if any("skip-link" in attrs.get("class", "").split() for _, attrs in self.stack):
            return
        self.outside.append(text)


def page(route):
    return Landmarks((ROOT / "site" / route.strip("/") / "index.html").read_text(encoding="utf-8"))


class LandmarkTests(unittest.TestCase):
    def test_every_page_keeps_content_in_landmarks(self):
        for route in ROUTES:
            with self.subTest(route=route):
                landmarks = page(route)
                self.assertEqual(landmarks.mains, 1)
                self.assertEqual(landmarks.outside, [], "Text outside header, nav, main, aside and footer")
                self.assertEqual(landmarks.nested_asides, 0, "No complementary landmark inside <main>")

    def test_homepage_quick_start_and_contribute_sections_are_in_main(self):
        for route in ("/", "/zh/"):
            with self.subTest(route=route):
                sections = page(route).in_main
                for key in ("collection", "corpus", "start", "contribute-section"):
                    self.assertIs(sections.get(key), True, f"{key} must be inside <main>")


if __name__ == "__main__":
    unittest.main()
