"""Disclosures whose native marker is hidden show a visible expand indicator instead."""

from html.parser import HTMLParser
import re
import unittest

from test_site_discovery import ROOT, ROUTES

STYLES = (ROOT / "site/styles.css").read_text(encoding="utf-8")
# details classes whose <summary> marker the stylesheet suppresses
HIDDEN_MARKER = set(re.findall(r"\.([\w-]+) summary::-webkit-details-marker\s*\{[^}]*display:\s*none", STYLES))


class Summaries(HTMLParser):
    """For each summary of a marker-less <details>: its text and its last child element."""

    def __init__(self, source):
        super().__init__(convert_charrefs=True)
        self.summaries = []
        self._details = []
        self._summary = None
        self._depth = 0
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "details":
            self._details.append(bool(HIDDEN_MARKER & set(attrs.get("class", "").split())))
        elif tag == "summary" and self._details and self._details[-1]:
            self._summary = {"text": [], "last": None}
            self._depth = 0
        elif self._summary is not None:
            if self._depth == 0:
                self._summary["last"] = {"tag": tag, "attrs": attrs, "text": ""}
            self._depth += 1

    def handle_endtag(self, tag):
        if tag == "details" and self._details:
            self._details.pop()
        elif tag == "summary" and self._summary is not None:
            self._summary["text"] = re.sub(r"\s+", " ", "".join(self._summary["text"])).strip()
            self.summaries.append(self._summary)
            self._summary = None
        elif self._summary is not None:
            self._depth -= 1

    def handle_data(self, value):
        if self._summary is not None:
            self._summary["text"].append(value)
            if self._depth == 1 and self._summary["last"]:
                self._summary["last"]["text"] += value


class DisclosureIndicatorTests(unittest.TestCase):
    def test_stylesheet_hides_markers_for_known_disclosures(self):
        self.assertIn("verification-legend", HIDDEN_MARKER)

    def test_every_marker_less_summary_ends_with_a_visible_indicator(self):
        checked = 0
        for route in ROUTES:
            with self.subTest(route=route):
                for summary in Summaries((ROOT / "site" / route.strip("/") / "index.html").read_text(encoding="utf-8")).summaries:
                    checked += 1
                    last = summary["last"]
                    self.assertIsNotNone(last, f"No indicator in summary {summary['text']!r}")
                    self.assertEqual((last["tag"], last["attrs"].get("aria-hidden"), last["text"].strip()),
                                     ("span", "true", "+"), f"Summary {summary['text']!r} needs a trailing + indicator")
        # Homepage (2 per language), new resources and model directory (1 each per language).
        self.assertGreaterEqual(checked, 8)


if __name__ == "__main__":
    unittest.main()
