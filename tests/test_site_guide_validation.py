"""A malformed data/search-guide.json stops the site build before anything is written."""

import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

from test_site_discovery import BUILD_INPUTS, ROOT


def rename_zh_section(guide):
    guide["zh"]["sections"][0]["id"] = guide["zh"]["sections"][0]["id"] + "-renamed"


def swap_zh_sections(guide):
    sections = guide["zh"]["sections"]
    sections[0], sections[1] = sections[1], sections[0]


def markup_in_section_id(guide):
    for language in ("en", "zh"):
        guide[language]["sections"][0]["id"] = 'what-is-jev"><script>alert(1)</script>'


def duplicate_section_id(guide):
    for language in ("en", "zh"):
        guide[language]["sections"][1]["id"] = guide[language]["sections"][0]["id"]


def plain_http_source(guide):
    guide["en"]["sections"][0]["paragraphs"][0]["sources"][0]["url"] = "http://docs.typesafe.ai/introduction"


def credential_source(guide):
    credentials = "fixture-user" + ":" + "fixture-password" + "@"
    guide["zh"]["sections"][0]["paragraphs"][0]["sources"][0]["url"] = "https://" + credentials + "docs.typesafe.ai/introduction"


def unlabeled_source(guide):
    guide["en"]["sections"][0]["paragraphs"][0]["sources"][0]["label"] = ""


def empty_intro(guide):
    guide["zh"]["intro"] = " "


def no_sections(guide):
    guide["en"]["sections"] = []


def empty_paragraph(guide):
    guide["en"]["sections"][0]["paragraphs"][0]["text"] = ""


def bad_date(guide):
    guide["updated"] = "17 October 2026"


MALFORMED = (rename_zh_section, swap_zh_sections, markup_in_section_id, duplicate_section_id, plain_http_source,
             credential_source, unlabeled_source, empty_intro, no_sections, empty_paragraph, bad_date)


@unittest.skipUnless(shutil.which("node"), "Node is required to build the site")
class SearchGuideValidationTests(unittest.TestCase):
    def build(self, change=None):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for name in BUILD_INPUTS:
                destination = root / name
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / name, destination)
            path = root / "data/search-guide.json"
            guide = json.loads(path.read_text(encoding="utf-8"))
            if change:
                change(guide)
            path.write_text(json.dumps(guide, ensure_ascii=False), encoding="utf-8", newline="\n")
            result = subprocess.run([shutil.which("node"), "scripts/build_site.mjs"], cwd=root,
                                    capture_output=True, text=True, encoding="utf-8", timeout=45)
            return result, (root / "site/guide/index.html").exists()

    def test_current_guide_builds(self):
        result, written = self.build()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(written)

    def test_malformed_guide_stops_the_build(self):
        for change in MALFORMED:
            with self.subTest(change=change.__name__):
                result, written = self.build(change)
                self.assertNotEqual(result.returncode, 0)
                self.assertRegex(result.stderr, r"(?i)search guide")
                self.assertFalse(written, "the build wrote pages before rejecting the guide")


if __name__ == "__main__":
    unittest.main()
