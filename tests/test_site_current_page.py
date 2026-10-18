"""Generated pages mark the current page in the main navigation, breadcrumb and topic links."""

from html.parser import HTMLParser
import unittest

from test_site_discovery import ROOT, TOPIC_SLUGS

SECTIONS = ("papers", "models", "topics", "discoveries", "guide")


class Navigation(HTMLParser):
    def __init__(self, source):
        super().__init__(convert_charrefs=True)
        self.nav = []          # (href, aria-current) for each main-nav link
        self.crumb_leaf = None  # aria-current of the breadcrumb's last element
        self.continue_links = []
        self._in = None
        self._after_continue = False
        self._heading = None
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        classes = attrs.get("class", "").split()
        if tag == "nav" and "main-nav" in classes:
            self._in = "nav"
        elif tag == "nav" and "breadcrumbs" in classes:
            self._in = "crumbs"
        elif tag == "nav" and "document-toc" in classes and self._after_continue:
            self._in = "continue"
        elif tag == "a" and self._in == "nav":
            self.nav.append((attrs.get("href"), attrs.get("aria-current")))
        elif tag == "a" and self._in == "continue":
            self.continue_links.append(attrs.get("href"))
        elif self._in == "crumbs" and tag in {"a", "span"} and attrs.get("aria-hidden") != "true":
            self.crumb_leaf = attrs.get("aria-current")
        if tag == "h2":
            self._heading = []

    def handle_endtag(self, tag):
        if tag == "nav":
            self._in = None
        if tag == "h2" and self._heading is not None:
            self._after_continue = "".join(self._heading).strip() in {"Continue reading", "继续阅读"}
            self._heading = None

    def handle_data(self, value):
        if self._heading is not None:
            self._heading.append(value)


def page(route):
    return Navigation((ROOT / "site" / route.strip("/") / "index.html").read_text(encoding="utf-8"))


class CurrentPageTests(unittest.TestCase):
    def test_section_pages_mark_their_own_nav_link_and_breadcrumb(self):
        for prefix in ("/", "/zh/"):
            for section in SECTIONS:
                route = f"{prefix}{section}/"
                with self.subTest(route=route):
                    nav = page(route)
                    self.assertEqual([href for href, current in nav.nav if current], [route])
                    self.assertEqual(dict(nav.nav)[route], "page")
                    self.assertEqual(nav.crumb_leaf, "page")

    def test_topic_notes_mark_the_topics_section_and_skip_themselves(self):
        for prefix in ("/", "/zh/"):
            for slug in TOPIC_SLUGS:
                route = f"{prefix}topics/{slug}/"
                with self.subTest(route=route):
                    nav = page(route)
                    self.assertEqual([(href, current) for href, current in nav.nav if current],
                                     [(f"{prefix}topics/", "true")])
                    self.assertEqual(nav.crumb_leaf, "page")
                    self.assertNotIn(route, nav.continue_links)
                    self.assertEqual(sorted(nav.continue_links),
                                     sorted(f"{prefix}topics/{other}/" for other in TOPIC_SLUGS if other != slug))


if __name__ == "__main__":
    unittest.main()
