"""Regressions for source identity, deduplication, and public-URL hygiene."""

import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts import build_source_index as index
from scripts.validate import public_url


def build_fixture(sources):
    """Build an isolated ledger without changing the real repository."""
    with tempfile.TemporaryDirectory(prefix="awesome-jev-test-") as directory:
        root = Path(directory)
        (root / "data").mkdir()
        rows = [
            {
                "url": url,
                "title": title,
                "relation": "adjacent",
                "verification_level": "metadata_only",
                "retrieved_at": "2026-10-15T00:00:00+00:00",
                "relevance": "Synthetic fixture for source identity checks.",
            }
            for url, title in sources
        ]
        (root / "data/ecosystem-sources.jsonl").write_text(
            "".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8"
        )
        with patch.object(index, "ROOT", root):
            return index.build()


class SourceIdentityTests(unittest.TestCase):
    def test_renamed_model_is_one_source_in_index_and_scan(self):
        from scripts.refresh_sources import identity
        legacy = "https://huggingface.co/lihe07/span-02"
        current = "https://huggingface.co/respanai/span-02"
        distinct = legacy + "0"
        # Different titles and no shared content hash: identity must survive a
        # later card revision without merging a similarly named model.
        payload = build_fixture([(legacy, "Old model card"),
                                 (current, "Current model card"),
                                 (distinct, "Unrelated model")])
        self.assertEqual(payload["counts"]["unique_records"], 2)
        self.assertEqual(payload["counts"]["duplicate_records"], 1)
        self.assertEqual({row["url"] for row in payload["sources"]}, {current, distinct})
        self.assertEqual(identity({"url": legacy}), identity({"url": current}))
        self.assertNotEqual(identity({"url": distinct}), identity({"url": current}))
        self.assertEqual(index.canonical(legacy + "/raw/fixture/README.md"),
                         current + "/raw/fixture/README.md")

    def test_renamed_tracker_stays_one_source_after_content_changes(self):
        current = "https://huggingface.co/spaces/multimodalart/jev-decision-index"
        legacy = "https://huggingface.co/spaces/multimodalart/jev-reproductions-tracker"
        distinct = legacy + "-fixture"
        rows = [
            {"url": legacy, "title": "Old tracker snapshot", "content_sha256": "a" * 64,
             "verification_level": "content_screened"},
            {"url": current, "title": "Current tracker snapshot", "content_sha256": "b" * 64,
             "verification_level": "editorial_reviewed"},
            {"url": distinct, "title": "Unrelated synthetic project", "content_sha256": "c" * 64,
             "verification_level": "content_screened"},
        ]
        with tempfile.TemporaryDirectory(prefix="awesome-jev-test-") as directory:
            root = Path(directory)
            (root / "data").mkdir()
            (root / "data/ecosystem-sources.jsonl").write_text(
                "".join(json.dumps({**row, "relation": "direct",
                                    "retrieved_at": "2026-10-16T00:00:00+00:00",
                                    "relevance": "Synthetic identity regression."}) + "\n"
                        for row in rows), encoding="utf-8")
            with patch.object(index, "ROOT", root):
                payload = index.build()
        self.assertEqual(payload["counts"]["unique_records"], 2)
        self.assertEqual(payload["counts"]["duplicate_records"], 1)
        sources = {row["url"]: row for row in payload["sources"]}
        self.assertEqual(set(sources), {current, distinct})
        self.assertEqual(sources[current]["content_sha256"], "b" * 64)
        self.assertEqual(sources[current]["verification_level"], "editorial_reviewed")

    def test_hub_experiment_code_is_a_project_not_model_weights(self):
        code = {"url":"https://huggingface.co/example/experiment-code", "source_type":"hf_repository", "topic":"implementation-repository", "relation":"direct"}
        self.assertEqual(index.category(code), "Projects")
        self.assertEqual(index.category({**code, "source_type":"hf_model", "topic":"decision-model-card"}), "Models")

    def test_resource_identity_queries_do_not_collapse_distinct_sources(self):
        # Dropping all query parameters silently merged distinct research papers
        # and reports. Exercise final source counts, not just URL formatting.
        sources = [
            ("https://openreview.net/forum?id=paper-alpha", "OpenReview alpha"),
            ("https://openreview.net/forum?id=paper-beta", "OpenReview beta"),
            ("https://citeseerx.ist.psu.edu/document?doi=10.1.1.100.1", "CiteSeer alpha"),
            ("https://citeseerx.ist.psu.edu/document?doi=10.1.1.100.2", "CiteSeer beta"),
            ("https://example.org/report?model=model-alpha", "Model report alpha"),
            ("https://example.org/report?model=model-beta", "Model report beta"),
        ]
        payload = build_fixture(sources)
        self.assertEqual(payload["counts"]["unique_records"], 6)
        self.assertEqual(payload["counts"]["duplicate_records"], 0)
        self.assertEqual({row["url"] for row in payload["sources"]}, {url for url, _ in sources})

    def test_tracking_does_not_inflate_a_resource_count(self):
        canonical = "https://example.org/report?model=alpha"
        tracked = canonical + "&utm_source=fixture&utm_campaign=example&fbclid=fixture&gclid=fixture&msclkid=fixture#results"
        payload = build_fixture([(canonical, "Model report"), (tracked, "Tracked report")])
        self.assertEqual(payload["counts"]["unique_records"], 1)
        self.assertEqual(payload["sources"][0]["url"], canonical)

    def test_arxiv_formats_versions_and_hf_mirror_count_once(self):
        urls = [
            "https://arxiv.org/pdf/1706.04599v2.pdf",
            "http://export.arxiv.org/abs/1706.04599v1",
            "https://arxiv.org/html/1706.04599v3",
            "https://huggingface.co/papers/1706.04599v4",
        ]
        payload = build_fixture([(url, f"Paper representation {number}") for number, url in enumerate(urls)])
        self.assertEqual(payload["counts"]["raw_records"], 4)
        self.assertEqual(payload["counts"]["unique_records"], 1)
        self.assertEqual(payload["counts"]["duplicate_records"], 3)
        self.assertEqual(payload["sources"][0]["url"], "https://arxiv.org/abs/1706.04599")

    def test_generic_scraped_headings_have_distinguishable_titles(self):
        payload = build_fixture([
            ("https://huggingface.co/example/model-alpha", "License"),
            ("https://huggingface.co/example/model-beta", "License"),
        ])
        titles = {row["title"] for row in payload["sources"]}
        self.assertEqual(len(titles), 2)
        self.assertNotIn("License", titles)
        self.assertEqual(payload["counts"]["unique_records"], 2)

    def test_extracted_markup_and_page_chrome_are_not_display_titles(self):
        badge = "[![Awesome](https://awesome.re/badge.svg)](https://awesome.re)"
        cases = {
            "https://github.com/example/awesome-list": (f"Awesome Jev {badge}", "Awesome Jev"),
            "https://github.com/example/truncated": (f"APA Awesome Jev {badge} [![Curated](https://img.shields.io/x.svg)](https://who", "APA Awesome Jev"),
            "https://github.com/example/watersheep": ("![](assets/logo.svg) WaterSheep", "WaterSheep"),
            "https://github.com/example/logo-only": ("![Example, a long logo description](assets/wordmark.svg)", "example/logo-only"),
            "https://github.com/example/foreman": ('<img src="https://example.org/icon.png" alt="" width="32"> Foreman', "Foreman"),
            "https://github.com/example/taste-lint": ("[Taste Lint](https://example.org/taste-lint)", "Taste Lint"),
            "https://github.com/example/gorilla": ("Gorilla: Connected APIs [[Project Website](https://example.org/)]", "Gorilla: Connected APIs"),
            "https://github.com/example/lanebreak": ("LaneBreak\\n\\nSupport ticket routing.\\n\\n```bash\\nnpm i\\n```\\n", "LaneBreak"),
            "https://arxiv.org/abs/1701.06538": ("[1701.06538] Outrageously Large Neural Networks", "Outrageously Large Neural Networks"),
            "https://aclanthology.org/2025.naacl-long.174": ("When2Call: When (not) to Call Tools - ACL Anthology", "When2Call: When (not) to Call Tools"),
            "https://zenodo.org/records/7299879": ("BPoMP: Benchmark of Poetical Minimal Pairs | Zenodo", "BPoMP: Benchmark of Poetical Minimal Pairs"),
            "https://dev.to/example/decider": ("decider: typed decisions - DEV Community Navigation menu Search Search Close", "decider: typed decisions"),
            "https://huggingface.co/datasets/example/reviews": ("Dataset Card for Dataset Name", "example/reviews"),
            # Angle brackets that are not HTML belong to the paper title.
            "https://arxiv.org/abs/1906.00274": ('[1906.00274] "President Vows to Cut <Taxes> Hair"', '"President Vows to Cut <Taxes> Hair"'),
            "https://example.org/entropy": ("Entropy After </Think> for early exiting", "Entropy After </Think> for early exiting"),
        }
        payload = build_fixture([(url, raw) for url, (raw, _) in cases.items()])
        titles = {row["url"]: row["title"] for row in payload["sources"]}
        self.assertEqual(titles, {url: expected for url, (_, expected) in cases.items()})
        self.assertEqual(payload["counts"]["unique_records"], len(cases))


class SourceIndexCheckTests(unittest.TestCase):
    """--check must cover every generated file, including the README badge."""

    def run_main(self, root, *args):
        with patch.object(index, "ROOT", root), patch("sys.argv", ["build_source_index.py", *args]), \
                contextlib.redirect_stdout(io.StringIO()):
            index.main()

    def test_check_names_each_stale_output(self):
        rows = [{"url": "https://example.org/report", "title": "Fixture report", "relation": "direct",
                 "verification_level": "content_screened", "retrieved_at": "2026-10-16T00:00:00+00:00",
                 "relevance": "Synthetic check regression."}]
        for name in ("site/data/source-index.json", "data/source-counts.json", "site/data/source-badge.json"):
            with self.subTest(name=name), tempfile.TemporaryDirectory(prefix="awesome-jev-test-") as directory:
                root = Path(directory)
                (root / "data").mkdir()
                (root / "data/ecosystem-sources.jsonl").write_text(
                    "".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")
                self.run_main(root)
                self.run_main(root, "--check")
                path = root / name
                path.write_text(path.read_text(encoding="utf-8").replace("1", "9"), encoding="utf-8")
                with self.assertRaises(SystemExit) as stale:
                    self.run_main(root, "--check")
                self.assertIn(name, str(stale.exception))
                path.unlink()
                with self.assertRaises(SystemExit) as missing:
                    self.run_main(root, "--check")
                self.assertIn(name, str(missing.exception))


class PublicSourceUrlTests(unittest.TestCase):
    def test_private_and_local_ipv4_are_not_public_sources(self):
        for host in ("127.0.0.1", "10.0.0.1", "172.16.0.1", "192.168.1.1", "169.254.1.1", "100.64.0.1", "0.0.0.0"):
            with self.subTest(host=host):
                self.assertFalse(public_url(f"http://{host}/source"))

    def test_private_and_local_ipv6_are_not_public_sources(self):
        for host in ("::1", "::", "fd00::1", "fe80::1", "::ffff:127.0.0.1"):
            with self.subTest(host=host):
                self.assertFalse(public_url(f"https://[{host}]/source"))

    def test_credential_bearing_urls_are_rejected(self):
        # Assemble clearly synthetic placeholders so no credential-shaped value
        # is committed, even in a regression fixture.
        value = "https://" + "fixture-user" + ":" + "fixture-password" + "@example.org/source"
        self.assertFalse(public_url(value))

    def test_secret_query_parameters_are_rejected(self):
        for key in ("api_key", "apikey", "access_token", "token", "signature", "API_KEY"):
            with self.subTest(key=key):
                self.assertFalse(public_url("https://example.org/source?" + key + "=fixture"))

    def test_public_identity_queries_remain_allowed(self):
        for value in (
            "https://openreview.net/forum?id=paper-alpha",
            "https://citeseerx.ist.psu.edu/document?doi=10.1.1.100.1",
            "https://example.org/report?model=model-alpha",
            "https://arxiv.org/abs/1706.04599",
        ):
            with self.subTest(value=value):
                self.assertTrue(public_url(value))


class ReservedSiteRouteTests(unittest.TestCase):
    """GitHub and Hub site routes are never discovered as repositories."""
    ROUTES = (
        "https://github.com/user-attachments/assets/0f3c5e1a-1111-4222-8333-944445555666",
        "https://github.com/User-Attachments/assets/0f3c5e1a-1111-4222-8333-944445555666",
        "https://github.com/apps/fixture-bot",
        "https://github.com/marketplace/actions/fixture",
        "https://github.com/search/advanced",
        "https://github.com/advisories/fixture",
        "https://github.com/customer-stories/fixture",
        "https://huggingface.co/api/models/fixture/model",
        "https://huggingface.co/api/datasets/fixture/data/tree/main",
        "https://huggingface.co/learn/nlp-course/chapter1/1",
        "https://huggingface.co/tasks/text-classification",
        "https://huggingface.co/models/fixture",
        "https://huggingface.co/posts/fixture/123",
    )

    def test_site_routes_are_not_canonical_sources(self):
        from scripts import collect_ecosystem as ecosystem
        from scripts import refresh_sources as refresh
        for url in self.ROUTES:
            with self.subTest(url=url):
                self.assertIsNone(ecosystem.canonical(url))
                with self.assertRaises(refresh.FetchError):
                    refresh.canonical_source(url)

    def test_repository_routes_still_canonicalize(self):
        from scripts import collect_ecosystem as ecosystem
        cases = {
            "https://github.com/Fixture-Owner/Router/blob/main/README.md": "https://github.com/fixture-owner/router",
            "https://github.com/fixture/search-tools": "https://github.com/fixture/search-tools",
            "https://huggingface.co/fixture/jev-model/tree/main": "https://huggingface.co/fixture/jev-model",
            "https://huggingface.co/datasets/fixture/decisions": "https://huggingface.co/datasets/fixture/decisions",
            "https://huggingface.co/spaces/fixture/demo": "https://huggingface.co/spaces/fixture/demo",
        }
        for url, expected in cases.items():
            with self.subTest(url=url):
                self.assertEqual(ecosystem.canonical(url), expected)

    def test_readme_image_embed_is_not_an_implementation_child(self):
        from scripts import collect_ecosystem as ecosystem
        readme = ("# Jev router\n\n![diagram](https://github.com/user-attachments/assets/0f3c5e1a-1111-4222-8333-944445555666)\n\n"
                  "Built on https://github.com/fixture/decision-core for typed decisions.\n\n"
                  + "Jev typed decision models need calibrated probability readouts for routing. " * 6)
        seed = {"url": "https://github.com/fixture/router", "title": "router", "topic": "implementation-repository",
                "relation": "direct", "relevance": "Fixture.", "discovered_from": ["https://example.org/index"], "discovery_depth": 0}
        with patch.object(ecosystem, "fetch", return_value=(readme.encode(), "https://raw.githubusercontent.com/fixture/router/main/README.md", "text/plain")):
            record, children = ecosystem.audit(seed)
        self.assertEqual(record["verification_level"], "content_screened")
        self.assertEqual([child["url"] for child in children], ["https://github.com/fixture/decision-core"])


if __name__ == "__main__":
    unittest.main()
