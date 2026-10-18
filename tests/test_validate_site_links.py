"""Absolute links to the project's own website and repository must resolve offline."""
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts import validate


SITE = "https://awesomejev.github.io"
REPO = "https://github.com/reacher-z/Awesome-Jev"


class OwnSiteLinkTests(unittest.TestCase):
    def test_directory_alias_does_not_make_valid_links_escape(self):
        alias = self.root.parent / "repository-alias"
        alias.symlink_to(self.root, target_is_directory=True)
        with patch.object(validate, "ROOT", alias), patch.object(validate, "errors", []):
            source = alias / "README.md"
            validate.local_link(source, "docs/source-audit.md#verification-levels")
            validate.local_link(source, SITE + "/papers/")
            self.assertEqual(validate.errors, [])
            validate.local_link(alias / "site/index.html", "../LICENSE")
            self.assertEqual(validate.errors, ["site/index.html: local link escapes site/"])

    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name) / "repo"
        for name, text in {
            "site/index.html": '<!doctype html><section id="corpus"></section>\n',
            "site/papers/index.html": '<!doctype html><h1 id="papers">Papers</h1>\n',
            "site/references.bib": "@misc{key,\n}\n",
            "docs/source-audit.md": "# Source audit\n\n## Verification levels\n",
            "data/README.md": "# Data\n",
            "LICENSE": "MIT\n",
        }.items():
            (self.root / name).parent.mkdir(parents=True, exist_ok=True)
            (self.root / name).write_text(text)

    def errors(self, *links, source="README.md"):
        path = self.root / source
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.suffix == ".html":
            path.write_text("".join(f'<a href="{link}">link</a>\n' for link in links))
        else:
            path.write_text("".join(f"[link]({link})\n" for link in links))
        with patch.object(validate, "ROOT", self.root), patch.object(validate, "errors", []):
            validate.check_text(path, path.read_text())
            return list(validate.errors)

    def test_existing_site_routes_files_and_anchors_pass(self):
        links = (SITE, SITE + "/", SITE + "/#corpus", SITE + "/?q=jev", SITE + "/papers", SITE + "/papers/#papers",
                 SITE + "/references.bib", "HTTPS://AwesomeJev.GitHub.io/papers/")
        self.assertEqual(self.errors(*links), [])
        self.assertEqual(self.errors(*links, source="site/zh/index.html"), [])

    def test_existing_repository_files_directories_and_anchors_pass(self):
        links = (REPO + "/blob/main/LICENSE", REPO + "/blob/main/docs/source-audit.md#verification-levels",
                 REPO + "/tree/main/data", REPO + "/tree/main", "https://github.com/reacher-z/awesome-jev/blob/main/LICENSE")
        self.assertEqual(self.errors(*links), [])
        self.assertEqual(self.errors(*links, source="site/index.html"), [])

    def test_missing_site_route_file_and_anchor_are_reported(self):
        links = (SITE + "/missing/", SITE + "/papers.json", SITE + "/papers/#missing")
        self.assertEqual(self.errors(*links), [
            f"README.md: missing local target: {SITE}/missing/",
            f"README.md: missing local target: {SITE}/papers.json",
            f"README.md: missing local anchor: {SITE}/papers/#missing",
        ])

    def test_missing_repository_file_and_anchor_are_reported(self):
        links = (REPO + "/blob/main/docs/missing.md", REPO + "/tree/main/scripts",
                 REPO + "/blob/main/docs/source-audit.md#missing")
        self.assertEqual(self.errors(*links, source="site/index.html"), [
            f"site/index.html: missing local target: {REPO}/blob/main/docs/missing.md",
            f"site/index.html: missing local target: {REPO}/tree/main/scripts",
            f"site/index.html: missing local anchor: {REPO}/blob/main/docs/source-audit.md#missing",
        ])

    def test_site_link_cannot_escape_the_repository(self):
        self.assertEqual(self.errors(SITE + "/../../outside"), ["README.md: local link escapes repository"])

    def test_other_branches_commits_repositories_and_hosts_stay_unchecked(self):
        links = (REPO + "/blob/dev/docs/missing.md", REPO + "/tree/0123abc/missing", REPO + "/pull/4",
                 REPO + "/blob/mainline/missing.md", "https://github.com/reacher-z/Awesome-Jev-Fork/blob/main/missing.md",
                 "https://awesomejev.github.io.example.com/missing/", "https://other.github.io/missing/")
        self.assertEqual(self.errors(*links), [])


class OwnSiteRouteNormalisationTests(unittest.TestCase):
    """Site routes are looked up as served: escapes decoded, dot segments kept inside site/."""
    setUp = OwnSiteLinkTests.setUp
    errors = OwnSiteLinkTests.errors

    def test_dot_segments_that_leave_the_site_are_reported(self):
        links = (SITE + "/../docs/source-audit.md", SITE + "/papers/../../data/README.md", SITE + "/%2e%2e/LICENSE")
        self.assertEqual(self.errors(*links), ["README.md: local link escapes site/"] * 3)
        self.assertEqual(self.errors("/../docs/source-audit.md", source="site/index.html"),
                         ["site/index.html: local link escapes site/"])

    def test_relative_links_in_published_pages_cannot_leave_the_site(self):
        # site/ is the published web root, so these 404 once deployed although
        # the files exist in the repository.
        self.assertEqual(self.errors("../docs/source-audit.md", "../LICENSE", "./../data/README.md", source="site/index.html"),
                         ["site/index.html: local link escapes site/"] * 3)
        self.assertEqual(self.errors("../../docs/source-audit.md", source="site/papers/index.html"),
                         ["site/papers/index.html: local link escapes site/"])
        # Relative links that stay inside site/, and the same links outside site/, still pass.
        self.assertEqual(self.errors("../index.html", "../papers/", "../references.bib", source="site/zh/index.html"), [])
        self.assertEqual(self.errors("../LICENSE", source="docs/guide.md"), [])

    def test_dot_segments_inside_the_site_resolve(self):
        self.assertEqual(self.errors(SITE + "/papers/../references.bib", SITE + "/papers/./#papers"), [])

    def test_percent_encoded_routes_are_decoded(self):
        (self.root / "site/papers/my file.html").write_text("<p>Spaced</p>\n")
        self.assertEqual(self.errors(SITE + "/papers/my%20file.html", "/papers/my%20file.html", source="site/zh/index.html"), [])
        self.assertEqual(self.errors(SITE + "/papers/my%20file.html", REPO + "/blob/main/site/papers/my%20file.html"), [])
        self.assertEqual(self.errors(SITE + "/papers/my%20missing.html"),
                         [f"README.md: missing local target: {SITE}/papers/my%20missing.html"])


if __name__ == "__main__":
    unittest.main()
