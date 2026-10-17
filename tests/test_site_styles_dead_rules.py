"""Every stylesheet selector names only classes and ids that a generated page or script can produce."""

from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"


def words(text):
    return set(re.findall(r"-?[_a-zA-Z][\w-]*", text))


def produced_tokens():
    """Class and id names in generated HTML and in browser scripts (interpolated parts included)."""
    corpus = "\n".join(path.read_text(encoding="utf-8") for path in sorted(SITE.rglob("*"))
                       if path.suffix in {".html", ".js", ".mjs"})
    classes, ids = set(), set()
    for match in re.finditer(r"""\bclass=\\?"([^"]*)"|\bclass=\\?'([^']*)'|\bclass=([\w-]+)""", corpus):
        classes |= words(next(group for group in match.groups() if group is not None))
    for match in re.finditer(r"classList\.(?:add|toggle|remove|replace)\(([^)]*)\)|className\s*\+?=\s*([^;\n]*)", corpus):
        classes |= words(next(group for group in match.groups() if group is not None))
    for match in re.finditer(r"""\bid=\\?"([^"]*)"|\bid=\\?'([^']*)'|\.id\s*=\s*([^;\n]*)""", corpus):
        ids |= words(next(group for group in match.groups() if group is not None))
    return classes, ids


def style_selectors(css):
    """(line, selector) for every style rule, skipping @font-face and @keyframes bodies."""
    css = re.sub(r"/\*[\s\S]*?\*/", lambda m: "\n" * m.group().count("\n"), css)
    selectors, start, depth_skip, index = [], 0, 0, 0
    while index < len(css):
        char = css[index]
        if char == "{":
            prelude = css[start:index].strip()
            if prelude.startswith("@") and not re.match(r"@(font-face|keyframes|-webkit-keyframes|page)\b", prelude):
                start = index + 1
            else:
                if not prelude.startswith("@") and not depth_skip:
                    line = css.count("\n", 0, start + len(css[start:index]) - len(css[start:index].lstrip())) + 1
                    selectors += [(line, part.strip()) for part in re.split(r",(?![^()]*\))", prelude)]
                # Skip the block, including nested blocks such as keyframe steps.
                depth = 1
                index += 1
                while depth:
                    depth += {"{": 1, "}": -1}.get(css[index], 0)
                    index += 1
                start = index
                continue
        elif char == "}":
            start = index + 1
        elif char == ";" and css[start:index].lstrip().startswith("@"):
            start = index + 1
        index += 1
    return selectors


def required_tokens(selector):
    """Classes and ids every match must carry: outside attribute brackets and functional pseudo-classes."""
    selector = re.sub(r"\[[^\]]*\]", "", selector)
    previous = None
    while previous != selector:
        previous, selector = selector, re.sub(r":(?:not|is|where|has|nth-[a-z-]+|lang|dir)\([^()]*\)", "", selector)
    return re.findall(r"\.(-?[_a-zA-Z][\w-]*)", selector), re.findall(r"#(-?[_a-zA-Z][\w-]*)", selector)


class DeadStyleRuleTests(unittest.TestCase):
    def test_no_selector_requires_a_class_or_id_that_nothing_produces(self):
        classes, ids = produced_tokens()
        selectors = style_selectors((SITE / "styles.css").read_text(encoding="utf-8"))
        self.assertGreater(len(selectors), 400)
        dead = []
        for line, selector in selectors:
            needed_classes, needed_ids = required_tokens(selector)
            missing = [f".{name}" for name in needed_classes if name not in classes] + [f"#{name}" for name in needed_ids if name not in ids]
            if missing:
                dead.append(f"site/styles.css:{line} {selector} (no page or script produces {', '.join(missing)})")
        self.assertEqual(dead, [], "Remove the dead rules or the markup they were written for:\n" + "\n".join(dead))


if __name__ == "__main__":
    unittest.main()
