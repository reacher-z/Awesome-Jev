"""Homepage templating inserts curated text literally, whatever `$` sequences it contains."""

from html.parser import HTMLParser
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

from test_site_discovery import BUILD_INPUTS, ROOT, CrawlPage

# Every substitution pattern that String.prototype.replace expands in a replacement string.
PROBE = "Costs US$$5; keeps $& and $1, $2, $` and $' verbatim."


class HeadValues(HTMLParser):
    def __init__(self, source):
        super().__init__(convert_charrefs=True)
        self.meta = {}
        self.placeholders = {}
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "meta" and "content" in attrs:
            self.meta[attrs.get("name") or attrs.get("property")] = attrs["content"]
        if "placeholder" in attrs and "id" in attrs:
            self.placeholders[attrs["id"]] = attrs["placeholder"]


class LiteralDollarTemplatingTests(unittest.TestCase):
    def test_dollar_sequences_in_catalog_text_are_published_literally(self):
        node = shutil.which("node")
        self.assertIsNotNone(node)
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for name in BUILD_INPUTS:
                destination = root / name
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / name, destination)
            catalog = root / "site/catalog.mjs"
            catalog.write_text(catalog.read_text() + "\n" + "\n".join(
                f"{target} = {json.dumps(PROBE)};" for target in (
                    "resources[0].en", "resources[0].zh",
                    "translations.en.metaDescription", "translations.zh.metaDescription",
                    "translations.en.searchPlaceholder", "translations.zh.searchPlaceholder",
                )) + "\n")
            result = subprocess.run([node, "scripts/build_site.mjs"], cwd=root, capture_output=True, text=True, timeout=45)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            for route in ("", "zh/"):
                with self.subTest(route="/" + route):
                    source = (root / "site" / route / "index.html").read_text()
                    self.assertIn(PROBE, [card["description"] for card in CrawlPage(source).cards])
                    head = HeadValues(source)
                    for key in ("description", "og:description", "twitter:description"):
                        self.assertEqual(head.meta[key], PROBE)
                    self.assertEqual(head.placeholders["resource-search"], PROBE)
                    self.assertEqual(source.count('name="description"'), 1, "Meta tags must not be duplicated by `$&`")
            papers = CrawlPage((root / "site/papers/index.html").read_text())
            self.assertIn(PROBE, [card["description"] for card in papers.cards])


if __name__ == "__main__":
    unittest.main()
