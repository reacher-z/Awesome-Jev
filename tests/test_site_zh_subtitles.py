"""Chinese resource subtitles translate descriptive qualifiers; names stay as written."""

from html.parser import HTMLParser
import re
import unittest

from test_site_discovery import ROOT

# Subtitle parts that are names, kept as written: publisher handles and publisher
# labels (the model directory shows the same `publisher`). Translate a new
# descriptor in localizedMetadata() (site/resource-view.mjs); add only names here.
NAMES = {
    "ai-ecoverse", "convaiinnovations", "emretheus", "hotchpotch", "iapp-technology", "mukaddamzaid",
    "ncchinh", "sgaseretto", "shlv", "ufak AI", "Ariño de la Rubia", "Jeva authors",
    "coldteadotai", "fabric-runtime", "atoma-run", "tasksource",
}
# License identifiers and formal license names retain their exact spelling.
LICENSE_IDENTIFIERS = {"AGPL-3.0-only", "LFM Open License v1.0"}
# "et al." in author lists, version tags, and the loanword "agent" used across the Chinese pages.
ALLOWED = re.compile(r"\bet al\.|\b(?:v\d[\w.]*|jev-\d[\w.]*)\b|\bagent\b")


class Subtitles(HTMLParser):
    """Collect the `by` text of each subtitle, without its category and provenance labels.

    A /papers/ table row has no subtitle; its date cell and author span carry the same metadata.
    """

    def __init__(self, source):
        super().__init__(convert_charrefs=True)
        self.subtitles = []
        self._depth = 0
        self._skip = 0
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        classes = dict(attrs).get("class", "").split()
        if "resource-subtitle" in classes:
            self._depth = 1
            self.subtitles.append([])
        elif {"paper-date", "paper-authors"} & set(classes):
            if "paper-date" in classes:
                self.subtitles.append([])
            else:
                self.subtitles[-1].append(" · ")
            self._depth = 1
        elif self._depth:
            self._depth += 1
            if self._skip or {"resource-category", "resource-provenance"} & set(classes):
                self._skip += 1

    def handle_endtag(self, tag):
        if self._depth:
            self._depth -= 1
            if self._skip:
                self._skip -= 1

    def handle_data(self, value):
        if self._depth and not self._skip:
            self.subtitles[-1].append(value)


def english_words(subtitle):
    parts = [part for part in subtitle.split(" · ") if part not in NAMES | LICENSE_IDENTIFIERS]
    return sorted(set(re.findall(r"\b[a-z]+\b", ALLOWED.sub("", " · ".join(parts)))))


class ChineseSubtitleTests(unittest.TestCase):
    def test_zh_subtitles_have_no_untranslated_english_descriptors(self):
        for route in ("zh/index.html", "zh/papers/index.html"):
            with self.subTest(route=route):
                parser = Subtitles((ROOT / "site" / route).read_text(encoding="utf-8"))
                self.assertGreater(len(parser.subtitles), 0)
                untranslated = []
                for parts in parser.subtitles:
                    text = re.sub(r"\s+", " ", "".join(parts)).strip(" ·")
                    if english_words(text):
                        untranslated.append(f"{text} ({', '.join(english_words(text))})")
                self.assertEqual(untranslated, [], "Translate these descriptors for the Chinese pages")

    def test_names_and_license_identifiers_stay_as_written(self):
        page = (ROOT / "site/zh/index.html").read_text(encoding="utf-8")
        for expected in ("ai-ecoverse · 浏览器移植版 · MIT", "SberAI · 独立运行时 · 代码 MIT",
                         "Jeva authors · 未声明许可", "Hugging Face · 社区", "ncchinh · 运行时 · Apache-2.0",
                         "coldteadotai · 规则检查 · MIT", "fabric-runtime · 进程编排 · MIT",
                         "atoma-run · agent 工作流 · AGPL-3.0-only",
                         "已知局限 · 2026 年 10 月 2 日审阅", "Chen et al. · 社区综述 v0.5"):
            self.assertTrue(expected in page, expected)

    def test_english_subtitles_are_unchanged(self):
        page = (ROOT / "site/index.html").read_text(encoding="utf-8")
        for expected in ("ai-ecoverse · browser port · MIT", "Jeva authors · license not declared",
                         "Limitations · reviewed October 2, 2026", "Hugging Face · community"):
            self.assertTrue(expected in page, expected)


if __name__ == "__main__":
    unittest.main()
