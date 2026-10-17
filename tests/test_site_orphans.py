"""Retired generated routes are reported by --check and removed by a build."""

import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

from test_site_discovery import BUILD_INPUTS, ROOT


class OrphanedGeneratedPageTests(unittest.TestCase):
    def test_removed_topic_pages_fail_check_and_are_deleted_without_touching_other_files(self):
        node = shutil.which("node")
        self.assertIsNotNone(node)
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for name in BUILD_INPUTS:
                destination = root / name
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / name, destination)

            def build(*args):
                return subprocess.run([node, "scripts/build_site.mjs", *args], cwd=root,
                                      capture_output=True, text=True, timeout=45)

            self.assertEqual(build().returncode, 0)
            # Hand-maintained files that share site/ with generated routes.
            kept = {
                "site/google0123456789abcdef.html": "google-site-verification: google0123456789abcdef.html\n",
                "site/indexnow-key.txt": "0123456789abcdef\n",
                "site/assets/vendor/index.html": "<!doctype html><title>Vendor asset</title>\n",
            }
            for name, content in kept.items():
                (root / name).parent.mkdir(parents=True, exist_ok=True)
                (root / name).write_text(content)

            topics_path = root / "data/research-topics.json"
            topics = json.loads(topics_path.read_text())
            retired = topics["topics"].pop()["slug"]
            topics_path.write_text(json.dumps(topics))
            orphans = [f"site/topics/{retired}/index.html", f"site/zh/topics/{retired}/index.html"]

            check = build("--check")
            self.assertNotEqual(check.returncode, 0, "--check must fail while a retired route is still on disk")
            for name in orphans:
                self.assertIn(f"Orphaned generated page: {name}", check.stderr)
                self.assertTrue((root / name).exists(), "--check must not modify site/")

            result = build()
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            for name in orphans:
                self.assertFalse((root / name).exists())
                self.assertFalse((root / name).parent.exists(), "The retired route directory should be removed")
            self.assertTrue((root / "site/topics/index.html").exists())
            for name, content in kept.items():
                self.assertEqual((root / name).read_text(), content)
            self.assertNotIn(retired, (root / "site/sitemap.xml").read_text())

            check = build("--check")
            self.assertEqual(check.returncode, 0, check.stdout + check.stderr)


if __name__ == "__main__":
    unittest.main()
