"""Every published .json file must parse, including files no script reads."""
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts import validate


class JsonFileTests(unittest.TestCase):
    def check(self, text):
        with tempfile.TemporaryDirectory() as tmp, patch.object(validate, "errors", []):
            root = Path(tmp)
            path = root / "data/editorial-audit.json"
            path.parent.mkdir()
            path.write_text(text)
            with patch.object(validate, "ROOT", root):
                validate.check_json(path, text)
            return list(validate.errors)

    def test_truncated_file_reports_its_position(self):
        self.assertEqual(self.check('{"broken": '), ["data/editorial-audit.json: invalid JSON at line 1, column 12"])

    def test_hand_edit_reports_line_and_column_without_echoing_content(self):
        errors = self.check('{\n  "a": 1,\n  "private": "do-not-echo",,\n}\n')
        self.assertEqual(errors, ["data/editorial-audit.json: invalid JSON at line 3, column 28"])

    def test_valid_json_passes(self):
        self.assertEqual(self.check('{"counts": [1, 2], "note": "\\u4e2d"}\n'), [])

    def test_nonstandard_constants_are_rejected(self):
        for constant in ("NaN", "Infinity", "-Infinity"):
            with self.subTest(constant=constant):
                self.assertEqual(
                    self.check(f'{{"value": {constant}}}'),
                    [f"data/editorial-audit.json: invalid JSON constant {constant}"],
                )

    def test_every_tracked_json_file_parses(self):
        with patch.object(validate, "errors", []):
            for path in validate.files():
                if path.suffix == ".json":
                    validate.check_json(path, path.read_text(encoding="utf-8"))
            self.assertEqual(validate.errors, [])

    def test_main_flow_rejects_a_broken_json_file(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(validate, "errors", []):
            root = Path(tmp)
            (root / "data").mkdir()
            (root / "data/editorial-audit.json").write_text('{"broken": ')
            with patch.object(validate, "ROOT", root), patch.object(validate, "check_index"), \
                    patch("builtins.print"):
                self.assertEqual(validate.main(), 1)
            self.assertIn("data/editorial-audit.json: invalid JSON at line 1, column 12", validate.errors)


if __name__ == "__main__":
    unittest.main()
