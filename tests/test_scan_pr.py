"""Security and idempotence checks for the scan-to-PR publication boundary."""

import http.client
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts import open_scan_pr as scan
from scripts.source_policy import SourcePolicy


IDENTITY = {"repository": scan.REPOSITORY, "base_sha": "a" * 40, "run_id": "123", "run_attempt": "1"}
OLD_SHA = "b" * 40


def files(retrieved_at="2026-10-15T00:00:00Z", content="public evidence"):
    row = {"url": "https://example.org/source", "title": "Synthetic source", "retrieved_at": retrieved_at, "evidence": content}
    data = {name: b"{}\n" for name in scan.ALLOWED}
    for name in scan.LEDGERS:
        data[name] = (json.dumps(row) + "\n").encode()
    data["data/scan-latest.json"] = json.dumps({"status": "success", "changed": True, "added_count": 1, "changed_count": 0}).encode()
    return data


def pinned_paper_files(version="v2", abstract="b" * 64, pending_version=None):
    data = files()
    url = "https://arxiv.org/abs/2609.10000"
    row = {"url": url, "title": "Pinned primary abstract", "verification_level": "abstract_checked",
           "abstract_sha256": abstract, "abstract_page_sha256": "c" * 64,
           "reviewed_version_url": url + version}
    data[scan.LEDGERS[0]] = b""
    data[scan.LEDGERS[1]] = (json.dumps(row) + "\n").encode()
    report = json.loads(data[scan.REPORT])
    report["editorial_refresh_candidates"] = []
    if pending_version:
        report["editorial_refresh_candidates"] = [{
            "url": url, "review_kind": "pinned_arxiv_abstract", "old_content_sha256": abstract,
            "observed_content_sha256": abstract, "observed_abstract_sha256": abstract,
            "old_reviewed_version_url": url + version, "observed_version_url": url + pending_version,
            "observed_verification_level": "abstract_checked", "retrieved_url": url,
            "note": "Pinned evidence awaits review.",
        }]
    data[scan.REPORT] = json.dumps(report).encode()
    return data


def artifact(directory, payload, identity=IDENTITY):
    manifest = {"format": 1, **identity, "changed": True, "files": {}}
    for name, data in payload.items():
        path = directory / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        manifest["files"][name] = {"sha256": scan.digest(data), "bytes": len(data)}
    (directory / "manifest.json").write_text(json.dumps(manifest))


class FakeGitHub:
    """No network; unexpected API writes fail the test."""

    def __init__(self, previous=False, opened=False, closed=False, owner=scan.BOT, main_sha=IDENTITY["base_sha"]):
        self.previous, self.opened, self.closed, self.owner, self.main_sha = previous, opened, closed, owner, main_sha
        self.calls = []

    def request(self, method, endpoint, data=None, optional=False):
        self.calls.append((method, endpoint, data))
        if method == "GET":
            if endpoint == "/git/ref/heads/main":
                return {"object": {"sha": self.main_sha}}
            if endpoint == "/git/ref/heads/" + scan.BRANCH:
                return {"object": {"sha": OLD_SHA}} if self.previous else None
            if endpoint.startswith("/pulls?"):
                if "state=closed" in endpoint:
                    return [{"number": 7, "merged_at": None}] if self.closed else []
                return [{"number": 7, "user": {"login": scan.BOT}, "body": scan.MARKER}] if self.opened else []
            if endpoint == "/commits/" + OLD_SHA:
                return {"committer": {"login": self.owner}, "commit": {"message": scan.TITLE}}
            if endpoint == "/git/commits/" + IDENTITY["base_sha"]:
                return {"tree": {"sha": "d" * 40}}
        if method == "POST" and endpoint in {"/git/blobs", "/git/trees", "/git/commits"}:
            return {"sha": "c" * 40}
        if method == "POST" and endpoint == "/git/refs":
            return {"ref": data["ref"]}
        if method == "PATCH" and endpoint == "/git/refs/heads/" + scan.BRANCH:
            return {"ref": "refs/heads/" + scan.BRANCH}
        if (method, endpoint) in {("POST", "/pulls"), ("PATCH", "/pulls/7")}:
            return {"html_url": "https://github.com/" + scan.REPOSITORY + "/pull/7"}
        raise AssertionError("Unexpected API operation: " + method + " " + endpoint)


class ArtifactBoundaryTests(unittest.TestCase):
    def test_pinned_version_changes_are_substantive_even_when_abstract_and_note_match(self):
        previous = pinned_paper_files(pending_version="v3")
        updated = pinned_paper_files(pending_version="v4")
        self.assertNotEqual(scan.meaningful_fingerprint(previous), scan.meaningful_fingerprint(updated))
        report = json.loads(updated[scan.REPORT])
        report["completed_at"] = "2026-10-20T00:00:00Z"
        report["editorial_refresh_candidates"][0]["retrieved_at"] = "2026-10-20T00:00:00Z"
        updated[scan.REPORT] = json.dumps(report).encode()
        self.assertEqual(scan.meaningful_fingerprint(pinned_paper_files(pending_version="v4")),
                         scan.meaningful_fingerprint(updated))

    def test_timestamp_only_changes_do_not_create_substantive_updates(self):
        self.assertEqual(scan.meaningful_fingerprint(files()), scan.meaningful_fingerprint(files("2026-10-16T00:00:00Z")))
        self.assertNotEqual(scan.meaningful_fingerprint(files()), scan.meaningful_fingerprint(files(content="changed public evidence")))

    def test_editorial_only_hash_changes_are_substantive_without_clock_churn(self):
        baseline = files()
        candidate = files()
        report = json.loads(candidate[scan.REPORT])
        report["editorial_refresh_candidates"] = [{"url": "https://example.org/source", "old_content_sha256": "a" * 64, "observed_content_sha256": "b" * 64, "retrieved_at": "2026-10-15T00:00:00Z"}]
        candidate[scan.REPORT] = json.dumps(report).encode()
        self.assertNotEqual(scan.meaningful_fingerprint(baseline), scan.meaningful_fingerprint(candidate))
        first = scan.meaningful_fingerprint(candidate)
        report["started_at"] = "2026-10-16T00:00:00Z"
        report["editorial_refresh_candidates"][0]["retrieved_at"] = "2026-10-16T00:00:00Z"
        candidate[scan.REPORT] = json.dumps(report).encode()
        self.assertEqual(first, scan.meaningful_fingerprint(candidate))
        without_report = {name: value for name, value in baseline.items() if name != scan.REPORT}
        self.assertEqual(scan.meaningful_fingerprint(without_report), scan.meaningful_fingerprint(baseline))

    def test_manifest_is_bound_to_run_and_source_commit(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            artifact(directory, files())
            _, loaded = scan.load_bundle(directory, IDENTITY)
            self.assertEqual(set(loaded), set(scan.ALLOWED))
            for key, value in (("run_id", "124"), ("run_attempt", "2"), ("base_sha", "e" * 40)):
                with self.subTest(key=key), self.assertRaises(scan.ScanError):
                    scan.load_bundle(directory, {**IDENTITY, key: value})

    def test_extra_code_file_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            artifact(directory, files())
            (directory / "injected.py").write_text("# Must never cross the artifact boundary\n")
            with self.assertRaises(scan.ScanError):
                scan.load_bundle(directory, IDENTITY)

    def test_symlink_and_hash_mismatch_are_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary) / "bundle"
            directory.mkdir()
            artifact(directory, files())
            target = directory / scan.ALLOWED[0]
            target.write_bytes(target.read_bytes() + b"\n")
            with self.assertRaises(scan.ScanError):
                scan.load_bundle(directory, IDENTITY)
            target.unlink()
            target.symlink_to(Path(temporary) / "elsewhere.jsonl")
            with self.assertRaises(scan.ScanError):
                scan.load_bundle(directory, IDENTITY)


class PublicationTests(unittest.TestCase):
    def test_same_abstract_new_version_in_open_pr_cannot_be_lost_after_failed_probe(self):
        previous = pinned_paper_files(version="v2", pending_version="v3")
        fresh = pinned_paper_files(version="v2")
        report = json.loads(fresh[scan.REPORT])
        report.update(status="partial", error_count=1,
                      errors=[{"url": "https://arxiv.org/abs/2609.10000", "code": "network_failure"}])
        fresh[scan.REPORT] = json.dumps(report).encode()
        with self.assertRaises(scan.ScanError):
            scan.ensure_pending_continuity(previous, fresh)
        # Retaining the unresolved item is valid even if the current scan failed.
        scan.ensure_pending_continuity(previous, pinned_paper_files(version="v2", pending_version="v3"))

    def test_accepting_a_pinned_candidate_requires_both_version_and_evidence(self):
        previous = pinned_paper_files(version="v2", pending_version="v3")
        for version, abstract in (("v2", "b" * 64), ("v3", "d" * 64)):
            with self.subTest(version=version, abstract=abstract), self.assertRaises(scan.ScanError):
                scan.ensure_pending_continuity(previous, pinned_paper_files(version=version, abstract=abstract))
        scan.ensure_pending_continuity(previous, pinned_paper_files(version="v3", abstract="b" * 64))
        accepted = pinned_paper_files(version="v3", abstract="b" * 64)
        row = json.loads(accepted[scan.LEDGERS[1]])
        row["reviewed_version_url"] = "https://arxiv.org/pdf/2609.10000v3.pdf"
        accepted[scan.LEDGERS[1]] = (json.dumps(row) + "\n").encode()
        scan.ensure_pending_continuity(previous, accepted)

    def test_same_url_stale_or_unversioned_queue_cannot_replace_known_pending_version(self):
        previous = pinned_paper_files(version="v2", pending_version="v3")
        for version in (None, "https://arxiv.org/abs/2609.10000v2", "https://arxiv.org/abs/2609.10001v4"):
            fresh = pinned_paper_files(version="v2", pending_version="v2")
            report = json.loads(fresh[scan.REPORT])
            report["editorial_refresh_candidates"][0]["observed_version_url"] = version
            report.update(status="partial", error_count=1)
            fresh[scan.REPORT] = json.dumps(report).encode()
            with self.subTest(version=version), self.assertRaises(scan.ScanError):
                scan.ensure_pending_continuity(previous, fresh)
            # A stale queue may remain only once the known v3 evidence was accepted.
            accepted = pinned_paper_files(version="v3")
            accepted[scan.REPORT] = fresh[scan.REPORT]
            scan.ensure_pending_continuity(previous, accepted)

    def test_same_or_newer_known_pending_version_can_update_its_evidence(self):
        previous = pinned_paper_files(version="v2", pending_version="v3")
        for version in ("v3", "v4", "v10"):
            fresh = pinned_paper_files(version="v2", pending_version=version)
            report = json.loads(fresh[scan.REPORT])
            candidate = report["editorial_refresh_candidates"][0]
            candidate["observed_abstract_sha256"] = candidate["observed_content_sha256"] = "d" * 64
            fresh[scan.REPORT] = json.dumps(report).encode()
            with self.subTest(version=version):
                scan.ensure_pending_continuity(previous, fresh)

    def test_ordinary_editorial_same_url_queue_replacement_remains_allowed(self):
        previous, fresh = files(), files()
        for payload, observed in ((previous, "b" * 64), (fresh, "c" * 64)):
            report = json.loads(payload[scan.REPORT])
            report["editorial_refresh_candidates"] = [{"url": "https://example.org/source", "observed_content_sha256": observed}]
            payload[scan.REPORT] = json.dumps(report).encode()
        scan.ensure_pending_continuity(previous, fresh)

    def test_main_advance_or_human_branch_edits_prevent_writes(self):
        for api in (FakeGitHub(main_sha="f" * 40), FakeGitHub(previous=True, owner="fixture-maintainer")):
            with self.subTest(api=api), self.assertRaises(scan.ScanError):
                scan.publish(api, IDENTITY, files())
            self.assertTrue(all(method == "GET" for method, _, _ in api.calls))

    def test_identical_pending_or_declined_update_is_not_reposted(self):
        for api in (FakeGitHub(previous=True, opened=True), FakeGitHub(previous=True, closed=True)):
            with self.subTest(api=api), patch.object(scan, "remote_comparison_files", return_value=files()):
                scan.publish(api, IDENTITY, files("2026-10-16T00:00:00Z"))
                self.assertTrue(all(method == "GET" for method, _, _ in api.calls))

    def test_new_pr_writes_only_allowlisted_data_to_dedicated_branch(self):
        api = FakeGitHub()
        scan.publish(api, IDENTITY, files())
        tree = next(data for method, endpoint, data in api.calls if (method, endpoint) == ("POST", "/git/trees"))
        self.assertEqual({row["path"] for row in tree["tree"]}, set(scan.ALLOWED))
        refs = [data for method, endpoint, data in api.calls if (method, endpoint) == ("POST", "/git/refs")]
        self.assertEqual(refs, [{"ref": "refs/heads/" + scan.BRANCH, "sha": "c" * 40}])
        pr = next(data for method, endpoint, data in api.calls if (method, endpoint) == ("POST", "/pulls"))
        self.assertEqual(pr["base"], "main")
        self.assertIn("/actions/runs/123", pr["body"])
        self.assertLessEqual(len(pr["body"]), 6000)
        self.assertNotIn("auto_merge", pr)

    def test_existing_bot_branch_is_updated_without_force_and_pr_is_reused(self):
        api = FakeGitHub(previous=True, opened=True)
        with patch.object(scan, "remote_comparison_files", return_value=files(content="older public evidence")):
            scan.publish(api, IDENTITY, files())
        ref = next(data for method, endpoint, data in api.calls if method == "PATCH" and endpoint.startswith("/git/refs/"))
        self.assertIs(ref["force"], False)
        commit = next(data for method, endpoint, data in api.calls if (method, endpoint) == ("POST", "/git/commits"))
        self.assertEqual(commit["parents"], [OLD_SHA, IDENTITY["base_sha"]])
        self.assertTrue(any(method == "PATCH" and endpoint == "/pulls/7" for method, endpoint, _ in api.calls))
        self.assertFalse(any(method == "POST" and endpoint == "/pulls" for method, endpoint, _ in api.calls))

    def test_open_pr_pending_only_source_cannot_disappear_on_next_scan(self):
        prior = files()
        extra = {"url": "https://example.org/pending-only", "title": "Previously discovered", "verification_level": "content_screened", "content_sha256": "b" * 64}
        prior[scan.LEDGERS[0]] += (json.dumps(extra) + "\n").encode()
        api = FakeGitHub(previous=True, opened=True)
        with patch.object(scan, "remote_comparison_files", return_value=prior), self.assertRaises(scan.ScanError):
            scan.publish(api, IDENTITY, files())
        self.assertTrue(all(method == "GET" for method, _, _ in api.calls))

    def test_pending_evidence_tier_cannot_be_downgraded(self):
        prior, fresh = files(), files()
        for name in scan.LEDGERS:
            row = json.loads(prior[name])
            row["verification_level"] = "content_screened"
            prior[name] = json.dumps(row).encode()
        with self.assertRaises(scan.ScanError):
            scan.ensure_pending_continuity(prior, fresh)

    def test_editorial_pending_loss_requires_acceptance_or_trusted_exclusion(self):
        prior, fresh = files(), files()
        report = json.loads(prior[scan.REPORT])
        report["editorial_refresh_candidates"] = [{"url": "https://example.org/source", "old_content_sha256": "a" * 64, "observed_content_sha256": "b" * 64}]
        prior[scan.REPORT] = json.dumps(report).encode()
        with self.assertRaises(scan.ScanError):
            scan.ensure_pending_continuity(prior, fresh)
        accepted = files()
        for name in scan.LEDGERS:
            row = json.loads(accepted[name])
            row["content_sha256"] = "b" * 64
            accepted[name] = json.dumps(row).encode()
        scan.ensure_pending_continuity(prior, accepted)
        policy = SourcePolicy({"https://example.org/source": {"reason": "Reviewed exclusion"}}, {}, scan.source_index.canonical)
        scan.ensure_pending_continuity(prior, fresh, policy)

    def test_trusted_exclusion_permits_intentional_pending_record_removal(self):
        prior = files()
        extra_url = "https://example.org/pending-only"
        prior[scan.LEDGERS[0]] += (json.dumps({"url": extra_url, "verification_level": "content_screened"}) + "\n").encode()
        policy = SourcePolicy({extra_url: {"reason": "Reviewed out-of-scope source"}}, {}, scan.source_index.canonical)
        scan.ensure_pending_continuity(prior, files(), policy)


class StubResponse:
    def __init__(self, body):
        self.body = body

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def read(self, limit):
        if isinstance(self.body, BaseException):
            raise self.body
        return self.body


class StubOpener:
    """Replays connection outcomes; an exception is raised from open() or read()."""

    def __init__(self, *outcomes):
        self.outcomes, self.calls = list(outcomes), 0

    def open(self, request, timeout):
        self.calls += 1
        outcome = self.outcomes.pop(0)
        if isinstance(outcome, ConnectionError):
            raise outcome
        return StubResponse(outcome)


class NullFieldAndConnectionErrorTests(unittest.TestCase):
    """GitHub nulls and http.client errors must stop with a specific ScanError."""

    def api_returning(self, endpoint, value, **options):
        api = FakeGitHub(**options)
        fallback = api.request

        def request(method, path, data=None, optional=False):
            if method == "GET" and path.startswith(endpoint):
                api.calls.append((method, path, data))
                return value
            return fallback(method, path, data, optional)
        api.request = request
        return api

    def test_unlinked_committer_is_reported_as_non_bot_branch_change(self):
        api = self.api_returning("/commits/" + OLD_SHA, {"committer": None, "commit": {"message": scan.TITLE}}, previous=True)
        with self.assertRaisesRegex(scan.ScanError, "non-bot changes"):
            scan.publish(api, IDENTITY, files())
        self.assertTrue(all(method == "GET" for method, _, _ in api.calls))

    def test_open_pr_with_null_body_or_user_is_refused(self):
        for pull in ({"number": 7, "user": {"login": scan.BOT}, "body": None},
                     {"number": 7, "user": None, "body": scan.MARKER}):
            with self.subTest(pull=pull):
                api = self.api_returning("/pulls?", [pull])
                with self.assertRaisesRegex(scan.ScanError, "non-bot or ambiguous"):
                    scan.publish(api, IDENTITY, files())
                self.assertTrue(all(method == "GET" for method, _, _ in api.calls))

    def request(self, method, *outcomes):
        api = scan.GitHub("fixture-token")
        api.opener = StubOpener(*outcomes)
        with patch.object(scan.time, "sleep"):
            try:
                return api.request(method, "/git/ref/heads/main"), api.opener.calls
            except scan.ScanError as exc:
                self.assertNotIn("fixture-token", str(exc))
                return exc, api.opener.calls

    def test_dropped_connection_on_a_read_is_retried(self):
        result, calls = self.request("GET", http.client.RemoteDisconnected("closed"), b'{"object": {"sha": "fixture"}}')
        self.assertEqual(result, {"object": {"sha": "fixture"}})
        self.assertEqual(calls, 2)

    def test_persistent_http_client_errors_end_in_a_connection_scan_error(self):
        for failure in (http.client.RemoteDisconnected("closed"), ConnectionResetError("reset"),
                        http.client.IncompleteRead(b"{")):
            with self.subTest(failure=type(failure).__name__):
                result, calls = self.request("GET", failure, failure, failure)
                self.assertIsInstance(result, scan.ScanError)
                self.assertIn("connection failed", str(result))
                self.assertEqual(calls, 3)

    def test_write_is_not_retried_after_a_dropped_connection(self):
        result, calls = self.request("POST", http.client.RemoteDisconnected("closed"), b"{}")
        self.assertIsInstance(result, scan.ScanError)
        self.assertIn("connection failed", str(result))
        self.assertEqual(calls, 1)


if __name__ == "__main__":
    unittest.main()
