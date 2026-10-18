"""The papers-per-week chart agrees with the README paper tables and stays accessible.

scripts/build_site.mjs draws the chart from site/catalog.mjs into assets/papers-by-week*.svg,
inlines it on /papers/ and regenerates the README block between the papers-by-week markers;
`node scripts/build_site.mjs --check` catches stale output. These tests check what the
generated output says: every week x theme count, recomputed here from the README paper tables
alone, appears in the README tables, the /papers/ tables and the drawn SVG segments; the
README picks a dark-theme file; and every chart carries a title, a description and a table.
"""

from datetime import date, timedelta
from html.parser import HTMLParser
from pathlib import Path
import re
import shutil
import unittest
import xml.etree.ElementTree as ET

from test_bibliography_consistency import README, readme_papers


ROOT = Path(__file__).resolve().parents[1]
SVG = "{http://www.w3.org/2000/svg}"
BLOCK = re.compile(r"<!-- papers-by-week:[^\n]*-->\n(.*?)\n<!-- /papers-by-week -->", re.S)


class Markup(HTMLParser):
    """Collect <source>/<img> attributes and the cell text of every table row."""

    def __init__(self, source):
        super().__init__(convert_charrefs=True)
        self.tags, self.rows, self._row, self._cell = [], [], None, None
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        if tag in {"source", "img", "svg"}:
            self.tags.append((tag, dict(attrs)))
        elif tag == "tr":
            self._row = []
        elif tag in {"th", "td"} and self._row is not None:
            self._cell = []

    def handle_endtag(self, tag):
        if tag in {"th", "td"} and self._cell is not None:
            self._row.append("".join(self._cell).strip())
            self._cell = None
        elif tag == "tr" and self._row is not None:
            self.rows.append(self._row)
            self._row = None

    def handle_data(self, value):
        if self._cell is not None:
            self._cell.append(value)


CURATED = {"en": r"Last curated: \*\*(\d{4}-\d{2}-\d{2})\*\*", "zh": r"最近整理：\*\*(\d{4}-\d{2}-\d{2})\*\*"}
SEGMENT = re.compile(r"^(\d{4})-W(\d{2}) \([^)]*\) · (.+?)[:：] ?(\d+)$")


def expected_counts(language):
    """Week labels and per-section counts recomputed from one README's paper tables.

    A revised paper's row gives its first-submission date; a v1 row's date is its first
    submission. Weeks are ISO weeks from the earliest one through the README's curation date,
    empty weeks included; sections keep README order.
    """
    papers, _, text = readme_papers(language)
    sections = [line[4:] for line in text.split("\n") if line.startswith("### ")]
    curated = date.fromisoformat(re.search(CURATED[language], README[language].read_text(encoding="utf-8"))[1])
    firsts = {paper: date.fromisoformat(row["first"] or row["date"]) for paper, row in papers.items()}
    monday = lambda day: day - timedelta(days=day.weekday())
    weeks, week = [], monday(min(firsts.values()))
    while week <= curated:
        weeks.append(week.isocalendar()[:2])
        week += timedelta(days=7)
    counts = [[sum(1 for paper, row in papers.items() if row["theme"] == section and firsts[paper].isocalendar()[:2] == key)
               for key in weeks] for section in sections]
    return weeks, counts, len(papers)


def table_counts(rows):
    """(week numbers, per-theme counts, row labels) from a chart table, checking its totals."""
    header, body, total = rows[0], rows[1:-1], rows[-1]
    weeks = [int(cell.removeprefix("W")) for cell in header[1:-1]]
    counts = [[int(cell) for cell in row[1:-1]] for row in body]
    for row, cells in zip(body, counts):
        assert int(row[-1]) == sum(cells), row
    assert [int(cell) for cell in total[1:-1]] == [sum(column) for column in zip(*counts)], total
    return weeks, counts, [row[0] for row in body], int(total[-1])


@unittest.skipUnless(shutil.which("node"), "Node is required to load the site catalog")
class PaperActivityChartTests(unittest.TestCase):
    def assert_table_matches_readme(self, rows, language):
        weeks, counts, total = expected_counts(language)
        shown_weeks, shown_counts, labels, shown_total = table_counts(rows)
        self.assertEqual(shown_weeks, [week for _, week in weeks], "week columns")
        self.assertEqual(shown_counts, counts, "week x theme counts, rows in README section order")
        self.assertEqual(shown_total, total)
        return weeks, counts, labels

    def test_readme_tables_give_every_week_and_theme_count(self):
        for language, path in README.items():
            with self.subTest(readme=path.name):
                block = BLOCK.search(path.read_text(encoding="utf-8"))
                self.assertIsNotNone(block, "papers-by-week block not found")
                self.assert_table_matches_readme(Markup(block[1]).rows, language)

    def test_drawn_segments_match_the_counts(self):
        for language, suffix in (("en", ""), ("zh", ".zh-CN")):
            rows = Markup(BLOCK.search(README[language].read_text(encoding="utf-8"))[1]).rows
            weeks, counts, labels = self.assert_table_matches_readme(rows, language)
            expected = {(year, week, labels[index]): count for index, row in enumerate(counts)
                        for (year, week), count in zip(weeks, row) if count}
            for mode in ("", "-dark"):
                with self.subTest(file=f"papers-by-week{mode}{suffix}.svg"):
                    root = ET.fromstring((ROOT / f"assets/papers-by-week{mode}{suffix}.svg").read_text(encoding="utf-8"))
                    drawn = {}
                    for mark in root.iter():
                        if mark.tag in {f"{SVG}rect", f"{SVG}path"} and mark.findtext(f"{SVG}title"):
                            match = SEGMENT.match(mark.findtext(f"{SVG}title"))
                            self.assertIsNotNone(match, mark.findtext(f"{SVG}title"))
                            drawn[(int(match[1]), int(match[2]), match[3])] = int(match[4])
                    self.assertEqual(drawn, expected, "one drawn segment per non-zero week x theme count")

    def test_readmes_offer_a_dark_theme_file_and_alt_text(self):
        for language, path in README.items():
            with self.subTest(readme=path.name):
                tags = dict(Markup(BLOCK.search(path.read_text(encoding="utf-8"))[1]).tags)
                self.assertEqual(tags["source"].get("media"), "(prefers-color-scheme: dark)")
                self.assertIn("-dark", tags["source"]["srcset"])
                self.assertGreater(len(tags["img"].get("alt", "")), 40)
                for name in (tags["source"]["srcset"], tags["img"]["src"]):
                    self.assertTrue((ROOT / name).is_file(), name)

    def test_chart_files_are_labelled_and_differ_only_in_colour(self):
        for suffix in ("", ".zh-CN"):
            with self.subTest(suffix=suffix):
                light = (ROOT / f"assets/papers-by-week{suffix}.svg").read_text(encoding="utf-8")
                dark = (ROOT / f"assets/papers-by-week-dark{suffix}.svg").read_text(encoding="utf-8")
                for source in (light, dark):
                    root = ET.fromstring(source)
                    self.assertEqual(root.get("role"), "img")
                    self.assertTrue(root.findtext(f"{SVG}title"))
                    self.assertTrue(root.findtext(f"{SVG}desc"))
                colourless = lambda text: re.sub(r"#[0-9a-f]{6}", "#", text)
                self.assertEqual(colourless(light), colourless(dark))

    def test_papers_pages_inline_the_chart_with_its_numbers(self):
        for language, route in (("en", "site/papers/index.html"), ("zh", "site/zh/papers/index.html")):
            with self.subTest(route=route):
                markup = Markup((ROOT / route).read_text(encoding="utf-8"))
                charts = [attrs for tag, attrs in markup.tags if tag == "svg" and "activity-chart" in attrs.get("class", "")]
                self.assertEqual(len(charts), 1)
                self.assertEqual(charts[0].get("role"), "img")
                tables = re.findall(r'<figure class="paper-activity">.*?(<table>.*?</table>)', (ROOT / route).read_text(encoding="utf-8"), re.S)
                self.assertEqual(len(tables), 1)
                self.assert_table_matches_readme(Markup(tables[0]).rows, language)


if __name__ == "__main__":
    unittest.main()
