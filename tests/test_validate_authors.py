"""Research records carry an id, and primary arXiv imports store authors as "Given Surname"."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts import validate


ROOT = Path(__file__).resolve().parents[1]
PRIMARY = {"id": "arxiv:2609.28613", "canonical_url": "https://arxiv.org/abs/2609.28613",
           "abstract_provider": "arxiv_primary_abstract_page", "authors": ["Tiantong Wu", "Wei Yang Bryan Lim"]}
OPENALEX = {"id": "doi:10.1234/fixture", "canonical_url": "https://doi.org/10.1234/fixture",
            "abstract_provider": "openalex_api", "authors": ["Fixture Author"]}


class RecordIdAndAuthorTests(unittest.TestCase):
    def check(self, *rows, name="research-sources.jsonl"):
        with tempfile.TemporaryDirectory() as tmp, patch.object(validate, "errors", []):
            root = Path(tmp)
            path = root / "data" / name
            path.parent.mkdir()
            path.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows),
                            encoding="utf-8", newline="\n")
            with patch.object(validate, "ROOT", root):
                validate.check_record_ids_and_authors(path)
            return list(validate.errors)

    def test_current_ledgers_pass(self):
        with patch.object(validate, "errors", []):
            for path in sorted((ROOT / "data").glob("*.jsonl")):
                validate.check_record_ids_and_authors(path)
            self.assertEqual(validate.errors, [])

    def test_every_primary_import_uses_given_surname_and_an_arxiv_id(self):
        rows = [json.loads(line) for line in (ROOT / "data/research-sources.jsonl").read_text(encoding="utf-8").splitlines()]
        primary = [row for row in rows if row.get("abstract_provider") == "arxiv_primary_abstract_page"]
        self.assertGreater(len(primary), 30)
        for row in primary:
            with self.subTest(url=row["canonical_url"]):
                self.assertEqual(row.get("id"), "arxiv:" + row["canonical_url"].rsplit("/", 1)[1])
                self.assertFalse([name for name in row["authors"] if "," in name])

    def test_valid_rows_and_single_names_pass(self):
        self.assertEqual(self.check(PRIMARY, OPENALEX, {**PRIMARY, "id": "arxiv:2609.30243",
                                                         "canonical_url": "https://arxiv.org/abs/2609.30243",
                                                         "authors": ["Rusdah", "Ana Madrid-García"]}), [])

    def test_issue_reproduction_surname_given_primary_authors_are_rejected(self):
        self.assertEqual(self.check({**PRIMARY, "authors": ["Wu, Tiantong", "Lim, Wei Yang Bryan"]}),
                         ['data/research-sources.jsonl:1: primary arXiv authors must be "Given Surname", not "Surname, Given"'])

    def test_provider_supplied_names_outside_primary_imports_are_left_alone(self):
        self.assertEqual(self.check({**OPENALEX, "authors": ["Hofman, Paul"]}), [])

    def test_issue_reproduction_research_record_without_id_is_rejected(self):
        row = dict(PRIMARY)
        del row["id"]
        self.assertEqual(self.check(OPENALEX, row), [
            "data/research-sources.jsonl:2: research record requires an id such as arxiv:<id>, doi:<doi> or openalex:<id>"])

    def test_malformed_duplicate_or_mismatched_ids_are_rejected(self):
        errors = self.check(PRIMARY, {**OPENALEX, "id": "10.1234/fixture"}, {**OPENALEX, "id": PRIMARY["id"]},
                            {**PRIMARY, "id": "arxiv:2609.30243", "canonical_url": "https://arxiv.org/abs/2609.30244"})
        self.assertEqual(errors, [
            "data/research-sources.jsonl:2: research record requires an id such as arxiv:<id>, doi:<doi> or openalex:<id>",
            "data/research-sources.jsonl:3: duplicate research record id",
            "data/research-sources.jsonl:4: primary arXiv record id must be arxiv:<canonical arXiv id>",
        ])

    def test_empty_or_non_string_primary_authors_are_rejected(self):
        for authors in ([], ["Tiantong Wu", ""], [{"name": "Tiantong Wu"}], None):
            with self.subTest(authors=authors):
                self.assertEqual(self.check({**PRIMARY, "authors": authors}),
                                 ["data/research-sources.jsonl:1: primary arXiv record requires a nonempty author list"])

    def test_ecosystem_ledger_rows_need_no_id(self):
        row = {"url": "https://github.com/example/jev-tool", "authors": ["Example, Maintainer"]}
        self.assertEqual(self.check(row, name="ecosystem-sources.jsonl"), [])


if __name__ == "__main__":
    unittest.main()
