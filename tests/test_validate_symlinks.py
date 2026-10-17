"""Every symlink, including a directory or dangling link, must fail validation."""
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts import validate


MESSAGE = "symlinks are not supported in the published artifact"


class SymlinkTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name) / "repo"
        (self.root / "site").mkdir(parents=True)
        (self.root / "site/index.html").write_text("<!doctype html><title>Fixture</title>\n")
        # A directory outside the repository whose contents the Pages artifact would deploy.
        self.outside = Path(temporary.name) / "outside"
        self.outside.mkdir()
        (self.outside / "token.txt").write_text("token = ghp_" + "A" * 36 + "\n")

    def link(self, name, target):
        try:
            os.symlink(target, self.root / name)
        except (OSError, NotImplementedError):
            self.skipTest("symlinks are unavailable on this platform")

    def symlink_errors(self):
        with patch.object(validate, "ROOT", self.root), patch.object(validate, "errors", []):
            validate.check_symlinks()
            return list(validate.errors)

    def test_directory_symlink_is_reported(self):
        self.link("site/linked-dir", self.outside)
        self.assertEqual(self.symlink_errors(), [f"site/linked-dir: {MESSAGE}"])

    def test_dangling_symlink_is_reported(self):
        self.link("site/dangling", self.root / "site/missing.html")
        self.assertEqual(self.symlink_errors(), [f"site/dangling: {MESSAGE}"])

    def test_file_symlink_is_left_to_the_file_rule(self):
        self.link("site/linked-file.txt", self.outside / "token.txt")
        self.assertEqual(self.symlink_errors(), [])

    def test_skipped_local_directories_are_ignored(self):
        (self.root / "node_modules").mkdir()
        self.link("node_modules/linked-dir", self.outside)
        self.assertEqual(self.symlink_errors(), [])

    def test_main_reports_each_symlink_once(self):
        self.link("site/linked-dir", self.outside)
        self.link("site/linked-file.txt", self.outside / "token.txt")
        self.link("site/dangling", "missing.html")
        with patch.object(validate, "ROOT", self.root), patch.object(validate, "errors", []), \
                patch.object(validate, "check_index"), patch("builtins.print"):
            self.assertEqual(validate.main(), 1)
            symlink_errors = sorted(error for error in validate.errors if MESSAGE in error)
        self.assertEqual(symlink_errors, [f"site/dangling: {MESSAGE}", f"site/linked-dir: {MESSAGE}",
                                          f"site/linked-file.txt: {MESSAGE}"])

    def test_repository_has_no_symlinks(self):
        with patch.object(validate, "errors", []):
            validate.check_symlinks()
            self.assertEqual(validate.errors, [])


if __name__ == "__main__":
    unittest.main()
