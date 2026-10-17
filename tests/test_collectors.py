"""Screening rules and URL identities the scheduled scan takes from the collectors, offline."""
import hashlib
import json
import unittest
from unittest.mock import patch

from scripts import build_source_index as index
from scripts import collect_ecosystem as ecosystem
from scripts import collect_research as research
from scripts import refresh_sources as refresh

# Neutral 29-word padding: it matches no topic rule, so each case's own sentence decides.
FILLER = ("The study reports experiments on several public datasets, compares strong baselines under matched budgets, "
          "and releases code and configuration files so that other groups can repeat every reported measurement.")


class EcosystemCanonicalTests(unittest.TestCase):
    def test_document_identities(self):
        cases = {
            # arXiv: any mirror, view or version is one abstract page.
            "https://arxiv.org/abs/2609.10000v3": "https://arxiv.org/abs/2609.10000",
            "http://export.arxiv.org/pdf/2609.10000v1": "https://arxiv.org/abs/2609.10000",
            "https://www.arxiv.org/html/2609.10000v2/": "https://arxiv.org/abs/2609.10000",
            "https://huggingface.co/papers/2609.10000": "https://arxiv.org/abs/2609.10000",
            "https://hf.co/papers/2609.10000": "https://arxiv.org/abs/2609.10000",
            # GitHub: one lowercase owner/repository, whatever file, clone or raw URL points into it.
            "https://github.com/fixture/router.git": "https://github.com/fixture/router",
            "https://www.github.com/Fixture/Router/tree/main/docs#usage": "https://github.com/fixture/router",
            "https://raw.githubusercontent.com/fixture/router/main/README.md": "https://github.com/fixture/router",
            "https://github.com/fixture//router/": "https://github.com/fixture/router",
            "https://github.com/fixture/router).": "https://github.com/fixture/router",
            "https://example.org/paper);": "https://example.org/paper",
            # Hugging Face: models keep owner/name; datasets and spaces keep their type prefix.
            "https://huggingface.co/fixture/jev-model/resolve/main/model.safetensors": "https://huggingface.co/fixture/jev-model",
            "https://huggingface.co/datasets/fixture/decisions/viewer/default/train": "https://huggingface.co/datasets/fixture/decisions",
            # ACL Anthology: the PDF and the landing page are one paper.
            "https://aclanthology.org/2024.acl-long.1.pdf": "https://aclanthology.org/2024.acl-long.1",
            "https://aclanthology.org/2024.acl-long.1/": "https://aclanthology.org/2024.acl-long.1",
            # Other hosts: https, lowercase host, no tracking query, fragment or trailing slash.
            "http://Example.org/Paper/?utm_source=feed#section": "https://example.org/Paper",
            "https://example.org": "https://example.org/",
        }
        for url, expected in cases.items():
            with self.subTest(url=url):
                self.assertEqual(ecosystem.canonical(url), expected)

    def test_non_document_urls_have_no_identity(self):
        for url in (
            "https://arxiv.org/list/cs.LG/recent",
            "https://github.com/fixture",
            "https://github.com/topics/jev",
            "https://github.com/orgs/fixture/repositories",
            "https://github.com/sponsors/fixture",
            "https://github.com/huggingface/transformers",
            "https://github.com/PyTorch/PyTorch/issues/1",
            "https://huggingface.co/fixture",
            "https://huggingface.co/datasets/fixture",
            "https://huggingface.co/papers/trending",
            "https://huggingface.co/docs/transformers/index",
            "https://huggingface.co/blog/jev",
            "https://huggingface.co/collections/fixture/decisions",
            "https://huggingface.co/spaces/Chunte/HFBA",
            "https://example.org/figure.PNG",
            "https://example.org/release.tar.gz",
            "https://x.com/fixture/status/1",
            "https://www.youtube.com/watch?v=fixture",
            "ftp://example.org/paper",
            "mailto:team@example.org",
            "https://user@example.org/private",
            "https://[invalid",
        ):
            with self.subTest(url=url):
                self.assertIsNone(ecosystem.canonical(url))

    def test_links_stop_at_markup_and_escape_delimiters(self):
        text = ('See https://github.com/a/b) and "https://example.org/x" <https://arxiv.org/abs/2609.1> '
                '`https://hf.co/c/d` [x](https://e.org/y] https://f.org/z\\n')
        self.assertEqual(ecosystem.links(text), ["https://github.com/a/b", "https://example.org/x", "https://arxiv.org/abs/2609.1",
                                                 "https://hf.co/c/d", "https://e.org/y", "https://f.org/z"])


class EcosystemIdentifyingQueryTests(unittest.TestCase):
    """docs/maintenance.md: OpenReview's `id` and CiteSeer's `doi` survive normalization."""

    def test_distinct_query_identified_documents_stay_distinct(self):
        cases = {
            "https://openreview.net/forum?id=HJz1vo0cYX": "https://openreview.net/forum?id=HJz1vo0cYX",
            "https://openreview.net/forum?id=BJeB5hVtvB": "https://openreview.net/forum?id=BJeB5hVtvB",
            "https://openreview.net/pdf?id=HJz1vo0cYX#page=2": "https://openreview.net/pdf?id=HJz1vo0cYX",
            "http://citeseerx.ist.psu.edu/viewdoc/summary?doi=10.1.1.1.1": "https://citeseerx.ist.psu.edu/viewdoc/summary?doi=10.1.1.1.1",
            "https://citeseerx.ist.psu.edu/viewdoc/download?type=pdf&doi=10.1.1.2.2&rep=rep1":
                "https://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.2.2&rep=rep1&type=pdf",
        }
        for url, expected in cases.items():
            with self.subTest(url=url):
                self.assertEqual(ecosystem.canonical(url), expected)

    def test_only_tracking_parameters_are_dropped(self):
        url = "https://openreview.net/forum?utm_source=feed&id=HJz1vo0cYX&fbclid=x&gclid=y&msclkid=z&UTM_medium=m"
        self.assertEqual(ecosystem.canonical(url), "https://openreview.net/forum?id=HJz1vo0cYX")

    def test_query_identity_matches_the_source_index(self):
        for url in ("https://openreview.net/forum?id=HJz1vo0cYX&utm_campaign=x",
                    "https://citeseerx.ist.psu.edu/viewdoc/download?type=pdf&doi=10.1.1.2.2"):
            with self.subTest(url=url):
                self.assertEqual(ecosystem.canonical(url), index.canonical(url))


class EligibilityTests(unittest.TestCase):
    def test_depth_and_topic_rules(self):
        cases = (
            ({"topic": "implementation-repository"}, True),
            ({"topic": "implementation-repository", "discovery_depth": 0, "matched_topics": []}, True),
            ({"topic": "training-dataset", "discovery_depth": 1}, True),
            ({"topic": "research-paper", "discovery_depth": 2}, True),
            ({"topic": "implementation-repository", "discovery_depth": 1, "matched_topics": ["Jev"]}, True),
            ({"topic": "implementation-repository", "discovery_depth": 1, "matched_topics": ["TypeSafe AI"]}, True),
            ({"topic": "decision-model-card", "discovery_depth": 1, "matched_topics": ["vision", "typed decisions"]}, True),
            ({"topic": "implementation-repository", "discovery_depth": 1, "matched_topics": ["calibration", "training"]}, False),
            ({"topic": "decision-model-card", "discovery_depth": 1, "matched_topics": ["vision"]}, False),
            ({"topic": "implementation-repository", "discovery_depth": 1}, False),
        )
        for record, expected in cases:
            with self.subTest(record=record):
                self.assertIs(ecosystem.eligible(record), expected)


class ReadableTests(unittest.TestCase):
    def test_html_drops_scripts_navigation_and_footers(self):
        page = (b"<html><head><title>Fixture &amp; page</title><style>p{}</style></head><body><nav>Menu</nav>"
                b"<p>Body  text &lt;ok&gt;</p><script>alert(1)</script><footer>Foot</footer><noscript>JS</noscript></body></html>")
        self.assertEqual(ecosystem.readable(page, "html"), ("Fixture & page Body text <ok>", "Fixture & page"))

    def test_markdown_keeps_link_text_and_drops_images(self):
        text = b"Intro\n# Jev Router\n![logo](logo.png) See [the docs](https://example.org/docs) now.\n"
        self.assertEqual(ecosystem.readable(text, "markdown"), ("Intro # Jev Router See the docs now.", "Jev Router"))


TOPICAL = "Jev router sends typed decisions to calibrated decision models and reads probability outputs. " * 4
OFF_TOPIC = "The project stores recipes for bread, soup and salad, with photos and shopping lists for each week of the year. " * 3
DEPENDENCIES = ("https://huggingface.co/datasets/fixture/decisions https://github.com/Fixture/Decision-Core "
                "https://arxiv.org/pdf/2609.10000v2 https://aclanthology.org/2024.acl-long.1.pdf "
                "https://huggingface.co/fixture/jev-decider https://huggingface.co/fixture/bert-base "
                "https://example.org/blog https://github.com/fixture/router https://x.com/fixture\n")
RELEVANCE = ("Direct scholarly, training-data, or implementation dependency linked by an index-listed artifact; "
             "not a claim about TypeSafe internals.")


def seed(url="https://github.com/fixture/router", topic="implementation-repository", relation="direct"):
    return {"url": url, "title": url.rsplit("/", 1)[-1], "topic": topic, "relation": relation, "relevance": "Fixture.",
            "discovered_from": ["https://example.org/index"], "discovery_depth": 0}


class AuditScreeningTests(unittest.TestCase):
    def audit(self, source, body, content_type="text/plain", fail_first=0):
        calls = []

        def fetch(url):
            calls.append(url)
            if len(calls) <= fail_first:
                raise ValueError("http_404")
            return body.encode(), url, content_type
        with patch.object(ecosystem, "fetch", side_effect=fetch):
            record, children = ecosystem.audit(source)
        return record, children, calls

    def test_topical_readme_is_screened_and_yields_only_scholarly_and_implementation_children(self):
        readme = "# Jev Router\n\n## Usage\n\n" + TOPICAL + "\n\nLinks: " + DEPENDENCIES
        record, children, calls = self.audit(seed(), readme, fail_first=1)
        self.assertEqual(calls, ["https://raw.githubusercontent.com/fixture/router/main/README.md",
                                 "https://raw.githubusercontent.com/fixture/router/main/readme.md"])
        self.assertEqual({key: record[key] for key in ("title", "verification_level", "status", "retrieved_url", "content_sha256",
                                                       "matched_topics", "section_headings", "evidence")}, {
            "title": "Jev Router", "verification_level": "content_screened", "status": "screened", "retrieved_url": calls[1],
            "content_sha256": hashlib.sha256(readme.encode()).hexdigest(),
            "matched_topics": ["Jev", "typed decisions", "calibration", "probability readout", "routing"],
            "section_headings": ["Jev Router", "Usage"],
            "evidence": "Retrieved and screened substantive repository README; discusses Jev, typed decisions, calibration, probability readout, routing.",
        })
        expected = (("https://huggingface.co/datasets/fixture/decisions", "training-dataset"),
                    ("https://github.com/fixture/decision-core", "implementation-repository"),
                    ("https://arxiv.org/abs/2609.10000", "research-paper"),
                    ("https://aclanthology.org/2024.acl-long.1", "research-paper"),
                    ("https://huggingface.co/fixture/jev-decider", "decision-model-card"))
        self.assertEqual(children, [{"url": url, "title": url.rsplit("/", 1)[-1], "topic": topic, "relation": "adjacent",
                                     "relevance": RELEVANCE, "discovered_from": ["https://github.com/fixture/router"],
                                     "discovery_depth": 1} for url, topic in expected])

    def test_short_blocked_or_off_topic_content_stays_metadata_only(self):
        for name, body in (("short", "# Jev\n\nJev typed decisions. " + DEPENDENCIES),
                           ("access denied", "Access denied for this region. " + TOPICAL + DEPENDENCIES),
                           ("empty repository", "This repository is empty. " + TOPICAL),
                           ("off topic", OFF_TOPIC + "https://github.com/fixture/recipes\n")):
            with self.subTest(case=name):
                record, children, _ = self.audit(seed(), body)
                self.assertEqual((record["verification_level"], record["status"]), ("metadata_only", "insufficient_content"))
                self.assertEqual(record["evidence"], "Retrieved page lacks sufficient readable topical content for content-screened status.")
                self.assertEqual(children, [])

    def test_direct_benchmark_provenance_can_stand_in_for_topic_terms(self):
        page = "<html><head><title>Fixture resource</title></head><body><p>" + OFF_TOPIC + "</p></body></html>"
        record, children, calls = self.audit(seed("https://example.org/benchmark", topic="benchmark-source"), page, "text/html; charset=utf-8")
        self.assertEqual(calls, ["https://example.org/benchmark"])
        self.assertEqual((record["verification_level"], record["title"], record["matched_topics"], record["section_headings"]),
                         ("content_screened", "Fixture resource", [], []))
        self.assertEqual(record["evidence"], "Retrieved and screened substantive content for a directly cited evaluation or training resource.")
        self.assertEqual(children, [])

    def test_adjacent_sources_are_screened_but_not_expanded(self):
        record, children, _ = self.audit(seed(relation="adjacent"), "# Jev Router\n\n" + TOPICAL + DEPENDENCIES)
        self.assertEqual(record["verification_level"], "content_screened")
        self.assertEqual(children, [])

    def test_hub_card_readme_and_unavailable_sources(self):
        record, _, calls = self.audit(seed("https://huggingface.co/fixture/jev-model", topic="decision-model-card"),
                                      "# Card\n\n" + TOPICAL, fail_first=1)
        self.assertEqual(calls, ["https://huggingface.co/fixture/jev-model/raw/main/README.md"])
        self.assertEqual((record["verification_level"], record["status"], record["fetch_errors"]),
                         ("metadata_only", "unavailable", ["ValueError: http_404"]))
        self.assertNotIn("content_sha256", record)


def openalex_work(number, **fields):
    return {"id": f"https://openalex.org/W{number}", "doi": None, "title": f"OpenAlex fixture {number}",
            "authorships": [], "publication_year": None, "primary_location": None, "locations": None,
            "abstract_inverted_index": None, **fields}


class OpenAlexConversionTests(unittest.TestCase):
    def test_abstract_is_rebuilt_in_position_order_and_arxiv_location_wins(self):
        work = openalex_work(1, doi="https://doi.org/10.1000/xyz", title="Proper scoring rules",
                             abstract_inverted_index={"rules": [2], "reward": [3], "Proper": [0], "scoring": [1, 4]},
                             authorships=[{"author": {"display_name": "A. Author"}}, {"author": {}}],
                             publication_year=2007, primary_location={"landing_page_url": "https://doi.org/10.1000/xyz"},
                             locations=[{"landing_page_url": None}, {"landing_page_url": "https://arxiv.org/abs/0704.0001v2"}])
        self.assertEqual(research.convert_openalex([work]), [{"paper": {
            "id": "0704.0001", "_record_id": "arxiv:0704.0001", "_canonical_url": "https://arxiv.org/abs/0704.0001",
            "title": "Proper scoring rules", "summary": "Proper scoring rules reward scoring",
            "authors": [{"name": "A. Author"}, {"name": ""}], "publishedAt": "2007"}}])

    def test_identity_falls_back_from_arxiv_to_doi_landing_page_and_work_id(self):
        works = [
            openalex_work(2, locations=[{"landing_page_url": "https://arxiv.org/pdf/cs/0101001v1"}]),
            openalex_work(3, doi="https://doi.org/10.1000/abc", primary_location={"landing_page_url": "https://publisher.example/abc"}),
            openalex_work(4, primary_location={"landing_page_url": "https://publisher.example/landing"}),
            openalex_work(5, title=None),
        ]
        converted = [item["paper"] for item in research.convert_openalex(works)]
        self.assertEqual([(p["id"], p["_record_id"], p["_canonical_url"]) for p in converted], [
            ("cs/0101001", "arxiv:cs/0101001", "https://arxiv.org/abs/cs/0101001"),
            ("doi:10.1000/abc", "doi:10.1000/abc", "https://doi.org/10.1000/abc"),
            ("openalex:W4", "openalex:W4", "https://publisher.example/landing"),
            ("openalex:W5", "openalex:W5", "https://openalex.org/W5"),
        ])
        # A missing abstract is never replaced by the title, so screening rejects it.
        self.assertEqual([(p["summary"], p["title"]) for p in converted][-1], ("", ""))


class ScreenTests(unittest.TestCase):
    # topic: ((accepted title, sentence), (rejected title, sentence)); every abstract is padded with FILLER.
    CASES = {
        "probability_calibration": (
            ("Temperature scaling for neural classifiers", "We study expected calibration error of neural network classifiers and how temperature scaling improves confidence estimates."),
            ("Calibrating laboratory scales", "We describe how technicians check calibration error of laboratory balances and record prediction intervals for each weighing session."),
        ),
        "proper_scoring_rules": (
            ("Strictly proper scoring rules for probabilistic forecasts", "We characterize scoring rules that reward honest probability forecasts."),
            ("A benchmark for weather forecasts", "We report the Brier score of each forecast system."),
        ),
        "selective_prediction": (
            ("Selective classification with deep networks", "A classifier may abstain on hard inputs to trade risk against coverage."),
            ("Voting behaviour in parliaments", "Members of parliament abstain from votes on budget bills while a classifier labels speeches."),
        ),
        "uncertainty_distribution_shift": (
            ("Predictive uncertainty under dataset shift", "We measure predictive uncertainty of neural networks under covariate shift."),
            ("Uncertainty in neural networks", "We discuss uncertainty in neural network weights during training."),
        ),
        "structured_constrained_decoding": (
            ("Grammar-constrained decoding for language models", "We enforce a JSON schema during generation from large language models."),
            ("Constrained decoding for error-correcting codes", "We study constrained decoding of convolutional codes over noisy channels."),
        ),
        "language_model_programming": (
            ("DSPy: compiling declarative language model calls", "DSPy compiles declarative pipelines of language model calls into optimized programs."),
            ("Chat assistants built on large language models", "We study chat assistants built on large language models and note one programmatic interface."),
        ),
        "judge_reliability": (
            ("Are LLM-as-a-judge evaluations reliable?", "We measure bias and consistency of large language models used as judges."),
            ("Large language models for essay feedback", "Teachers apply a rubric to grade essays and we report the consistency of graders."),
        ),
        "efficient_routing_cascades": (
            ("Early-exit classifiers for efficient inference", "Neural classifiers with early exit branches reduce compute on easy inputs."),
            ("Traffic routing in road networks", "We study cost-sensitive routing of delivery vehicles with early exit ramps."),
        ),
    }

    def test_each_topic_has_an_accepted_and_a_rejected_case(self):
        self.assertEqual(set(self.CASES), set(research.RULES))
        self.assertEqual(research.screen("Padding only", FILLER + " Done."), {})
        for topic, ((title, sentence), (near_title, near_sentence)) in self.CASES.items():
            with self.subTest(topic=topic):
                self.assertEqual(list(research.screen(title, sentence + " " + FILLER)), [topic])
                self.assertEqual(research.screen(near_title, near_sentence + " " + FILLER), {})

    def test_evidence_terms_are_the_first_hit_of_each_rule_without_repeats(self):
        (title, sentence), _ = self.CASES["probability_calibration"]
        self.assertEqual(research.screen(title, sentence + " " + FILLER),
                         {"probability_calibration": ["Temperature scal", "neural", "classif"]})
        (title, sentence), _ = self.CASES["language_model_programming"]
        self.assertEqual(research.screen(title, sentence + " " + FILLER), {"language_model_programming": ["DSPy"]})

    def test_core_concept_twice_in_the_abstract_substitutes_for_the_title(self):
        abstract = "We compare the Brier score and the logarithmic scoring rule for forecast systems. " + FILLER
        self.assertEqual(research.screen("Evaluating weather forecasts", abstract),
                         {"proper_scoring_rules": ["Brier score", "forecast"]})

    def test_short_abstracts_and_direct_jev_papers_are_not_background(self):
        (title, sentence), _ = self.CASES["probability_calibration"]
        self.assertEqual(research.screen(title, sentence), {})
        for direct in ("Jev models report these probabilities.", "System One models report these probabilities."):
            with self.subTest(direct=direct):
                self.assertEqual(research.screen(title, sentence + " " + direct + " " + FILLER), {})


class EvidenceExcerptTests(unittest.TestCase):
    def test_excerpt_is_twenty_words_around_the_first_matched_term(self):
        words = " ".join(f"w{i}" for i in range(40))
        self.assertEqual(research.evidence(words.replace("w15", "calibration"), ["absent", "Calibration"]),
                         "… " + " ".join(["w10", "w11", "w12", "w13", "w14", "calibration"] + [f"w{i}" for i in range(16, 30)]) + " …")
        self.assertEqual(research.evidence(words, ["absent"]), " ".join(f"w{i}" for i in range(20)) + " …")
        self.assertEqual(research.evidence("short calibrated text", ["calibrated"]), "short calibrated text")


def wrapper(*papers, provider=research.PROVIDER):
    return {"data": [{"paper": paper} for paper in papers], "retrieved_at": "2026-10-15T00:00:00+00:00",
            "http_status": 200, "retrieval_url": "https://example.org/search", "provider": provider}


def paper(paper_id, title, sentence, **fields):
    return {"id": paper_id, "title": title, "summary": sentence + " " + FILLER, "authors": [{"name": "A. Author"}, {}],
            "publishedAt": "2026-09-01T00:00:00.000Z", **fields}


class BuildRecordsTests(unittest.TestCase):
    def test_invalid_ids_direct_papers_and_rejections_are_counted_not_recorded(self):
        (title, sentence), (near_title, near_sentence) = ScreenTests.CASES["selective_prediction"]
        records, audit = research.build_records([("selective_prediction", "selective prediction", wrapper(
            paper("not-an-arxiv-id", title, sentence),
            paper("2609.20001", "Jev selective decisions", sentence),
            paper("2609.20002", near_title, near_sentence),
            paper("2609.20003v4", title, sentence),
        ))])
        self.assertEqual([r["id"] for r in records], ["arxiv:2609.20003"])
        self.assertEqual(audit["counts"], {"invalid_or_missing_arxiv_id": 1, "candidate_appearances": 3,
                                           "direct_jev_appearances_excluded": 1, "topic_screen_rejected_appearances": 1,
                                           "distinct_screened_candidates": 1})
        self.assertEqual(audit["direct_jev_discoveries"], {"2609.20001": "Jev selective decisions"})

    def test_record_carries_screening_provenance(self):
        (title, sentence), _ = ScreenTests.CASES["structured_constrained_decoding"]
        summary = sentence + " " + FILLER  # as stored: provider whitespace collapsed
        noisy = "  " + sentence.replace(" ", "\n  ", 3)
        [record], _ = research.build_records([("structured_constrained_decoding", "grammar constrained decoding",
                                               wrapper(paper("2609.20004v2", "  " + title + "\n", noisy)))])
        self.assertEqual({key: record[key] for key in ("id", "canonical_url", "title", "authors", "year", "published_at", "topic",
                                                       "matched_topics", "relation", "verification_level", "abstract_provider",
                                                       "abstract_sha256", "abstract_word_count", "evidence_terms", "relevance",
                                                       "discovery_queries", "retrieval_url", "http_status")}, {
            "id": "arxiv:2609.20004", "canonical_url": "https://arxiv.org/abs/2609.20004", "title": title,
            "authors": ["A. Author"], "year": 2026, "published_at": "2026-09-01T00:00:00.000Z",
            "topic": "structured_constrained_decoding", "matched_topics": ["structured_constrained_decoding"],
            "relation": "background", "verification_level": "abstract_checked", "abstract_provider": research.PROVIDER,
            "abstract_sha256": research.sha(summary), "abstract_word_count": len(summary.split()),
            "evidence_terms": ["Grammar-constrained", "language models"],
            "relevance": research.TOPIC_RELEVANCE["structured_constrained_decoding"],
            "discovery_queries": ["grammar constrained decoding"], "retrieval_url": "https://example.org/search", "http_status": 200,
        })
        self.assertLessEqual(len(record["evidence_excerpt"].replace("…", "").split()), 20)
        self.assertIn("Hugging Face Papers", record["abstract_origin"])

    def test_primary_topic_prefers_the_query_topic_when_it_matched(self):
        (title, sentence), _ = ScreenTests.CASES["probability_calibration"]
        both = sentence + " Predictive uncertainty under covariate shift is also measured."
        for query_topic, expected in (("uncertainty_distribution_shift", "uncertainty_distribution_shift"),
                                      ("probability_calibration", "probability_calibration"),
                                      ("judge_reliability", "probability_calibration")):
            with self.subTest(query_topic=query_topic):
                [record], _ = research.build_records([(query_topic, "query", wrapper(paper("2609.20005", title, both)))])
                self.assertEqual(record["matched_topics"], ["probability_calibration", "uncertainty_distribution_shift"])
                self.assertEqual(record["topic"], expected)
                self.assertEqual(record["relevance"], research.TOPIC_RELEVANCE[expected])

    def test_openalex_records_keep_their_doi_identity_and_provider(self):
        (title, sentence), _ = ScreenTests.CASES["proper_scoring_rules"]
        words = (sentence + " " + FILLER).split()
        work = openalex_work(6, doi="https://doi.org/10.1000/scoring", title=title, publication_year=2007,
                             abstract_inverted_index={word: [i] for i, word in reversed(list(enumerate(words)))})
        [record], _ = research.build_records([("proper_scoring_rules", "proper scoring rules",
                                               wrapper(*[i["paper"] for i in research.convert_openalex([work])], provider="openalex_api"))])
        self.assertEqual((record["id"], record["canonical_url"], record["year"], record["abstract_provider"]),
                         ("doi:10.1000/scoring", "https://doi.org/10.1000/scoring", 2007, "openalex_api"))
        self.assertIn("OpenAlex", record["abstract_origin"])

    def test_repeat_appearances_keep_the_best_rank_and_all_queries(self):
        (title, sentence), _ = ScreenTests.CASES["efficient_routing_cascades"]
        other = paper("2609.20007", "Unrelated cascade fixture", "Classifier cascades reduce compute for neural models.")
        records, _ = research.build_records([
            ("efficient_routing_cascades", "early exit", wrapper(other, paper("2609.20006", title, sentence))),
            ("efficient_routing_cascades", "classifier cascade", wrapper(paper("2609.20006v2", title, sentence))),
        ])
        record = next(r for r in records if r["id"] == "arxiv:2609.20006")
        self.assertEqual((record["_rank"], record["discovery_queries"]), (0, ["classifier cascade", "early exit"]))


def candidate(record_id, topic, rank=0, queries=1):
    return {"id": record_id, "topic": topic, "_rank": rank, "discovery_queries": [f"q{i}" for i in range(queries)]}


class SelectBalancedTests(unittest.TestCase):
    def test_round_robin_across_topics_in_query_order(self):
        records = [candidate("c1", "probability_calibration", 1), candidate("c0", "probability_calibration", 0),
                   candidate("c2", "probability_calibration", 2), candidate("s0", "selective_prediction"),
                   candidate("j0", "judge_reliability"), candidate("j1", "judge_reliability", 1)]
        selected = research.select_balanced(records, 4)
        self.assertEqual([r["id"] for r in selected], ["j0", "c0", "c1", "s0"])
        self.assertTrue(all("_rank" not in r for r in selected))

    def test_ties_prefer_more_discovery_queries_then_id(self):
        def records():
            return [candidate("b", "selective_prediction"), candidate("c", "selective_prediction", queries=3),
                    candidate("a", "selective_prediction")]
        self.assertEqual([r["id"] for r in research.select_balanced(records(), 2)], ["a", "c"])
        self.assertEqual([r["id"] for r in research.select_balanced(records(), 1)], ["c"])

    def test_target_bounds(self):
        records = [candidate("c0", "probability_calibration"), candidate("s0", "selective_prediction")]
        self.assertEqual(research.select_balanced([dict(r) for r in records], 0), [])
        self.assertEqual([r["id"] for r in research.select_balanced([dict(r) for r in records], 10)], ["c0", "s0"])


REVISION = "a" * 40
BASE = ecosystem.SPACE_URL + "/raw/" + REVISION + "/"


class FakeFetcher:
    def __init__(self, documents):
        self.documents, self.calls = documents, []

    def fetch(self, url):
        self.calls.append(url)
        if url not in self.documents:
            raise refresh.FetchError("http_404")
        return self.documents[url], url, "text/plain"


def index_documents(revision=REVISION):
    padding = {"padding": "x" * 100}
    return {
        "https://huggingface.co/api/spaces/" + ecosystem.SPACE: json.dumps({"sha": revision}).encode(),
        BASE + "README.md": ("---\ntitle: Fixture index\nmodels:\n- fixture/jev-model\n- fixture/other-model\n---\n\n"
                             "# Fixture index\n" + "Index description. " * 5).encode(),
        BASE + "news.html": ('<a href="https://github.com/Fixture/Router">router</a> <a href="https://x.com/fixture">post</a> '
                             '<img src="https://example.org/figure.png"> <a href="' + ecosystem.SPACE_URL + '">self</a>').encode(),
        BASE + "data/index.json": json.dumps({"models": [
            {"meta": {"model_url": "https://huggingface.co/fixture/jev-model", "code_url": "https://github.com/fixture/router.git"}},
            "not a model", {"meta": None}], **padding}).encode(),
        BASE + "data/methodology.json": json.dumps({
            "benchmarks": [{"url": "https://arxiv.org/abs/2609.10000v2"}],
            "added_benchmarks": [{"paper": "https://aclanthology.org/2024.acl-long.1.pdf"}],
            "reproduce": {"github": "https://github.com/fixture/harness"}, **padding}).encode(),
        BASE + "data/vision.json": json.dumps({"items": [{"link": "https://huggingface.co/datasets/fixture/vision-decisions/tree/main"}],
                                               **padding}).encode(),
        BASE + "data/v03.json": b"{}",  # too short to be index content
    }


class DiscoverIndexTests(unittest.TestCase):
    def test_index_files_seed_canonical_sources_with_first_origin_kept(self):
        scan = refresh.Scan(FakeFetcher(index_documents()))
        records, seeds = scan.discover_index()
        self.assertEqual(scan.index_revision, REVISION)
        self.assertEqual({key: (row["topic"], row["relation"], row["discovered_from"]) for key, row in seeds.items()}, {
            "https://huggingface.co/fixture/jev-model": ("decision-model-card", "direct", [BASE + "README.md"]),
            "https://huggingface.co/fixture/other-model": ("decision-model-card", "direct", [BASE + "README.md"]),
            "https://github.com/fixture/router": ("implementation-repository", "direct", [BASE + "data/index.json"]),
            "https://arxiv.org/abs/2609.10000": ("benchmark-source", "adjacent", [BASE + "data/methodology.json"]),
            "https://aclanthology.org/2024.acl-long.1": ("benchmark-source", "adjacent", [BASE + "data/methodology.json"]),
            "https://github.com/fixture/harness": ("evaluation-harness", "direct", [BASE + "data/methodology.json"]),
            "https://huggingface.co/datasets/fixture/vision-decisions": ("vision-decision-artifact", "direct", [BASE + "data/vision.json"]),
        })
        self.assertTrue(all(row["url"] == key and row["discovery_depth"] == 0 for key, row in seeds.items()))
        self.assertEqual(scan.excluded, 2)  # the blocked social link and the image; the index itself is skipped silently
        self.assertEqual([r["url"] for r in records], [ecosystem.SPACE_URL] + [ecosystem.SPACE_URL + "/blob/main/" + name for name in (
            "news.html", "data/index.json", "data/methodology.json", "data/vision.json")])
        self.assertTrue(all(r["resolved_revision"] == REVISION and r["verification_level"] == "content_screened" for r in records))
        self.assertEqual(scan.errors, [{"url": BASE + "data/v03.json", "code": "index_file_failed:ValueError"}])

    def test_unpinned_revision_stops_discovery(self):
        fetcher = FakeFetcher(index_documents(revision="main"))
        scan = refresh.Scan(fetcher)
        self.assertEqual(scan.discover_index(), ([], {}))
        self.assertEqual(fetcher.calls, ["https://huggingface.co/api/spaces/" + ecosystem.SPACE])
        self.assertEqual(scan.errors, [{"url": ecosystem.SPACE_URL, "code": "index_discovery_failed:ValueError"}])


if __name__ == "__main__":
    unittest.main()
