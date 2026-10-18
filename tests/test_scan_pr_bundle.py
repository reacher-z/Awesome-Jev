"""Artifact creation, restoration and remote-ledger checks on the scan publication boundary, offline."""
import base64
import contextlib
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import Mock, patch
import urllib.error

from scripts import open_scan_pr as scan


IDENTITY = {"repository": scan.REPOSITORY, "base_sha": "a" * 40, "run_id": "123", "run_attempt": "1"}
BRANCH_SHA = "b" * 40
TREE_SHA = "c" * 40
CHANGED = "Source scan: partial; validated source changes found."
UNCHANGED = "No substantive source changes; no PR update. See the collector summary for this run's provider status."
LINKED = "Refusing to restore data through a linked path."


def payload(evidence="public evidence", retrieved_at="2026-10-15T00:00:00Z", status="success", changed=True):
    row = {"url": "https://example.org/source", "title": "Synthetic source", "retrieved_at": retrieved_at, "evidence": evidence}
    data = {name: b"{}\n" for name in scan.ALLOWED}
    for name in scan.LEDGERS:
        data[name] = (json.dumps(row) + "\n").encode()
    data[scan.REPORT] = json.dumps({"status": status, "changed": changed}).encode()
    return data


def write_tree(root, files):
    for name, data in files.items():
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)


def artifact(directory, files, identity=IDENTITY):
    write_tree(directory, files)
    manifest = {"format": 1, **identity, "changed": True,
                "files": {name: {"sha256": scan.digest(data), "bytes": len(data)} for name, data in files.items()}}
    (directory / "manifest.json").write_text(json.dumps(manifest))


def git(root, *args):
    env = {**os.environ, "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1"}
    subprocess.run(["git", "-c", "user.name=Fixture", "-c", "user.email=fixture@example.org",
                    "-c", "commit.gpgsign=false", *args], cwd=root, env=env, check=True, capture_output=True)


class BoundaryCase(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory(prefix="awesome-jev-scan-")
        self.addCleanup(directory.cleanup)
        self.tmp = Path(directory.name).resolve()
        self.root = self.tmp / "repo"
        self.root.mkdir()
        root = patch.object(scan, "ROOT", self.root)
        root.start()
        self.addCleanup(root.stop)

    def assertRefused(self, message, function, *args):
        with self.assertRaises(scan.ScanError) as caught:
            function(*args)
        self.assertEqual(str(caught.exception), message)


@unittest.skipUnless(shutil.which("git"), "git is required to build the base commit")
class BundleTests(BoundaryCase):
    """bundle() against a temporary git checkout whose HEAD is the scan's base commit."""

    def setUp(self):
        super().setUp()
        write_tree(self.root, payload())
        git(self.root, "init", "-q")
        git(self.root, "add", "-A")
        git(self.root, "commit", "-q", "-m", "Base ledgers")
        self.output, self.summary = self.tmp / "github-output", self.tmp / "step-summary"
        # The real runner sets both; never let a test append to the job's own files.
        environment = patch.dict(os.environ, {"GITHUB_OUTPUT": str(self.output), "GITHUB_STEP_SUMMARY": str(self.summary)})
        environment.start()
        self.addCleanup(environment.stop)
        self.directory = self.tmp / "bundle"

    def bundle(self):
        printed = io.StringIO()
        with contextlib.redirect_stdout(printed):
            scan.bundle(self.directory, IDENTITY)
        return self.output.read_text(), self.summary.read_text(), printed.getvalue()

    def test_substantive_change_writes_a_bundle_that_load_bundle_accepts(self):
        working = payload(evidence="updated public evidence", status="partial")
        write_tree(self.root, working)
        self.assertEqual(self.bundle(), ("changed=true\n", CHANGED + "\n", CHANGED + "\n"))
        written = sorted(p.relative_to(self.directory).as_posix() for p in self.directory.rglob("*") if p.is_file())
        self.assertEqual(written, sorted([*scan.ALLOWED, "manifest.json"]))
        manifest = json.loads((self.directory / "manifest.json").read_text())
        self.assertEqual(manifest, {"format": 1, **IDENTITY, "changed": True, "files": {
            name: {"sha256": scan.digest(data), "bytes": len(data)} for name, data in working.items()}})
        _, loaded = scan.load_bundle(self.directory, IDENTITY)
        self.assertEqual(loaded, working)

    def test_clock_only_churn_against_head_is_not_published(self):
        write_tree(self.root, payload(retrieved_at="2026-10-16T12:00:00Z"))
        self.assertEqual(self.bundle()[:2], ("changed=false\n", UNCHANGED + "\n"))
        self.assertFalse(self.directory.exists())

    def test_collector_change_flag_gates_publication(self):
        write_tree(self.root, payload(evidence="updated public evidence", changed=False))
        self.assertEqual(self.bundle()[0], "changed=false\n")
        self.assertFalse(self.directory.exists())

    def test_failed_scan_is_refused_before_any_output(self):
        write_tree(self.root, payload(evidence="updated public evidence", status="failed"))
        self.assertRefused("Collector reported failure; no update will be published.", scan.bundle, self.directory, IDENTITY)
        self.assertFalse(self.output.exists())
        self.assertFalse(self.directory.exists())

    def test_invalid_scan_report_is_refused(self):
        for report in ({"status": "success"}, {"status": "success", "changed": "true"},
                       {"status": "skipped", "changed": True}, {"changed": True}):
            with self.subTest(report=report):
                (self.root / scan.REPORT).write_text(json.dumps(report))
                self.assertRefused("Invalid scan report.", scan.bundle, self.directory, IDENTITY)
        self.assertFalse(self.output.exists())

    def test_existing_bundle_directory_is_refused(self):
        self.directory.mkdir()
        self.assertRefused("Bundle directory must be new.", scan.bundle, self.directory, IDENTITY)

    def test_total_size_budget_is_enforced(self):
        working = payload(evidence="updated public evidence")
        write_tree(self.root, working)
        total = sum(map(len, working.values()))
        with patch.object(scan, "MAX_TOTAL_BYTES", total - 1):
            self.assertRefused("Artifact exceeds the size budget.", scan.bundle, self.directory, IDENTITY)
        self.assertFalse(self.directory.exists())
        with patch.object(scan, "MAX_TOTAL_BYTES", total):
            self.assertEqual(self.bundle()[0], "changed=true\n")

    def test_invalid_or_linked_working_files_are_refused(self):
        invalid, linked = "Artifact contains invalid UTF-8 or JSON data.", "Missing, oversized, or linked source artifact."
        badge = self.root / "site/data/source-badge.json"
        cases = (
            (scan.LEDGERS[0], lambda path: path.write_text('["not", "a", "record"]\n'), invalid),
            ("site/data/source-index.json", lambda path: path.write_bytes(b"\xff{}"), invalid),
            ("site/data/source-badge.json", lambda path: (path.unlink(), path.symlink_to(self.tmp / "badge.json")), linked),
            ("data/source-counts.json", lambda path: path.unlink(), linked),
        )
        (self.tmp / "badge.json").write_text("{}")
        for name, damage, message in cases:
            with self.subTest(file=name):
                write_tree(self.root, payload(evidence="updated public evidence"))
                if badge.is_symlink():
                    badge.unlink()
                write_tree(self.root, {"site/data/source-badge.json": b"{}\n"})
                damage(self.root / name)
                self.assertRefused(message, scan.bundle, self.directory, IDENTITY)
                self.assertFalse(self.directory.exists())

    def test_base_ledgers_are_required_but_a_missing_base_report_is_allowed(self):
        git(self.root, "rm", "-q", "--cached", scan.REPORT)
        git(self.root, "commit", "-q", "-m", "Drop report from base")
        write_tree(self.root, payload(evidence="updated public evidence"))
        self.assertEqual(self.bundle()[0], "changed=true\n")
        shutil.rmtree(self.directory)
        git(self.root, "rm", "-q", "--cached", scan.LEDGERS[1])
        git(self.root, "commit", "-q", "-m", "Drop research ledger from base")
        self.assertRefused("Cannot read the base source ledgers.", scan.bundle, self.directory, IDENTITY)

    def test_summary_without_runner_files_only_prints(self):
        with patch.dict(os.environ):
            os.environ.pop("GITHUB_STEP_SUMMARY")
            printed = io.StringIO()
            with contextlib.redirect_stdout(printed):
                scan.write_summary("Fixture summary")
        self.assertEqual(printed.getvalue(), "Fixture summary\n")
        self.assertFalse(self.summary.exists())


class RestoreTests(BoundaryCase):
    def setUp(self):
        super().setUp()
        self.files = payload(evidence="restored public evidence")
        self.directory = self.tmp / "work/bundle"
        self.directory.mkdir(parents=True)
        artifact(self.directory, self.files)
        self.outside = self.tmp / "outside"
        self.outside.mkdir()

    def restore(self, identity=IDENTITY):
        with contextlib.redirect_stdout(io.StringIO()) as printed:
            scan.restore(self.directory, identity)
        return printed.getvalue()

    def repository_files(self):
        return sorted(p.relative_to(self.root).as_posix() for p in self.root.rglob("*") if p.is_file())

    def test_restore_writes_exactly_the_allowlisted_files(self):
        write_tree(self.root, {name: b"{}\n" for name in scan.ALLOWED})
        self.assertIn("Restored the six allowlisted data files", self.restore())
        self.assertEqual(self.repository_files(), sorted(scan.ALLOWED))
        self.assertEqual({name: (self.root / name).read_bytes() for name in scan.ALLOWED}, self.files)

    def test_bundle_is_verified_before_anything_is_written(self):
        (self.directory / scan.LEDGERS[0]).write_bytes(b"{}\n")
        self.assertRefused("Artifact data does not match its manifest hash.", self.restore)
        self.assertRefused("Artifact does not belong to this workflow run and base commit.", self.restore,
                           {**IDENTITY, "run_attempt": "2"})
        self.assertEqual(self.repository_files(), [])

    def test_linked_data_directory_is_refused(self):
        (self.root / "data").symlink_to(self.outside, target_is_directory=True)
        self.assertRefused(LINKED, self.restore)
        self.assertEqual(list(self.outside.iterdir()), [])

    def test_link_that_stays_inside_the_repository_is_still_refused(self):
        (self.root / "mirror").mkdir()
        (self.root / "site").symlink_to(self.root / "mirror", target_is_directory=True)
        self.assertRefused(LINKED, self.restore)
        self.assertEqual(list((self.root / "mirror").rglob("*")), [])

    def test_linked_target_file_is_refused(self):
        victim = self.outside / "victim.jsonl"
        victim.write_text("keep\n")
        (self.root / "data").mkdir()
        (self.root / scan.LEDGERS[0]).symlink_to(victim)
        self.assertRefused(LINKED, self.restore)
        self.assertEqual(victim.read_text(), "keep\n")

    def test_an_allowlist_entry_resolving_outside_the_repository_is_refused(self):
        # Guards a future allowlist edit: a parent reference must not write beside the checkout.
        escape = "../escape.json"
        (self.directory.parent / "escape.json").write_text("{}\n")
        with patch.object(scan, "ALLOWED", (escape, *scan.ALLOWED)):
            artifact(self.directory, {**self.files, escape: b"{}\n"})
            self.assertRefused(LINKED, self.restore)
        self.assertFalse((self.tmp / "escape.json").exists())
        self.assertEqual(self.repository_files(), [])


def tree_entry(path, number, size=10):
    return {"path": path, "mode": "100644", "type": "blob", "sha": f"{number:040x}", "size": size}


class FakeTreeAPI:
    """Serves one automation-branch commit; anything else fails the test."""

    def __init__(self, files, entry_changes=None, truncated=False, encoding="base64"):
        self.files, self.truncated, self.encoding = files, truncated, encoding
        self.entries = [tree_entry("README.md", 99)]
        self.blobs = {}
        for number, (name, data) in enumerate(files.items(), 1):
            entry = {**tree_entry(name, number, size=len(data)), **(entry_changes or {}).get(name, {})}
            self.entries.append(entry)
            self.blobs[entry["sha"]] = data
        self.calls = []

    def request(self, method, endpoint, data=None, optional=False):
        self.calls.append((method, endpoint))
        if method != "GET":
            raise AssertionError("remote comparison must only read")
        if endpoint == "/git/commits/" + BRANCH_SHA:
            return {"tree": {"sha": TREE_SHA}}
        if endpoint == f"/git/trees/{TREE_SHA}?recursive=1":
            return {"sha": TREE_SHA, "truncated": self.truncated, "tree": self.entries}
        if endpoint.startswith("/git/blobs/") and endpoint[11:] in self.blobs:
            return {"encoding": self.encoding, "content": base64.b64encode(self.blobs[endpoint[11:]]).decode()}
        raise AssertionError("Unexpected API operation: " + method + " " + endpoint)


class RemoteComparisonTests(unittest.TestCase):
    def remote(self, **options):
        files = options.pop("files", {name: payload()[name] for name in scan.COMPARISON_FILES})
        api = FakeTreeAPI(files, **options)
        return api, (lambda: scan.remote_comparison_files(api, BRANCH_SHA))

    def assertRefused(self, message, function):
        with self.assertRaises(scan.ScanError) as caught:
            function()
        self.assertEqual(str(caught.exception), message)

    def test_returns_decoded_comparison_blobs_from_the_branch_commit(self):
        api, compare = self.remote()
        self.assertEqual(compare(), {name: payload()[name] for name in scan.COMPARISON_FILES})
        self.assertEqual([endpoint for _, endpoint in api.calls[:2]],
                         ["/git/commits/" + BRANCH_SHA, f"/git/trees/{TREE_SHA}?recursive=1"])
        self.assertEqual(len(api.calls), 2 + len(scan.COMPARISON_FILES))

    def test_missing_report_defaults_to_empty_but_missing_ledger_is_refused(self):
        files = {name: payload()[name] for name in scan.LEDGERS}
        _, compare = self.remote(files=files)
        self.assertEqual(compare(), {**files, scan.REPORT: b"{}"})
        _, compare = self.remote(files={scan.LEDGERS[0]: files[scan.LEDGERS[0]], scan.REPORT: b"{}"})
        self.assertRefused("Cannot verify the automation branch source ledgers.", compare)

    def test_truncated_tree_is_refused_before_reading_blobs(self):
        api, compare = self.remote(truncated=True)
        self.assertRefused("Cannot verify a truncated repository tree.", compare)
        self.assertFalse(any(endpoint.startswith("/git/blobs/") for _, endpoint in api.calls))

    def test_links_executables_trees_and_oversized_blobs_are_refused(self):
        for changes in ({"mode": "120000"}, {"mode": "100755"}, {"type": "tree", "mode": "040000"}, {"type": "commit"},
                        {"size": scan.MAX_FILE_BYTES + 1}):
            for name in (scan.LEDGERS[1], scan.REPORT):
                with self.subTest(file=name, changes=changes):
                    _, compare = self.remote(entry_changes={name: changes})
                    self.assertRefused("Cannot verify the automation branch source ledgers.", compare)

    def test_unexpected_blob_encoding_is_refused(self):
        _, compare = self.remote(encoding="utf-8")
        self.assertRefused("Unexpected GitHub blob encoding.", compare)

    def test_decoded_blob_larger_than_its_tree_entry_is_refused(self):
        files = {name: payload()[name] for name in scan.COMPARISON_FILES}
        limit = max(map(len, files.values()))
        api = FakeTreeAPI(files, entry_changes={scan.LEDGERS[0]: {"size": 1}})
        api.blobs[f"{1:040x}"] = b"x" * (limit + 1)
        with patch.object(scan, "MAX_FILE_BYTES", limit):
            self.assertRefused("Remote ledger exceeds the size budget.", lambda: scan.remote_comparison_files(api, BRANCH_SHA))
            api.blobs[f"{1:040x}"] = b"x" * limit
            self.assertEqual(len(scan.remote_comparison_files(api, BRANCH_SHA)[scan.LEDGERS[0]]), limit)


class GitHubRequestTests(unittest.TestCase):
    TOKEN = "fixture-token-value"

    def setUp(self):
        self.api = scan.GitHub(self.TOKEN)
        self.api.opener = Mock()
        sleep = patch.object(scan.time, "sleep")
        self.sleep = sleep.start()
        self.addCleanup(sleep.stop)

    def http_error(self, code):
        error = urllib.error.HTTPError("https://api.github.com/fixture", code, "fixture", {}, io.BytesIO())
        self.addCleanup(error.close)
        return error

    def respond(self, *outcomes):
        def opened(request, timeout):
            outcome = next(responses)
            if isinstance(outcome, BaseException):
                raise outcome
            return io.BytesIO(outcome)
        responses = iter(outcomes)
        self.api.opener.open.side_effect = opened

    def assertRefused(self, message, *args, **kwargs):
        with self.assertRaises(scan.ScanError) as caught:
            self.api.request(*args, **kwargs)
        self.assertEqual(str(caught.exception), message)
        self.assertNotIn(self.TOKEN, str(caught.exception))

    def test_requests_go_only_to_the_repository_api_with_the_token(self):
        self.respond(b'{"ok": true}')
        self.assertEqual(self.api.request("POST", "/pulls", {"title": "x"}), {"ok": True})
        (request,), options = self.api.opener.open.call_args
        self.assertEqual((request.full_url, request.get_method(), request.data, options),
                         ("https://api.github.com/repos/" + scan.REPOSITORY + "/pulls", "POST", b'{"title": "x"}', {"timeout": 30}))
        self.assertEqual(request.get_header("Authorization"), "Bearer " + self.TOKEN)

    def test_invalid_endpoints_are_refused_before_any_request(self):
        for endpoint in ("pulls", "/../../orgs/x", "/pulls\nHost: example.org", "https://example.org/x"):
            with self.subTest(endpoint=endpoint):
                self.assertRefused("Invalid GitHub API endpoint.", "GET", endpoint)
        self.api.opener.open.assert_not_called()

    def test_redirects_are_refused_so_the_token_is_not_forwarded(self):
        self.assertTrue(any(isinstance(handler, scan.NoRedirect) for handler in scan.GitHub(self.TOKEN).opener.handlers))
        with self.assertRaises(scan.ScanError):
            scan.NoRedirect().redirect_request(None, None, 302, "Found", {}, "https://example.org/")

    def test_empty_body_is_none_and_oversized_body_is_refused(self):
        self.respond(b"", b"x" * 11)
        self.assertIsNone(self.api.request("PATCH", "/pulls/7", {"body": ""}))
        with patch.object(scan, "MAX_TOTAL_BYTES", 5):
            self.assertRefused("GitHub API response exceeds the size budget.", "GET", "/pulls")

    def test_reads_retry_transient_failures_with_backoff(self):
        self.respond(self.http_error(503), urllib.error.URLError("reset"), b"[]")
        self.assertEqual(self.api.request("GET", "/pulls"), [])
        self.assertEqual([c.args for c in self.sleep.call_args_list], [(2,), (4,)])
        self.respond(self.http_error(502), self.http_error(502), self.http_error(502))
        self.assertRefused("GitHub API GET failed with HTTP 502; no response body or credential is logged.", "GET", "/pulls")

    def test_writes_and_client_errors_are_not_retried(self):
        for outcome, method, message in (
                (self.http_error(503), "POST", "GitHub API POST failed with HTTP 503; no response body or credential is logged."),
                (urllib.error.URLError("reset"), "PATCH", "GitHub API connection failed; rerun after checking the workflow status."),
                (self.http_error(404), "GET", "GitHub API GET failed with HTTP 404; no response body or credential is logged.")):
            with self.subTest(method=method):
                self.api.opener.open.reset_mock()
                self.respond(outcome, b"{}")
                self.assertRefused(message, method, "/git/refs", {} if method != "GET" else None)
                self.assertEqual(self.api.opener.open.call_count, 1)
        self.sleep.assert_not_called()

    def test_optional_missing_resource_is_none(self):
        self.respond(self.http_error(404))
        self.assertIsNone(self.api.request("GET", "/git/ref/heads/" + scan.BRANCH, optional=True))
        self.respond(self.http_error(403))
        self.assertRefused("GitHub API GET failed with HTTP 403; no response body or credential is logged.",
                           "GET", "/git/ref/heads/" + scan.BRANCH, optional=True)


if __name__ == "__main__":
    unittest.main()
