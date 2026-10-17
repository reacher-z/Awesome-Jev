"""Only rendered Markdown headings, not comments inside fenced code, define anchors."""
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts import validate


GUIDE = """# Quickstart

```sh
# Install the SDK
pip install example
```

~~~python
# Configure the client
<a id="fenced-tag"></a>
~~~

## Install

```sh
# Install
```

## Install

<a id="rendered-tag"></a>
"""


class FencedAnchorTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        (self.root / "docs").mkdir()
        (self.root / "docs/quickstart.md").write_text(GUIDE)

    def link_errors(self, *links):
        readme = self.root / "README.md"
        readme.write_text("".join(f"[link](docs/quickstart.md#{link})\n" for link in links))
        with patch.object(validate, "ROOT", self.root), patch.object(validate, "errors", []):
            validate.check_text(readme, readme.read_text())
            return list(validate.errors)

    def test_fenced_comments_and_tags_define_no_anchor(self):
        with patch.object(validate, "ROOT", self.root):
            anchors = validate.anchors(self.root / "docs/quickstart.md")
        self.assertEqual(anchors, {"quickstart", "install", "install-1", "rendered-tag"})

    def test_links_to_fenced_comments_are_reported(self):
        errors = self.link_errors("install-the-sdk", "configure-the-client", "fenced-tag", "install-2")
        self.assertEqual(errors, [f"README.md: missing local anchor: docs/quickstart.md#{link}"
                                  for link in ("install-the-sdk", "configure-the-client", "fenced-tag", "install-2")])

    def test_links_to_rendered_headings_pass(self):
        self.assertEqual(self.link_errors("quickstart", "install", "install-1", "rendered-tag"), [])

    def test_html_ids_are_unchanged_outside_markdown(self):
        page = self.root / "page.html"
        page.write_text("<pre>```</pre><h2 id=\"kept\">Kept</h2><pre>```</pre>\n")
        with patch.object(validate, "ROOT", self.root):
            self.assertEqual(validate.anchors(page), {"kept"})


if __name__ == "__main__":
    unittest.main()
