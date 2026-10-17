"""Without JavaScript the homepage keeps a working route to every listing and shows no inert controls."""

from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
HOMEPAGES = {"en": ("site/index.html", "/papers/"), "zh": ("site/zh/index.html", "/zh/papers/")}


def section(html, element_id):
    start = html.index(f'id="{element_id}"')
    return html[start:html.index("</section>", start)]


class NoScriptTests(unittest.TestCase):
    def test_corpus_section_links_the_source_data_without_javascript(self):
        # The corpus disclosure, and the recovery links inside it, are hidden without JavaScript.
        for language, (page, _) in HOMEPAGES.items():
            corpus = section((ROOT / page).read_text(encoding="utf-8"), "corpus")
            fallback = re.findall(r"<noscript>([\s\S]*?)</noscript>", corpus)
            self.assertEqual(len(fallback), 1, f"{language}: corpus section needs one <noscript> block")
            self.assertIn('href="/data/source-index.json"', fallback[0], language)
            self.assertIn('href="https://github.com/reacher-z/Awesome-Jev/tree/main/data"', fallback[0], language)

    def test_noscript_note_links_the_papers_directory_in_the_page_language(self):
        for language, (page, papers) in HOMEPAGES.items():
            collection = section((ROOT / page).read_text(encoding="utf-8"), "collection")
            notes = re.findall(r"<noscript>([\s\S]*?)</noscript>", collection)
            self.assertEqual(len(notes), 1, language)
            self.assertIn(f'<a href="{papers}">', notes[0], language)

    def test_script_only_controls_are_hidden_without_javascript(self):
        css = (ROOT / "site/styles.css").read_text(encoding="utf-8")
        rule = re.search(r"((?:html:not\(\.js\) [^,{]+,\s*)*html:not\(\.js\) [^,{]+)\{\s*display:\s*none;", css)
        self.assertIsNotNone(rule, "Missing the html:not(.js) rule")
        hidden = {selector.strip().removeprefix("html:not(.js) ") for selector in rule.group(1).split(",")}
        # The copy button has no handler without app.js.
        self.assertLessEqual({".collection-controls", ".corpus-disclosure", "#copy-code"}, hidden)


if __name__ == "__main__":
    unittest.main()
