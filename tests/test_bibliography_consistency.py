"""The README paper tables, their stated counts, references.bib and the site catalog describe the same papers.

Paper metadata is maintained by hand in README.md, README.zh-CN.md, references.bib and
site/catalog.mjs. These tests parse all four and require, for every arXiv ID, the same
version, version date, first-submission date, title and author credit, and require the
counts the READMEs state to equal the counted entries.
"""

from pathlib import Path
import json
import re
import shutil
import subprocess
import unittest

from scripts.validate import bib_fields


ROOT = Path(__file__).resolve().parents[1]
README = {"en": ROOT / "README.md", "zh": ROOT / "README.zh-CN.md"}
PAPERS_HEADING = {"en": "Papers", "zh": "论文"}
WHATS_NEW_HEADING = {"en": "What's new", "zh": "最近更新"}
ROW = re.compile(
    r"^\| (?P<date>\d{4}-\d{2}-\d{2})<br>v(?P<version>\d+)"
    r"(?:<br>(?:first submitted |首次提交<br>)(?P<first>\d{4}-\d{2}-\d{2}))? "
    r"\| \[(?P<title>.+?)\]\(https://arxiv\.org/abs/(?P<id>\d{4}\.\d{4,5})v(?P<url_version>\d+)\)"
    r"<br>(?P<authors>[^|]+?) \| (?P<finding>[^|]+?) \| (?P<artifacts>[^|]+?) \|$"
)
NEW_ITEM = re.compile(
    r"^- (?P<date>\d{4}-\d{2}-\d{2}) · v(?P<version>\d+) · "
    r"\[(?P<title>.+?)\]\(https://arxiv\.org/abs/(?P<id>\d{4}\.\d{4,5})v(?P<url_version>\d+)\)"
    r" — (?:in |见)\[(?P<section>[^\]]+)\]\(#(?P<anchor>[^)]+)\)$"
)
STATED_PAPERS = {"en": r"All (\d+) direct studies below", "zh": r"下列 (\d+) 项直接研究"}
STATED_BIB = {"en": r"\[references\.bib\]\(references\.bib\) \((\d+) entries\)",
              "zh": r"共 (\d+) 条书目信息收录于 \[references\.bib\]\(references\.bib\)"}
BIB_NOTE = re.compile(r"^Version (\d+), (\d{4}-\d{2}-\d{2})(?:; first posted (\d{4}-\d{2}-\d{2}))?; preprint$")


def section(text, heading, level="## "):
    """Return the lines under `level + heading` up to the next heading of the same or higher level."""
    lines = text.split("\n")
    start = lines.index(level + heading) + 1
    stop = next((n for n in range(start, len(lines))
                 if lines[n].startswith("#") and len(lines[n]) - len(lines[n].lstrip("#")) <= len(level) - 1),
                len(lines))
    return lines[start:stop]


def slug(heading):
    return re.sub(r"[^\w\- ]", "", heading.casefold()).replace(" ", "-")


def readme_papers(language):
    """Parse the paper-table rows of the Papers section, collecting rows that do not parse and repeated IDs."""
    text = README[language].read_text(encoding="utf-8")
    lines = section(text, PAPERS_HEADING[language])
    papers, theme, malformed = {}, None, []
    for number, line in enumerate(lines):
        if line.startswith("### "):
            theme = line[4:]
            continue
        if not line.startswith("|") or line.startswith("| :---"):
            continue
        if number + 1 < len(lines) and lines[number + 1].startswith("| :---"):
            continue  # Table header.
        match = ROW.match(line)
        if not match:
            malformed.append(line[:120])
            continue
        row = match.groupdict()
        row["theme"] = theme
        row["artifact_urls"] = re.findall(r"\]\((https?://[^)\s]+)\)", row["artifacts"])
        if row["id"] in papers:
            malformed.append(f"duplicate {row['id']}")
        papers[row["id"]] = row
    return papers, malformed, "\n".join(lines)


def bibliography():
    """Return all entry keys, {arXiv ID: fields} for the direct-study entries, and repeated eprints."""
    text = (ROOT / "references.bib").read_text(encoding="utf-8")
    keys, papers, repeated = [], {}, []
    for head in re.finditer(r"^@(\w+)\{([^,\s]+),", text, re.M):
        if head[1].casefold() in {"comment", "preamble", "string"}:
            continue
        keys.append(head[2])
        depth, start = 0, text.index("{", head.start())
        for end in range(start, len(text)):
            depth += {"{": 1, "}": -1}.get(text[end], 0)
            if depth == 0:
                break
        fields = {name: value[1:-1] if value.startswith("{") else value
                  for name, value in bib_fields(text[head.end():end]) or []}
        if fields.get("note", "").startswith("Version"):
            fields["key"] = head[2]
            paper = fields.get("eprint", head[2])
            if paper in papers:
                repeated.append(paper)
            papers[paper] = fields
    return keys, papers, repeated


def catalog_papers():
    script = (
        'import {resources} from "./site/catalog.mjs";'
        'console.log(JSON.stringify(resources.filter(row => row.category === "Papers")));'
    )
    result = subprocess.run(["node", "--input-type=module", "-e", script],
                            cwd=ROOT, text=True, capture_output=True, check=True)
    papers, repeated = {}, []
    for row in json.loads(result.stdout):
        match = re.fullmatch(r"https://arxiv\.org/abs/(\d{4}\.\d{4,5})v(\d+)", row["url"])
        row["id"], row["version"] = (match[1], match[2]) if match else (row["url"], None)
        if row["id"] in papers:
            repeated.append(row["id"])
        papers[row["id"]] = row
    return papers, repeated


def plain_title(title):
    """BibTeX or Markdown title text without case-protecting braces and with uniform quotes."""
    title = title.replace("``", '"').replace("''", '"').replace("{", "").replace("}", "")
    title = re.sub(r"[“”]", '"', title)
    title = re.sub(r"[‘’]", "'", title)
    return re.sub(r"\s+", " ", title).strip()


@unittest.skipUnless(shutil.which("node"), "Node is required to load the site catalog")
class BibliographyConsistencyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.readme, cls.malformed, cls.papers_text = {}, {}, {}
        for language in README:
            cls.readme[language], cls.malformed[language], cls.papers_text[language] = readme_papers(language)
        cls.bib_keys, cls.bib, cls.bib_repeated = bibliography()
        cls.catalog, cls.catalog_repeated = catalog_papers()

    def test_every_paper_table_row_parses(self):
        for language, rows in self.malformed.items():
            self.assertEqual(rows, [], f"{README[language].name}: unparsed paper rows")

    def test_readmes_bibliography_and_catalog_list_the_same_papers(self):
        expected = set(self.catalog)
        self.assertTrue(expected)
        for language, papers in self.readme.items():
            self.assertEqual(set(papers), expected, f"{README[language].name} papers differ from site/catalog.mjs")
        self.assertEqual(set(self.bib), expected, "references.bib direct-study eprints differ from site/catalog.mjs")
        self.assertEqual(self.bib_repeated, [], "references.bib lists a paper twice")
        self.assertEqual(self.catalog_repeated, [], "site/catalog.mjs lists a paper twice")

    def test_stated_counts_match_the_lists(self):
        for language, path in README.items():
            text = path.read_text(encoding="utf-8")
            stated = re.search(STATED_PAPERS[language], self.papers_text[language])
            self.assertIsNotNone(stated, f"{path.name}: paper count sentence not found")
            self.assertEqual(int(stated[1]), len(self.readme[language]), f"{path.name}: stated paper count")
            stated = re.search(STATED_BIB[language], text)
            self.assertIsNotNone(stated, f"{path.name}: bibliography count sentence not found")
            self.assertEqual(int(stated[1]), len(self.bib_keys), f"{path.name}: stated references.bib entry count")

    def test_english_and_chinese_rows_agree(self):
        english, chinese = self.readme["en"], self.readme["zh"]
        for paper in english.keys() & chinese.keys():
            for field in ("date", "version", "first", "url_version", "title", "authors", "artifact_urls"):
                self.assertEqual(english[paper][field], chinese[paper][field], f"{paper}: README {field} differs between languages")

    def test_versions_and_dates_agree(self):
        for paper, entry in self.catalog.items():
            with self.subTest(paper=paper):
                credit, date, version = entry["by"].rsplit(" · ", 2)
                self.assertEqual((date, version), (entry["date"], "v" + entry["version"]), "catalog by-line date and version")
                for language, papers in self.readme.items():
                    row = papers.get(paper)
                    if row:
                        self.assertEqual((row["date"], row["version"], row["url_version"]),
                                         (entry["date"], entry["version"], entry["version"]), f"{README[language].name} date and version")
                bib = self.bib.get(paper)
                if bib:
                    note = BIB_NOTE.match(bib.get("note", ""))
                    self.assertIsNotNone(note, f"references.bib {bib['key']}: note format")
                    self.assertEqual((note[1], note[2]), (entry["version"], entry["date"]), f"references.bib {bib['key']}: note")
                    self.assertEqual(bib.get("date"), entry["date"], f"references.bib {bib['key']}: date")
                    self.assertEqual(bib.get("year"), entry["date"][:4], f"references.bib {bib['key']}: year")
                    self.assertEqual(bib.get("url"), entry["url"], f"references.bib {bib['key']}: url")
                    self.assertEqual(bib.get("doi"), f"10.48550/arXiv.{paper}", f"references.bib {bib['key']}: doi")

    def test_first_submission_dates_agree(self):
        for paper, entry in self.catalog.items():
            with self.subTest(paper=paper):
                revised = entry["version"] != "1"
                for language, papers in self.readme.items():
                    row = papers.get(paper)
                    if not row:
                        continue
                    self.assertEqual(row["first"], entry["first_submitted"] if revised else None,
                                     f"{README[language].name}: a revised paper shows its first submission date, a v1 paper none")
                bib = self.bib.get(paper)
                note = BIB_NOTE.match(bib.get("note", "")) if bib else None
                if note:
                    self.assertEqual(note[3], entry["first_submitted"] if revised else None,
                                     f"references.bib {bib['key']}: only revised notes give the first-posted date")

    def test_titles_agree(self):
        for paper, entry in self.catalog.items():
            with self.subTest(paper=paper):
                for language, papers in self.readme.items():
                    if paper in papers:
                        self.assertEqual(plain_title(papers[paper]["title"]), plain_title(entry["title"]), f"{README[language].name} title")
                if paper in self.bib:
                    self.assertEqual(plain_title(self.bib[paper]["title"]), plain_title(entry["title"]), "references.bib title")

    def test_author_credits_agree(self):
        for paper, entry in self.catalog.items():
            with self.subTest(paper=paper):
                credit = entry["by"].rsplit(" · ", 2)[0]
                row = self.readme["en"].get(paper)
                if row:
                    self.assertEqual(row["authors"], credit, "README and catalog author credits")

    def test_whats_new_lists_the_ten_newest_table_rows(self):
        for language, path in README.items():
            with self.subTest(readme=path.name):
                text = path.read_text(encoding="utf-8")
                items = [line for line in section(text, WHATS_NEW_HEADING[language]) if line.startswith("- ")]
                papers = self.readme[language]
                parsed = []
                for line in items:
                    match = NEW_ITEM.match(line)
                    self.assertIsNotNone(match, f"unparsed What's new item: {line[:120]}")
                    item = match.groupdict()
                    row = papers.get(item["id"])
                    self.assertIsNotNone(row, f"What's new lists {item['id']}, which is not in the paper tables")
                    self.assertEqual((item["date"], item["version"], item["url_version"], item["title"], item["section"]),
                                     (row["date"], row["version"], row["url_version"], row["title"], row["theme"]),
                                     f"What's new item for {item['id']} disagrees with its table row")
                    self.assertEqual(item["anchor"], slug(row["theme"]), f"What's new anchor for {item['id']}")
                    parsed.append(item)
                self.assertEqual(len(parsed), min(10, len(papers)), "What's new lists ten studies")
                dates = [item["date"] for item in parsed]
                self.assertEqual(dates, sorted(dates, reverse=True), "What's new is ordered newest first")
                listed = {item["id"] for item in parsed}
                older = [row["date"] for paper, row in papers.items() if paper not in listed]
                if parsed and older:
                    self.assertLessEqual(max(older), dates[-1], "a newer study is missing from What's new")


if __name__ == "__main__":
    unittest.main()
