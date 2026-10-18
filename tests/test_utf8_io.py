"""Repository text must be read and written as UTF-8 whatever the locale."""

import ast
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
# An ASCII locale without UTF-8 mode or locale coercion, as on a minimal
# container, a CI image without locales, or a Windows code page.
ASCII_ENV = {**os.environ, "LC_ALL": "C", "LANG": "C", "PYTHONUTF8": "0",
             "PYTHONCOERCECLOCALE": "0", "PYTHONIOENCODING": "ascii"}


def run(*args, cwd=ROOT):
    return subprocess.run([sys.executable, "-X", "utf8=0", *map(str, args)], cwd=cwd, env=ASCII_ENV,
                          capture_output=True, timeout=120)


class Utf8LocaleIndependenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        probe = run("-c", "import locale; print(locale.getpreferredencoding(False))")
        encoding = probe.stdout.decode("ascii", "replace").strip().lower().replace("-", "")
        if probe.returncode or encoding in {"utf8", ""}:
            raise unittest.SkipTest("this platform does not provide a non-UTF-8 locale")

    def test_repository_checks_pass_under_an_ascii_locale(self):
        # build_expansion_report.py --check is deliberately absent: it recomputes a
        # frozen report from the live source index, which every source scan changes.
        for script in (["scripts/build_source_index.py", "--check"],
                       ["scripts/validate.py"]):
            with self.subTest(script=script[0]):
                result = run(*script)
                self.assertEqual(result.returncode, 0, result.stderr.decode("utf-8", "replace")[-2000:])

    def test_index_round_trips_non_ascii_ledger_text_under_an_ascii_locale(self):
        title = "Évaluation des décisions typées — 类型化决策"
        row = {"url": "https://example.org/typed-decisions", "title": title, "relation": "direct",
               "verification_level": "content_screened", "retrieved_at": "2026-10-16T00:00:00+00:00",
               "relevance": "Synthetic non-ASCII fixture – en dash and CJK text."}
        with tempfile.TemporaryDirectory(prefix="awesome-jev-test-") as directory:
            root = Path(directory)
            (root / "scripts").mkdir()
            (root / "data").mkdir()
            for name in ("build_source_index.py", "source_policy.py"):
                shutil.copy(ROOT / "scripts" / name, root / "scripts" / name)
            (root / "data/ecosystem-sources.jsonl").write_bytes(
                (json.dumps(row, ensure_ascii=False) + "\n").encode("utf-8"))
            for args in ([], ["--check"]):
                result = run("scripts/build_source_index.py", *args, cwd=root)
                self.assertEqual(result.returncode, 0, result.stderr.decode("utf-8", "replace")[-2000:])
            index = (root / "site/data/source-index.json").read_bytes()
            self.assertIn(title.encode("utf-8"), index)
            self.assertNotIn(b"\r\n", index)
            self.assertEqual(json.loads(index.decode("utf-8"))["sources"][0]["title"], title)


class ExplicitTextEncodingTests(unittest.TestCase):
    """Scripts that need the network cannot run here, so check every call site."""

    def test_script_text_io_names_utf8_and_unix_newlines(self):
        missing = []
        for path in sorted((ROOT / "scripts").glob("*.py")):
            for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
                if not isinstance(node, ast.Call):
                    continue
                func = node.func
                name = func.attr if isinstance(func, ast.Attribute) else func.id if isinstance(func, ast.Name) else ""
                keywords = {keyword.arg: keyword.value for keyword in node.keywords}
                mode = keywords.get("mode", node.args[1] if len(node.args) > 1 else None)
                binary = isinstance(mode, ast.Constant) and "b" in str(mode.value)
                text_open = name == "open" and isinstance(func, ast.Name) and not binary
                if name in {"read_text", "write_text"} or text_open:
                    encoding = keywords.get("encoding")
                    if not (isinstance(encoding, ast.Constant) and encoding.value == "utf-8"):
                        missing.append(f"{path.name}:{node.lineno} {name}() without encoding='utf-8'")
                if name == "write_text":
                    newline = keywords.get("newline")
                    if not (isinstance(newline, ast.Constant) and newline.value == "\n"):
                        missing.append(f"{path.name}:{node.lineno} write_text() without newline='\\n'")
        self.assertEqual(missing, [])


if __name__ == "__main__":
    unittest.main()
