"""llms.txt lists every canonical page in both languages, including each topic note."""

import json
import re
import unittest
import xml.etree.ElementTree as ET

from test_site_discovery import BASE, ROOT

NS = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
LINK = re.compile(r"^- \[([^\]]+)\]\(([^)]+)\)(?:: (\S.*))?$")


class LlmsTxtRouteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = (ROOT / "site/llms.txt").read_text(encoding="utf-8")
        cls.entries = {}
        for line in cls.text.splitlines():
            match = LINK.match(line)
            if match:
                cls.entries.setdefault(match[2], []).append((match[1], match[3]))

    def test_every_sitemap_route_is_listed_once_with_a_description(self):
        tree = ET.fromstring((ROOT / "site/sitemap.xml").read_bytes())
        locations = [node.text for node in tree.findall("sm:url/sm:loc", NS)]
        pages = {url: entries for url, entries in self.entries.items() if url.startswith(BASE + "/") and url.endswith("/")}
        self.assertEqual(set(pages), set(locations))
        for url, entries in pages.items():
            with self.subTest(url=url):
                self.assertEqual(len(entries), 1)
                self.assertTrue(entries[0][1], "Every page link needs a description")
                if "/zh/" in url:
                    self.assertRegex("".join(entries[0]), r"[\u4e00-\u9fff]", "Chinese routes need Chinese labels")

    def test_topic_notes_use_their_localized_title_and_description(self):
        topics = json.loads((ROOT / "data/research-topics.json").read_text(encoding="utf-8"))["topics"]
        for topic in topics:
            for language, prefix in (("en", "/"), ("zh", "/zh/")):
                url = f"{BASE}{prefix}topics/{topic['slug']}/"
                with self.subTest(url=url):
                    self.assertEqual(self.entries.get(url), [(topic[language]["title"], topic[language]["description"])])

    def test_markdown_export_label_mentions_research_topics(self):
        labels = [label for label, _ in self.entries[BASE + "/llms-full.txt"]]
        self.assertEqual(labels, ["Guide, curated resources and research topics in Markdown"])
        self.assertIn("# Research topics", (ROOT / "site/llms-full.txt").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
