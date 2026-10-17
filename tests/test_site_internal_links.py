"""Every local link in the generated pages reaches an existing file, element or icon.

The crawl covers href and src values on site-relative and https://awesomejev.github.io URLs,
#fragments in the target page, and /assets/fontawesome/icons.svg#symbol references in <use>.
Hard-coded cross-page fragments in scripts/build_site.mjs must also stop the build when their
target disappears, instead of publishing a broken link.
"""

from html.parser import HTMLParser
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest
from urllib.parse import unquote, urljoin, urlsplit

from test_site_discovery import BUILD_INPUTS, ROOT

SITE = ROOT / "site"
ORIGIN = "awesomejev.github.io"
LINK_ATTRIBUTES = {"href", "src", "xlink:href"}


class LinkCollector(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids, self.links = set(), []

    def handle_starttag(self, tag, attrs):
        for name, value in attrs:
            if name == "id" and value:
                self.ids.add(value)
            elif name in LINK_ATTRIBUTES and value is not None:
                self.links.append((tag, value))


def page_url(path):
    relative = path.relative_to(SITE).as_posix()
    return "/" + (relative[:-len("index.html")] if relative.endswith("index.html") else relative)


def target_file(path):
    """Map a site path to the file GitHub Pages serves for it."""
    file = SITE / unquote(path).lstrip("/")
    return file / "index.html" if path.endswith("/") or file.is_dir() else file


class InternalLinkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pages = {}
        for path in sorted(SITE.rglob("*.html")):
            collector = LinkCollector()
            collector.feed(path.read_text(encoding="utf-8"))
            cls.pages[path] = collector
        cls.svg_ids = {}

    def ids(self, file):
        if file in self.pages:
            return self.pages[file].ids
        if file not in self.svg_ids:
            self.svg_ids[file] = set(re.findall(r'\bid="([^"]+)"', file.read_text(encoding="utf-8")))
        return self.svg_ids[file]

    def test_local_paths_and_fragments_resolve(self):
        self.assertGreater(len(self.pages), 10)
        broken = []
        for path, collector in self.pages.items():
            base = page_url(path)
            for tag, value in collector.links:
                url = urlsplit(urljoin("https://" + ORIGIN + base, value))
                if url.scheme != "https" or url.netloc != ORIGIN:
                    continue
                file = target_file(url.path)
                where = f"{path.relative_to(ROOT)} <{tag}> {value}"
                if not file.is_file():
                    broken.append(f"{where}: missing {file.relative_to(ROOT)}")
                elif url.fragment and file.suffix in {".html", ".svg"} and unquote(url.fragment) not in self.ids(file):
                    broken.append(f"{where}: no id {url.fragment!r} in {file.relative_to(ROOT)}")
        self.assertEqual(broken, [])


@unittest.skipUnless(shutil.which("node"), "Node is required to build the site")
class HardCodedFragmentTests(unittest.TestCase):
    def build(self, change):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for name in BUILD_INPUTS:
                destination = root / name
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / name, destination)
            change(root)
            return subprocess.run([shutil.which("node"), "scripts/build_site.mjs"], cwd=root,
                                  capture_output=True, text=True, encoding="utf-8", timeout=45)

    def test_renamed_guide_section_linked_from_the_model_directory_stops_the_build(self):
        def rename(root):
            path = root / "data/search-guide.json"
            guide = json.loads(path.read_text(encoding="utf-8"))
            for language in ("en", "zh"):
                for section in guide[language]["sections"]:
                    if section["id"] == "models-and-licenses":
                        section["id"] = "models-licenses"
            path.write_text(json.dumps(guide, ensure_ascii=False), encoding="utf-8", newline="\n")

        result = self.build(rename)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("guide section #models-and-licenses", result.stderr)

    def test_removed_homepage_anchor_stops_the_build(self):
        # A data-id="corpus" attribute is not a fragment target.
        for replacement in ('id="sources"', 'data-id="corpus"'):
            def remove(root):
                path = root / "templates/index.html"
                text = path.read_text(encoding="utf-8")
                self.assertEqual(text.count(' id="corpus"') + text.count('\nid="corpus"'), 1)
                text = re.sub(r'(?<![\w-])id="corpus"', replacement, text)
                path.write_text(text, encoding="utf-8", newline="\n")

            with self.subTest(replacement=replacement):
                result = self.build(remove)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("homepage element #corpus", result.stderr)


if __name__ == "__main__":
    unittest.main()
