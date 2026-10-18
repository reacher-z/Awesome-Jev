"""Interface strings exist in both languages; a missing one stops the build."""

import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest

from test_site_discovery import BUILD_INPUTS, ROOT


class InterfaceTranslationParityTests(unittest.TestCase):
    def test_catalog_languages_share_keys_and_cover_every_template_key(self):
        keys = json.loads(subprocess.check_output(
            [shutil.which("node"), "--input-type=module", "-e",
             "import {translations} from './site/catalog.mjs';"
             "process.stdout.write(JSON.stringify({en:Object.keys(translations.en),zh:Object.keys(translations.zh)}));"],
            cwd=ROOT, text=True, encoding="utf-8"))
        self.assertEqual(sorted(keys["en"]), sorted(keys["zh"]))
        template = (ROOT / "templates/index.html").read_text(encoding="utf-8")
        used = set(re.findall(r'\bdata-i18n(?:-aria|-placeholder)?="([^"]+)"', template))
        self.assertTrue(used)
        self.assertEqual(used - set(keys["zh"]), set())

    def test_missing_interface_translation_stops_the_build(self):
        node = shutil.which("node")
        self.assertIsNotNone(node)
        cases = {
            "collectionTitle": ("site/catalog.mjs", "\ndelete translations.zh.collectionTitle;\n"),
            "englishOnlyProbe": ("site/catalog.mjs", '\ntranslations.en.englishOnlyProbe = "Only in English";\n'),
            "templateOnlyProbe": ("templates/index.html", '\n<p data-i18n="templateOnlyProbe">Only in the template</p>\n'),
        }
        for key, (name, addition) in cases.items():
            with self.subTest(key=key), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                for source in BUILD_INPUTS:
                    destination = root / source
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(ROOT / source, destination)
                path = root / name
                path.write_text(path.read_text(encoding="utf-8") + addition, encoding="utf-8", newline="\n")
                result = subprocess.run([node, "scripts/build_site.mjs"], cwd=root, capture_output=True,
                                        text=True, encoding="utf-8", timeout=45)
                self.assertNotEqual(result.returncode, 0, "A missing translation must not publish English fallback text")
                self.assertIn("Missing interface translations", result.stderr)
                self.assertIn(key, result.stderr)
                self.assertFalse((root / "site/zh/index.html").exists())


if __name__ == "__main__":
    unittest.main()
