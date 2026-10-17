"""Chinese pages mark English resource titles with lang="en" (WCAG 3.1.2 Language of Parts)."""

from html.parser import HTMLParser
import re
import unittest

from test_site_discovery import ROOT

CJK = re.compile(r"[㐀-鿿]")
LISTS = ("index.html", "papers/index.html", "models/index.html", "discoveries/index.html")


class TitleLinks(HTMLParser):
    """Title links of resource rows (h3.resource-title), model-table rows (tr.model-row th) and
    paper-table rows (a.paper-title)."""

    def __init__(self, source):
        super().__init__(convert_charrefs=True)
        self.titles = []
        self._title_parent = False
        self._link = None
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        classes = attrs.get("class", "").split()
        if tag == "h3" and "resource-title" in classes or tag == "tr" and "model-row" in classes:
            self._title_parent = True
        elif tag == "a" and (self._title_parent or "paper-title" in classes):
            self._link = {"lang": attrs.get("lang"), "text": []}

    def handle_endtag(self, tag):
        if tag == "a" and self._link is not None:
            self.titles.append((re.sub(r"\s+", " ", "".join(self._link["text"])).strip(), self._link["lang"]))
            self._link = None
            self._title_parent = False

    def handle_data(self, value):
        if self._link is not None:
            self._link["text"].append(value)


def titles(route):
    return TitleLinks((ROOT / "site" / route).read_text(encoding="utf-8")).titles


class LanguageOfPartsTests(unittest.TestCase):
    def test_zh_lists_mark_english_titles(self):
        for name in LISTS:
            with self.subTest(page="zh/" + name):
                rows = titles("zh/" + name)
                self.assertGreater(len(rows), 0)
                unmarked = [text for text, lang in rows if not CJK.search(text) and lang != "en"]
                self.assertEqual(unmarked, [], "English titles on a zh-CN page need lang=\"en\"")
                mislabeled = [text for text, lang in rows if CJK.search(text) and lang == "en"]
                self.assertEqual(mislabeled, [], "Titles containing Chinese must not be marked English")

    def test_english_lists_add_no_language_override(self):
        for name in LISTS:
            with self.subTest(page=name):
                rows = titles(name)
                self.assertGreater(len(rows), 0)
                self.assertEqual([text for text, lang in rows if lang], [])


if __name__ == "__main__":
    unittest.main()
