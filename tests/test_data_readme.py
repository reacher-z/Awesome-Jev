"""data/README.md must describe every data file, and each review record must be linked from its page."""

from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
README = DATA / "README.md"
ROW = re.compile(r"^\| `([^`/]+\.jsonl?)` \|", re.MULTILINE)


def data_files() -> set[str]:
    return {path.name for path in DATA.iterdir() if path.suffix in {".json", ".jsonl"}}


def section(text: str, heading: str) -> str:
    start = text.index(f"\n## {heading}\n")
    end = text.find("\n## ", start + 1)
    return text[start:end if end != -1 else None]


class DataReadmeTests(unittest.TestCase):
    def setUp(self):
        self.text = README.read_text(encoding="utf-8")

    def test_every_data_file_has_a_table_row(self):
        rows = ROW.findall(self.text)
        self.assertEqual(sorted(name for name in set(rows) if rows.count(name) > 1), [], "duplicate rows")
        self.assertEqual(sorted(data_files() - set(rows)), [], "data files missing from data/README.md")
        self.assertEqual(sorted(set(rows) - data_files()), [], "data/README.md rows for missing files")

    def test_has_a_chinese_section(self):
        chinese = section(self.text, "中文说明")
        self.assertRegex(chinese, r"[一-鿿]{20}")

    def test_review_records_are_linked_from_the_page_they_support(self):
        rows = re.findall(r"^\| `([^`]+)` \| [^|]+ \| (.+) \|$", section(self.text, "Review and audit records"), re.MULTILINE)
        self.assertGreater(len(rows), 0)
        for name, cell in rows:
            with self.subTest(record=name):
                targets = re.findall(r"\]\(([^)#]+)(?:#[^)]*)?\)", cell)
                self.assertTrue(targets, "no page linked")
                for target in targets:
                    page = (DATA / target).resolve()
                    self.assertTrue(page.is_file(), target)
                    link = re.search(r"\]\([^)]*" + re.escape(name) + r"\)", page.read_text(encoding="utf-8"))
                    self.assertIsNotNone(link, f"{target} does not link back to {name}")


if __name__ == "__main__":
    unittest.main()
