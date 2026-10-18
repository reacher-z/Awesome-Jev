"""Incremental evidence and public-network boundary regressions, no network."""
import hashlib
import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch

from scripts import refresh_sources as refresh
from scripts import validate


def row(url="https://example.org/source", body="earlier", level="content_screened", **extra):
    return {"url": url, "title": "Fixture source", "topic": "fixture", "relation": "direct",
            "verification_level": level, "retrieved_at": "2026-10-15T00:00:00Z",
            "content_sha256": hashlib.sha256(body.encode()).hexdigest(),
            "relevance": "Synthetic regression fixture.", "checked_via": "Fixture content.", **extra}


def ledger(*rows):
    return refresh.Ledger(list(rows), [json.dumps(r, ensure_ascii=True) + "\r\n" for r in rows])


def catalog(root, papers=()):
    path = root / "site/papers.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"papers": list(papers)}))
    return path


def paper(number=0, **extra):
    return {"category": "Papers", "title": "Jev source fixture " + str(number),
            "url": f"https://arxiv.org/abs/2609.{10000 + number}v1", **extra}


ABSTRACT = "Typed decisions require separate accuracy and probability checks for reliable model choices. " * 4


def arxiv_page(version=2, abstract=ABSTRACT):
    return (f'<html><meta name="citation_date" content="2026/09/01" />'
            f'<td class="tablecell arxividv"><span><a href="https://arxiv.org/abs/2609.10000v{version}">version</a></span></td>'
            f'<blockquote class="abstract mathjax"><span>Abstract:</span> {abstract}</blockquote></html>').encode()


def primary_abstract(version=2, abstract=ABSTRACT):
    result = row("https://arxiv.org/abs/2609.10000", level="abstract_checked", status="screened",
        abstract_provider="arxiv_primary_abstract_page", abstract_sha256=refresh.research.sha(" ".join(abstract.split())),
        abstract_page_sha256=hashlib.sha256(arxiv_page(version, abstract)).hexdigest(),
        reviewed_version=f"v{version}", reviewed_version_url=f"https://arxiv.org/abs/2609.10000v{version}",
        published_at="2026-09-01", first_submitted="2026-09-01", reviewed_version_date="2026-10-03",
        canonical_page_separately_fetched=True, full_text_reviewed=False, editorial_reviewed=False)
    result.pop("content_sha256")
    return result


class CuratedDiscoveryTests(unittest.TestCase):
    def test_catalog_version_is_fetched_but_identity_stays_canonical(self):
        with tempfile.TemporaryDirectory() as tmp:
            seeds = refresh.curated_paper_seeds(catalog(Path(tmp), [paper(url="https://arxiv.org/pdf/2609.10000v2.pdf")]))
        url = "https://arxiv.org/abs/2609.10000"
        fetcher = Mock()
        fetcher.fetch.side_effect = lambda target: (arxiv_page(), target, "text/html")
        scan = refresh.Scan(fetcher, curated_seeds=seeds)
        with patch.object(scan, "discover_index", return_value=([], {})), contextlib.redirect_stdout(io.StringIO()):
            records = scan.scan_ecosystem(ledger())
        fetcher.fetch.assert_called_once_with(url + "v2")
        self.assertEqual(records[0]["url"], url)
        self.assertEqual(records[0]["retrieved_url"], url + "v2")

    def test_every_catalog_paper_is_seeded_independent_of_external_search(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            entries = [paper(i) for i in range(7)]
            seeds = refresh.curated_paper_seeds(catalog(root, entries))
            self.assertEqual(set(seeds), {refresh.index.canonical(p["url"]) for p in entries})
            # A later catalog addition must need no collector code change.
            entries.append(paper(7))
            self.assertEqual(len(refresh.curated_paper_seeds(catalog(root, entries))), 8)

    def test_versions_deduplicate_and_excluded_catalog_sources_are_not_fetched(self):
        entries = [paper(), paper(url="https://arxiv.org/pdf/2609.10000v2.pdf"), paper(1)]
        with tempfile.TemporaryDirectory() as tmp:
            seeds = refresh.curated_paper_seeds(catalog(Path(tmp), entries))
        self.assertEqual(len(seeds), 2)
        allowed, excluded = "https://arxiv.org/abs/2609.10000", "https://arxiv.org/abs/2609.10001"
        policy = Mock()
        policy.exclusion.side_effect = lambda url: {"reason": "Fixture exclusion"} if url == excluded else None
        scan = refresh.Scan(refresh.PublicFetcher(), curated_seeds=seeds, policy=policy)
        external = {allowed: {**seeds[allowed], "discovered_from": ["https://example.org/index"]}}
        with patch.object(scan, "discover_index", return_value=([], external)), patch.object(refresh.ecosystem, "audit", side_effect=lambda seed: (row(seed["url"]), [])) as audit, contextlib.redirect_stdout(io.StringIO()):
            records = scan.scan_ecosystem(ledger(row(allowed)))
        self.assertEqual(audit.call_count, 1)
        self.assertEqual(records[0]["url"], allowed)
        self.assertEqual(scan.curation_excluded, {excluded})
        self.assertIn(refresh.CURATED_PAPERS_ORIGIN, audit.call_args.args[0]["discovered_from"])

    def test_catalog_labels_never_replace_fetched_evidence_or_grant_review(self):
        with tempfile.TemporaryDirectory() as tmp:
            seeds = refresh.curated_paper_seeds(catalog(Path(tmp), [paper(verification_level="editorial_reviewed", content_sha256="catalog-claim")]))
        seed = next(iter(seeds.values()))
        self.assertNotIn("verification_level", seed)
        self.assertNotIn("content_sha256", seed)
        raw = b"<html><title>Jev fixture</title><p>" + b"Typed decision models require careful probability calibration and reliable evaluation. " * 8 + b"</p></html>"
        fetcher = Mock()
        fetcher.fetch.return_value = (raw, seed["url"], "text/html")
        scan = refresh.Scan(fetcher, curated_seeds=seeds)
        with patch.object(scan, "discover_index", return_value=([], {})), contextlib.redirect_stdout(io.StringIO()):
            records = scan.scan_ecosystem(ledger())
        self.assertEqual(records[0]["verification_level"], "content_screened")
        self.assertEqual(records[0]["content_sha256"], hashlib.sha256(raw).hexdigest())
        fetcher.fetch.side_effect = refresh.FetchError("network_failure")
        with patch.object(scan, "discover_index", return_value=([], {})), contextlib.redirect_stdout(io.StringIO()):
            failed = scan.scan_ecosystem(ledger())
        self.assertEqual(failed[0]["verification_level"], "metadata_only")
        self.assertNotIn("content_sha256", failed[0])

    def test_malformed_catalog_fails_before_network_without_echoing_input(self):
        invalid = ["https://example.org/paper", "https://127.0.0.1/paper",
                   "https://arxiv.org/abs/2609.10000?token=fixture-sensitive-value",
                   "https://arxiv.org/abs/2609.10000#fragment"]
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for url in invalid:
                catalog(root, [paper(url=url)])
                with self.subTest(url=url.split("?", 1)[0]), patch.object(refresh, "ROOT", root), patch.object(refresh.PublicFetcher, "fetch") as fetch, contextlib.redirect_stderr(io.StringIO()) as output:
                    with self.assertRaises(SystemExit) as error:
                        refresh.main([])
                    self.assertEqual(error.exception.code, 2)
                    self.assertIn("invalid_curated_paper_entry_1", output.getvalue())
                    self.assertNotIn(url, output.getvalue())
                    fetch.assert_not_called()
            catalog(root).write_text("not JSON")
            with self.assertRaisesRegex(ValueError, "invalid_curated_paper_catalog"):
                refresh.curated_paper_seeds(root / "site/papers.json")


class DiagnosticTests(unittest.TestCase):
    def test_fixed_fetch_codes_preserved_but_arbitrary_messages_never_logged(self):
        for message in ("http_429", "http_503", "network_failure", "dns_resolution_failed"):
            self.assertEqual(refresh.safe_exception_code(refresh.FetchError(message)), message)
        private_message = "upstream response contains fixture-sensitive-value"
        fetcher = Mock()
        fetcher.fetch.side_effect = refresh.FetchError(private_message)
        scan = refresh.Scan(fetcher)
        scan.query("direct", "Jev", refresh.research.PROVIDER)
        self.assertEqual(scan.errors[0]["code"], "paper_query_failed:unclassified_fetch_error")
        self.assertNotIn(private_message, json.dumps(scan.errors))
        fetcher.fetch.side_effect = refresh.FetchError("http_429")
        with patch.object(refresh.time, "sleep"):
            scan.query("direct", "Jev", refresh.research.PROVIDER)
        self.assertEqual(scan.errors[1]["code"], "paper_query_failed:http_429")

    def test_error_totals_cover_all_issues_even_when_examples_are_truncated(self):
        issues = [{"url": f"https://example.org/source-{i}", "code": "unavailable"} for i in range(101)]
        issues += [{"url": "https://example.org/query", "code": "paper_query_failed:http_429"}]
        report = refresh.error_report(issues)
        self.assertEqual(report["error_count"], 102)
        self.assertEqual(report["error_examples_count"], 100)
        self.assertTrue(report["error_examples_truncated"])
        self.assertEqual(report["error_code_counts"], {"paper_query_failed:http_429": 1, "unavailable": 101})
        empty = refresh.error_report([])
        self.assertFalse(empty["error_examples_truncated"])
        self.assertEqual(empty["error_code_counts"], {})


class IncrementalEvidenceTests(unittest.TestCase):
    def test_same_ledger_alias_cannot_bypass_stronger_editorial_record(self):
        current = "https://huggingface.co/spaces/multimodalart/jev-decision-index"
        legacy = "https://huggingface.co/spaces/multimodalart/jev-reproductions-tracker"
        reviewed = row(current, body="reviewed", level="editorial_reviewed", status="screened")
        shadow = row(legacy, body="historical", status="screened")
        for order in ((reviewed, shadow), (shadow, reviewed)):
            with self.subTest(first=order[0]["url"]):
                old = ledger(*order)
                result, changes = refresh.merge_records(old, [row(current, body="new", status="screened")])
                self.assertEqual(result.lines, old.lines)
                self.assertEqual(changes["changed"], [])
                self.assertEqual(changes["added"], [])
                self.assertEqual(len(changes["editorial_review_required"]), 1)
                self.assertEqual(changes["editorial_review_required"][0]["old_content_sha256"], reviewed["content_sha256"])

    def test_same_ledger_alias_refresh_preserves_unique_historical_urls(self):
        current = "https://huggingface.co/respanai/span-02"
        legacy = "https://huggingface.co/lihe07/span-02"
        current_row = row(current, body="current", status="screened")
        legacy_row = row(legacy, body="legacy", status="screened")
        for order in ((current_row, legacy_row), (legacy_row, current_row)):
            with self.subTest(first=order[0]["url"]):
                old = ledger(*order)
                observation = row(legacy, body="changed", status="screened", canonical_url=current)
                result, changes = refresh.merge_records(old, [observation])
                urls = [r.get("canonical_url", r["url"]) for r in result.rows]
                self.assertEqual(len(set(urls)), 2)
                self.assertEqual(set(urls), {current, legacy})
                position = next(i for i, r in enumerate(old.rows) if r["url"] == legacy)
                self.assertEqual(result.lines[position], old.lines[position])
                updated = next(r for r in result.rows if r["url"] == current)
                self.assertEqual(updated["content_sha256"], observation["content_sha256"])
                self.assertEqual(changes["changed"], [current])
                self.assertEqual(changes["added"], [])

    def test_cross_ledger_primary_page_cannot_be_added_or_promoted_again(self):
        prior = primary_abstract()
        originals = (ledger(), ledger(prior))
        page = row(prior["url"], status="screened", retrieved_url=prior["reviewed_version_url"],
                   content_sha256=prior["abstract_page_sha256"])
        eco, scholarly = refresh.route_observations(originals, [page], [])
        self.assertEqual(eco, [])
        result, changes = refresh.merge_records(originals[1], scholarly)
        self.assertEqual(result.lines, originals[1].lines)
        self.assertEqual(result.rows[0]["verification_level"], "abstract_checked")
        self.assertFalse(changes["added"] or changes["changed"] or changes["editorial_review_required"])

    def test_direct_scholarly_discovery_returns_to_existing_research_ledger(self):
        prior = primary_abstract()
        old = ledger(prior)
        same = dict(prior, abstract_provider="huggingface_papers_api", canonical_page_separately_fetched=False,
                    retrieved_at="2026-10-20T00:00:00Z")
        eco, scholarly = refresh.route_observations((ledger(), old), [same], [])
        result, changes = refresh.merge_records(old, scholarly)
        self.assertEqual(eco, [])
        self.assertEqual(result.lines, old.lines)
        self.assertFalse(changes["added"] or changes["changed"])

    def test_changed_primary_abstract_queues_review_without_mixing_version_fields(self):
        prior = primary_abstract()
        old = ledger(prior)
        observed = dict(prior, abstract_sha256=refresh.research.sha("changed abstract"),
                        observed_version_url=prior["url"] + "v3", published_at="2026-10-20")
        result, changes = refresh.merge_records(old, [observed])
        self.assertEqual(result.lines, old.lines)
        self.assertEqual(result.rows[0]["first_submitted"], "2026-09-01")
        self.assertEqual(result.rows[0]["reviewed_version"], "v2")
        event = changes["editorial_review_required"][0]
        self.assertEqual(event["old_reviewed_version_url"], prior["url"] + "v2")
        self.assertEqual(event["observed_version_url"], prior["url"] + "v3")
        self.assertFalse(changes["added"] or changes["changed"])

    def test_pinned_page_noop_does_not_hide_changed_provider_abstract(self):
        prior = primary_abstract()
        old = ledger(prior)
        same_page = row(prior["url"], status="screened", content_sha256=prior["abstract_page_sha256"])
        changed = {**prior, "abstract_provider": "huggingface_papers_api",
                   "abstract_sha256": refresh.research.sha("different provider abstract")}
        changed.pop("reviewed_version_url")
        result, changes = refresh.merge_records(old, [same_page, changed])
        self.assertEqual(result.lines, old.lines)
        event = changes["editorial_review_required"][0]
        self.assertIsNone(event["observed_version_url"])
        self.assertEqual(event["observed_content_sha256"], changed["abstract_sha256"])

    def test_pinned_review_candidate_never_grants_automatic_editorial_status(self):
        prior = primary_abstract()
        claimed_review = row(prior["url"], body="changed source", level="editorial_reviewed",
                             editorial_reviewed=True, retrieved_url=prior["url"] + "v3")
        result, changes = refresh.merge_records(ledger(prior), [claimed_review])
        self.assertEqual(result.rows, [prior])
        self.assertEqual(changes["editorial_review_required"][0]["observed_verification_level"], "content_screened")
        self.assertEqual(claimed_review["verification_level"], "editorial_reviewed")  # Input not mutated.

    def test_historical_cross_ledger_duplicates_are_retained_without_new_rows(self):
        url = "https://arxiv.org/abs/2609.12345"
        originals = (ledger(row(url, body="body")), ledger(row(url, body="abstract", level="abstract_checked")))
        eco, scholarly = refresh.route_observations(originals, [], [row(url, body="body")])
        updated_eco, ec = refresh.merge_records(originals[0], eco)
        updated_research, rc = refresh.merge_records(originals[1], scholarly)
        self.assertEqual(updated_eco.lines, originals[0].lines)
        self.assertEqual(updated_research.lines, originals[1].lines)
        self.assertEqual(ec["added"] + rc["added"], [])

    def test_new_cross_ledger_identity_is_assigned_once(self):
        value = row("https://arxiv.org/abs/2609.12345")
        eco, scholarly = refresh.route_observations((ledger(), ledger()), [value], [dict(value)])
        a, ec = refresh.merge_records(ledger(), eco)
        b, rc = refresh.merge_records(ledger(), scholarly)
        self.assertEqual(len(a.rows) + len(b.rows), 1)
        self.assertEqual(len(ec["added"]) + len(rc["added"]), 1)

    def test_canonical_body_fetch_updates_only_page_provenance_not_review_scope(self):
        url = "https://arxiv.org/abs/2609.12345"
        prior = row(url, level="abstract_checked", abstract_provider="huggingface_papers_api",
                    abstract_sha256=hashlib.sha256(b"original abstract").hexdigest(),
                    canonical_page_separately_fetched=False, full_text_reviewed=False,
                    editorial_reviewed=False)
        prior.pop("content_sha256")
        fresh = row(url, body="primary page", status="screened", retrieved_url=url + "v2")
        result, _ = refresh.merge_records(ledger(prior), [fresh])
        updated = result.rows[0]
        self.assertTrue(updated["canonical_page_separately_fetched"])
        for field in ("abstract_provider", "abstract_sha256", "full_text_reviewed", "editorial_reviewed"):
            self.assertEqual(updated[field], prior[field])
        self.assertEqual(updated["verification_level"], "content_screened")

    def test_same_body_legacy_flag_repair_preserves_dates_and_other_evidence(self):
        url = "https://arxiv.org/abs/2609.12345"
        prior = row(url, status="screened", canonical_page_separately_fetched=False,
                    abstract_provider="huggingface_papers_api", full_text_reviewed=False,
                    editorial_reviewed=False, editorial_note="Retain this note")
        fresh = row(url, status="screened", retrieved_url=url,
                    retrieved_at="2026-10-16T00:00:00Z", title="Changed automatic title")
        result, changes = refresh.merge_records(ledger(prior), [fresh])
        self.assertEqual(result.rows[0], {**prior, "canonical_page_separately_fetched": True})
        self.assertEqual(changes["changed"], [url])
        # Repeating the same observation becomes a byte-identical no-op.
        repeated, repeated_changes = refresh.merge_records(result, [fresh])
        self.assertEqual(repeated.lines, result.lines)
        self.assertEqual(repeated_changes["changed"], [])

    def test_mirror_body_does_not_substantiate_a_canonical_page_claim(self):
        url = "https://arxiv.org/abs/2609.12345"
        prior = row(url, canonical_page_separately_fetched=False,
                    abstract_provider="huggingface_papers_api", full_text_reviewed=False,
                    editorial_reviewed=False)
        fresh = row(url, body="changed mirror body", status="screened",
                    retrieved_url="https://example.org/paper-mirror",
                    canonical_page_separately_fetched=True)
        result, _ = refresh.merge_records(ledger(prior), [fresh])
        self.assertFalse(result.rows[0]["canonical_page_separately_fetched"])
        self.assertFalse(result.rows[0]["full_text_reviewed"])
        self.assertFalse(result.rows[0]["editorial_reviewed"])

    def test_canonical_page_flag_requires_body_hash_and_screened_status(self):
        url = "https://arxiv.org/abs/2609.12345"
        valid = row(url, status="screened", retrieved_url=url)
        for candidate in [dict(valid, status="unavailable"),
                          dict(valid, content_sha256=""),
                          dict(valid, verification_level="abstract_checked"),
                          dict(valid, retrieved_url=None)]:
            with self.subTest(candidate_status=candidate.get("status")):
                self.assertFalse(refresh.canonical_page_observed(candidate))

    def test_unchanged_hash_preserves_exact_old_record_bytes_and_manual_fields(self):
        prior = row(editorial_note="Manually inspected evidence", title="Corrected title")
        old = ledger(prior)
        new = row(retrieved_at="2026-10-16T00:00:00Z", title="Automatically extracted title")
        result, changes = refresh.merge_records(old, [new])
        self.assertEqual(result.lines, old.lines)
        self.assertEqual(result.rows, old.rows)
        self.assertFalse(changes["added"] or changes["changed"])

    def test_refetched_content_drops_fields_of_the_earlier_observation(self):
        # #103: a relevance rescreen of earlier bytes does not cover new content,
        # and a later successful fetch supersedes an earlier failure's errors.
        rescreened = row(status="screened", relevance_rescreened_at="2026-10-15T01:00:00Z")
        failed = row(level="metadata_only", status="unavailable", fetch_errors=["network_failure"])
        failed.pop("content_sha256")
        fresh = row(body="changed bytes", status="screened", retrieved_at="2026-10-16T04:00:00Z")
        for prior, dropped in ((rescreened, "relevance_rescreened_at"), (failed, "fetch_errors")):
            with self.subTest(dropped=dropped):
                result, changes = refresh.merge_records(ledger(prior), [fresh])
                self.assertEqual(changes["changed"], [prior["url"]])
                self.assertNotIn(dropped, result.rows[0])
                self.assertEqual(result.rows[0], {k: v for k, v in {**prior, **fresh}.items() if k != dropped})
                with tempfile.TemporaryDirectory() as tmp:
                    path = Path(tmp) / "sources.jsonl"
                    path.write_text("".join(result.lines), encoding="utf-8")
                    with patch.object(validate, "ROOT", Path(tmp)), patch.object(validate, "errors", []) as errors:
                        validate.check_ledger(path)
                        self.assertEqual(errors, [])
        # A rescreen of the bytes the row still holds is kept.
        same = row(status="screened", relevance_rescreened_at="2026-10-16T05:00:00Z")
        result, _ = refresh.merge_records(ledger(same), [row(status="screened", retrieved_at="2026-10-16T06:00:00Z")])
        self.assertEqual(result.rows, [same])

    def test_validator_rejects_a_stale_rescreen_and_errors_on_a_screened_row(self):
        cases = {
            "relevance_rescreened_at predates retrieved_at": row(status="screened", retrieved_at="2026-10-16T04:04:00+00:00",
                                                                 relevance_rescreened_at="2026-10-16T01:23:38+00:00"),
            "relevance_rescreened_at must be an ISO timestamp": row(status="screened", relevance_rescreened_at="yesterday"),
            "must not keep fetch_errors": row(status="screened", fetch_errors=["network_failure"]),
        }
        valid = [row(status="screened", relevance_rescreened_at="2026-10-15T00:00:00Z"),
                 row(status="screened", relevance_rescreened_at="2026-10-16T00:00:00+00:00"),
                 row(level="metadata_only", status="unavailable", fetch_errors=["network_failure"])]
        for message, record in [*cases.items(), *((None, record) for record in valid)]:
            with self.subTest(message=message, record=record), tempfile.TemporaryDirectory() as tmp:
                path = Path(tmp) / "sources.jsonl"
                path.write_text(json.dumps(record) + "\n", encoding="utf-8")
                with patch.object(validate, "ROOT", Path(tmp)), patch.object(validate, "errors", []) as errors:
                    validate.check_ledger(path)
                    if message is None:
                        self.assertEqual(errors, [])
                    else:
                        self.assertEqual(len(errors), 1)
                        self.assertIn(message, errors[0])

    def test_partial_failure_keeps_prior_success_and_accepts_new_source(self):
        old = ledger(row())
        failed = row(level="metadata_only", status="unavailable")
        failed.pop("content_sha256")
        added = row("https://example.org/new", body="new evidence")
        result, changes = refresh.merge_records(old, [failed, added])
        self.assertEqual(result.lines[0], old.lines[0])
        self.assertEqual(len(result.rows), 2)
        self.assertEqual(changes["preserved_after_failure"], 1)

    def test_missing_provider_results_never_remove_prior_rows(self):
        old = ledger(row(), row("https://example.org/second", body="second"))
        result, changes = refresh.merge_records(old, [])
        self.assertEqual(result, old)
        self.assertEqual(changes["added"], [])

    def test_changed_editorial_source_is_preserved_pending_human_review(self):
        old = ledger(row(level="editorial_reviewed", editorial_note="Reviewed original"))
        fresh = row(body="new source revision")
        result, changes = refresh.merge_records(old, [fresh])
        self.assertEqual(result.lines, old.lines)
        self.assertEqual(len(changes["editorial_review_required"]), 1)
        self.assertEqual(changes["editorial_review_required"][0]["observed_content_sha256"], fresh["content_sha256"])

    def test_automated_new_record_never_receives_editorial_tier(self):
        result, _ = refresh.merge_records(ledger(), [row(level="editorial_reviewed")])
        self.assertEqual(result.rows[0]["verification_level"], "content_screened")

    def test_lower_evidence_tier_does_not_replace_fuller_prior_evidence(self):
        old = ledger(row())
        result, _ = refresh.merge_records(old, [row(body="abstract revision", level="abstract_checked")])
        self.assertEqual(result.lines, old.lines)

    def test_duplicate_versions_and_mirrored_content_do_not_inflate_additions(self):
        a = row("https://arxiv.org/abs/2609.12345v1", body="paper")
        b = row("https://arxiv.org/pdf/2609.12345v2.pdf", body="paper")
        c = row("https://example.org/mirror", body="paper")
        result, changes = refresh.merge_records(ledger(), [a, b, c])
        self.assertEqual(len(result.rows), 1)
        self.assertEqual(len(changes["added"]), 1)

    def test_max_new_limits_only_additions_not_existing_rows(self):
        old = ledger(row())
        incoming = [row("https://example.org/a", "a"), row("https://example.org/b", "b")]
        result, changes = refresh.merge_records(old, incoming, max_new=1)
        self.assertEqual(result.lines[0], old.lines[0])
        self.assertEqual(len(changes["added"]), 1)

    def test_metadata_only_new_source_is_tracked_with_its_original_tier(self):
        result, _ = refresh.merge_records(ledger(), [row(level="metadata_only", status="unavailable")])
        self.assertEqual(result.rows[0]["verification_level"], "metadata_only")

    def test_ledger_read_and_noop_preserve_crlf_bytes(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "sources.jsonl"
            raw = ledger(row()).lines[0].encode()
            path.write_bytes(raw)
            loaded = refresh.Ledger.read(path)
            result, _ = refresh.merge_records(loaded, [row(retrieved_at="later")])
            self.assertFalse(refresh.write_if_changed(path, "".join(result.lines)))
            self.assertEqual(path.read_bytes(), raw)

    def test_pending_review_survives_fetch_failure_and_same_hash_new_snapshot_url(self):
        old = row(level="editorial_reviewed")
        fresh = row(body="changed", retrieved_url="https://example.org/revision-a")
        _, change = refresh.merge_records(ledger(old), [fresh])
        previous = {"editorial_refresh_candidates": change["editorial_review_required"]}
        pending, changed, _ = refresh.pending_reviews(previous, [], [old])
        self.assertEqual(pending, previous["editorial_refresh_candidates"])
        self.assertFalse(changed)
        observed = [dict(pending[0], retrieved_url="https://example.org/revision-b")]
        pending2, changed2, _ = refresh.pending_reviews(previous, observed, [old])
        self.assertEqual(pending2, pending)
        self.assertFalse(changed2)

    def test_more_than_100_pending_examples_do_not_create_repeated_changes(self):
        old = [row(f"https://example.org/source-{i:03}", level="editorial_reviewed") for i in range(120)]
        fresh = [dict(r, content_sha256=hashlib.sha256(b"new").hexdigest(), verification_level="content_screened") for r in old]
        _, changes = refresh.merge_records(ledger(*old), fresh)
        pending, _, count = refresh.pending_reviews({}, changes["editorial_review_required"], old)
        self.assertEqual(count, 120)
        self.assertEqual(len(pending), 100)
        _, changed, _ = refresh.pending_reviews({"editorial_refresh_candidates": pending}, changes["editorial_review_required"], old)
        self.assertFalse(changed)


class JsonlLineSeparatorTests(unittest.TestCase):
    """U+2028, U+2029 and U+0085 in fetched text must never split a ledger record."""
    TITLE = "Jev Router\u2028typed decisions\u2029v2\u0085notes"

    def test_scraped_unicode_line_breaks_round_trip_as_one_ledger_record(self):
        url = "https://github.com/fixture/router"
        body = ("# " + self.TITLE + "\n\n## Usage\u2028examples\n\n"
                + "Jev typed decision models need calibrated probability readouts for routing. " * 6).encode()
        seed = {"url": url, "title": "router", "topic": "implementation-repository", "relation": "adjacent",
                "relevance": "Synthetic regression fixture.", "discovered_from": ["https://example.org/index"], "discovery_depth": 0}
        with patch.object(refresh.ecosystem, "fetch", return_value=(body, "https://raw.githubusercontent.com/fixture/router/main/README.md", "text/plain")):
            record, _ = refresh.ecosystem.audit(seed)
        self.assertEqual(record["title"], self.TITLE)
        merged, changes = refresh.merge_records(ledger(), [record])
        self.assertEqual(changes["added"], [url])
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "sources.jsonl"
            refresh.write_if_changed(path, "".join(merged.lines))
            raw = path.read_bytes()
            self.assertEqual(len(raw.decode("utf-8").splitlines()), 1)
            loaded = refresh.Ledger.read(path)
        self.assertEqual(loaded.rows[0]["title"], self.TITLE)
        self.assertEqual(loaded.rows[0]["section_headings"][:2], [self.TITLE, "Usage\u2028examples"])
        self.assertEqual(loaded.lines, merged.lines)

    def test_every_ledger_reader_splits_records_only_at_newline(self):
        from scripts import open_scan_pr
        rows = [row("https://example.org/a", title=self.TITLE, status="screened"),
                row("https://example.org/b", body="other", status="screened")]
        # The unescaped form an earlier writer produced: four splitlines() pieces.
        text = "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows)
        self.assertGreater(len(text.splitlines()), len(rows))
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "data").mkdir()
            path = root / "data/ecosystem-sources.jsonl"
            path.write_text(text, encoding="utf-8")
            self.assertEqual([r["title"] for r in refresh.Ledger.read(path).rows], [self.TITLE, "Fixture source"])
            with patch.object(refresh.index, "ROOT", root):
                self.assertEqual(refresh.index.build()["counts"]["raw_records"], 2)
            with patch.object(validate, "ROOT", root), patch.object(validate, "errors", []) as errors:
                self.assertEqual(len(validate.check_ledger(path)), 2)
                self.assertEqual(errors, [])
            self.assertEqual(open_scan_pr.read_data(path), text.encode("utf-8"))
            open_scan_pr.meaningful_fingerprint({name: text.encode("utf-8") for name in open_scan_pr.LEDGERS})


class PinnedArxivObservationTests(unittest.TestCase):
    def scan(self, fetcher, prior):
        url = prior["url"]
        seed = {"url": url, "title": prior["title"], "topic": "research-paper", "relation": "direct",
                "relevance": "Fixture paper.", "discovery_depth": 0, "fetch_url": prior["reviewed_version_url"],
                "discovered_from": [refresh.CURATED_PAPERS_ORIGIN]}
        scan = refresh.Scan(fetcher, curated_seeds={url: seed}, pinned_sources={url: prior})
        with patch.object(scan, "discover_index", return_value=([], {})), contextlib.redirect_stdout(io.StringIO()):
            observations = scan.scan_ecosystem(ledger(), max_new=0)
        return scan, observations

    def test_latest_version_with_same_abstract_is_observed_without_repinning(self):
        prior = primary_abstract()
        fetcher = Mock()
        fetcher.fetch.side_effect = lambda target: (arxiv_page(2 if target.endswith("v2") else 3), target, "text/html")
        scan, observations = self.scan(fetcher, prior)
        self.assertFalse(scan.errors)
        self.assertEqual({o["observed_version_url"] for o in observations}, {prior["url"] + "v2", prior["url"] + "v3"})
        self.assertTrue(all(o["verification_level"] == "abstract_checked" for o in observations))
        old = ledger(prior)
        result, changes = refresh.merge_records(old, observations)
        self.assertEqual(result.lines, old.lines)
        event = changes["editorial_review_required"][0]
        self.assertEqual(event["observed_version_url"], prior["url"] + "v3")
        self.assertEqual(event["old_content_sha256"], event["observed_content_sha256"])
        pending, changed, _ = refresh.pending_reviews({}, [event], result.rows)
        self.assertTrue(changed)
        previous = {"editorial_refresh_candidates": pending}
        # A provider failure cannot clear a same-abstract, different-version queue.
        retained, changed, _ = refresh.pending_reviews(previous, [], result.rows)
        self.assertEqual(retained, pending)
        self.assertFalse(changed)
        repeat = dict(event, retrieved_url="https://arxiv.org/abs/2609.10000v3")
        repeated, changed, _ = refresh.pending_reviews(previous, [repeat], result.rows)
        self.assertEqual(repeated, pending)
        self.assertFalse(changed)
        accepted = dict(prior, reviewed_version="v3", reviewed_version_url=prior["url"] + "v3")
        cleared, changed, _ = refresh.pending_reviews(previous, [], [accepted])
        self.assertEqual(cleared, [])
        self.assertTrue(changed)

    def test_same_abstract_same_version_keeps_exact_record_despite_page_clock_changes(self):
        prior = primary_abstract()
        fetcher = Mock()
        fetcher.fetch.side_effect = lambda target: (arxiv_page() + b'<!-- changed navigation -->', target, "text/html")
        _, observations = self.scan(fetcher, prior)
        old = ledger(prior)
        result, changes = refresh.merge_records(old, observations)
        self.assertEqual(result.lines, old.lines)
        self.assertFalse(changes["added"] or changes["changed"] or changes["editorial_review_required"])

    def test_failed_latest_probe_and_stale_provider_cannot_replace_known_pending_version(self):
        prior = primary_abstract()
        newer = primary_abstract(version=3, abstract=ABSTRACT + "New revision.")
        existing = refresh.primary_review_candidate(prior, newer)
        previous = {"editorial_refresh_candidates": [existing]}
        fetcher = Mock()
        def response(target):
            if target.endswith("v2"):
                return arxiv_page(), target, "text/html"
            raise refresh.FetchError("network_failure")
        fetcher.fetch.side_effect = response
        scan, observations = self.scan(fetcher, prior)
        self.assertTrue(scan.errors)
        for version in (None, prior["url"] + "v1", prior["url"] + "v2"):
            with self.subTest(provider_version=version):
                provider = {**prior, "abstract_provider": "huggingface_papers_api",
                            "abstract_sha256": refresh.research.sha("Stale provider abstract")}
                provider.pop("reviewed_version_url")
                if version:
                    provider["observed_version_url"] = version
                result, changes = refresh.merge_records(ledger(prior), observations + [provider])
                pending, changed, count = refresh.pending_reviews(previous, changes["editorial_review_required"], result.rows)
                self.assertEqual(pending, [existing])
                self.assertIs(pending[0], existing)
                self.assertFalse(changed)
                self.assertEqual(count, 1)

    def test_same_or_newer_pending_version_can_record_changed_abstract(self):
        prior = primary_abstract()
        existing = refresh.primary_review_candidate(prior, primary_abstract(version=3))
        previous = {"editorial_refresh_candidates": [existing]}
        for version in (3, 4):
            with self.subTest(version=version):
                incoming = refresh.primary_review_candidate(prior, primary_abstract(version=version, abstract=ABSTRACT + "Changed."))
                pending, changed, count = refresh.pending_reviews(previous, [incoming], [prior])
                self.assertEqual(pending, [incoming])
                self.assertTrue(changed)
                self.assertEqual(count, 1)

    def test_page_version_mismatch_and_failed_latest_probe_preserve_existing_evidence(self):
        prior = primary_abstract()
        fetcher = Mock()
        def response(target):
            if target.endswith("v2"):
                return arxiv_page(3), target, "text/html"
            raise refresh.FetchError("network_failure")
        fetcher.fetch.side_effect = response
        scan, observations = self.scan(fetcher, prior)
        self.assertEqual(observations, [])
        self.assertEqual(len(scan.errors), 2)
        self.assertIn("arxiv_version_mismatch", scan.errors[0]["code"])
        old = ledger(prior)
        result, changes = refresh.merge_records(old, observations)
        self.assertEqual(result.lines, old.lines)
        self.assertFalse(changes["added"] or changes["changed"])


class MalformedPinnedPageTests(unittest.TestCase):
    """Malformed fetched HTML is one document error, never an aborted scan."""
    PROSE = b"Typed decision models require careful probability calibration and reliable evaluation. " * 8

    def scan(self, pinned_page):
        prior = primary_abstract()
        other = "https://example.org/other-source"
        seeds = {
            prior["url"]: {"url": prior["url"], "title": prior["title"], "topic": "research-paper", "relation": "direct",
                           "relevance": "Fixture paper.", "discovery_depth": 0, "fetch_url": prior["reviewed_version_url"],
                           "discovered_from": [refresh.CURATED_PAPERS_ORIGIN]},
            other: {"url": other, "title": "Other source", "topic": "research-paper", "relation": "adjacent",
                    "relevance": "Fixture source.", "discovery_depth": 0, "discovered_from": [refresh.CURATED_PAPERS_ORIGIN]},
        }
        fetcher = Mock()
        fetcher.fetch.side_effect = lambda target: ((pinned_page if "arxiv.org" in target else b"<html><p>" + self.PROSE + b"</p></html>"),
                                                    target, "text/html")
        scan = refresh.Scan(fetcher, curated_seeds=seeds, pinned_sources={prior["url"]: prior})
        with patch.object(scan, "discover_index", return_value=([], {})), contextlib.redirect_stdout(io.StringIO()):
            records = scan.scan_ecosystem(ledger())
        return scan, records, other

    def test_valueless_attributes_do_not_break_the_abstract_parser(self):
        parser = refresh.ArxivAbstractPage()
        parser.feed('<td class>x</td><blockquote class>y</blockquote><meta name="citation_date" content>')
        self.assertEqual((parser.parts, parser.version, parser.published_at), ([], None, None))
        parser = refresh.ArxivAbstractPage()
        parser.feed("<td class><a>v9</a></td><blockquote class>noise</blockquote>" + arxiv_page().decode())
        self.assertEqual(parser.version, "https://arxiv.org/abs/2609.10000v2")
        self.assertEqual(parser.published_at, "2026-09-01")
        self.assertIn("Typed decisions require", " ".join(parser.parts))

    def test_malformed_pinned_page_is_a_document_error_and_scan_continues(self):
        scan, records, other = self.scan(b"<html><blockquote class>" + self.PROSE + b"</blockquote></html>")
        self.assertEqual([r["url"] for r in records], [other])
        self.assertEqual({e["code"] for e in scan.errors}, {"pinned_paper_observation_failed:invalid_arxiv_abstract_page"})

    def test_other_attribute_errors_stay_contained_to_one_document(self):
        with patch.object(refresh.ArxivAbstractPage, "handle_starttag", side_effect=AttributeError("fixture")):
            scan, records, other = self.scan(arxiv_page())
        self.assertEqual([r["url"] for r in records], [other])
        self.assertEqual({e["code"] for e in scan.errors}, {"pinned_paper_observation_failed:AttributeError"})
        original = refresh.ecosystem.audit
        def audit(seed):
            if seed["url"] == other:
                raise AttributeError("fixture")
            return original(seed)
        with patch.object(refresh.ecosystem, "audit", side_effect=audit):
            scan, records, _ = self.scan(arxiv_page())
        self.assertEqual({r["observed_version_url"] for r in records}, {"https://arxiv.org/abs/2609.10000v2"})
        self.assertEqual(scan.errors, [{"url": other, "code": "document_failed:AttributeError"}])


class PublicFetchTests(unittest.TestCase):
    def test_discovery_excludes_inference_api_and_normalizes_acl_pdf(self):
        with self.assertRaises(refresh.FetchError):
            refresh.canonical_source("https://api.codiv.ai/v1/systemone")
        self.assertEqual(refresh.canonical_source("https://aclanthology.org/2025.gem-1.63.pdf"), "https://aclanthology.org/2025.gem-1.63")

    def test_invalid_protocol_private_ip_and_credential_urls_are_rejected(self):
        credentials = "https://" + "fixture-user" + ":" + "fixture-password" + "@example.org/source"
        for url in ["file:///fixture", "ftp://example.org/a", "http://127.0.0.1/a", "https://[::1]/a", "http://example.internal/a", "https://example.org/?token=fixture", credentials]:
            with self.subTest(url=url.split(":", 1)[0]):
                with self.assertRaises(refresh.FetchError):
                    refresh.public_url(url)

    def test_redirect_to_private_address_is_rejected_before_second_request(self):
        client = refresh.PublicFetcher()
        with patch.object(client, "_request", return_value=(302, {"location": "http://127.0.0.1/private"}, b"")) as request:
            with self.assertRaises(refresh.FetchError):
                client.fetch("https://example.org/source")
            self.assertEqual(request.call_count, 1)

    def test_mixed_public_private_dns_rejected_before_connection(self):
        answers = [(2, 1, 6, "", ("93.184.216.34", 443)), (2, 1, 6, "", ("127.0.0.1", 443))]
        with patch.object(refresh.socket, "getaddrinfo", return_value=answers), patch.object(refresh.http.client, "HTTPSConnection") as connection:
            with self.assertRaises(refresh.FetchError):
                refresh.PublicFetcher()._request("https://example.org/source")
            connection.assert_not_called()

    def test_connection_pins_public_ip_but_retains_tls_hostname(self):
        response = Mock(status=200)
        response.getheaders.return_value = [("Content-Type", "text/plain")]
        response.read.return_value = b"public fixture"
        connection = Mock()
        connection.getresponse.return_value = response
        connection.request.side_effect = lambda *a, **k: connection._create_connection(("ignored.example", 443), 18)
        with patch.object(refresh, "public_addresses", return_value=["93.184.216.34"]), patch.object(refresh.http.client, "HTTPSConnection", return_value=connection) as https, patch.object(refresh.socket, "create_connection") as socket_connect:
            refresh.PublicFetcher()._request("https://example.org/source")
            self.assertEqual(https.call_args.args[:2], ("example.org", 443))
            self.assertEqual(socket_connect.call_args.args[0], ("93.184.216.34", 443))

    def test_retry_backoff_accepts_transient_failure_without_exposing_response(self):
        client = refresh.PublicFetcher(retries=2)
        replies = [(429, {"retry-after": "0"}, b""), (503, {}, b""), (200, {"content-type": "text/plain"}, b"ok")]
        with patch.object(client, "_request", side_effect=replies) as request, patch.object(refresh.time, "sleep"):
            self.assertEqual(client.fetch("https://example.org/source")[0], b"ok")
            self.assertEqual(request.call_count, 3)

    def test_body_cache_has_total_byte_budget(self):
        client = refresh.PublicFetcher(cache_bytes=5)
        with patch.object(client, "_request", return_value=(200, {}, b"four")):
            client.fetch("https://example.org/a")
            client.fetch("https://example.org/b")
        self.assertLessEqual(client.cached_bytes, 5)
        self.assertEqual(list(client.cache), ["https://example.org/b"])

    def test_biomedical_jev_is_not_direct_ai_research(self):
        self.assertFalse(refresh.direct_paper("Japanese encephalitis virus (JEV)", "A neural model supports clinical decisions using JEV infection probabilities."))
        self.assertTrue(refresh.direct_paper("Jev evaluation", "TypeSafe's typed decision model is evaluated for probability calibration."))


class PinnedAddressFallbackTests(unittest.TestCase):
    """Every validated DNS answer is dialled in order; none is resolved again."""
    ANSWERS = [(10, 1, 6, "", ("2606:4700::1", 443, 0, 0)), (2, 1, 6, "", ("93.184.216.34", 443))]

    def connection(self):
        response = Mock(status=200)
        response.getheaders.return_value = [("Content-Type", "text/plain")]
        response.read.return_value = b"public fixture"
        connection = Mock()
        connection.getresponse.return_value = response
        connection.request.side_effect = lambda *a, **k: connection._create_connection(("ignored.example", 443), 18)
        return connection

    def dial(self, reachable=()):
        targets = []
        def connect(address, timeout, source_address=None):
            targets.append(address)
            if address[0] not in reachable:
                raise OSError("fixture unreachable")
            return Mock()
        return targets, connect

    def test_unreachable_first_address_falls_back_to_next_validated_address(self):
        targets, connect = self.dial(reachable={"93.184.216.34"})
        with patch.object(refresh.socket, "getaddrinfo", return_value=self.ANSWERS), patch.object(refresh.http.client, "HTTPSConnection", return_value=self.connection()) as https, patch.object(refresh.socket, "create_connection", side_effect=connect):
            status, _, body = refresh.PublicFetcher()._request("https://example.org/source")
        self.assertEqual((status, body), (200, b"public fixture"))
        self.assertEqual(https.call_args.args[:2], ("example.org", 443))
        self.assertEqual(targets, [("2606:4700::1", 443), ("93.184.216.34", 443)])

    def test_all_unreachable_addresses_are_tried_before_network_failure(self):
        targets, connect = self.dial()
        with patch.object(refresh.socket, "getaddrinfo", return_value=self.ANSWERS), patch.object(refresh.http.client, "HTTPSConnection", return_value=self.connection()), patch.object(refresh.socket, "create_connection", side_effect=connect):
            with self.assertRaises(refresh.FetchError) as raised:
                refresh.PublicFetcher(retries=0).fetch("https://example.org/source")
        self.assertEqual(str(raised.exception), "network_failure")
        self.assertEqual(targets, [("2606:4700::1", 443), ("93.184.216.34", 443)])

    def test_fallback_never_dials_an_unvalidated_address(self):
        targets, connect = self.dial()
        with patch.object(refresh, "public_addresses", return_value=["2606:4700::1", "127.0.0.1"]), patch.object(refresh.http.client, "HTTPSConnection", return_value=self.connection()), patch.object(refresh.socket, "create_connection", side_effect=connect):
            with self.assertRaises(refresh.FetchError) as raised:
                refresh.PublicFetcher()._request("https://example.org/source")
        self.assertEqual(str(raised.exception), "dns_non_public_address")
        self.assertEqual(targets, [("2606:4700::1", 443)])


class RefreshRunTests(unittest.TestCase):
    def test_new_direct_paper_satisfies_the_public_ledger_schema(self):
        scan = refresh.Scan(refresh.PublicFetcher())
        abstract = "TypeSafe Jev is a typed decision model. " + "This synthetic fixture discusses probability calibration and model evaluation. " * 5
        wrapper = {"data": [{"paper": {"id": "2609.12345", "title": "Jev calibration fixture", "summary": abstract, "authors": [{"name": "Fixture Author"}]}}], "retrieved_at": "2026-10-15T00:00:00Z", "retrieval_url": "https://huggingface.co/api/papers/search?q=Jev", "provider": "huggingface_papers_api", "http_status": 200}
        with patch.object(scan, "query", side_effect=lambda topic, q, provider: (topic, q, wrapper)), patch.object(scan, "scan_arxiv", return_value=[]):
            _, direct = scan.scan_research(smoke=True)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "sources.jsonl"
            path.write_text(json.dumps(direct[0]) + "\n")
            with patch.object(validate, "ROOT", Path(tmp)), patch.object(validate, "errors", []) as errors:
                validate.check_ledger(path)
                self.assertEqual(errors, [])

    def test_all_provider_failures_return_failure_and_preserve_previous_ledger(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "data").mkdir()
            original = "".join(ledger(row()).lines)
            (root / "data/ecosystem-sources.jsonl").write_bytes(original.encode())
            (root / "data/research-sources.jsonl").write_text("")
            (root / "data/source-counts.json").write_text(json.dumps({"counts": {"checked_sources": 1}}))
            catalog(root)
            with patch.object(refresh, "ROOT", root), patch.object(refresh.Scan, "scan_ecosystem", return_value=[]), patch.object(refresh.Scan, "scan_research", return_value=([], [])), patch.object(refresh.subprocess, "run"), patch.dict(refresh.os.environ, {}, clear=True), contextlib.redirect_stdout(io.StringIO()):
                code = refresh.main([])
            report = json.loads((root / "data/scan-latest.json").read_text())
            self.assertEqual(code, 1)
            self.assertEqual(report["status"], "failed")
            self.assertFalse(report["changed"])
            self.assertEqual((root / "data/ecosystem-sources.jsonl").read_bytes(), original.encode())

    def test_smoke_does_not_write_ledgers_or_report_or_build_index(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "data").mkdir()
            (root / "data/source-counts.json").write_text(json.dumps({"counts": {}}))
            catalog(root)
            with patch.object(refresh, "ROOT", root), patch.object(refresh.Scan, "scan_ecosystem", return_value=[row()]), patch.object(refresh.Scan, "scan_research", return_value=([], [])), patch.object(refresh.subprocess, "run") as build, patch.dict(refresh.os.environ, {}, clear=True), contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(refresh.main(["--smoke"]), 0)
            build.assert_not_called()
            self.assertFalse((root / "data/scan-latest.json").exists())
            self.assertFalse((root / "data/ecosystem-sources.jsonl").exists())


class RetryAfterTests(unittest.TestCase):
    """Fetchers wait for the server's Retry-After, in seconds or as an HTTP-date, within a budget."""

    def fetch(self, *replies):
        client = refresh.PublicFetcher(retries=2)
        sleeps = []
        replies = list(replies) + [replies[-1]] * 3
        with patch.object(client, "_request", side_effect=replies) as request, patch.object(refresh.time, "sleep", side_effect=sleeps.append):
            try:
                result = client.fetch("https://example.org/source")[0]
            except refresh.FetchError as error:
                result = str(error)
        return result, sleeps, request.call_count

    def http_date(self, seconds):
        import email.utils
        from datetime import timedelta
        return email.utils.format_datetime(refresh.datetime.now(refresh.timezone.utc) + timedelta(seconds=seconds), usegmt=True)

    def test_retry_after_value_is_parsed_as_seconds_or_http_date(self):
        current = refresh.datetime(2026, 10, 16, 9, 9, tzinfo=refresh.timezone.utc)
        cases = {"60": 60, " 7 ": 7, "0": 0, "Fri, 16 Oct 2026 09:10:00 GMT": 60, "Friday, 16-Oct-26 09:10:00 GMT": 60,
                 "Thu, 15 Oct 2026 09:10:00 GMT": 0, "9" * 20: float("inf"), "": None, "-1": None, "1.5": None, "soon": None}
        for value, expected in cases.items():
            with self.subTest(value=value):
                self.assertEqual(refresh.research.retry_after_seconds(value, current), expected)
        self.assertIsNone(refresh.research.retry_after_seconds(None, current))

    def test_requested_delay_within_budget_is_honoured(self):
        limited = (429, {"retry-after": "60"}, b"")
        self.assertEqual(self.fetch(limited), ("http_429", [60, 60], 3))
        self.assertEqual(self.fetch(limited, (200, {"content-type": "text/plain"}, b"ok")), (b"ok", [60], 2))
        result, sleeps, requests = self.fetch((503, {"retry-after": self.http_date(30)}, b""))
        self.assertEqual((result, requests), ("http_503", 3))
        self.assertEqual(len(sleeps), 2)
        self.assertTrue(all(28 <= delay <= 30 for delay in sleeps), sleeps)
        # Without a usable header the bounded exponential backoff is unchanged.
        self.assertEqual(self.fetch((429, {"retry-after": "soon"}, b"")), ("http_429", [1, 2], 3))

    def test_delay_beyond_budget_stops_without_another_request(self):
        for value in ("120", self.http_date(3600)):
            with self.subTest(value=value):
                self.assertEqual(self.fetch((429, {"retry-after": value}, b"")), ("retry_after_exceeded", [], 1))
        self.assertEqual(refresh.safe_exception_code(refresh.FetchError("retry_after_exceeded")), "retry_after_exceeded")

    def test_research_collector_uses_the_same_retry_after_rules(self):
        import urllib.error
        collect = refresh.research
        for value, expected_sleeps, expected_calls, expected_error in (
                ("45", [45, 45, 45], 4, "HTTP Error 429: Too Many Requests"),
                ("120", [], 1, "retry_after_exceeded")):
            with self.subTest(value=value), tempfile.TemporaryDirectory() as tmp:
                collector = collect.Collector(Path(tmp) / "cache", workers=1)
                error = urllib.error.HTTPError(collect.API, 429, "Too Many Requests", {"Retry-After": value}, None)
                sleeps = []
                # Advance the pacing clock so only Retry-After waits are recorded.
                with patch.object(collect.urllib.request, "urlopen", side_effect=error) as urlopen, patch.object(collect.time, "sleep", side_effect=sleeps.append), patch.object(collect.time, "monotonic", side_effect=range(0, 1000, 10)):
                    _, _, result = collector.fetch("direct", "Jev")
                self.assertEqual(sleeps, expected_sleeps)
                self.assertEqual(urlopen.call_count, expected_calls)
                self.assertEqual((result["retrieval_status"], result["error"]), ("failed", expected_error))


class RetryBudgetTests(unittest.TestCase):
    """Retry-After waits share a per-host not-before time and a scan-wide deadline (#204)."""

    def setUp(self):
        self.clock, self.sleeps, self.requests = [1000.0], [], []
        patcher = patch.multiple(refresh.time, monotonic=lambda: self.clock[0], sleep=self.sleep)
        patcher.start()
        self.addCleanup(patcher.stop)
        self.during_first_wait = lambda: None

    def sleep(self, seconds):
        start = self.clock[0]
        self.sleeps.append(seconds)
        if len(self.sleeps) == 1:
            self.during_first_wait()
        self.clock[0] = max(self.clock[0], start + seconds)

    def client(self, replies, **options):
        client = refresh.PublicFetcher(**options)

        def request(url):
            self.requests.append((url, self.clock[0] - 1000))
            return replies[url].pop(0)
        client._request = request
        return client

    def test_other_workers_wait_for_a_host_that_asked_for_a_delay(self):
        ok = (200, {"content-type": "text/plain"}, b"ok")
        client = self.client({"https://example.org/a": [(429, {"retry-after": "30"}, b""), ok],
                              "https://example.org/b": [ok], "https://example.com/c": [ok]})

        def other_workers():  # 5 s into the first worker's wait
            self.clock[0] += 5
            client.fetch("https://example.com/c")
            client.fetch("https://example.org/b")
        self.during_first_wait = other_workers
        self.assertEqual(client.fetch("https://example.org/a")[0], b"ok")
        self.assertEqual(self.requests, [("https://example.org/a", 0), ("https://example.com/c", 5),
                                         ("https://example.org/b", 30), ("https://example.org/a", 30)])
        self.assertEqual(self.sleeps, [30, 25])
        self.assertFalse(client.budget_exhausted)

    def test_scan_deadline_stops_waits_and_new_requests(self):
        limited = (429, {"retry-after": "60"}, b"")
        client = self.client({"https://example.org/a": [limited] * 3, "https://example.org/b": [],
                              "https://example.com/c": []}, budget=100)
        with self.assertRaisesRegex(refresh.FetchError, "^retry_budget_exhausted$"):
            client.fetch("https://example.org/a")
        # The second 60 s wait would end after the deadline: no sleep, no third request.
        self.assertEqual((self.sleeps, len(self.requests)), ([60], 2))
        self.assertTrue(client.budget_exhausted)
        self.clock[0] = 1000 + 100
        for url in ("https://example.org/b", "https://example.com/c"):
            with self.subTest(url=url), self.assertRaisesRegex(refresh.FetchError, "^retry_budget_exhausted$"):
                client.fetch(url)
        self.assertEqual(len(self.requests), 2)
        self.assertEqual(refresh.safe_exception_code(refresh.FetchError("retry_budget_exhausted")), "retry_budget_exhausted")

    def test_plain_backoff_holds_only_the_failing_request(self):
        # Only a host that signalled rate limiting (429 or Retry-After) holds
        # every worker; a 5xx without Retry-After delays just its own retry.
        ok = (200, {"content-type": "text/plain"}, b"ok")
        for status, b_sent, sleeps in ((503, 0.5, [1]), (429, 1, [1, 0.5])):
            with self.subTest(status=status):
                self.clock[0], self.sleeps[:], self.requests[:] = 1000.0, [], []
                client = self.client({"https://example.org/a": [(status, {}, b""), ok], "https://example.org/b": [ok]})

                def other_worker():  # 0.5 s into the first worker's backoff
                    self.clock[0] += 0.5
                    client.fetch("https://example.org/b")
                self.during_first_wait = other_worker
                self.assertEqual(client.fetch("https://example.org/a")[0], b"ok")
                self.assertEqual(self.requests, [("https://example.org/a", 0), ("https://example.org/b", b_sent),
                                                 ("https://example.org/a", 1)])
                self.assertEqual(self.sleeps, sleeps)

    def test_each_phase_has_its_own_share_of_the_deadline(self):
        ok = (200, {"content-type": "text/plain"}, b"ok")
        limited = (429, {"retry-after": "60"}, b"")
        client = self.client({"https://example.org/a": [limited] * 3, "https://example.com/c": [ok]}, budget=100)
        client.begin_phase("ecosystem", 70)
        with self.assertRaisesRegex(refresh.FetchError, "^retry_budget_exhausted$"):
            client.fetch("https://example.org/a")
        # The second 60 s wait would end after the ecosystem share; research,
        # which starts at 60 s, still has its full 30 s and more of the total.
        client.begin_phase("research", 30)
        self.assertEqual(client.deadline, 1000 + 100)
        self.assertEqual(client.fetch("https://example.com/c")[0], b"ok")
        self.assertEqual(client.exhausted_phases, ["ecosystem"])
        # A phase that overran its share still leaves the next one its own.
        self.clock[0] = 1000.0
        late = self.client({}, budget=100)
        late.begin_phase("ecosystem", 70)
        self.clock[0] = 1000 + 95
        late.begin_phase("research", 30)
        self.assertEqual(late.deadline, 1000 + 95 + 30)

    def test_slow_ecosystem_phase_does_not_fail_the_research_queries(self):
        def scan_ecosystem(scan, *args):
            # The ecosystem phase used the whole scan-wide budget.
            self.clock[0] = 1000 + refresh.SCAN_TIME_BUDGET_SECONDS + 1
            with self.assertRaisesRegex(refresh.FetchError, "^retry_budget_exhausted$"):
                scan.fetcher._hold("example.org")
            return [row()]

        def scan_research(scan, *args):
            phases.append(scan.fetcher.phase)
            scan.fetcher._hold("huggingface.co")  # research APIs are still contacted
            scan.successful_queries += 1
            return [], []
        phases = []
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "data").mkdir()
            (root / "data/ecosystem-sources.jsonl").write_bytes("".join(ledger(row()).lines).encode())
            (root / "data/research-sources.jsonl").write_text("")
            (root / "data/source-counts.json").write_text(json.dumps({"counts": {"checked_sources": 1}}))
            (root / "summary.md").write_text("")
            catalog(root)
            with patch.object(refresh, "ROOT", root), patch.object(refresh.Scan, "scan_ecosystem", scan_ecosystem), \
                    patch.object(refresh.Scan, "scan_research", scan_research), patch.object(refresh.subprocess, "run"), \
                    patch.dict(refresh.os.environ, {"GITHUB_STEP_SUMMARY": str(root / "summary.md")}, clear=True), \
                    contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(refresh.main([]), 0)
            report = json.loads((root / "data/scan-latest.json").read_text())
            summary = (root / "summary.md").read_text()
        self.assertEqual(phases, ["research"])
        self.assertEqual((report["status"], report["retry_budget_exhausted"]), ("partial", True))
        self.assertEqual(report["retry_budget_exhausted_phases"], ["ecosystem"])
        self.assertEqual(report["phase_budget_seconds"], refresh.PHASE_TIME_BUDGET_SECONDS)
        self.assertIn("exhausted in the ecosystem phase", summary)

    def test_default_budget_is_conservative_and_leaves_time_for_the_job(self):
        self.assertEqual(refresh.SCAN_TIME_BUDGET_SECONDS, 18 * 60)
        self.assertEqual(set(refresh.PHASE_TIME_BUDGET_SECONDS), {"ecosystem", "research"})
        self.assertEqual(refresh.PublicFetcher().deadline, 1000 + refresh.SCAN_TIME_BUDGET_SECONDS)
        workflow = (refresh.ROOT / ".github/workflows/scan-sources.yml").read_text(encoding="utf-8")
        job_minutes = int(workflow.split("timeout-minutes:", 1)[1].split()[0])
        self.assertLessEqual(refresh.SCAN_TIME_BUDGET_SECONDS, (job_minutes - 5) * 60)

    def test_scan_report_records_an_exhausted_budget(self):
        summary = {}
        for exhausted in (False, True):
            def scan_ecosystem(scan, *args):
                scan.fetcher.budget_exhausted = exhausted
                return [row()]
            with tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                (root / "data").mkdir()
                (root / "data/ecosystem-sources.jsonl").write_bytes("".join(ledger(row()).lines).encode())
                (root / "data/research-sources.jsonl").write_text("")
                (root / "data/source-counts.json").write_text(json.dumps({"counts": {"checked_sources": 1}}))
                (root / "summary.md").write_text("")
                catalog(root)
                with patch.object(refresh, "ROOT", root), patch.object(refresh.Scan, "scan_ecosystem", scan_ecosystem), \
                        patch.object(refresh.Scan, "scan_research", return_value=([], [])), patch.object(refresh.subprocess, "run"), \
                        patch.dict(refresh.os.environ, {"GITHUB_STEP_SUMMARY": str(root / "summary.md")}, clear=True), \
                        contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(refresh.main([]), 0)
                report = json.loads((root / "data/scan-latest.json").read_text())
                summary[exhausted] = (root / "summary.md").read_text()
            with self.subTest(exhausted=exhausted):
                self.assertIs(report["retry_budget_exhausted"], exhausted)
                self.assertEqual(report["retry_budget_seconds"], refresh.SCAN_TIME_BUDGET_SECONDS)
                self.assertEqual(report["status"], "partial" if exhausted else "success")
        self.assertIn("retry budget", summary[True].lower())
        self.assertNotIn("retry budget", summary[False].lower())


if __name__ == "__main__":
    unittest.main()
