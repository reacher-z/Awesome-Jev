"""Offline crawlability, bilingual identity, and visible structured-data checks."""

from datetime import date
from collections import Counter
from html.parser import HTMLParser
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest
from urllib.parse import parse_qs, urljoin, urlsplit
from urllib.robotparser import RobotFileParser
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://awesomejev.github.io"
PAIRS = (("/", "/zh/"), ("/guide/", "/zh/guide/"), ("/papers/", "/zh/papers/"), ("/models/", "/zh/models/"), ("/discoveries/", "/zh/discoveries/"))
TOPIC_SLUGS = ("option-label-bias", "audiojev", "graph-decision-benchmarks")
PAIRS += (("/topics/", "/zh/topics/"),) + tuple((f"/topics/{slug}/", f"/zh/topics/{slug}/") for slug in TOPIC_SLUGS)
ROUTES = tuple(route for pair in PAIRS for route in pair)
BUILD_INPUTS = (
    "scripts/build_site.mjs", "templates/index.html", "data/search-guide.json", "data/research-topics.json",
    "data/expansion-progress-2026-10-16.json", "data/discovery-translations.zh-CN.json", "references.bib",
    "site/app.js", "site/model-directory.js", "site/paper-directory.js", "site/catalog.mjs", "site/resource-view.mjs", "site/styles.css",
)
# The build also draws the papers-per-week chart and rewrites its region in both READMEs.
BUILD_INPUTS += ("scripts/paper_activity.mjs", "README.md", "README.zh-CN.md")


def words(value):
    return re.sub(r"\s+", " ", value).strip()


def objects(value):
    """Walk inline JSON-LD graphs, including nested mainEntity ItemLists."""
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from objects(child)
    elif isinstance(value, list):
        for child in value:
            yield from objects(child)


def has_type(value, wanted):
    kind = value.get("@type", "")
    return wanted in kind if isinstance(kind, list) else kind == wanted


class CrawlPage(HTMLParser):
    def __init__(self, source):
        super().__init__(convert_charrefs=True)
        self.language = ""
        self.canonicals = []
        self.alternates = []
        self.robots = []
        self.cards = []
        self.headings = []
        self.structured = []
        self.import_maps = []
        self.scripts = []
        self.stylesheets = []
        self.body_text = []
        self.ids = []
        self.links = []
        self._in_body = False
        self._script = None
        self._script_text = []
        self._h1 = None
        self._card = None
        self._card_title = False
        self._card_description = False
        self._model_row = False
        self._style = False
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if "id" in attrs:
            self.ids.append(attrs["id"])
        if tag == "a" and "href" in attrs:
            self.links.append(attrs["href"])
        classes = set(attrs.get("class", "").split())
        if tag == "html":
            self.language = attrs.get("lang", "")
        elif tag == "body":
            self._in_body = True
        elif tag == "link":
            relation = attrs.get("rel", "").split()
            if "canonical" in relation:
                self.canonicals.append(attrs.get("href", ""))
            if "alternate" in relation and "hreflang" in attrs:
                self.alternates.append((attrs["hreflang"], attrs.get("href", "")))
            if "stylesheet" in relation:
                self.stylesheets.append(attrs.get("href", ""))
        elif tag == "meta" and attrs.get("name", "").lower() in {"robots", "googlebot", "bingbot"}:
            self.robots.append(attrs.get("content", ""))
        elif tag == "script":
            self._script = attrs.get("type", "other")
            self._script_text = []
            self.scripts.append(attrs)
        elif tag == "style":
            self._style = True
        elif tag == "h1":
            self._h1 = []
        elif (tag == "article" and "resource-row" in classes) or (tag == "tr" and classes & {"model-row", "paper-row"}):
            self._model_row = tag == "tr"
            self._card_title = "model-row" in classes
            self._card = {"url": "", "name": [], "text": [], "description": [], "hidden": "hidden" in attrs or attrs.get("aria-hidden") == "true",
                          "category": attrs.get("data-category", ""), "relation": attrs.get("data-relation", ""),
                          "verification_level": attrs.get("data-verification-level", "")}
        elif tag == "h3" and self._card is not None:
            self._card_title = True
        elif tag == "a" and self._card is not None and "paper-title" in classes:
            self._card_title = True
            self._card["url"] = attrs.get("href", "")
        elif tag == "a" and self._card is not None and self._card_title:
            self._card["url"] = attrs.get("href", "")
        elif self._card is not None and ((tag == "p" and "resource-description" in classes) or (tag == "td" and classes & {"model-scope", "paper-finding"})):
            self._card_description = True

    def handle_endtag(self, tag):
        if tag == "script":
            if self._script == "application/ld+json":
                self.structured.append(json.loads("".join(self._script_text)))
            elif self._script == "importmap":
                self.import_maps.append(json.loads("".join(self._script_text)))
            self._script = None
        elif tag == "style":
            self._style = False
        elif tag == "body":
            self._in_body = False
        elif tag == "h1" and self._h1 is not None:
            self.headings.append(words("".join(self._h1)))
            self._h1 = None
        elif tag == "h3" or (tag == "a" and self._model_row):
            self._card_title = False
        elif tag in {"p", "td"}:
            self._card_description = False
        elif (tag == "article" or (tag == "tr" and self._model_row)) and self._card is not None:
            self._card["name"] = words("".join(self._card["name"]))
            self._card["text"] = words(" ".join(self._card["text"]))
            self._card["description"] = words("".join(self._card["description"]))
            self.cards.append(self._card)
            self._card = None
            self._model_row = False

    def handle_data(self, value):
        if self._script is not None:
            self._script_text.append(value)
            return
        if self._style:
            return
        if self._in_body:
            self.body_text.append(value)
        if self._h1 is not None:
            self._h1.append(value)
        if self._card is not None and self._card_title:
            self._card["name"].append(value)
        if self._card is not None:
            self._card["text"].append(value)
            if self._card_description:
                self._card["description"].append(value)


class SiteDiscoveryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pages = {}
        for route in ROUTES:
            path = ROOT / "site" / route.strip("/") / "index.html"
            cls.pages[route] = CrawlPage(path.read_text(encoding="utf-8"))

    def test_homepages_publish_the_curated_collection_without_javascript(self):
        for route in ("/", "/zh/"):
            with self.subTest(route=route):
                cards = self.pages[route].cards
                self.assertGreaterEqual(len(cards), 60)
                self.assertTrue(all(card["name"] and not card["hidden"] for card in cards))
                self.assertTrue(all(urlsplit(card["url"]).scheme in {"http", "https"} and urlsplit(card["url"]).netloc for card in cards))
                self.assertEqual(len({card["url"] for card in cards}), len(cards))
        self.assertEqual([c["url"] for c in self.pages["/"].cards], [c["url"] for c in self.pages["/zh/"].cards])

    def test_home_module_graph_and_styles_resolve_to_current_file_bytes(self):
        imports_pattern = re.compile(
            r"^\s*(?:import\s+(?:[^;\n]*?\bfrom\s+)?|export\s+[^;\n]*?\bfrom\s+)[\"']([^\"']+)[\"']",
            re.MULTILINE,
        )

        def check_version(url):
            parsed = urlsplit(url)
            self.assertEqual(parsed.netloc, urlsplit(BASE).netloc)
            path = (ROOT / "site" / parsed.path.lstrip("/")).resolve()
            self.assertTrue(path.is_relative_to(ROOT / "site"))
            expected = hashlib.sha256(path.read_bytes()).hexdigest()[:12]
            self.assertEqual(parse_qs(parsed.query), {"v": [expected]})
            return path

        for route in ("/", "/zh/"):
            with self.subTest(route=route):
                page = self.pages[route]
                self.assertEqual(len(page.import_maps), 1)
                module_positions = [i for i, script in enumerate(page.scripts) if script.get("type") == "module"]
                map_positions = [i for i, script in enumerate(page.scripts) if script.get("type") == "importmap"]
                self.assertEqual(len(module_positions), 1)
                self.assertLess(map_positions[0], module_positions[0], "Map must precede module resolution")
                entry = urljoin(BASE + route, page.scripts[module_positions[0]]["src"])
                self.assertEqual(urlsplit(entry).path, "/app.js")
                mappings = {urljoin(BASE + route, key): urljoin(BASE + route, value)
                            for key, value in page.import_maps[0]["imports"].items()}
                queue, visited, mapped = [entry], set(), set()
                while queue:
                    module_url = queue.pop()
                    if module_url in visited:
                        continue
                    visited.add(module_url)
                    path = check_version(module_url)
                    for specifier in imports_pattern.findall(path.read_text()):
                        dependency = urljoin(module_url, specifier)
                        self.assertIn(dependency, mappings, "Every imported module needs a versioned resolution")
                        mapped.add(dependency)
                        queue.append(mappings[dependency])
                self.assertEqual(mapped, set(mappings))

        for route, page in self.pages.items():
            with self.subTest(stylesheet_route=route):
                self.assertEqual(len(page.stylesheets), 1)
                check_version(urljoin(BASE + route, page.stylesheets[0]))

    def test_catalog_update_changes_static_content_and_module_url_without_manual_version_bump(self):
        node = shutil.which("node")
        self.assertIsNotNone(node)
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for name in BUILD_INPUTS:
                destination = root / name
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / name, destination)

            def build(*args):
                result = subprocess.run([node, "scripts/build_site.mjs", *args], cwd=root,
                                        capture_output=True, text=True, timeout=45)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

            def home():
                return CrawlPage((root / "site/index.html").read_text())

            build()
            before = home()
            published = {p.relative_to(root): p.read_bytes() for p in (root / "site").rglob("*") if p.is_file()}
            build()
            self.assertEqual(published, {p.relative_to(root): p.read_bytes() for p in (root / "site").rglob("*") if p.is_file()})
            build("--check")

            catalog = root / "site/catalog.mjs"
            probe = {"category": "Guides", "title": "Cache coherency probe", "url": "https://example.org/cache-probe",
                     "by": "Test fixture", "en": "A newly published resource.", "zh": "新发布的资源。"}
            catalog.write_text(catalog.read_text() + "\nresources.push(" + json.dumps(probe) + ");\n")
            stale = subprocess.run([node, "scripts/build_site.mjs", "--check"], cwd=root,
                                   capture_output=True, text=True, timeout=45)
            self.assertNotEqual(stale.returncode, 0, "A changed catalog must invalidate the generated pages")
            build()
            after = home()
            self.assertIn(probe["url"], [card["url"] for card in after.cards])
            self.assertEqual(len(after.cards), len(before.cards) + 1)
            self.assertNotEqual(before.import_maps[0]["imports"]["/catalog.mjs"], after.import_maps[0]["imports"]["/catalog.mjs"])
            self.assertEqual(before.import_maps[0]["imports"]["/resource-view.mjs"], after.import_maps[0]["imports"]["/resource-view.mjs"])
            before_entry = next(s["src"] for s in before.scripts if s.get("type") == "module")
            after_entry = next(s["src"] for s in after.scripts if s.get("type") == "module")
            self.assertEqual(before_entry, after_entry, "Unchanged application bytes should retain their cache URL")
            build("--check")

            for filename in ("app.js", "resource-view.mjs", "styles.css"):
                path = root / "site" / filename
                path.write_text(path.read_text() + "\n/* Cache invalidation fixture. */\n")
            build()
            changed = home()
            self.assertNotEqual(after_entry, next(s["src"] for s in changed.scripts if s.get("type") == "module"))
            self.assertNotEqual(after.import_maps[0]["imports"]["/resource-view.mjs"], changed.import_maps[0]["imports"]["/resource-view.mjs"])
            self.assertNotEqual(after.stylesheets, changed.stylesheets)
            build("--check")

    def test_each_language_page_has_a_distinct_self_canonical_and_reciprocal_alternates(self):
        observed = []
        for english, chinese in PAIRS:
            for route in (english, chinese):
                with self.subTest(route=route):
                    page = self.pages[route]
                    self.assertEqual(page.canonicals, [BASE + route])
                    observed.extend(page.canonicals)
                    alternates = dict(page.alternates)
                    self.assertEqual(len(alternates), len(page.alternates))
                    self.assertEqual(alternates.get("en"), BASE + english)
                    self.assertEqual(alternates.get("zh-CN"), BASE + chinese)
                    if "x-default" in alternates:
                        self.assertEqual(alternates["x-default"], BASE + english)
                    self.assertTrue(page.language.lower().startswith("zh" if route.startswith("/zh/") else "en"))
                    self.assertEqual(len(page.headings), 1)
        self.assertEqual(len(set(observed)), len(ROUTES))

    def test_chinese_routes_contain_translated_body_text_before_scripts_run(self):
        for route in (route for route in ROUTES if route.startswith("/zh/")):
            with self.subTest(route=route):
                self.assertGreater(len(re.findall(r"[\u4e00-\u9fff]", "".join(self.pages[route].body_text))), 30)

    def test_language_and_titles_come_only_from_generated_html(self):
        for route in ROUTES:
            with self.subTest(route=route):
                self.assertEqual(self.pages[route].language, "zh-CN" if route.startswith("/zh/") else "en")
        app = (ROOT / "site/app.js").read_text(encoding="utf-8")
        for write in (r"documentElement\.lang\s*=[^=]", r"document\.title\s*=[^=]", r"\.content\s*=[^=]"):
            self.assertIsNone(re.search(write, app), "site/app.js must not rewrite the generated language, title or meta tags")
        styles = (ROOT / "site/styles.css").read_text(encoding="utf-8")
        self.assertIsNone(re.search(r'\[lang="?zh"?\]', styles), 'Chinese rules must also match lang="zh-CN"; use :lang(zh)')

    def test_result_count_live_region_uses_speakable_text(self):
        statuses = json.loads(subprocess.check_output(
            [shutil.which("node"), "--input-type=module", "-e",
             "import {translations as t} from './site/catalog.mjs'; process.stdout.write(JSON.stringify(['en', 'zh'].map(l => [t[l].resourceCount(5, 134), t[l].resourceCount(0, 134)])));"],
            cwd=ROOT, text=True))
        for language, (some, none) in zip(("en", "zh"), statuses):
            with self.subTest(language=language):
                self.assertIn("5", some)
                self.assertIn("134", some)
                self.assertNotRegex(some + none, r"\b0\d|/|[A-Z]{2,}", "Screen readers announce this text as written")
                self.assertNotRegex(none, r"\d", "An empty result needs words, not a zero count")

    def test_homepage_translation_preserves_interactive_controls(self):
        required = {"resource-search", "resource-list", "result-count", "corpus-search", "corpus-list", "start", "copy-code", "copy-status"}
        for route in ("/", "/zh/"):
            with self.subTest(route=route):
                ids = self.pages[route].ids
                self.assertTrue(required.issubset(ids), "A translation/build replacement removed a required interaction target")
                self.assertEqual(len(ids), len(set(ids)), "Generated HTML must not duplicate interaction IDs")

    def test_item_lists_match_visible_link_titles_order_and_counts(self):
        for route in ("/", "/zh/", "/papers/", "/zh/papers/", "/models/", "/zh/models/", "/discoveries/", "/zh/discoveries/"):
            with self.subTest(route=route):
                page = self.pages[route]
                if "models" in route:
                    self.assertGreater(len(page.cards), 0)
                elif "discoveries" not in route:
                    self.assertGreaterEqual(len(page.cards), 20)
                item_lists = [item for block in page.structured for item in objects(block) if has_type(item, "ItemList")]
                self.assertEqual(len(item_lists), 1)
                listing = item_lists[0]
                items = listing["itemListElement"]
                self.assertEqual(listing["numberOfItems"], len(page.cards))
                self.assertEqual(len(items), len(page.cards))
                for number, (item, card) in enumerate(zip(items, page.cards), 1):
                    self.assertTrue(has_type(item, "ListItem"))
                    self.assertEqual(item["position"], number)
                    self.assertEqual(item["url"], card["url"])
                    self.assertEqual(words(item["name"]), card["name"])

    def test_model_directory_preserves_the_collection_and_export_in_both_languages(self):
        exported = json.loads((ROOT / "site/models.json").read_text())
        self.assertEqual(exported["url"], BASE + "/models/")
        self.assertTrue(exported["scope"])
        models = exported["models"]
        expected = json.loads(subprocess.check_output(
            [shutil.which("node"), "--input-type=module", "-e",
             "import {resources} from './site/catalog.mjs'; process.stdout.write(JSON.stringify(resources.filter(row => row.category === 'Models')));"],
            cwd=ROOT, text=True))
        self.assertEqual(models, expected)
        model_urls = {row["url"] for row in expected}
        self.assertTrue(all(row["category"] == "Models" for row in models))
        for language, prefix in (("en", "/"), ("zh", "/zh/")):
            with self.subTest(language=language):
                page = self.pages[prefix + "models/"]
                home_models = [card for card in self.pages[prefix].cards if card["url"] in model_urls]
                for compact, home in zip(page.cards, home_models):
                    self.assertEqual({key:compact[key] for key in ("name", "url", "description")},
                                     {key:home[key] for key in ("name", "url", "description")})
                self.assertEqual([card["url"] for card in page.cards], [row["url"] for row in models])
                self.assertEqual([card["description"] for card in page.cards], [words(row[language]) for row in models])
                for card, model in zip(page.cards, models):
                    self.assertIn(model["publisher"], card["text"])
                    if model["license"] not in {"Not declared", "Apache-2.0 weights; MIT server"}:
                        self.assertIn(model["license"], card["text"])
                self.assertTrue(all(not card["hidden"] for card in page.cards))
                self.assertIn(prefix + "models/", self.pages[prefix].links)
                self.assertIn(prefix + "models/", self.pages[prefix + "guide/"].links)
                self.assertIn("/models.json", page.links)

    def test_paper_directory_is_a_complete_static_table_in_both_languages(self):
        exported = json.loads((ROOT / "site/papers.json").read_text())
        papers, themes = exported["papers"], {theme["id"]: theme for theme in exported["themes"]}
        for language, prefix in (("en", "/"), ("zh", "/zh/")):
            with self.subTest(language=language):
                route = prefix + "papers/"
                page = self.pages[route]
                self.assertEqual([card["url"] for card in page.cards], [paper["url"] for paper in papers])
                self.assertEqual([card["description"] for card in page.cards], [words(paper[language]) for paper in papers])
                for card, paper in zip(page.cards, papers):
                    self.assertFalse(card["hidden"])
                    self.assertIn(paper["date"], card["text"])
                    self.assertIn(themes[paper["theme"]]["short"][language], card["text"])
                    if "artifact_note" in paper:
                        self.assertIn(words(paper["artifact_note"][language]), card["text"])
                    for kind, urls in paper.get("artifacts", {}).items():
                        for url in [] if kind == "unverified" else [urls] if isinstance(urls, str) else urls:
                            self.assertIn(url, page.links)
                # Filters and sorting are enhancements: without JavaScript their controls stay hidden.
                source = (ROOT / "site" / route.strip("/") / "index.html").read_text(encoding="utf-8")
                controls = re.findall(r"<[a-z]+[^>]*\bdata-paper-controls\b[^>]*>", source)
                self.assertTrue(controls)
                self.assertTrue(all(re.search(r"\bhidden\b", tag) for tag in controls))
                # The papers-with-code checkbox counts what the homepage checkbox counts.
                home = (ROOT / "site" / prefix.strip("/") / "index.html").read_text(encoding="utf-8")
                count = re.compile(r'id="(?:paper-)?code-filter" />.*?<span class="filter-count" aria-hidden="true">(\d+)</span>')
                self.assertEqual(count.search(source)[1], count.search(home)[1])
                self.assertEqual(int(count.search(source)[1]), source.count('data-code="true"'))

    def test_new_source_directory_preserves_every_accepted_resource_and_evidence_label(self):
        report = json.loads((ROOT / "data/expansion-progress-2026-10-16.json").read_text())
        translations = json.loads((ROOT / "data/discovery-translations.zh-CN.json").read_text())["translations"]
        sources = {row["url"]: row for row in report["additions"]}
        self.assertEqual(len(sources), report["accepted_new_sources"])
        labels = {
            "en": {"direct": "Directly related", "adjacent": "Related field", "background": "Research background",
                   "editorial_reviewed": "Editorially reviewed", "content_screened": "Content screened", "abstract_checked": "Abstract checked"},
            "zh": {"direct": "直接相关", "adjacent": "邻近领域", "background": "研究背景",
                   "editorial_reviewed": "编辑审阅", "content_screened": "内容筛查", "abstract_checked": "摘要核查"},
        }
        for route, language in (("/discoveries/", "en"), ("/zh/discoveries/", "zh")):
            with self.subTest(route=route):
                page = self.pages[route]
                self.assertEqual(len(page.cards), len(sources))
                self.assertEqual({card["url"] for card in page.cards}, set(sources))
                self.assertEqual(Counter(card["category"] for card in page.cards), report["by_category"])
                self.assertIn("/data/expansion-progress.json", page.links)
                for card in page.cards:
                    source = sources[card["url"]]
                    self.assertFalse(card["hidden"])
                    self.assertEqual(card["name"], words(source["title"]))
                    description = source["description"] if language == "en" else translations[source["description"]]
                    self.assertEqual(words(description), card["description"])
                    if language == "zh":
                        self.assertRegex(description, r"[\u3400-\u9fff]", "Every Chinese directory entry needs a translated description")
                        self.assertNotEqual(words(source["description"]), card["description"])
                    self.assertEqual(card["relation"], source["relation"])
                    self.assertEqual(card["verification_level"], source["verification_level"])
                    self.assertIn(labels[language][source["relation"]], card["text"])
                    self.assertIn(labels[language][source["verification_level"]], card["text"])
        self.assertEqual([card["url"] for card in self.pages["/discoveries/"].cards], [card["url"] for card in self.pages["/zh/discoveries/"].cards])

    def test_changed_or_missing_source_translation_stops_build_before_publication(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for name in BUILD_INPUTS:
                destination = root / name
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / name, destination)
            path = root / "data/expansion-progress-2026-10-16.json"
            report = json.loads(path.read_text())
            # A newly discovered material limitation must not keep an old translation.
            report["additions"][0]["description"] += " A newly reported reproduction limit."
            path.write_text(json.dumps(report))
            result = subprocess.run([shutil.which("node"), "scripts/build_site.mjs"], cwd=root,
                                    capture_output=True, text=True, timeout=45)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Missing Chinese discovery description translation", result.stderr)
            self.assertFalse((root / "site/zh/discoveries/index.html").exists())

            localization_path = root / "data/discovery-translations.zh-CN.json"
            localization = json.loads(localization_path.read_text())
            localization["translations"][report["additions"][0]["description"]] = "翻译后的新条目，并保留新增的复现限制。"
            localization_path.write_text(json.dumps(localization))
            result = subprocess.run([shutil.which("node"), "scripts/build_site.mjs"], cwd=root,
                                    capture_output=True, text=True, timeout=45)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("翻译后的新条目，并保留新增的复现限制。", (root / "site/zh/discoveries/index.html").read_text())

    def test_homepages_link_localized_discoveries_and_download_matches_source_report(self):
        self.assertIn("/discoveries/", self.pages["/"].links)
        self.assertIn("/zh/discoveries/", self.pages["/zh/"].links)
        original = json.loads((ROOT / "data/expansion-progress-2026-10-16.json").read_text())
        published = json.loads((ROOT / "site/data/expansion-progress.json").read_text())
        self.assertEqual(published, original)

    def test_guide_article_headline_matches_visible_page_heading(self):
        for route in ("/guide/", "/zh/guide/") + tuple(route for route in ROUTES if any(f"/topics/{slug}/" in route for slug in TOPIC_SLUGS)):
            with self.subTest(route=route):
                page = self.pages[route]
                articles = [item for block in page.structured for item in objects(block) if has_type(item, "Article")]
                self.assertEqual(len(articles), 1)
                self.assertEqual(words(articles[0]["headline"]), page.headings[0])
                citations = articles[0].get("citation", [])
                self.assertTrue(citations, "The research guide must expose its source citations")
                self.assertTrue(set(citations).issubset(page.links), "Structured citations must also be visible page links")
                self.assertTrue(all(urlsplit(url).scheme in {"http", "https"} and urlsplit(url).netloc for url in citations))

    def test_topic_answers_and_evidence_are_visible_without_javascript(self):
        topics = json.loads((ROOT / "data/research-topics.json").read_text())["topics"]
        self.assertEqual({topic["slug"] for topic in topics}, set(TOPIC_SLUGS))
        for topic in topics:
            for language, prefix in (("en", "/"), ("zh", "/zh/")):
                route = prefix + "topics/" + topic["slug"] + "/"
                with self.subTest(route=route):
                    page = self.pages[route]
                    visible = words(" ".join(page.body_text))
                    self.assertIn(words(topic[language]["answer"]), visible)
                    self.assertIn(words(topic[language]["scope"]), visible)
                    for section in topic[language]["sections"]:
                        self.assertIn(words(section["text"]), visible)
                        self.assertIn(section["id"], page.ids)
                    article = next(item for block in page.structured for item in objects(block) if has_type(item, "Article"))
                    self.assertEqual(article["datePublished"], topic["published"])
                    self.assertEqual(article["dateModified"], topic["updated"])
                    self.assertIn(BASE + prefix + "topics/", [item.get("item") for block in page.structured for item in objects(block) if has_type(item, "ListItem")])

    def test_every_topic_is_reachable_through_ordinary_internal_links(self):
        for prefix in ("/", "/zh/"):
            index = prefix + "topics/"
            self.assertIn(index, self.pages[prefix].links)
            for slug in TOPIC_SLUGS:
                route = index + slug + "/"
                for source in (index, prefix + "papers/", prefix + "guide/"):
                    self.assertIn(route, self.pages[source].links)
                self.assertIn(index, self.pages[route].links)
            structured = [item for block in self.pages[index].structured for item in objects(block) if has_type(item, "ItemList")]
            self.assertEqual(len(structured), 1)
            self.assertEqual(structured[0]["numberOfItems"], len(TOPIC_SLUGS))
            for item in structured[0]["itemListElement"]:
                self.assertIn(urlsplit(item["url"]).path, self.pages[index].links)
                self.assertIn(words(item["name"]), words(" ".join(self.pages[index].body_text)))

    def test_search_and_answer_engine_crawlers_are_not_blocked(self):
        robots_text = (ROOT / "site/robots.txt").read_text()
        rules = RobotFileParser()
        rules.parse(robots_text.splitlines())
        for agent in ("Googlebot", "Bingbot", "OAI-SearchBot"):
            for route, page in self.pages.items():
                with self.subTest(agent=agent, route=route):
                    self.assertTrue(rules.can_fetch(agent, BASE + route))
                    self.assertFalse(any(set(re.split(r"[,\s]+", value.lower())) & {"noindex", "none"} for value in page.robots))
        self.assertIn(BASE + "/sitemap.xml", rules.site_maps() or [])

    def test_sitemap_lists_all_canonical_pages(self):
        tree = ET.fromstring((ROOT / "site/sitemap.xml").read_bytes())
        ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        locations = [node.text for node in tree.findall("sm:url/sm:loc", ns)]
        self.assertEqual(set(locations), {BASE + route for route in ROUTES})
        self.assertEqual(len(locations), len(set(locations)))
        for modified in tree.findall("sm:url/sm:lastmod", ns):
            date.fromisoformat(modified.text[:10])

    def test_generated_discovery_artifacts_are_current(self):
        node = shutil.which("node")
        self.assertIsNotNone(node, "Node.js is required to verify generated site artifacts")
        result = subprocess.run([node, "scripts/build_site.mjs", "--check"], cwd=ROOT, capture_output=True, text=True, timeout=45)
        output = (result.stdout + result.stderr).replace(str(ROOT), ".")[:1500]
        self.assertEqual(result.returncode, 0, output)


if __name__ == "__main__":
    unittest.main()
