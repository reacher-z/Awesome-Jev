"""Absent PR proposals stay proposals with unchanged provenance and bounded writes."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts import open_scan_pr as scan
from scripts.source_policy import SourcePolicy


IDENTITY = {"repository": scan.REPOSITORY, "base_sha": "a" * 40, "run_id": "12", "run_attempt": "1"}
HEAD = "b" * 40


def payload(*rows):
    result = {name: b"{}\n" for name in scan.ALLOWED}
    result[scan.LEDGERS[0]] = b""
    result[scan.LEDGERS[1]] = b"".join((json.dumps(row, ensure_ascii=False) + "\r\n").encode() for row in rows)
    result[scan.REPORT] = b'{"changed":true,"status":"partial","added_count":2}\n'
    return result


def source(name, level="abstract_checked"):
    return {"url": "https://example.org/" + name, "title": name, "verification_level": level,
            "abstract_sha256": "c" * 64, "retrieved_at": "2026-10-16T00:00:00Z"}


class ReadOnlyAPI:
    def __init__(self, head=HEAD, owner=scan.BOT):
        self.head, self.owner = head, owner
        self.calls = []

    def request(self, method, endpoint, data=None, optional=False):
        self.calls.append((method, endpoint))
        if method != "GET":
            raise AssertionError("Reconciliation must not write to GitHub")
        if endpoint == "/git/ref/heads/main":
            return {"object": {"sha": IDENTITY["base_sha"]}}
        if endpoint == "/git/ref/heads/" + scan.BRANCH:
            return {"object": {"sha": self.head}}
        if endpoint.startswith("/pulls?"):
            return [{"user": {"login": self.owner}, "body": scan.MARKER}]
        if endpoint == "/commits/" + self.head:
            return {"committer": {"login": self.owner}, "commit": {"message": scan.TITLE}}
        raise AssertionError(endpoint)


class PendingCarryTests(unittest.TestCase):
    def test_missing_rows_keep_exact_evidence_and_dates_without_becoming_fresh(self):
        old, fresh = payload(source("older")), payload(source("current"))
        result, carried = scan.carry_pending_records(old, fresh)
        self.assertEqual(result[scan.LEDGERS[1]], fresh[scan.LEDGERS[1]] + old[scan.LEDGERS[1]])
        self.assertEqual(carried, ["https://example.org/older"])
        report = json.loads(result[scan.REPORT])
        self.assertEqual(report["added_count"], 2)
        self.assertEqual(report["carried_forward_pending_count"], 1)
        self.assertNotIn("carried_forward_pending_count", json.loads(fresh[scan.REPORT]))
        repeated, again = scan.carry_pending_records(old, result)
        self.assertEqual(repeated, result)
        self.assertEqual(again, [])
        for name in set(scan.ALLOWED) - {scan.LEDGERS[1], scan.REPORT}:
            self.assertEqual(result[name], fresh[name])

    def test_current_records_and_reviewed_exclusions_are_never_overwritten(self):
        old = payload(source("current", "content_screened"), source("excluded"))
        fresh = payload(source("current"))
        policy = SourcePolicy({"https://example.org/excluded": {}}, {}, scan.pending_source_key)
        # Empty policy records are falsey; real exclusion records are nonempty.
        policy.exclusions["https://example.org/excluded"] = {"reason": "Reviewed exclusion"}
        result, carried = scan.carry_pending_records(old, fresh, policy)
        self.assertEqual(result, fresh)
        self.assertEqual(carried, [])
        with self.assertRaises(scan.ScanError):
            scan.ensure_pending_continuity(old, result, policy)

    def test_prior_aliases_are_carried_once_using_the_stronger_row(self):
        legacy = source("alias", "metadata_only")
        legacy["url"] = "https://huggingface.co/lihe07/span-02"
        current = {**legacy, "url": "https://huggingface.co/respanai/span-02", "verification_level": "content_screened"}
        result, carried = scan.carry_pending_records(payload(legacy, current), payload())
        self.assertEqual(len(carried), 1)
        self.assertEqual([json.loads(line) for line in result[scan.LEDGERS[1]].splitlines()], [current])

    def test_reconciliation_rebuilds_only_trusted_data_and_rehashes_the_bundle(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve() / "repo"
            artifact = Path(directory).resolve() / "artifact"
            files = payload(source("current"))
            manifest = {"format": 1, **IDENTITY, "changed": True, "files": {}}
            for name, content in files.items():
                for folder in (root, artifact):
                    path = folder / name
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_bytes(content)
                manifest["files"][name] = {"sha256": scan.digest(content), "bytes": len(content)}
            (artifact / "manifest.json").write_text(json.dumps(manifest))
            api = ReadOnlyAPI()
            with patch.object(scan, "ROOT", root), patch.object(scan, "remote_comparison_files", return_value=payload(source("older"))), \
                 patch.object(scan.subprocess, "run") as run, patch.dict(scan.os.environ, {"GH_TOKEN": "fixture", "GITHUB_TOKEN": "fixture"}):
                scan.reconcile_pending(api, artifact, IDENTITY)
            run.assert_called_once()
            self.assertEqual(run.call_args.args[0], [scan.sys.executable, "scripts/build_source_index.py"])
            self.assertNotIn("GH_TOKEN", run.call_args.kwargs["env"])
            self.assertNotIn("GITHUB_TOKEN", run.call_args.kwargs["env"])
            updated, loaded = scan.load_bundle(artifact, IDENTITY)
            self.assertEqual(updated["pending_pr_head"], HEAD)
            self.assertEqual(json.loads(loaded[scan.REPORT])["carried_forward_pending_count"], 1)
            for name in scan.ALLOWED:
                self.assertEqual((root / name).read_bytes(), loaded[name])
            self.assertTrue(all(method == "GET" for method, _ in api.calls))

    def test_concurrent_pending_branch_change_stops_before_any_remote_write(self):
        api = ReadOnlyAPI(head="d" * 40)
        with self.assertRaisesRegex(scan.ScanError, "changed after reconciliation"):
            scan.publish(api, IDENTITY, payload(), pending_head=HEAD)
        self.assertTrue(all(method == "GET" for method, _ in api.calls))

    def test_non_bot_pr_is_refused_without_mutating_the_restored_files(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve() / "repo"
            files = payload(source("current"))
            for name, data in files.items():
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(data)
            api = ReadOnlyAPI(owner="fixture-maintainer")
            with patch.object(scan, "ROOT", root), patch.object(scan, "load_bundle", return_value=({}, files)), \
                 patch.object(scan, "remote_comparison_files") as remote, self.assertRaises(scan.ScanError):
                scan.reconcile_pending(api, root / "bundle", IDENTITY)
            remote.assert_not_called()
            self.assertTrue(all((root / name).read_bytes() == data for name, data in files.items()))

    def test_malformed_old_evidence_is_not_carried(self):
        bad = payload(source("unknown", "unreviewed-fixture-level"))
        with self.assertRaises(scan.ScanError):
            scan.carry_pending_records(bad, payload())


if __name__ == "__main__":
    unittest.main()
