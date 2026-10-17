"""The README resource tables and site/catalog.mjs list the same curated resources.

Every row of the Models, Benchmarks, Datasets, SDKs and Practical guides tables in both READMEs
must name a catalog entry of the matching category, so a resource cannot be listed in a README
but left off the website. Paper tables are checked by test_bibliography_consistency.py.
"""

from pathlib import Path
import json
import re
import shutil
import subprocess
import unittest


ROOT = Path(__file__).resolve().parents[1]
README = {"en": ROOT / "README.md", "zh": ROOT / "README.zh-CN.md"}
SECTIONS = {
    "Models": ("模型", "Models"),
    "Benchmarks and evaluation tools": ("基准与评测工具", "Evaluations"),
    "Datasets": ("数据集", "Datasets"),
    "SDKs and integrations": ("SDK 与集成", "Tools"),
    "Practical guides": ("实践指南", "Guides"),
}
# Pages of an already listed resource, such as its methodology or reading site, are not separate entries.
COMPANION_LABELS = {"en": {"Methodology", "News", "Source", "Site"}, "zh": {"方法", "动态", "源文件", "在线阅读"}}
LINK = re.compile(r"\[([^\]]+)\]\((https?://[^)\s]+)\)")


def resource_cells(language, heading):
    """Return the first cell of every table row under `## heading`."""
    lines = README[language].read_text(encoding="utf-8").split("\n")
    start = lines.index("## " + heading) + 1
    stop = next((n for n in range(start, len(lines)) if lines[n].startswith("## ")), len(lines))
    return [line.split(" | ")[0] for line in lines[start:stop] if line.startswith("| [")]


def catalog():
    script = 'import {resources} from "./site/catalog.mjs"; console.log(JSON.stringify(resources));'
    result = subprocess.run(["node", "--input-type=module", "-e", script],
                            cwd=ROOT, text=True, capture_output=True, check=True)
    return {row["url"]: row["category"] for row in json.loads(result.stdout)}


@unittest.skipUnless(shutil.which("node"), "Node is required to load the site catalog")
class ReadmeCatalogResourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = catalog()

    def headings(self):
        for english, (chinese, category) in SECTIONS.items():
            yield "en", english, category
            yield "zh", chinese, category

    def test_every_resource_row_names_a_catalog_entry_of_its_category(self):
        for language, heading, category in self.headings():
            cells = resource_cells(language, heading)
            self.assertTrue(cells, f"{README[language].name}: no rows under {heading}")
            for cell in cells:
                label, url = LINK.search(cell).groups()
                with self.subTest(readme=README[language].name, resource=label):
                    self.assertIn(url, self.catalog, "README resource missing from site/catalog.mjs")
                    self.assertEqual(self.catalog[url], category, "catalog category")

    def test_further_links_are_catalog_entries_or_companion_pages(self):
        for language, heading, _ in self.headings():
            for cell in resource_cells(language, heading):
                for label, url in LINK.findall(cell)[1:]:
                    with self.subTest(readme=README[language].name, link=label):
                        self.assertTrue(url in self.catalog or label in COMPANION_LABELS[language],
                                        f"{url} is neither in site/catalog.mjs nor a companion page")

    def test_both_readmes_list_the_same_resources(self):
        for english, (chinese, _) in SECTIONS.items():
            with self.subTest(section=english):
                urls = {language: sorted(url for cell in resource_cells(language, heading)
                                         for _, url in LINK.findall(cell))
                        for language, heading in (("en", english), ("zh", chinese))}
                self.assertEqual(urls["en"], urls["zh"])


if __name__ == "__main__":
    unittest.main()
