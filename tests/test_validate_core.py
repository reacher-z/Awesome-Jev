"""validate.py link, anchor, leak, index and repository-hygiene rules, offline."""
import contextlib
import io
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch

from scripts import validate

# Samples are assembled at runtime so this file does not trip the leak scan itself.
TOKEN = "gh" + "p_" + "A1b2C3d4" * 5
LEAKS = {
    "personal filesystem path": "/" + "home/alice/notes.txt",
    "GitHub credential": TOKEN,
    "model API credential": "h" + "f_" + "Q" * 34,
    "cloud access key": "AK" + "IA" + "ABCDEFGHIJ234567",
    "private key": "-----BEGIN " + "OPENSSH PRIVATE KEY-----",
    "credential-bearing URL": "https://" + "deploy:s3cret@example.org/repo.git",
}
NEAR_MISSES = (
    "Install under /home/ or /Users/ on your machine.",
    "huggingface_hub.hf_hub_download(repo_id='example/model')",
    "Tokens look like gh" + "p_short and AK" + "IA1234.",
    "-----BEGIN PUBLIC KEY-----",
    "Mail maintainers at https://example.org/contact@team or user@example.org.",
)


class RepoCase(unittest.TestCase):
    """A temporary repository standing in for validate.ROOT, with a fresh error list."""

    def setUp(self):
        directory = tempfile.TemporaryDirectory(prefix="awesome-jev-validate-")
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name).resolve()
        for name, value in (("ROOT", self.root), ("errors", [])):
            patcher = patch.object(validate, name, value)
            patcher.start()
            self.addCleanup(patcher.stop)

    def write(self, relative, text="", data=None):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        if data is None:
            path.write_text(text, encoding="utf-8")
        else:
            path.write_bytes(data)
        return path

    def check(self, relative, text):
        """Run check_text on a new file and return only the errors it added."""
        before = len(validate.errors)
        validate.check_text(self.write(relative, text), text)
        return validate.errors[before:]

    def link(self, relative, value):
        before = len(validate.errors)
        validate.local_link(self.root / relative, value)
        return validate.errors[before:]


class FilesAndMarkupTests(RepoCase):
    def test_files_lists_sorted_regular_files_and_skips_tool_directories(self):
        for relative in ("b.md", "a/z.txt", ".git/config", "node_modules/pkg/index.js", ".venv/lib/x.py",
                         "docs/__pycache__/m.pyc", ".cache/c.json", "tmp/scratch.md", "site/artifacts/a.html"):
            self.write(relative)
        (self.root / "empty-directory").mkdir()
        self.assertEqual(validate.files(), [self.root / "a/z.txt", self.root / "b.md"])

    def test_markup_collects_link_attributes_and_ids_only(self):
        parser = validate.Markup()
        parser.feed('<a href="a.md" id="top">x</a><img src="i.png" name="pic"><svg><use xlink:href="#icon"/></svg>'
                    '<a href="">empty</a><div data-href="x.md" class="y" title="z.md"></div>')
        self.assertEqual(parser.links, ["a.md", "i.png", "#icon"])
        self.assertEqual(parser.ids, {"top", "pic"})


class AnchorTests(RepoCase):
    def test_markdown_heading_slugs_follow_github_rules(self):
        path = self.write("docs/guide.md", "\n".join((
            "# Getting Started",
            "## Getting Started",
            "### API & Usage <sup>beta</sup>",
            "## [Linked](https://example.org) heading ##",
            "#### Café &amp; Résumé",
            "    # Indented code is not a heading",
            "#Missing space is not a heading",
            '<a id="custom"></a>',
        )))
        self.assertEqual(validate.anchors(path), {"getting-started", "getting-started-1", "api--usage-beta",
                                                  "linked-heading", "café--résumé", "custom"})

    def test_html_anchors_come_from_ids_and_names_not_heading_text(self):
        path = self.write("site/page.html", '# Not markdown\n<h2>Heading</h2><section id="s1"></section><a name="old"></a>')
        self.assertEqual(validate.anchors(path), {"s1", "old"})


class LocalLinkTests(RepoCase):
    def setUp(self):
        super().setUp()
        self.write("README.md", "# Title\n")
        self.write("docs/guide.md", "# Install\n")
        self.write("docs/space name.md", "# Spaced\n")
        self.write("docs/folder/README.md", "# Folder notes\n")
        self.write("assets/logo.svg", '<svg xmlns="http://www.w3.org/2000/svg"><g id="mark"/></svg>')
        self.write("site/index.html", '<h1 id="top">Home</h1>')
        self.write("site/papers/index.html", '<p id="list">Papers</p>')

    def test_external_empty_and_template_values_are_ignored(self):
        for value in ("https://example.org/missing.md", "mailto:team@example.org", "//cdn.example.org/x.js",
                      "data:image/png;base64,AAAA", "#", "", "   ", "{{ page.url }}/missing.md"):
            with self.subTest(value=value):
                self.assertEqual(self.link("README.md", value), [])

    def test_existing_targets_anchors_and_directory_indexes_pass(self):
        for value in ("docs/guide.md", "docs/guide.md#install", "./docs/guide.md?plain=1#install",
                      "<docs/guide.md>", "docs/guide.md?a=1&amp;b=2", "docs/space%20name.md#spaced",
                      "docs/folder/", "docs/folder#folder-notes", "assets/logo.svg#mark", "#title"):
            with self.subTest(value=value):
                self.assertEqual(self.link("README.md", value), [])

    def test_missing_targets_and_anchors_are_reported_with_the_link(self):
        cases = {
            "docs/missing.md": "README.md: missing local target: docs/missing.md",
            "docs/guide.md#setup": "README.md: missing local anchor: docs/guide.md#setup",
            "#nowhere": "README.md: missing local anchor: #nowhere",
            "docs/folder#missing": "README.md: missing local anchor: docs/folder#missing",
            "assets/logo.svg#gone": "README.md: missing local anchor: assets/logo.svg#gone",
        }
        for value, message in cases.items():
            with self.subTest(value=value):
                self.assertEqual(self.link("README.md", value), [message])

    def test_root_absolute_routes_resolve_against_site_only_for_site_pages(self):
        self.assertEqual(self.link("site/index.html", "/papers/"), [])
        self.assertEqual(self.link("site/index.html", "/papers/#list"), [])
        self.assertEqual(self.link("site/index.html", "/papers/#missing"),
                         ["site/index.html: missing local anchor: /papers/#missing"])
        self.assertEqual(self.link("site/index.html", "/models/"),
                         ["site/index.html: missing local target: /models/"])
        # Outside site/, a leading slash means the repository root.
        self.assertEqual(self.link("README.md", "/docs/guide.md#install"), [])
        self.assertEqual(self.link("README.md", "/papers/"), ["README.md: missing local target: /papers/"])

    def test_links_escaping_the_repository_are_rejected(self):
        self.assertEqual(self.link("README.md", "../outside.md"), ["README.md: local link escapes repository"])
        self.assertEqual(self.link("docs/guide.md", "../../outside.md"),
                         ["docs/guide.md: local link escapes repository"])

    # Bug: root-absolute paths are not percent-decoded (relative paths are), so the valid route
    # /papers/my%20file.html is reported as a missing target. Remove this marker once fixed.
    @unittest.expectedFailure
    def test_percent_encoded_root_absolute_route_resolves(self):
        self.write("site/papers/my file.html", "<p>Spaced</p>")
        self.assertEqual(self.link("site/index.html", "papers/my%20file.html"), [])
        self.assertEqual(self.link("site/index.html", "/papers/my%20file.html"), [])


class CheckTextTests(RepoCase):
    def test_every_leak_pattern_is_reported_without_echoing_the_value(self):
        self.assertEqual(set(LEAKS), set(validate.LEAK_PATTERNS), "add a sample for each leak pattern")
        for label, sample in LEAKS.items():
            with self.subTest(label=label):
                errors = self.check("notes/leak.txt", f"before {sample} after\n")
                self.assertEqual(errors, [f"notes/leak.txt: possible {label}; inspect locally (value redacted)"])
                self.assertNotIn(sample, "".join(errors))

    def test_windows_and_macos_profile_paths_are_personal_paths(self):
        for sample in ("C:" + "\\Users\\alice\\repo", "/" + "Users/alice/repo"):
            with self.subTest(sample=sample):
                self.assertEqual(self.check("notes/path.md", sample + "\n"),
                                 ["notes/path.md: possible personal filesystem path; inspect locally (value redacted)"])

    def test_near_misses_are_not_reported(self):
        for text in NEAR_MISSES:
            with self.subTest(text=text):
                self.assertEqual(self.check("notes/benign.md", text + "\n"), [])

    def test_fail_redacts_secrets_in_locations(self):
        validate.fail(f"notes/{TOKEN}.txt", "message")
        self.assertEqual(validate.errors, ["notes/[redacted].txt: message"])

    def test_markdown_inline_reference_and_embedded_html_links_are_checked(self):
        self.write("docs/guide.md", "# Install\n")
        errors = self.check("README.md", "\n".join((
            "[ok](docs/guide.md#install) [bad inline](missing-inline.md \"Title\")",
            "[angle](<missing angle.md>)",
            "[ref]: missing-ref.md",
            '<img src="missing-img.png" alt="">',
        )))
        self.assertCountEqual(errors, ["README.md: missing local target: " + value for value in (
            "missing-inline.md", "missing angle.md", "missing-ref.md", "missing-img.png")])

    def test_fenced_markdown_examples_are_not_link_checked(self):
        text = "```md\n[example](missing-a.md)\n```\n~~~\n[ref]: missing-b.md\n~~~\n[real](missing-c.md)\n"
        self.assertEqual(self.check("README.md", text), ["README.md: missing local target: missing-c.md"])

    def test_html_attributes_and_css_urls_are_checked(self):
        self.write("site/styles.css", "")
        self.write("site/img/ok.png", "")
        html_errors = self.check("site/page.html", '<link href="styles.css"><a href="missing.html">x</a>'
                                 '<div style="background: url(\'missing-bg.png\')"></div>')
        self.assertCountEqual(html_errors, ["site/page.html: missing local target: missing.html",
                                            "site/page.html: missing local target: missing-bg.png"])
        css_errors = self.check("site/styles.css", 'a { background: url(img/ok.png); }\n'
                                '@font-face { src: url( "fonts/missing.woff2" ); }\n'
                                'b { background: url(data:image/png;base64,AAAA); }\n')
        self.assertEqual(css_errors, ["site/styles.css: missing local target: fonts/missing.woff2"])

    def test_svg_references_are_checked(self):
        self.write("assets/sprite.svg", '<svg><symbol id="present"/></svg>')
        errors = self.check("assets/icon.svg", '<svg><use xlink:href="sprite.svg#present"/><use href="sprite.svg#gone"/></svg>')
        self.assertEqual(errors, ["assets/icon.svg: missing local anchor: sprite.svg#gone"])

    def test_html_templates_skip_link_checks_but_not_the_leak_scan(self):
        text = f'<a href="missing.html">x</a><div style="background:url(missing.png)"></div><!-- {TOKEN} -->'
        self.assertEqual(self.check("templates/page.html", text),
                         ["templates/page.html: possible GitHub credential; inspect locally (value redacted)"])

    def test_python_syntax_errors_report_the_line(self):
        self.assertEqual(self.check("scripts/good.py", "def ok():\n    return 1\n"), [])
        self.assertEqual(self.check("scripts/bad.py", "x = 1\ndef broken(:\n    pass\n"),
                         ["scripts/bad.py: Python syntax error at line 2"])


def index_source(number, level="content_screened"):
    return {"title": f"Fixture {number}", "url": f"https://example.org/source/{number}", "category": "Papers",
            "description": "Synthetic index row.", "year": "2026", "status": "Content screened", "relation": "direct",
            "verification_level": level, "content_sha256": "a" * 64}


def index_payload(count=1501):
    counts = {"editorial_reviewed": 0, "content_screened": count, "abstract_checked": 0, "metadata_only": 0,
              "raw_records": count, "unique_records": count, "duplicate_records": 0, "checked_sources": count}
    return {"generated_at": "2026-10-17T00:00:00+00:00", "counts": counts,
            "sources": [index_source(n) for n in range(count)], "duplicates": []}


class CheckIndexTests(RepoCase):
    def run_index(self, payload, expected=None, snapshot=None, returncode=0):
        self.write("site/data/source-index.json", payload if isinstance(payload, str) else json.dumps(payload))
        if snapshot is None:
            snapshot = {"generated_at": payload["generated_at"], "counts": payload["counts"]}
        self.write("data/source-counts.json", json.dumps(snapshot))
        with patch.object(validate.subprocess, "run", return_value=Mock(returncode=returncode)) as run:
            validate.check_index(payload["counts"]["raw_records"] if expected is None else expected)
        return list(validate.errors), run

    def test_consistent_index_passes_and_runs_the_generator_check(self):
        errors, run = self.run_index(index_payload())
        self.assertEqual(errors, [])
        run.assert_called_once_with([sys.executable, "scripts/build_source_index.py", "--check"],
                                    cwd=self.root, capture_output=True, text=True)

    def test_missing_index_or_snapshot_asks_for_a_rebuild(self):
        validate.check_index(1)
        self.write("site/data/source-index.json", json.dumps(index_payload(2)))
        validate.check_index(2)
        self.assertEqual(validate.errors, ["source index: run python3 scripts/build_source_index.py"] * 2)

    def test_each_reconciliation_rule_reports_its_own_error(self):
        def duplicate_url(p): p["sources"][1]["url"] = p["sources"][0]["url"]
        def raw_mismatch(p): p["counts"]["raw_records"] += 1
        def level_mismatch(p): p["counts"]["metadata_only"] = 1
        def checked_mismatch(p): p["counts"]["checked_sources"] -= 1
        def private_url(p): p["sources"][0]["url"] = "http://localhost/fixture"
        cases = (
            ("ledger total", None, 1500, "not all nonexcluded source ledger records are accounted for"),
            ("field", lambda p: p["sources"][0].pop("content_sha256"), None, "missing website source fields"),
            ("unique", duplicate_url, None, "unique source count or URL deduplication mismatch"),
            ("raw", raw_mismatch, None, "raw, unique, and duplicate counts do not reconcile"),
            ("audit", lambda p: p["duplicates"].append({"url": "https://example.org/x"}), None,
             "duplicate audit count mismatch"),
            ("levels", level_mismatch, None, "verification-level counts do not reconcile"),
            ("checked", checked_mismatch, None, "checked source count must reconcile and exceed 1,500"),
            ("public", private_url, None, "invalid public source URL"),
        )
        for name, mutate, expected, message in cases:
            with self.subTest(rule=name):
                validate.errors.clear()
                payload = index_payload()
                if mutate:
                    mutate(payload)
                errors, _ = self.run_index(payload, expected=expected)
                self.assertEqual(errors, ["source index: " + message])

    def test_checked_sources_must_exceed_1500(self):
        errors, _ = self.run_index(index_payload(1500))
        self.assertEqual(errors, ["source index: checked source count must reconcile and exceed 1,500"])

    def test_stale_count_snapshot_is_reported(self):
        payload = index_payload()
        errors, _ = self.run_index(payload, snapshot={"generated_at": "2026-10-16T00:00:00+00:00",
                                                      "counts": payload["counts"]})
        self.assertEqual(errors, ["data/source-counts.json: count snapshot is stale"])

    def test_stale_generated_index_is_reported(self):
        errors, _ = self.run_index(index_payload(), returncode=1)
        self.assertEqual(errors, ["source index: generated index is stale; run python3 scripts/build_source_index.py"])

    def test_malformed_index_is_a_schema_error(self):
        payload = index_payload()
        for name, document in (("truncated", json.dumps(payload)[:-10]),
                               ("no counts", json.dumps({k: v for k, v in payload.items() if k != "counts"}))):
            with self.subTest(document=name):
                validate.errors.clear()
                self.write("site/data/source-index.json", document)
                self.write("data/source-counts.json", "{}")
                with patch.object(validate.subprocess, "run") as run:
                    validate.check_index(1501)
                self.assertEqual(validate.errors, ["source index: invalid index or count-snapshot schema"])
                run.assert_not_called()


LEDGER_ROW = {"url": "https://example.org/source", "title": "Fixture source", "topic": "direct-decision-research",
              "relation": "direct", "retrieved_at": "2026-10-15T00:00:00Z", "verification_level": "metadata_only",
              "relevance": "Synthetic validator fixture."}


class MainTests(RepoCase):
    """main() on a minimal clean repository; check_index and Node lookup are isolated."""

    def setUp(self):
        super().setUp()
        self.write("README.md", "# Fixture\n\nSee [the guide](docs/guide.md#install).\n")
        self.write("docs/guide.md", "# Install\n")
        self.write("data/sources.jsonl", json.dumps(LEDGER_ROW) + "\n")
        self.write("data/sources.excluded.jsonl", json.dumps({**LEDGER_ROW, "url": "https://example.org/excluded"}) + "\n")
        index = patch.object(validate, "check_index")
        self.check_index = index.start()
        self.addCleanup(index.stop)
        which = patch.object(validate.shutil, "which", return_value="node")
        self.which = which.start()
        self.addCleanup(which.stop)

    def main(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            code = validate.main()
        return code, list(validate.errors), output.getvalue()

    def test_clean_repository_passes_and_counts_only_nonexcluded_ledgers(self):
        code, errors, output = self.main()
        self.assertEqual((code, errors), (0, []))
        self.assertTrue(output.startswith("Validated 4 files and 1 source ledger records"), output)
        self.check_index.assert_called_once_with(1)

    def test_private_configuration_and_key_files_are_rejected(self):
        for relative in (".env", ".env.local", "config/.npmrc", ".netrc", "certs/site.pem", "deploy/id.key"):
            with self.subTest(file=relative):
                validate.errors.clear()
                path = self.write(relative, "placeholder\n")
                code, errors, _ = self.main()
                path.unlink()
                self.assertEqual((code, errors), (1, [f"{relative}: private configuration or key file must not be published"]))

    def test_env_example_is_allowed(self):
        self.write(".env.example", "API_URL=https://example.org\n")
        self.assertEqual(self.main()[:2], (0, []))

    def test_symlinks_are_rejected_without_being_read(self):
        outside = tempfile.TemporaryDirectory(prefix="awesome-jev-outside-")
        self.addCleanup(outside.cleanup)
        target = Path(outside.name) / "secret.md"
        target.write_text(f"{TOKEN}\n[x](missing.md)\n", encoding="utf-8")
        try:
            (self.root / "docs/linked.md").symlink_to(target)
        except OSError:
            self.skipTest("symlinks unavailable")
        code, errors, _ = self.main()
        self.assertEqual((code, errors), (1, ["docs/linked.md: symlinks are not supported in the published artifact"]))

    def test_invalid_utf8_is_reported_and_not_scanned_further(self):
        self.write("docs/latin1.md", data=b"caf\xe9 [x](missing.md)\n")
        code, errors, _ = self.main()
        self.assertEqual((code, errors), (1, ["docs/latin1.md: expected UTF-8 text"]))

    def test_private_values_in_filenames_are_reported_redacted(self):
        self.write(f"notes/{TOKEN}.txt", "benign\n")
        code, errors, _ = self.main()
        self.assertEqual((code, errors), (1, ["notes/[redacted].txt: possible private value in filename"]))

    def test_text_files_including_license_and_gitignore_are_scanned(self):
        self.write(".gitignore", LEAKS["personal filesystem path"] + "\n")
        self.write("LICENSE", "Copyright fixture\n")
        self.write("docs/broken.md", "[x](missing.md)\n")
        code, errors, _ = self.main()
        self.assertEqual(code, 1)
        self.assertCountEqual(errors, [".gitignore: possible personal filesystem path; inspect locally (value redacted)",
                                       "docs/broken.md: missing local target: missing.md"])

    def test_ledger_errors_surface_and_an_empty_corpus_fails(self):
        self.write("data/sources.jsonl", "not json\n")
        self.write("data/archive/old.jsonl", "not json either\n")  # only data/*.jsonl are ledgers
        code, errors, _ = self.main()
        self.assertEqual((code, errors), (1, ["data/sources.jsonl:1: invalid JSON record", "data: no source ledger records"]))
        self.check_index.assert_called_once_with(0)

    def test_curation_policy_is_loaded_and_applied_to_ledgers(self):
        exclusion = {"url": LEDGER_ROW["url"], "reason": "Fixture exclusion.", "evidence_url": LEDGER_ROW["url"],
                     "reviewed_at": "2026-10-16T00:00:00Z"}
        self.write("data/source-curation.json", json.dumps({"schema_version": 1, "exclusions": [exclusion], "annotations": []}))
        code, errors, _ = self.main()
        self.assertEqual((code, errors), (1, ["data/sources.jsonl:1: source is explicitly excluded by data/source-curation.json"]))

    def test_invalid_curation_policy_is_reported(self):
        self.write("data/source-curation.json", "{}")
        code, errors, _ = self.main()
        self.assertEqual((code, errors), (1, ["data/source-curation.json: Unsupported source-curation schema."]))

    def test_missing_node_is_reported(self):
        self.which.return_value = None
        code, errors, _ = self.main()
        self.assertEqual((code, errors), (1, ["JavaScript: Node.js is required for syntax validation"]))

    @unittest.skipUnless(shutil.which("node"), "Node.js is not installed")
    def test_javascript_syntax_is_checked_with_node(self):
        self.which.return_value = shutil.which("node")
        self.write("site/ok.js", "const value = 1;\n")
        self.write("site/bad.mjs", "const = ;\n")
        code, errors, _ = self.main()
        self.assertEqual((code, errors), (1, ["site/bad.mjs: JavaScript syntax check failed"]))

    def test_failure_output_lists_80_errors_then_a_remainder(self):
        self.write("docs/broken.md", "".join(f"[x](missing-{n}.md)\n" for n in range(85)))
        code, _, output = self.main()
        lines = output.splitlines()
        self.assertEqual(code, 1)
        self.assertEqual((lines[0], len(lines), lines[-1]), ("Validation failed:", 82, "- 5 additional errors"))
        self.assertEqual(lines[1], "- docs/broken.md: missing local target: missing-0.md")


if __name__ == "__main__":
    unittest.main()
