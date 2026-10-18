#!/usr/bin/env python3
"""Transfer validated data between trusted scan jobs and maintain one bot PR.

Only six fixed JSON/JSONL files can cross the job boundary. No downloaded code
is executed. The workflow token supports GitHub-only reads during reconciliation
and the final publishing step; it is never logged, written to disk or passed to
the local index builder.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import html
import http.client
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

try:
    from . import build_source_index as source_index
    from .source_policy import load_policy
except ImportError:
    import build_source_index as source_index
    from source_policy import load_policy

ROOT = Path(__file__).resolve().parents[1]
REPOSITORY = "reacher-z/Awesome-Jev"
BRANCH = "automation/source-scan"
BASE_BRANCH = "main"
TITLE = "chore: refresh public source index"
MARKER = "<!-- awesome-jev-source-scan -->"
BOT = "github-actions[bot]"
BOT_EMAIL = "41898282+github-actions[bot]@users.noreply.github.com"
ALLOWED = (
    "data/ecosystem-sources.jsonl",
    "data/research-sources.jsonl",
    "data/scan-latest.json",
    "data/source-counts.json",
    "site/data/source-index.json",
    "site/data/source-badge.json",
    # A scan prunes exclusion-screen rows for sources it accepts.
    "data/ecosystem-sources.excluded.jsonl",
)
LEDGERS = ALLOWED[:2]
REPORT = "data/scan-latest.json"
COMPARISON_FILES = (*LEDGERS, REPORT)
MAX_FILE_BYTES = 32 * 1024 * 1024
MAX_TOTAL_BYTES = 128 * 1024 * 1024
SHA = re.compile(r"^[0-9a-f]{40}$")
SHA256 = re.compile(r"^[0-9a-f]{64}$")


class ScanError(RuntimeError):
    pass


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git(*args: str) -> str:
    result = subprocess.run(["git", *args], cwd=ROOT, check=True, capture_output=True, text=True)
    return result.stdout.strip()


def context() -> dict:
    if os.environ.get("GITHUB_REPOSITORY") != REPOSITORY:
        raise ScanError("Publishing is restricted to the canonical project repository.")
    if os.environ.get("GITHUB_REF") != "refs/heads/main" or os.environ.get("GITHUB_EVENT_NAME") not in {"schedule", "workflow_dispatch"}:
        raise ScanError("Only a scheduled or manually dispatched main-branch run is accepted.")
    sha = os.environ.get("GITHUB_SHA", "")
    run_id = os.environ.get("GITHUB_RUN_ID", "")
    attempt = os.environ.get("GITHUB_RUN_ATTEMPT", "")
    if not SHA.fullmatch(sha) or not run_id.isdigit() or not attempt.isdigit():
        raise ScanError("Missing trusted workflow identity.")
    if git("rev-parse", "HEAD") != sha:
        raise ScanError("Checkout does not match the workflow base commit.")
    return {"repository": REPOSITORY, "base_sha": sha, "run_id": run_id, "run_attempt": attempt}


def read_data(path: Path) -> bytes:
    if path.is_symlink() or not path.is_file() or path.stat().st_size > MAX_FILE_BYTES:
        raise ScanError("Missing, oversized, or linked source artifact.")
    data = path.read_bytes()
    try:
        text = data.decode("utf-8")
        if path.suffix == ".jsonl":
            for line in text.split("\n"):
                if line.strip() and not isinstance(json.loads(line), dict):
                    raise ValueError("record")
        elif not isinstance(json.loads(text), dict):
            raise ValueError("object")
    except (UnicodeDecodeError, ValueError):
        raise ScanError("Artifact contains invalid UTF-8 or JSON data.") from None
    return data


def meaningful_fingerprint(files: dict[str, bytes]) -> str:
    """Ignore retrieval-clock churn while retaining source content and claims."""
    normalized = []
    for name in LEDGERS:
        rows = []
        for line in files[name].decode("utf-8").split("\n"):
            if not line.strip():
                continue
            row = json.loads(line)
            row = {k: v for k, v in row.items() if k not in {"retrieved_at", "relevance_rescreened_at"}}
            rows.append(json.dumps(row, sort_keys=True, ensure_ascii=False, separators=(",", ":")))
        normalized.append((name, sorted(rows)))
    report = json.loads(files.get(REPORT, b"{}"))
    pending = report.get("editorial_refresh_candidates", [])
    if not isinstance(pending, list) or any(not isinstance(item, dict) for item in pending):
        raise ScanError("Invalid editorial-refresh candidate list.")
    evidence_keys = {"url", "old_content_sha256", "observed_content_sha256", "observed_verification_level", "retrieved_url", "note",
                     "review_kind", "old_reviewed_version_url", "observed_version_url", "observed_abstract_sha256"}
    stable_pending = [json.dumps({k: v for k, v in item.items() if k in evidence_keys}, sort_keys=True, ensure_ascii=False, separators=(",", ":")) for item in pending]
    normalized.append(("editorial_refresh_candidates", sorted(stable_pending)))
    return digest(json.dumps(normalized, ensure_ascii=False, separators=(",", ":")).encode())


def write_summary(text: str) -> None:
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as stream:
            stream.write(text + "\n")
    print(text)


def bundle(directory: Path, identity: dict) -> None:
    if directory.exists():
        raise ScanError("Bundle directory must be new.")
    report = json.loads((ROOT / "data/scan-latest.json").read_text(encoding="utf-8"))
    if not isinstance(report.get("changed"), bool) or report.get("status") not in {"success", "partial", "failed"}:
        raise ScanError("Invalid scan report.")
    if report["status"] == "failed":
        raise ScanError("Collector reported failure; no update will be published.")
    files = {name: read_data(ROOT / name) for name in ALLOWED}
    if sum(map(len, files.values())) > MAX_TOTAL_BYTES:
        raise ScanError("Artifact exceeds the size budget.")
    baseline = {}
    for name in COMPARISON_FILES:
        previous = subprocess.run(["git", "show", f"HEAD:{name}"], cwd=ROOT, capture_output=True)
        if previous.returncode and name != REPORT:
            raise ScanError("Cannot read the base source ledgers.")
        baseline[name] = previous.stdout if previous.returncode == 0 else b"{}"
    changed = report["changed"] and meaningful_fingerprint(files) != meaningful_fingerprint(baseline)
    if os.environ.get("GITHUB_OUTPUT"):
        with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as stream:
            stream.write("changed=" + str(changed).lower() + "\n")
    write_summary("Source scan: " + report["status"] + "; validated source changes found." if changed else "No substantive source changes; no PR update. See the collector summary for this run's provider status.")
    if not changed:
        return
    directory.mkdir(parents=True)
    manifest = {"format": 1, **identity, "changed": True, "files": {}}
    for name, data in files.items():
        target = directory / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        manifest["files"][name] = {"sha256": digest(data), "bytes": len(data)}
    (directory / "manifest.json").write_text(json.dumps(manifest, sort_keys=True) + "\n", encoding="utf-8", newline="\n")


def load_bundle(directory: Path, identity: dict) -> tuple[dict, dict[str, bytes]]:
    if directory.is_symlink() or not directory.is_dir():
        raise ScanError("Invalid artifact directory.")
    for path in directory.rglob("*"):
        if path.is_symlink():
            raise ScanError("Artifact symlinks are not permitted.")
        if path.is_file() and path.relative_to(directory).as_posix() not in {*ALLOWED, "manifest.json"}:
            raise ScanError("Artifact contains a file outside the fixed data allowlist.")
    try:
        manifest = json.loads(read_data(directory / "manifest.json"))
    except (ValueError, TypeError):
        raise ScanError("Invalid artifact manifest.") from None
    if manifest.get("format") != 1 or manifest.get("changed") is not True or any(manifest.get(k) != v for k, v in identity.items()):
        raise ScanError("Artifact does not belong to this workflow run and base commit.")
    if set(manifest.get("files", {})) != set(ALLOWED):
        raise ScanError("Artifact file allowlist mismatch.")
    files = {}
    for name in ALLOWED:
        data = read_data(directory / name)
        expected = manifest["files"][name]
        if not isinstance(expected, dict) or not isinstance(expected.get("sha256"), str) or not SHA256.fullmatch(expected["sha256"]):
            raise ScanError("Invalid artifact file manifest.")
        if expected.get("bytes") != len(data) or expected.get("sha256") != digest(data):
            raise ScanError("Artifact data does not match its manifest hash.")
        files[name] = data
    if sum(map(len, files.values())) > MAX_TOTAL_BYTES:
        raise ScanError("Artifact exceeds the size budget.")
    return manifest, files


def restore(directory: Path, identity: dict) -> None:
    _, files = load_bundle(directory, identity)
    for name, data in files.items():
        target = ROOT / name
        ancestry = [ROOT.joinpath(*Path(name).parts[:n]) for n in range(1, len(Path(name).parts) + 1)]
        if any(path.is_symlink() for path in ancestry) or not target.resolve().is_relative_to(ROOT):
            raise ScanError("Refusing to restore data through a linked path.")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
    print("Restored the six allowlisted data files; trusted repository code is unchanged.")


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise ScanError("Unexpected GitHub API redirect; token was not forwarded.")


class GitHub:
    def __init__(self, token: str):
        self.token = token
        self.opener = urllib.request.build_opener(NoRedirect)

    def request(self, method: str, endpoint: str, data: dict | None = None, optional: bool = False):
        if not endpoint.startswith("/") or ".." in endpoint or "\n" in endpoint:
            raise ScanError("Invalid GitHub API endpoint.")
        url = "https://api.github.com/repos/" + REPOSITORY + endpoint
        body = json.dumps(data).encode() if data is not None else None
        headers = {"Authorization": "Bearer " + self.token, "Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2026-03-10", "Content-Type": "application/json", "User-Agent": "Awesome-Jev-source-scan"}
        # Retry reads only. Retrying writes could create duplicate commits/PRs.
        for attempt in range(3 if method == "GET" else 1):
            try:
                with self.opener.open(urllib.request.Request(url, body, headers, method=method), timeout=30) as response:
                    raw = response.read(MAX_TOTAL_BYTES * 2 + 1)
                    if len(raw) > MAX_TOTAL_BYTES * 2:
                        raise ScanError("GitHub API response exceeds the size budget.")
                    return json.loads(raw) if raw else None
            except urllib.error.HTTPError as exc:
                if optional and exc.code == 404:
                    return None
                if method == "GET" and exc.code in {429, 500, 502, 503, 504} and attempt < 2:
                    time.sleep(2 ** (attempt + 1))
                    continue
                raise ScanError(f"GitHub API {method} failed with HTTP {exc.code}; no response body or credential is logged.") from None
            # urllib does not wrap errors raised while reading the status line or
            # body (RemoteDisconnected, IncompleteRead), so catch them here too.
            except (urllib.error.URLError, TimeoutError, http.client.HTTPException, ConnectionError):
                if method == "GET" and attempt < 2:
                    time.sleep(2 ** (attempt + 1))
                    continue
                raise ScanError("GitHub API connection failed; rerun after checking the workflow status.") from None


def remote_comparison_files(api: GitHub, commit_sha: str) -> dict[str, bytes]:
    commit = api.request("GET", "/git/commits/" + commit_sha)
    tree = api.request("GET", "/git/trees/" + commit["tree"]["sha"] + "?recursive=1")
    if tree.get("truncated"):
        raise ScanError("Cannot verify a truncated repository tree.")
    entries = {item["path"]: item for item in tree["tree"]}
    result = {}
    for name in COMPARISON_FILES:
        item = entries.get(name, {})
        if not item and name == REPORT:
            result[name] = b"{}"
            continue
        if item.get("type") != "blob" or item.get("mode") != "100644" or item.get("size", 0) > MAX_FILE_BYTES:
            raise ScanError("Cannot verify the automation branch source ledgers.")
        blob = api.request("GET", "/git/blobs/" + item["sha"])
        if blob.get("encoding") != "base64":
            raise ScanError("Unexpected GitHub blob encoding.")
        result[name] = base64.b64decode(blob["content"])
        if len(result[name]) > MAX_FILE_BYTES:
            raise ScanError("Remote ledger exceeds the size budget.")
    return result


def pr_body(report: dict, identity: dict) -> str:
    def count(key):
        value = report.get(key, 0)
        return value if isinstance(value, int) and not isinstance(value, bool) and 0 <= value <= 1000000 else 0
    status = report.get("status") if report.get("status") in {"success", "partial"} else "partial"
    run_url = f"https://github.com/{REPOSITORY}/actions/runs/{identity['run_id']}"
    return f"""{MARKER}
This scan updates public source ledgers and their generated browser index.

- Scan status: **{status}**.
- Newly discovered records: **{count('added_count')}**; changed records: **{count('changed_count')}**.
- Older pending sources retained without a fresh fetch: **{count('carried_forward_pending_count')}**.
- Records requiring editorial inspection: **{count('editorial_review_required_count')}**.
- [Collector, regression tests, and repository validation]({run_url}) ran before this PR was prepared. Inspect that run for partial-provider failures and exact verification scope.

Each record retains public-source provenance and its verification level. Automated retrieval and screening are not human or scientific review and do not reproduce experiments. This workflow never merges or approves a PR and does not mirror updates to the website repository. GitHub may require approval before workflows on a bot-created PR run; this description does not claim that PR CI has run.

## Checklist

- [x] I linked canonical public sources in the ledgers.
- [x] I stated the verification level and relevant limitations.
- [x] I included dates or versions for changing claims where provided by the sources.
- [x] I checked for credentials, private paths, and unlicensed assets using the repository validator; no third-party assets were added.
- [x] I ran the regression tests and repository validator before publication.

Maintainers should inspect the diff and the scan report before deciding whether to merge.
"""[:6000]


def arxiv_version(value) -> tuple[str, int] | None:
    match = re.fullmatch(r"https://arxiv\.org/(?:abs|pdf)/(\d{4}\.\d{4,5})v([1-9]\d*)(?:\.pdf)?", value) if isinstance(value, str) else None
    return (match[1], int(match[2])) if match else None


def review_candidate_replaced(previous: dict, fresh: dict) -> bool:
    """A new queue item must not obscure a known version held only in the PR."""
    if previous.get("review_kind") != "pinned_arxiv_abstract":
        return True
    old_version = arxiv_version(previous.get("observed_version_url"))
    if not old_version:
        return True
    new_version = arxiv_version(fresh.get("observed_version_url"))
    return bool(fresh.get("review_kind") == "pinned_arxiv_abstract" and new_version
                and new_version[0] == old_version[0] and new_version[1] >= old_version[1])


def review_candidate_accepted(item: dict, current: dict) -> bool:
    """A matching abstract alone cannot accept a different pinned paper version."""
    if item.get("review_kind") == "pinned_arxiv_abstract":

        observed_version = item.get("observed_version_url")
        if observed_version and (not arxiv_version(observed_version)
                                 or arxiv_version(current.get("reviewed_version_url")) != arxiv_version(observed_version)):
            return False
        abstract = item.get("observed_abstract_sha256")
        if abstract:
            return bool(isinstance(abstract, str) and SHA256.fullmatch(abstract)
                        and current.get("abstract_sha256") == abstract)
        page = item.get("observed_abstract_page_sha256")
        return bool(isinstance(page, str) and SHA256.fullmatch(page)
                    and current.get("abstract_page_sha256") == page)
    observed_hash = item.get("observed_content_sha256")
    return bool(observed_hash and current.get("content_sha256", current.get("abstract_sha256")) == observed_hash)


def pending_source_key(url: str) -> str:
    """Compare document identity while retaining revisions in the evidence rows."""
    key = source_index.canonical(html.unescape(url))
    index_files = "https://huggingface.co/spaces/multimodalart/jev-decision-index/blob/"
    if key.startswith(index_files):
        key = re.sub(r"/blob/[^/]+/", "/blob/main/", key, count=1)
    return key


def carry_pending_records(previous, fresh, policy=None):
    """Keep absent, still-pending rows verbatim; never replace a fresh observation."""
    ranks = {"metadata_only": 0, "abstract_checked": 1, "content_screened": 2, "editorial_reviewed": 3}
    def key_of(row):
        if not isinstance(row, dict):
            raise ScanError("Invalid pending source record.")
        url = row.get("canonical_url", row.get("url", ""))
        if not isinstance(url, str) or not url:
            raise ScanError("Cannot establish pending source identity.")
        return pending_source_key(url)
    known, candidates = set(), {}
    for name in LEDGERS:
        for line in fresh[name].decode("utf-8").splitlines():
            if line.strip():
                row = json.loads(line)
                known.add(key_of(row))
        for line in previous[name].decode("utf-8").splitlines(keepends=True):
            if not line.strip():
                continue
            row = json.loads(line)
            key = key_of(row)
            rank = ranks.get(row.get("verification_level", "metadata_only"))
            if rank is None:
                raise ScanError("Unknown evidence level in pending source data.")
            if key not in candidates or rank > candidates[key][0]:
                candidates[key] = (rank, name, line.encode("utf-8"))
    result, carried = dict(fresh), []
    for key, (_, name, line) in sorted(candidates.items()):
        if key in known or policy and policy.exclusion(key):
            continue
        separator = b"\n" if result[name] and not result[name].endswith(b"\n") else b""
        result[name] += separator + line + (b"" if line.endswith(b"\n") else b"\n")
        carried.append(key)
    if carried:
        report = json.loads(result[REPORT])
        report.update(changed=True, carried_forward_pending_count=len(carried), carried_forward_pending_urls=carried,
                      pending_carry_note="Absent candidates retained from the prior unmerged bot PR with original evidence and retrieval dates; not newly fetched or accepted into main.")
        result[REPORT] = (json.dumps(report, ensure_ascii=False, indent=2) + "\n").encode()
    return result, carried


def reconcile_pending(api, directory, identity, policy=None):
    """Prepare only allowlisted data; validation must run again before publish."""
    manifest, fresh = load_bundle(directory, identity)
    if any((ROOT / name).read_bytes() != data for name, data in fresh.items()):
        raise ScanError("Checkout differs from the restored artifact before reconciliation.")
    if api.request("GET", "/git/ref/heads/main")["object"]["sha"] != identity["base_sha"]:
        raise ScanError("Main advanced after scanning; pending data was not reconciled.")
    branch = api.request("GET", "/git/ref/heads/" + BRANCH, optional=True)
    query = urllib.parse.urlencode({"state": "open", "head": REPOSITORY.split("/")[0] + ":" + BRANCH, "base": BASE_BRANCH, "per_page": 10})
    opened = api.request("GET", "/pulls?" + query)
    if not isinstance(opened, list):
        raise ScanError("Cannot verify the pending scan PR list.")
    if not opened:
        print("No open scan PR to reconcile.")
        return
    if (len(opened) != 1 or not isinstance(branch, dict) or not isinstance(opened[0], dict)
            or (opened[0].get("user") or {}).get("login") != BOT
            or MARKER not in (opened[0].get("body") or "")):
        raise ScanError("Refusing to reconcile a non-bot or ambiguous scan PR.")
    head = branch["object"]["sha"]
    if not isinstance(head, str) or not SHA.fullmatch(head):
        raise ScanError("Invalid pending branch identity.")
    commit = api.request("GET", "/commits/" + head)
    if (not isinstance(commit, dict) or (commit.get("committer") or {}).get("login") != BOT
            or not ((commit.get("commit") or {}).get("message") or "").startswith(TITLE)):
        raise ScanError("Pending branch contains non-bot changes; no reconciliation performed.")
    previous = remote_comparison_files(api, head)
    prepared, carried = carry_pending_records(previous, fresh, policy)
    for name in (*LEDGERS, REPORT):
        (ROOT / name).write_bytes(prepared[name])
    # Use only trusted base-branch code, without a publishing token in the child.
    if carried:
        environment = {key: value for key, value in os.environ.items() if key not in {"GH_TOKEN", "GITHUB_TOKEN"}}
        subprocess.run([sys.executable, "scripts/build_source_index.py"], cwd=ROOT, env=environment,
                       check=True, capture_output=True, timeout=60)
    files = {name: read_data(ROOT / name) for name in ALLOWED}
    if sum(map(len, files.values())) > MAX_TOTAL_BYTES:
        raise ScanError("Reconciled artifact exceeds the size budget.")
    manifest["pending_pr_head"] = head
    manifest["files"] = {name: {"sha256": digest(data), "bytes": len(data)} for name, data in files.items()}
    for name, data in files.items():
        (directory / name).write_bytes(data)
    (directory / "manifest.json").write_text(json.dumps(manifest, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    print(f"Retained {len(carried)} absent pending sources without changing their evidence. Revalidate all six data files before publication.")


def accepted_primary_snapshot(prior: dict, current: dict, accepted: dict) -> bool:
    """A reviewed primary record on trusted main can replace old page screening.

    This exception never accepts a change introduced only by the fresh scan, an
    editorial downgrade, or loss of a versioned pending primary abstract.
    """
    version = arxiv_version(accepted.get("reviewed_version_url"))
    if (prior.get("verification_level") != "content_screened"
            or prior.get("abstract_provider") == "arxiv_primary_abstract_page"
            or prior.get("reviewed_version_url") or not version
            or accepted.get("abstract_provider") != "arxiv_primary_abstract_page"
            or accepted.get("verification_level") != "abstract_checked"
            or accepted.get("canonical_page_separately_fetched") is not True
            or accepted.get("reviewed_version") != "v" + str(version[1])):
        return False
    identity = "https://arxiv.org/abs/" + version[0]
    for field in ("url", "canonical_url", "retrieved_url", "retrieval_url", "observed_version_url"):
        observed = arxiv_version(prior.get(field))
        if observed and (observed[0] != version[0] or observed[1] > version[1]):
            return False
    if any(pending_source_key(row.get("canonical_url", row.get("url", ""))) != identity
           for row in (prior, current, accepted)):
        return False
    fields = ("abstract_provider", "verification_level", "canonical_page_separately_fetched",
              "reviewed_version", "reviewed_version_url", "abstract_sha256", "abstract_page_sha256")
    return (all(isinstance(accepted.get(key), str) and SHA256.fullmatch(accepted[key])
                for key in ("abstract_sha256", "abstract_page_sha256"))
            and all(current.get(key) == accepted.get(key) for key in fields))


def ensure_pending_continuity(previous: dict[str, bytes], fresh: dict[str, bytes], policy=None, accepted=None) -> None:
    """Do not erase evidence held only in an unmerged bot PR on a bad scan."""
    ranks = {"metadata_only": 0, "abstract_checked": 1, "content_screened": 2, "editorial_reviewed": 3}

    def records(payload):
        found = {}
        for name in LEDGERS:
            for line in payload[name].decode("utf-8").split("\n"):
                if not line.strip():
                    continue
                row = json.loads(line)
                url = row.get("canonical_url", row.get("url", ""))
                if not isinstance(url, str) or not url:
                    raise ScanError("Cannot establish pending source identity.")
                key = pending_source_key(url)
                level = row.get("verification_level", "metadata_only")
                if level not in ranks:
                    raise ScanError("Cannot establish pending source verification level.")
                if key not in found or ranks[level] > ranks[found[key].get("verification_level", "metadata_only")]:
                    found[key] = row
        return found

    before, after = records(previous), records(fresh)
    on_main = records(accepted) if accepted is not None else {}
    missing = downgraded = 0
    for key, prior in before.items():
        if policy and policy.exclusion(key):
            continue
        current = after.get(key)
        if current is None:
            missing += 1
        elif (ranks[current.get("verification_level", "metadata_only")] < ranks[prior.get("verification_level", "metadata_only")]
              and not accepted_primary_snapshot(prior, current, on_main.get(key, {}))):
            downgraded += 1
    prior_queue = json.loads(previous.get(REPORT, b"{}")).get("editorial_refresh_candidates", [])
    fresh_queue = json.loads(fresh.get(REPORT, b"{}")).get("editorial_refresh_candidates", [])
    queued_by_url = {}
    for item in fresh_queue:
        queued_by_url.setdefault(pending_source_key(item["url"]), []).append(item)
    unexplained = 0
    for item in prior_queue:
        key = pending_source_key(item["url"])
        if (policy and policy.exclusion(key)
                or any(review_candidate_replaced(item, queued) for queued in queued_by_url.get(key, []))):
            continue
        current = after.get(key, {})
        if not review_candidate_accepted(item, current):
            unexplained += 1
    if missing or downgraded or unexplained:
        raise ScanError(f"Pending PR evidence would be lost ({missing} missing, {downgraded} downgraded, {unexplained} unresolved editorial changes). Existing PR retained; review or merge it before retrying.")


def publish(api: GitHub, identity: dict, files: dict[str, bytes], policy=None, pending_head=None) -> str:
    main_ref = api.request("GET", "/git/ref/heads/main")
    if main_ref["object"]["sha"] != identity["base_sha"]:
        raise ScanError("Main advanced after scanning; rerun instead of overwriting newer source data.")
    branch_ref = api.request("GET", "/git/ref/heads/" + BRANCH, optional=True)
    previous_sha = branch_ref["object"]["sha"] if branch_ref else None
    if pending_head is not None and (not isinstance(pending_head, str) or not SHA.fullmatch(pending_head) or previous_sha != pending_head):
        raise ScanError("Pending PR changed after reconciliation; no branch was updated.")
    query = urllib.parse.urlencode({"state": "open", "head": REPOSITORY.split("/")[0] + ":" + BRANCH, "base": BASE_BRANCH, "per_page": 10})
    opened = api.request("GET", "/pulls?" + query)
    if len(opened) > 1 or (opened and ((opened[0].get("user") or {}).get("login") != BOT or MARKER not in (opened[0].get("body") or ""))):
        raise ScanError("Refusing to overwrite a non-bot or ambiguous source-scan pull request.")
    unchanged = False
    if previous_sha:
        previous = api.request("GET", "/commits/" + previous_sha)
        # GitHub returns "committer": null when the email is not linked to an account.
        if (previous.get("committer") or {}).get("login") != BOT or not previous.get("commit", {}).get("message", "").startswith(TITLE):
            raise ScanError("The dedicated automation branch has non-bot changes; maintainer inspection is required.")
        previous_files = remote_comparison_files(api, previous_sha)
        if opened:
            accepted_files = remote_comparison_files(api, identity["base_sha"])
            ensure_pending_continuity(previous_files, files, policy, accepted=accepted_files)
        unchanged = meaningful_fingerprint(previous_files) == meaningful_fingerprint(files)
    if unchanged and opened:
        return "The existing scan PR already contains these substantive source changes; no update made."
    if unchanged and previous_sha:
        closed_query = urllib.parse.urlencode({"state": "closed", "head": REPOSITORY.split("/")[0] + ":" + BRANCH, "base": BASE_BRANCH, "per_page": 10, "sort": "updated", "direction": "desc"})
        closed = api.request("GET", "/pulls?" + closed_query)
        if any(not row.get("merged_at") for row in closed):
            return "These changes were already closed without merging; no PR was reopened."
    if not unchanged:
        main = api.request("GET", "/git/commits/" + identity["base_sha"])
        tree_entries = []
        for name in ALLOWED:
            blob = api.request("POST", "/git/blobs", {"content": base64.b64encode(files[name]).decode("ascii"), "encoding": "base64"})
            tree_entries.append({"path": name, "mode": "100644", "type": "blob", "sha": blob["sha"]})
        tree = api.request("POST", "/git/trees", {"base_tree": main["tree"]["sha"], "tree": tree_entries})
        parents = [previous_sha, identity["base_sha"]] if previous_sha and previous_sha != identity["base_sha"] else [identity["base_sha"]]
        bot = {"name": BOT, "email": BOT_EMAIL}
        commit = api.request("POST", "/git/commits", {"message": TITLE + "\n\nValidated source scan run " + identity["run_id"], "tree": tree["sha"], "parents": parents, "author": bot, "committer": bot})
        # Recheck both refs immediately before the only branch mutation.
        if api.request("GET", "/git/ref/heads/main")["object"]["sha"] != identity["base_sha"]:
            raise ScanError("Main changed during publication; no branch was updated.")
        current = api.request("GET", "/git/ref/heads/" + BRANCH, optional=True)
        if (current["object"]["sha"] if current else None) != previous_sha:
            raise ScanError("Automation branch changed concurrently; no branch was overwritten.")
        if previous_sha:
            api.request("PATCH", "/git/refs/heads/" + BRANCH, {"sha": commit["sha"], "force": False})
        else:
            api.request("POST", "/git/refs", {"ref": "refs/heads/" + BRANCH, "sha": commit["sha"]})
    report = json.loads(files["data/scan-latest.json"])
    body = pr_body(report, identity)
    if opened:
        pr = api.request("PATCH", "/pulls/" + str(opened[0]["number"]), {"title": TITLE, "body": body})
    else:
        pr = api.request("POST", "/pulls", {"title": TITLE, "head": BRANCH, "base": BASE_BRANCH, "body": body, "maintainer_can_modify": True})
    return "Source scan PR: " + pr["html_url"]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("bundle", "restore", "reconcile", "publish"))
    parser.add_argument("--directory", type=Path, required=True)
    args = parser.parse_args()
    try:
        identity = context()
        if args.command == "bundle":
            bundle(args.directory, identity)
        elif args.command == "restore":
            restore(args.directory, identity)
        else:
            manifest, files = load_bundle(args.directory, identity)
            if any((ROOT / name).read_bytes() != data for name, data in files.items()):
                raise ScanError("Validated checkout data changed after restoration.")
            token = os.environ.get("GH_TOKEN", "")
            if not token:
                raise ScanError("Scan PR reconciliation and publication require the workflow GITHUB_TOKEN.")
            policy = load_policy(ROOT / "data/source-curation.json", source_index.canonical)
            if args.command == "reconcile":
                reconcile_pending(GitHub(token), args.directory, identity, policy=policy)
            else:
                write_summary(publish(GitHub(token), identity, files, policy=policy, pending_head=manifest.get("pending_pr_head")))
        return 0
    except (ScanError, KeyError, TypeError, ValueError, OSError, subprocess.CalledProcessError) as exc:
        # Public-source responses, filesystem paths, and credentials stay out of logs.
        message = str(exc) if isinstance(exc, ScanError) else "Invalid scan artifact or local repository state."
        print("Source scan publication stopped: " + message, file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
