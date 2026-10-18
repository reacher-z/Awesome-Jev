"""Pending evidence survives URL repair and maintainer-reviewed primary snapshots."""
import json
import unittest
from scripts import open_scan_pr as scan


def bundle(*rows, queue=()):
    return {scan.LEDGERS[0]: b"", scan.LEDGERS[1]: b"".join((json.dumps(row) + "\n").encode() for row in rows),
            scan.REPORT: json.dumps({"editorial_refresh_candidates": list(queue)}).encode()}


def primary():
    url = "https://arxiv.org/abs/2610.00381"
    return dict(url=url, verification_level="abstract_checked", abstract_provider="arxiv_primary_abstract_page",
                reviewed_version_url=url + "v1", reviewed_version="v1", canonical_page_separately_fetched=True,
                abstract_sha256="b" * 64, abstract_page_sha256="c" * 64)


class ContinuityIdentityTests(unittest.TestCase):
    def test_index_file_revision_keeps_identity_and_requires_matching_review(self):
        prefix = "https://huggingface.co/spaces/multimodalart/jev-decision-index/blob/"
        old = dict(url=prefix + "older/data/index.json", verification_level="editorial_reviewed", content_sha256="a" * 64)
        fresh = {**old, "url": prefix + "newer/data/index.json", "content_sha256": "b" * 64}
        queue = dict(url=prefix + "main/data/index.json", observed_content_sha256="b" * 64)
        scan.ensure_pending_continuity(bundle(old, queue=[queue]), bundle(fresh))
        with self.assertRaises(scan.ScanError):
            scan.ensure_pending_continuity(bundle(old, queue=[queue]), bundle({**fresh, "content_sha256": "d" * 64}))

    def test_html_escaped_query_repair_preserves_identifying_parameters(self):
        old = dict(canonical_url="https://example.org/oai?verb=getRecord&amp;identifier=one", verification_level="abstract_checked")
        new = {**old, "canonical_url": "https://example.org/oai?verb=getRecord&identifier=one"}
        scan.ensure_pending_continuity(bundle(old), bundle(new))
        with self.assertRaises(scan.ScanError):
            scan.ensure_pending_continuity(bundle(old), bundle({**new, "canonical_url": "https://example.org/oai?verb=getRecord&identifier=two"}))

    def test_main_accepted_primary_abstract_supersedes_unversioned_page_screening(self):
        accepted = primary()
        old = dict(url=accepted["url"], verification_level="content_screened", content_sha256="a" * 64)
        scan.ensure_pending_continuity(bundle(old), bundle(accepted), accepted=bundle(accepted))
        # Scan-only conversion, altered evidence and incomplete provenance must stop.
        for main in (None, bundle(), bundle({**accepted, "abstract_sha256": "d" * 64}),
                     bundle({**accepted, "canonical_page_separately_fetched": False})):
            with self.subTest(main=main is not None), self.assertRaises(scan.ScanError):
                scan.ensure_pending_continuity(bundle(old), bundle(accepted), accepted=main)

    def test_editorial_or_versioned_pending_evidence_cannot_use_the_exception(self):
        accepted = primary()
        for old in ({**accepted, "verification_level": "editorial_reviewed"},
                    {**accepted, "verification_level": "content_screened", "reviewed_version_url": accepted["url"] + "v2"},
                    dict(url=accepted["url"], verification_level="content_screened", retrieved_url=accepted["url"] + "v2")):
            with self.subTest(level=old["verification_level"]), self.assertRaises(scan.ScanError):
                scan.ensure_pending_continuity(bundle(old), bundle(accepted), accepted=bundle(accepted))
        pending = dict(url=accepted["url"], review_kind="pinned_arxiv_abstract",
                       observed_version_url=accepted["url"] + "v2", observed_abstract_sha256=accepted["abstract_sha256"])
        with self.assertRaises(scan.ScanError):
            scan.ensure_pending_continuity(bundle(accepted, queue=[pending]), bundle(accepted), accepted=bundle(accepted))


if __name__ == "__main__":
    unittest.main()
