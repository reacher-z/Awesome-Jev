"""Reviewed curation must not rewrite provider evidence or re-add exclusions."""

import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts import build_source_index as index
from scripts import refresh_sources as refresh
from scripts import source_policy as policy_module
from scripts import validate


URL = "https://arxiv.org/abs/2609.12345"


def evidence(url=URL):
    return {"url": url, "evidence_url": url + "v2", "reviewed_at": "2026-10-16T06:00:00Z"}


def config(exclusions=None, annotations=None):
    return {"schema_version": 1, "exclusions": exclusions or [], "annotations": annotations or []}


def provider_row():
    return {"url": URL, "title": "Provider title", "topic": "probability_calibration", "relation": "background", "published_at": "2026-10-01", "retrieved_at": "2026-10-16T00:00:00Z", "verification_level": "abstract_checked", "abstract_sha256": "a" * 64, "abstract_word_count": 50, "retrieval_status": "success", "http_status": 200, "editorial_reviewed": False, "abstract_provider": "fixture", "screening_method": "fixture", "relevance": "Provider relevance"}


def write_policy(root, document):
    path = root / "data/source-curation.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(document))
    return policy_module.load_policy(path, index.canonical)


class SourcePolicyTests(unittest.TestCase):
    def test_forbids_evidence_grade_hash_and_retrieval_overrides(self):
        with tempfile.TemporaryDirectory() as temporary:
            for field in ("verification_level", "content_sha256", "abstract_sha256", "retrieved_at", "published_at"):
                with self.subTest(field=field), self.assertRaises(policy_module.PolicyError):
                    write_policy(Path(temporary), config(annotations=[{**evidence(), "note": "Primary metadata check.", field: "forbidden"}]))

    def test_canonical_alias_cannot_reintroduce_excluded_source(self):
        with tempfile.TemporaryDirectory() as temporary:
            policy = write_policy(Path(temporary), config(exclusions=[{**evidence(), "reason": "Outside collection scope."}]))
            incoming = {**provider_row(), "url": "https://huggingface.co/papers/2609.12345v3"}
            merged, changes = refresh.merge_records(refresh.Ledger([], []), [incoming], policy=policy)
            self.assertEqual(merged.rows, [])
            self.assertEqual(len(changes["curation_excluded"]), 1)

    def test_refresh_does_not_silently_delete_existing_excluded_evidence(self):
        with tempfile.TemporaryDirectory() as temporary:
            policy = write_policy(Path(temporary), config(exclusions=[{**evidence(), "reason": "Requires a reviewed removal."}]))
            row = provider_row()
            old = refresh.Ledger([row], [json.dumps(row) + "\n"])
            merged, _ = refresh.merge_records(old, [], policy=policy)
            self.assertEqual(merged, old)

    def test_excluded_source_fails_validation_and_index_build(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            policy = write_policy(root, config(exclusions=[{**evidence(), "reason": "Out of scope."}]))
            ledger = root / "data/ecosystem-sources.jsonl"
            ledger.write_text(json.dumps(provider_row()) + "\n")
            with patch.object(validate, "ROOT", root), patch.object(validate, "errors", []):
                validate.check_ledger(ledger, policy)
                self.assertTrue(any("explicitly excluded" in item for item in validate.errors))
            with patch.object(index, "ROOT", root), self.assertRaises(policy_module.PolicyError):
                index.build()

    def test_display_annotation_preserves_raw_provider_fields_and_verification(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            annotation = {**evidence(), "note": "Primary title and first submission checked.", "title": "Corrected primary title", "first_submitted": "2025-09-10", "topic": "judge_reliability", "relation": "direct", "relevance": "Corrected topical relevance."}
            write_policy(root, config(annotations=[annotation]))
            row = provider_row()
            original = json.dumps(row) + "\n"
            ledger = root / "data/ecosystem-sources.jsonl"
            ledger.write_text(original)
            with patch.object(index, "ROOT", root):
                payload = index.build()
            shown = payload["sources"][0]
            self.assertEqual(shown["title"], annotation["title"])
            self.assertEqual(shown["year"], "2025")
            self.assertEqual(shown["topic"], "judge_reliability")
            self.assertEqual(shown["relation"], "direct")
            self.assertEqual(shown["description"], annotation["relevance"])
            self.assertEqual(shown["verification_level"], row["verification_level"])
            self.assertEqual(shown["content_sha256"], row["abstract_sha256"])
            self.assertEqual(shown["retrieved_at"], row["retrieved_at"])
            self.assertEqual(shown["curation"]["provider_title"], row["title"])
            self.assertEqual(shown["curation"]["provider_published_at"], row["published_at"])
            self.assertEqual(shown["curation"]["evidence_url"], annotation["evidence_url"])
            self.assertEqual(ledger.read_text(), original)
            self.assertEqual(payload["counts"]["raw_records"], 1)

    def test_duplicate_or_conflicting_canonical_rules_are_rejected(self):
        first = {**evidence(), "reason": "Out of scope."}
        alias = {**evidence("https://arxiv.org/pdf/2609.12345v2"), "reason": "Same logical source."}
        with tempfile.TemporaryDirectory() as temporary:
            with self.assertRaises(policy_module.PolicyError):
                write_policy(Path(temporary), config(exclusions=[first, alias]))
            with self.assertRaises(policy_module.PolicyError):
                write_policy(Path(temporary), config(exclusions=[first], annotations=[{**evidence(), "note": "Conflicting annotation."}]))


class GithubCasePolicyTests(unittest.TestCase):
    """Curation written as GitHub displays a URL matches the scanner's lowercase identity."""
    DISPLAYED = "https://github.com/FuturePPO/TypeSafe_Register"
    SCANNED = "https://github.com/futureppo/typesafe_register"

    def test_mixed_case_exclusion_blocks_lowercase_scanner_identity(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            policy = write_policy(root, config(exclusions=[{**evidence(self.DISPLAYED), "reason": "Outside collection scope."}]))
            self.assertEqual(list(policy.exclusions), [self.SCANNED])
            incoming = {**provider_row(), "url": self.SCANNED}
            merged, changes = refresh.merge_records(refresh.Ledger([], []), [incoming], policy=policy)
            self.assertEqual(merged.rows, [])
            self.assertEqual(changes["curation_excluded"], [self.SCANNED])
            ledger = root / "data/ecosystem-sources.jsonl"
            ledger.write_text(json.dumps(incoming) + "\n")
            with patch.object(validate, "ROOT", root), patch.object(validate, "errors", []):
                validate.check_ledger(ledger, policy)
                self.assertTrue(any("explicitly excluded" in item for item in validate.errors))
            with patch.object(index, "ROOT", root), self.assertRaises(policy_module.PolicyError):
                index.build()

    def test_mixed_case_annotation_applies_and_case_aliases_conflict(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            write_policy(root, config(annotations=[{**evidence(self.DISPLAYED), "note": "Title checked.", "title": "TypeSafe Register"}]))
            (root / "data/ecosystem-sources.jsonl").write_text(json.dumps({**provider_row(), "url": self.SCANNED}) + "\n")
            with patch.object(index, "ROOT", root):
                shown = index.build()["sources"][0]
            self.assertEqual(shown["title"], "TypeSafe Register")
            self.assertEqual(shown["url"], self.SCANNED)
            with self.assertRaises(policy_module.PolicyError):
                write_policy(root, config(exclusions=[{**evidence(self.DISPLAYED), "reason": "Out of scope."},
                                                      {**evidence(self.SCANNED), "reason": "Same repository."}]))

    def test_paths_below_the_repository_keep_their_case(self):
        self.assertEqual(index.canonical("https://www.github.com/Owner/Repo/blob/Main/Docs/Guide.md"),
                         "https://github.com/owner/repo/blob/Main/Docs/Guide.md")
        self.assertEqual(index.canonical("https://github.com/Owner/Repo.git"), "https://github.com/owner/repo")


if __name__ == "__main__":
    unittest.main()
