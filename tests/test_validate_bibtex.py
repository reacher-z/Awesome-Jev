"""The published references.bib must parse: balanced entries, unique keys, required fields."""
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts import validate


ROOT = Path(__file__).resolve().parents[1]
ENTRY = """@misc{lee2026jev,
  title = {{Jev}: Typed Decisions, with Commas = and "Quotes"},
  author = "Lee, Ada and Kim, Bo",
  year = {2026},
  url = {https://arxiv.org/abs/2610.00001v1?a=b,c}
}
"""


class BibtexTests(unittest.TestCase):
    def check(self, text, name="references.bib"):
        with tempfile.TemporaryDirectory() as tmp, patch.object(validate, "errors", []):
            root = Path(tmp)
            path = root / name
            path.write_text(text)
            with patch.object(validate, "ROOT", root):
                validate.check_bibtex(path)
            return list(validate.errors)

    def test_repository_bibliographies_pass(self):
        with patch.object(validate, "errors", []):
            for path in (ROOT / "references.bib", ROOT / "site/references.bib"):
                validate.check_bibtex(path)
            self.assertEqual(validate.errors, [])

    def test_well_formed_entry_with_nested_braces_quotes_and_url_punctuation_passes(self):
        self.assertEqual(self.check("% Comment with {braces} and @ sign.\n\n" + ENTRY + "% trailing note\n"), [])

    def test_unclosed_entry_reusing_an_existing_key_is_rejected(self):
        # The reproduction from the issue: an appended entry that is never closed.
        original = (ROOT / "references.bib").read_text()
        line = original.count("\n") + 2
        errors = self.check(original + "\n@article{guo2017calibration,\n  title = {Duplicate key, unclosed entry}\n")
        self.assertEqual(errors, [f"references.bib:{line}: duplicate BibTeX key guo2017calibration",
                                  f"references.bib:{line}: unbalanced braces in BibTeX entry guo2017calibration"])

    def test_unclosed_entry_before_another_entry_is_rejected(self):
        errors = self.check(ENTRY.replace("\n}\n", "\n\n") + ENTRY.replace("lee2026jev", "kim2026jev"))
        self.assertEqual(errors, ["references.bib:1: unbalanced braces in BibTeX entry lee2026jev"])

    def test_extra_closing_brace_is_rejected(self):
        errors = self.check(ENTRY.replace("year = {2026}", "year = {2026}}"))
        self.assertEqual(errors, ["references.bib:1: unbalanced braces in BibTeX entry lee2026jev"])

    def test_duplicate_keys_are_rejected_case_insensitively(self):
        errors = self.check(ENTRY + "\n" + ENTRY.replace("lee2026jev", "Lee2026Jev"))
        self.assertEqual(errors, ["references.bib:8: duplicate BibTeX key Lee2026Jev"])

    def test_missing_required_fields_are_rejected(self):
        for field, line in (("title", "  title = {{Jev}: Typed Decisions, with Commas = and \"Quotes\"},\n"),
                            ("author", "  author = \"Lee, Ada and Kim, Bo\",\n"),
                            ("year", "  year = {2026},\n")):
            with self.subTest(field=field):
                self.assertEqual(self.check(ENTRY.replace(line, "")),
                                 [f"references.bib:1: BibTeX entry lee2026jev is missing {field}"])
        self.assertEqual(self.check(ENTRY.replace("author = \"Lee, Ada and Kim, Bo\"", "author = {}")),
                         ["references.bib:1: BibTeX entry lee2026jev is missing author"])

    def test_year_must_have_four_digits(self):
        for year in ("{26}", "{2026a}", "{October 2026}"):
            with self.subTest(year=year):
                self.assertEqual(self.check(ENTRY.replace("{2026}", year)),
                                 ["references.bib:1: BibTeX entry lee2026jev needs a four-digit year"])
        self.assertEqual(self.check(ENTRY.replace("{2026}", "2026")), [])

    def test_malformed_header_and_field_are_rejected(self):
        self.assertEqual(self.check("% Comments only.\n"), ["references.bib: no BibTeX entries"])
        self.assertEqual(self.check(ENTRY.replace("@misc{lee2026jev,", "@misc{lee2026jev")),
                         ["references.bib:1: malformed BibTeX entry header"])
        self.assertEqual(self.check(ENTRY.replace("  year = {2026},", "  year {2026},")),
                         ["references.bib:1: malformed field in BibTeX entry lee2026jev"])

    def test_main_flow_rejects_a_broken_published_copy(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(validate, "errors", []):
            root = Path(tmp)
            (root / "references.bib").write_text(ENTRY)
            (root / "site").mkdir()
            (root / "site/references.bib").write_text(ENTRY + ENTRY)
            with patch.object(validate, "ROOT", root), patch.object(validate, "check_index"), \
                    patch("builtins.print"):
                self.assertEqual(validate.main(), 1)
            self.assertIn("site/references.bib:7: duplicate BibTeX key lee2026jev", validate.errors)
            self.assertFalse(any(error.startswith("references.bib") for error in validate.errors))


if __name__ == "__main__":
    unittest.main()
