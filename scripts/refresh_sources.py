#!/usr/bin/env python3
"""Incrementally refresh public sources without erasing earlier evidence.

Downloaded documents are untrusted data. Only short evidence and hashes enter
the ledgers; response bodies are cached in memory, never in the repository.
No credentials, cookies, proxy settings or downloaded code are used.
"""
from __future__ import annotations

import argparse
from collections import Counter, OrderedDict
import concurrent.futures as cf
from dataclasses import dataclass
from datetime import datetime, timezone
from html.parser import HTMLParser
import hashlib
import http.client
import ipaddress
import json
import os
from pathlib import Path
import re
import socket
import ssl
import subprocess
import sys
import threading
import time
import urllib.parse

try:
    from . import collect_ecosystem as ecosystem
    from . import collect_research as research
    from . import build_source_index as index
    from .source_policy import credential_query, load_policy
    from .validate import LEAK_PATTERNS
except ImportError:
    import collect_ecosystem as ecosystem
    import collect_research as research
    import build_source_index as index
    from source_policy import credential_query, load_policy
    from validate import LEAK_PATTERNS

ROOT = Path(__file__).resolve().parents[1]
LEVEL = {"metadata_only": 0, "abstract_checked": 1, "content_screened": 2, "editorial_reviewed": 3}
DIRECT_QUERIES = ["Jev TypeSafe", "typed decision model", "System One model Jev", "RLCD calibrated decisions"]
MAX_BODY = 6_000_000
# Scan-wide deadline for issuing requests, including Retry-After and backoff
# waits. It leaves the 25-minute scan job time to merge, rebuild and validate,
# so a heavily rate-limited run ends partial instead of hitting the job timeout.
SCAN_TIME_BUDGET_SECONDS = 18 * 60
SAFE_FETCH_ERRORS = frozenset({
    "unsafe_url_syntax", "unsafe_url_scheme_or_credentials", "unsupported_port",
    "non_public_host", "credential_query_rejected", "non_public_ip",
    "dns_non_public_address", "dns_resolution_failed", "response_size_limit",
    "network_failure", "redirect_without_location", "unsupported_binary_document",
    "redirect_limit", "excluded_discovery_url", "retry_after_exceeded",
    "retry_budget_exhausted", "invalid_arxiv_abstract_page", "arxiv_version_mismatch",
})
CURATED_PAPERS_ORIGIN = "https://awesomejev.github.io/papers.json"
# json.dumps(ensure_ascii=False) leaves these unescaped, but str.splitlines()
# and many line-oriented tools treat them as record breaks.
LINE_BREAK_ESCAPES = str.maketrans({"\u0085": "\\u0085", "\u2028": "\\u2028", "\u2029": "\\u2029"})


def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class FetchError(Exception):
    """Safe, fixed-message exception: never include response text or secrets."""


def safe_exception_code(error):
    """Expose only known fixed fetch codes, never arbitrary exception messages."""
    if isinstance(error, FetchError):
        code = str(error)
        if code in SAFE_FETCH_ERRORS or re.fullmatch(r"http_[1-5][0-9]{2}", code):
            return code
        return "unclassified_fetch_error"
    name = type(error).__name__
    return name if name in {"ValueError", "TypeError", "KeyError", "AttributeError", "JSONDecodeError"} else "unclassified_error"


def error_report(errors, limit=100):
    """Count every issue before truncating the public diagnostic examples."""
    examples = sorted(errors, key=lambda r: json.dumps(r, sort_keys=True))[:limit]
    return {"error_count": len(errors), "errors": examples,
            "error_code_counts": dict(sorted(Counter(item["code"] for item in errors).items())),
            "error_examples_count": len(examples), "error_examples_truncated": len(errors) > len(examples)}


def curated_paper_seeds(path):
    """Read trusted catalog URLs, without trusting its descriptions as evidence."""
    try:
        if path.is_symlink() or path.stat().st_size > 2_000_000:
            raise ValueError("invalid_catalog_file")
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValueError):
        raise ValueError("invalid_curated_paper_catalog") from None
    if not isinstance(data, dict) or not isinstance(data.get("papers"), list):
        raise ValueError("invalid_curated_paper_catalog_schema")
    seeds = {}
    for position, paper in enumerate(data["papers"], 1):
        if (not isinstance(paper, dict) or paper.get("category") != "Papers"
                or not isinstance(paper.get("title"), str) or not paper["title"].strip()
                or len(paper["title"]) > 500 or re.search(r"[\x00-\x1f]", paper["title"])
                or not isinstance(paper.get("url"), str)
                or not re.fullmatch(r"https://arxiv\.org/(?:abs|pdf)/[0-9]{4}\.[0-9]{4,5}(?:v[1-9][0-9]*)?(?:\.pdf)?", paper["url"])):
            # Only the entry number is diagnostic; never echo malformed input.
            raise ValueError("invalid_curated_paper_entry_" + str(position))
        url = canonical_source(paper["url"])
        fetch_url = paper["url"].replace("/pdf/", "/abs/").removesuffix(".pdf")
        seeds.setdefault(url, {"url": url, "title": paper["title"].strip(),
            "fetch_url": fetch_url,
            "topic": "research-paper", "relation": "direct", "discovery_depth": 0,
            "relevance": "Direct paper listed in the maintained catalog; source-page screening does not imply full-paper review or reproduced findings.",
            "discovered_from": [CURATED_PAPERS_ORIGIN]})
    return seeds


def public_url(url: str):
    """Validate syntax before DNS or requests; document identifiers remain intact."""
    if not isinstance(url, str) or len(url) > 4096 or re.search(r"[\x00-\x20\\]", url):
        raise FetchError("unsafe_url_syntax")
    try:
        p = urllib.parse.urlsplit(url)
        host = (p.hostname or "").rstrip(".").lower()
        if p.scheme not in {"http", "https"} or not host or p.username is not None or p.password is not None:
            raise FetchError("unsafe_url_scheme_or_credentials")
        if p.port not in {None, 80 if p.scheme == "http" else 443}:
            raise FetchError("unsupported_port")
        if "." not in host and ":" not in host:
            raise FetchError("non_public_host")
        if host in {"localhost", "localhost.localdomain"} or host.endswith((".localhost", ".local", ".internal", ".home", ".lan")):
            raise FetchError("non_public_host")
        if credential_query(p.query):
            raise FetchError("credential_query_rejected")
        try:
            if not ipaddress.ip_address(host).is_global:
                raise FetchError("non_public_ip")
        except ValueError:
            host.encode("idna")
        return p
    except (ValueError, UnicodeError):
        raise FetchError("unsafe_url_syntax") from None


def public_addresses(host: str, port: int):
    """Resolve once; require every result to be global and pin the connection."""
    try:
        rows = socket.getaddrinfo(host, port, type=socket.SOCK_STREAM)
        addresses = list(dict.fromkeys(row[4][0] for row in rows))
        if not addresses or any(not ipaddress.ip_address(a).is_global for a in addresses):
            raise FetchError("dns_non_public_address")
        return addresses
    except (OSError, ValueError):
        raise FetchError("dns_resolution_failed") from None


class PublicFetcher:
    """Bounded GETs with checked redirects, DNS pinning and no ambient auth."""
    def __init__(self, retries=2, timeout=18, pause=0.0, cache_bytes=32 * 1024 * 1024, budget=SCAN_TIME_BUDGET_SECONDS):
        self.retries, self.timeout, self.pause = retries, timeout, pause
        self.cache = OrderedDict()
        self.cache_bytes = cache_bytes
        self.cached_bytes = 0
        self.lock = threading.Lock()
        self.requests = 0
        # Workers share each host's not-before time, so a Retry-After or backoff
        # delay holds every request to that host, and one scan-wide deadline.
        self.not_before = {}
        self.budget = budget
        self.deadline = time.monotonic() + budget
        self.budget_exhausted = False

    def _hold(self, host, ready=0.0, delay=0.0):
        """Wait for the host's not-before time and any new `delay`, within the deadline.

        `ready` is the time this request has already waited until; the result
        is the new one. A wait that would end at or after the deadline is not
        started: no further request is sent and the scan reports a partial result.
        """
        with self.lock:
            current = max(time.monotonic(), ready)
            shared = self.not_before.get(host, 0.0)
            until = max(shared, current + delay)
            if until >= self.deadline:
                self.budget_exhausted = True
                raise FetchError("retry_budget_exhausted")
            if delay:
                self.not_before[host] = until
        wait = max(delay, shared - current)
        if wait > 0:
            time.sleep(wait)
        return until

    def _request(self, url):
        p = public_url(url)
        host = p.hostname.encode("idna").decode("ascii")
        port = p.port or (443 if p.scheme == "https" else 80)
        addresses = public_addresses(host, port)
        connection_type = http.client.HTTPSConnection if p.scheme == "https" else http.client.HTTPConnection
        kwargs = {"timeout": self.timeout}
        if p.scheme == "https":
            kwargs["context"] = ssl.create_default_context()
        conn = connection_type(host, port, **kwargs)
        # HTTPSConnection still verifies the original hostname/SNI; only TCP is
        # pinned, preventing a second DNS resolution from reaching a private IP.
        def pinned_connection(_address, timeout, source_address=None):
            # Like socket.create_connection, try each validated address in turn.
            error = OSError("no_address")
            for address in addresses:
                if not ipaddress.ip_address(address).is_global:
                    raise FetchError("dns_non_public_address")
                try:
                    return socket.create_connection((address, port), timeout, source_address)
                except OSError as exc:
                    error = exc
            raise error
        conn._create_connection = pinned_connection
        try:
            target = urllib.parse.urlunsplit(("", "", p.path or "/", p.query, ""))
            conn.request("GET", target, headers={"User-Agent": "AwesomeJev-Public-Refresh/1.0", "Accept": "application/json,text/plain,text/html", "Accept-Encoding": "identity"})
            with self.lock:
                self.requests += 1
            response = conn.getresponse()
            headers = {k.lower(): v for k, v in response.getheaders()}
            body = response.read(MAX_BODY + 1) if response.status == 200 else b""
            if len(body) > MAX_BODY:
                raise FetchError("response_size_limit")
            return response.status, headers, body
        finally:
            conn.close()

    def fetch(self, url):
        public_url(url)
        with self.lock:
            cached = self.cache.get(url)
            if cached:
                self.cache.move_to_end(url)
        if cached:
            return cached
        current, ready = url, 0.0
        for hop in range(6):
            host = public_url(current).hostname
            for attempt in range(self.retries + 1):
                ready = self._hold(host, ready)
                try:
                    status, headers, raw = self._request(current)
                except FetchError as e:
                    if str(e) == "dns_resolution_failed" and attempt < self.retries:
                        time.sleep(min(2 ** attempt, 8))
                        continue
                    raise
                except (OSError, http.client.HTTPException):
                    if attempt == self.retries:
                        raise FetchError("network_failure") from None
                    time.sleep(min(2 ** attempt, 8))
                    continue
                if status == 429 or 500 <= status < 600:
                    if attempt == self.retries:
                        raise FetchError("http_" + str(status))
                    delay = research.retry_after_seconds(headers.get("retry-after"))
                    if delay is not None and delay > research.MAX_RETRY_AFTER_SECONDS:
                        # Never send a request the server has asked us not to send.
                        raise FetchError("retry_after_exceeded")
                    ready = self._hold(host, ready, min(2 ** attempt, 8) if delay is None else delay)
                    continue
                break
            if status in {301, 302, 303, 307, 308}:
                location = headers.get("location", "")
                if not location:
                    raise FetchError("redirect_without_location")
                target = urllib.parse.urljoin(current, location)
                public_url(target)  # Reject before the next network request.
                current = target
                continue
            if status != 200:
                raise FetchError("http_" + str(status))
            ctype = headers.get("content-type", "")
            if raw.startswith(b"%PDF") or ctype.startswith(("image/", "audio/", "video/")):
                raise FetchError("unsupported_binary_document")
            result = raw, current, ctype
            with self.lock:
                if len(raw) <= self.cache_bytes:
                    previous = self.cache.pop(url, None)
                    if previous:
                        self.cached_bytes -= len(previous[0])
                    while self.cache and self.cached_bytes + len(raw) > self.cache_bytes:
                        _, removed = self.cache.popitem(last=False)
                        self.cached_bytes -= len(removed[0])
                    self.cache[url] = result
                    self.cached_bytes += len(raw)
            if self.pause:
                time.sleep(self.pause)
            return result
        raise FetchError("redirect_limit")


def canonical_source(url):
    public_url(url)
    p = urllib.parse.urlsplit(url)
    if p.hostname in ecosystem.BLOCKED_HOSTS or p.path.lower().endswith((".png", ".jpg", ".svg", ".gif", ".woff", ".woff2", ".zip", ".tar.gz", ".mp4", ".db")):
        raise FetchError("excluded_discovery_url")
    if p.hostname in {"github.com", "www.github.com", "raw.githubusercontent.com", "huggingface.co", "hf.co"}:
        result = ecosystem.canonical(url)
    elif p.hostname == "aclanthology.org":
        result = index.canonical(url).removesuffix(".pdf")
    else:
        result = index.canonical(url)
    if not result:
        raise FetchError("excluded_discovery_url")
    public_url(result)
    return result


def identity(row):
    url = row.get("url") or row.get("canonical_url") or ""
    public_url(url)
    key = index.canonical(url)
    if urllib.parse.urlsplit(key).hostname == "github.com":
        key = key.lower()
    # Revisions are provenance, not new logical source documents.
    if key.startswith(ecosystem.SPACE_URL + "/blob/"):
        key = re.sub(r"/blob/[^/]+/", "/blob/main/", key, count=1)
    return key


def jsonl_record(row):
    """Serialize one ledger record as exactly one newline-terminated line."""
    return json.dumps(row, ensure_ascii=False, sort_keys=True).translate(LINE_BREAK_ESCAPES) + "\n"


def content_hash(row):
    return row.get("content_sha256") or row.get("abstract_sha256")


def record_safe(row):
    try:
        identity(row)
        for key in ("retrieved_url", "retrieval_url"):
            if row.get(key):
                public_url(row[key])
        for url in row.get("discovered_from", []):
            public_url(url)
        text = json.dumps(row, ensure_ascii=False)
        return not any(pattern.search(text) for pattern in LEAK_PATTERNS.values())
    except (FetchError, TypeError, ValueError):
        return False


@dataclass
class Ledger:
    rows: list[dict]
    lines: list[str]

    @classmethod
    def read(cls, path):
        if not path.exists():
            return cls([], [])
        # Records end at "\n" only; splitlines() would also break a record at
        # U+2028, U+2029 or U+0085 inside a JSON string.
        lines = re.findall(r"[^\n]*\n|[^\n]+\Z", path.read_bytes().decode("utf-8"))
        if any(not line.strip() for line in lines):
            raise ValueError("blank_ledger_record")
        return cls([json.loads(line) for line in lines], lines)


def canonical_page_observed(incoming):
    """Require an actually screened body fetched from this canonical source."""
    if incoming.get("verification_level") != "content_screened" or incoming.get("status") != "screened":
        return False
    if not re.fullmatch(r"[a-f0-9]{64}", str(incoming.get("content_sha256", ""))):
        return False
    source = incoming.get("canonical_url") or incoming.get("url")
    fetched = incoming.get("retrieved_url")
    try:
        public_url(source)
        public_url(fetched)
        return index.canonical(source) == index.canonical(fetched)
    except FetchError:
        return False


def has_abstract_provenance(record):
    return any(key in record for key in ("abstract_provider", "abstract_sha256", "canonical_page_separately_fetched"))


def arxiv_version_url(url):
    if not isinstance(url, str):
        return None
    match = re.fullmatch(r"https://arxiv\.org/(?:abs|pdf)/(\d{4}\.\d{4,5}v[1-9]\d*)(?:\.pdf)?", url)
    return "https://arxiv.org/abs/" + match[1] if match else None


def pinned_primary_abstract(row):
    version = arxiv_version_url(row.get("reviewed_version_url"))
    return (row.get("abstract_provider") == "arxiv_primary_abstract_page"
            and row.get("verification_level") == "abstract_checked"
            and bool(version) and identity(row) == index.canonical(version))


def observed_version(row):
    return next((version for field in ("observed_version_url", "reviewed_version_url", "retrieved_url", "retrieval_url")
                 if (version := arxiv_version_url(row.get(field)))), None)


def same_primary_observation(prior, incoming):
    version = observed_version(incoming)
    if version and version != arxiv_version_url(prior.get("reviewed_version_url")):
        return False
    return bool((incoming.get("abstract_sha256") and incoming["abstract_sha256"] == prior.get("abstract_sha256"))
                or (incoming.get("content_sha256") and incoming["content_sha256"] == prior.get("abstract_page_sha256")))


def primary_review_candidate(prior, incoming):
    version = observed_version(incoming)
    return {"url": identity(prior), "review_kind": "pinned_arxiv_abstract",
        "old_content_sha256": content_hash(prior), "observed_content_sha256": content_hash(incoming),
        "old_reviewed_version_url": prior.get("reviewed_version_url"), "observed_version_url": version,
        "old_first_submitted": prior.get("first_submitted", prior.get("published_at")),
        "observed_first_submitted": incoming.get("published_at"),
        "observed_abstract_sha256": incoming.get("abstract_sha256"),
        "observed_abstract_page_sha256": incoming.get("abstract_page_sha256", incoming.get("content_sha256")),
        "observed_verification_level": incoming["verification_level"],
        "retrieved_url": incoming.get("retrieved_url", incoming.get("retrieval_url")),
        "note": "Pinned primary abstract preserved without a grade change; observed version: "
                + (version or "not identified by the provider") + ". Maintainer review is required before replacing the pinned evidence."}


def merge_records(old: Ledger, incoming, max_new=None, policy=None):
    """Keep old bytes on unchanged hashes/failure; never grant editorial status."""
    rows, lines = list(old.rows), list(old.lines)
    positions, strengths, aliases = {}, {}, {}
    for i, row in enumerate(rows):
        key = identity(row)
        aliases[key] = aliases.get(key, 0) + 1
        # Historical aliases can share one logical source. Prefer protected
        # evidence, then the canonical spelling; ledger order is not authority.
        strength = (pinned_primary_abstract(row), LEVEL.get(row.get("verification_level"), 0),
                    row.get("canonical_url", row.get("url")) == key)
        if key not in positions or strength > strengths[key]:
            positions[key], strengths[key] = i, strength
    hashes = {content_hash(row) for row in rows if content_hash(row)}
    changes = {"added": [], "changed": [], "editorial_review_required": [], "duplicates": 0, "preserved_after_failure": 0, "rejected": 0, "curation_excluded": []}
    candidates, pinned_observations = {}, {}
    for row in incoming:
        if not record_safe(row):
            changes["rejected"] += 1
            continue
        if row.get("verification_level") == "editorial_reviewed":
            row = {**row, "verification_level": "content_screened",
                   "checked_via": "Automated public-source refresh; editorial review not performed."}
            if "editorial_reviewed" in row:
                row["editorial_reviewed"] = False
        key = identity(row)
        if policy and policy.exclusion(key):
            if key not in changes["curation_excluded"]:
                changes["curation_excluded"].append(key)
            continue
        if key in positions and pinned_primary_abstract(rows[positions[key]]):
            pinned_observations.setdefault(key, []).append(row)
        if key not in candidates or LEVEL.get(row.get("verification_level"), 0) > LEVEL.get(candidates[key].get("verification_level"), 0):
            candidates[key] = row
    for key, candidate in sorted(candidates.items()):
        new = dict(candidate)
        new.pop("_rank", None)
        if key in positions:
            i = positions[key]
            prior = rows[i]
            if pinned_primary_abstract(prior):
                changed = []
                for observation in pinned_observations[key]:
                    if (not content_hash(observation) or observation.get("verification_level") == "metadata_only"
                            or observation.get("status") in {"unavailable", "audit_error", "insufficient_content"}):
                        changes["preserved_after_failure"] += 1
                    elif not same_primary_observation(prior, observation):
                        changed.append(observation)
                if changed:
                    # A successful pinned-page no-op must not hide a newer
                    # abstract found by another provider in the same scan.
                    def priority(observation):
                        version = observed_version(observation)
                        return (int(version.rsplit("v", 1)[1]) if version else 0,
                                observation.get("abstract_provider") == "arxiv_primary_abstract_page")
                    changes["editorial_review_required"].append(primary_review_candidate(prior, max(changed, key=priority)))
                continue
            if content_hash(new) and content_hash(new) == content_hash(prior):
                if has_abstract_provenance(prior) and prior.get("canonical_page_separately_fetched") is not True and canonical_page_observed(new):
                    # A substantive provenance repair, not a timestamp refresh:
                    # retain every other field, including prior abstract evidence.
                    repaired = {**prior, "canonical_page_separately_fetched": True}
                    rows[i] = repaired
                    lines[i] = jsonl_record(repaired)
                    changes["changed"].append(key)
                continue
            if LEVEL.get(new.get("verification_level"), 0) < LEVEL.get(prior.get("verification_level"), 0) and prior.get("verification_level") != "editorial_reviewed":
                changes["preserved_after_failure"] += 1
                continue
            if new.get("verification_level") == "metadata_only" or new.get("status") in {"unavailable", "audit_error", "insufficient_content"}:
                changes["preserved_after_failure"] += 1
                continue
            if prior.get("verification_level") == "editorial_reviewed":
                changes["editorial_review_required"].append({"url": key, "old_content_sha256": content_hash(prior), "observed_content_sha256": content_hash(new), "observed_verification_level": new["verification_level"], "retrieved_url": new.get("retrieved_url", new.get("retrieval_url")), "note": "Prior reviewed record preserved; changed content requires maintainer review."})
                continue
            # Retain fields the machine collector does not own, including any
            # manually supplied notes; preserve explicit editorial annotations.
            merged = {**prior, **new}
            if aliases.get(key, 0) > 1:
                # Refresh one owner without turning another retained alias
                # into an exact duplicate of its stored URL identity.
                for field in ("url", "canonical_url"):
                    if field in prior:
                        merged[field] = prior[field]
                    else:
                        merged.pop(field, None)
            for field in ("editorial_note", "manual_notes", "reviewed_by", "review_date", "curated"):
                if field in prior:
                    merged[field] = prior[field]
            if has_abstract_provenance(merged) and new.get("verification_level") == "content_screened":
                merged["canonical_page_separately_fetched"] = canonical_page_observed(new)
            rows[i] = merged
            lines[i] = jsonl_record(merged)
            if content_hash(merged):
                hashes.add(content_hash(merged))
            changes["changed"].append(key)
        else:
            if max_new is not None and len(changes["added"]) >= max_new:
                continue
            if content_hash(new) and content_hash(new) in hashes:
                changes["duplicates"] += 1
                continue
            if has_abstract_provenance(new) and new.get("verification_level") == "content_screened":
                new["canonical_page_separately_fetched"] = canonical_page_observed(new)
            positions[key] = len(rows)
            rows.append(new)
            separator = "\n" if lines and not lines[-1].endswith("\n") else ""
            lines.append(separator + jsonl_record(new))
            if content_hash(new):
                hashes.add(content_hash(new))
            changes["added"].append(key)
    return Ledger(rows, lines), changes


def route_observations(originals, ecosystem_rows, research_rows):
    """Send observations to an existing owner; retain historical duplicate rows."""
    owners, strengths = {}, {}
    for number, ledger in enumerate(originals):
        for row in ledger.rows:
            key = identity(row)
            strength = (pinned_primary_abstract(row), LEVEL.get(row.get("verification_level"), 0))
            if key not in owners or strength > strengths[key]:
                owners[key], strengths[key] = number, strength
    routed = [[], []]
    for default_owner, batch in enumerate((ecosystem_rows, research_rows)):
        for row in batch:
            try:
                key = identity(row)
            except (FetchError, TypeError, ValueError):
                routed[default_owner].append(row)  # merge_records records the rejection.
                continue
            owner = owners.setdefault(key, default_owner)
            routed[owner].append(row)
    return routed


class ArxivAbstractPage(HTMLParser):
    """Parse source text only; never execute paper HTML or its instructions."""
    def __init__(self):
        super().__init__()
        self.in_abstract = self.in_version = False
        self.parts, self.version, self.published_at = [], None, None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "blockquote" and "abstract" in (attrs.get("class") or "").split():
            self.in_abstract = True
        if tag == "td" and "arxividv" in (attrs.get("class") or "").split():
            self.in_version = True
        if self.in_version and tag == "a":
            self.version = arxiv_version_url(attrs.get("href")) or self.version
        if tag == "meta" and attrs.get("name") == "citation_date":
            value = (attrs.get("content") or "").replace("/", "-")
            if re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
                self.published_at = value

    def handle_endtag(self, tag):
        if tag == "blockquote":
            self.in_abstract = False
        if tag == "td":
            self.in_version = False

    def handle_data(self, data):
        if self.in_abstract:
            self.parts.append(data)


class Scan:
    def __init__(self, fetcher, workers=8, curated_seeds=None, policy=None, pinned_sources=None, known_keys=None):
        self.fetcher, self.workers = fetcher, workers
        self.curated_seeds, self.policy = curated_seeds or {}, policy
        self.pinned_sources = pinned_sources or {}
        self.known_keys = set(known_keys or ())
        self.curation_excluded = set()
        self.errors, self.excluded = [], 0
        self.lock = threading.Lock()
        self.index_revision = None
        self.api_gate = threading.Lock()
        self.next_api_request = 0.0
        self.successful_queries = 0

    def error(self, url, code):
        try:
            public_url(url)
            item = {"url": url, "code": code[:80]}
        except FetchError:
            item = {"url_sha256": hashlib.sha256(str(url).encode()).hexdigest(), "code": "unsafe_discovery_url"}
        with self.lock:
            self.errors.append(item)

    def discover_index(self):
        seeds, records = {}, []
        try:
            info = json.loads(self.fetcher.fetch("https://huggingface.co/api/spaces/" + ecosystem.SPACE)[0])
            revision = info["sha"]
            if not re.fullmatch(r"[a-f0-9]{40}", revision):
                raise ValueError("invalid_revision")
            self.index_revision = revision
        except (FetchError, ValueError, KeyError, TypeError) as e:
            self.error(ecosystem.SPACE_URL, "index_discovery_failed:" + safe_exception_code(e))
            return records, seeds
        base = ecosystem.SPACE_URL + "/raw/" + revision + "/"
        files = {}
        for name in ("README.md", "news.html", "data/index.json", "data/methodology.json", "data/vision.json", "data/v03.json"):
            try:
                raw, resolved, _ = self.fetcher.fetch(base + name)
                parsed = json.loads(raw) if name.endswith(".json") else None
                if len(raw) < 100 or name.endswith(".json") and not isinstance(parsed, dict):
                    raise ValueError("insufficient_index_content")
                files[name] = parsed if parsed is not None else raw.decode("utf-8", errors="replace")
                records.append({"url": ecosystem.SPACE_URL if name == "README.md" else ecosystem.SPACE_URL + "/blob/main/" + name,
                    "title": "Jev Decision Index — " + name, "topic": "community-evaluation-index", "relation": "direct", "verification_level": "content_screened", "status": "screened", "retrieved_at": now(), "retrieved_url": resolved, "resolved_revision": revision, "content_sha256": hashlib.sha256(raw).hexdigest(), "content_bytes": len(raw), "checked_via": "Automated retrieval and structural inspection of current community index source; not editorial review.", "evidence": "Current public index document parsed for linked artifacts and evaluation provenance.", "relevance": "Community source for independent Jev-inspired implementations and evaluation.", "discovered_from": [ecosystem.SPACE_URL]})
            except (FetchError, ValueError, TypeError) as e:
                self.error(base + name, "index_file_failed:" + safe_exception_code(e))

        def add(url, topic, relation, origin, why):
            try:
                key = canonical_source(url)
                if key == ecosystem.SPACE_URL:
                    return
                seeds.setdefault(key, {"url": key, "title": key.rsplit("/", 1)[-1], "topic": topic, "relation": relation, "relevance": why, "discovered_from": [origin], "discovery_depth": 0})
            except FetchError:
                self.excluded += 1
        readme = files.get("README.md", "")
        front = readme.split("---")[1] if isinstance(readme, str) and readme.count("---") >= 2 else ""
        for model in re.findall(r"^-\s+([^\s]+/[^\s]+)\s*$", front, re.M):
            add("https://huggingface.co/" + model, "decision-model-card", "direct", base + "README.md", "Model explicitly linked by the current Jev Decision Index.")
        idx = files.get("data/index.json") or {}
        for model in as_list(idx.get("models")) if isinstance(idx, dict) else []:
            if not isinstance(model, dict):
                continue
            meta = model.get("meta") or {}
            for field, topic in (("model_url", "decision-model-card"), ("code_url", "implementation-repository")):
                if isinstance(meta, dict) and meta.get(field):
                    add(meta[field], topic, "direct", base + "data/index.json", "Artifact linked by current evaluated-entrant metadata.")
        for url in ecosystem.links(str(files.get("news.html", ""))):
            add(url, "ecosystem-news-artifact", "direct", base + "news.html", "Artifact linked by the current community news corpus; source claims require separate validation.")
        methodology = files.get("data/methodology.json") or {}
        if isinstance(methodology, dict):
            for bench in as_list(methodology.get("benchmarks")) + as_list(methodology.get("added_benchmarks")):
                for url in ecosystem.links(json.dumps(bench)):
                    add(url, "benchmark-source", "adjacent", base + "data/methodology.json", "Upstream evaluation source cited by the Decision Index methodology.")
            reproduction = methodology.get("reproduce")
            repo = reproduction.get("github") if isinstance(reproduction, dict) else None
            if repo:
                add(repo, "evaluation-harness", "direct", base + "data/methodology.json", "Public reproduction harness linked by the index; private tests may remain unavailable.")
        for url in ecosystem.links(json.dumps(files.get("data/vision.json", {}))):
            add(url, "vision-decision-artifact", "direct", base + "data/vision.json", "Artifact linked by the current vision evaluation metadata.")
        return records, seeds

    def audit_source(self, seed):
        """Keep logical identity separate from the exact page requested."""
        key = identity(seed)
        target = seed.get("fetch_url", seed["url"])
        request_seed = {k: v for k, v in seed.items() if k != "fetch_url"}
        request_seed["url"] = target
        row, children = ecosystem.audit(request_seed)
        ecosystem.classify_relation(row)
        row["url"] = key
        if key not in self.pinned_sources:
            return [row], children

        observations = []
        # Check the pinned evidence and observe the current public version.
        # The latter is only a review candidate, never an automatic repinning.
        for requested in dict.fromkeys((target, key)):
            if requested == target and row.get("verification_level") == "metadata_only":
                self.error(requested, row.get("status", "content_unavailable"))
                continue
            try:
                raw, final, _ = self.fetcher.fetch(requested)
                parser = ArxivAbstractPage()
                parser.feed(raw.decode("utf-8"))
                abstract = re.sub(r"^\s*Abstract:\s*", "", " ".join(" ".join(parser.parts).split()))
                if (len(abstract.split()) < 30 or not parser.version
                        or index.canonical(parser.version) != key or index.canonical(final) != key):
                    raise FetchError("invalid_arxiv_abstract_page")
                if arxiv_version_url(requested) and parser.version != arxiv_version_url(requested):
                    raise FetchError("arxiv_version_mismatch")
                observations.append({"url": key, "title": seed["title"], "topic": "research-paper",
                    "relation": "direct", "verification_level": "abstract_checked", "status": "screened",
                    "retrieved_at": now(), "retrieval_url": final, "retrieval_status": "success", "http_status": 200,
                    "abstract_provider": "arxiv_primary_abstract_page", "abstract_sha256": research.sha(abstract),
                    "abstract_page_sha256": hashlib.sha256(raw).hexdigest(), "abstract_word_count": len(abstract.split()),
                    "observed_version_url": parser.version, "published_at": parser.published_at,
                    "canonical_page_separately_fetched": True, "full_text_reviewed": False, "editorial_reviewed": False,
                    "relevance": "Observed primary abstract for a pinned paper; changes require maintainer review.",
                    "screening_method": "Primary arXiv abstract and version metadata only; no full-paper review or reproduction."})
            except (FetchError, ValueError, UnicodeError, AttributeError) as error:
                self.error(requested, "pinned_paper_observation_failed:" + safe_exception_code(error))
        return observations, children if observations else []

    def scan_ecosystem(self, old, max_new=None, smoke=False):
        records, seeds = self.discover_index()
        for key, seed in self.curated_seeds.items():
            origins = set(seeds.get(key, {}).get("discovered_from", [])) | set(seed["discovered_from"])
            seeds[key] = {**seed, "discovered_from": sorted(origins)}
        for key, prior in self.pinned_sources.items():
            seed = seeds.get(key, {"url": key, "title": prior["title"], "topic": "research-paper",
                "relation": "direct", "discovery_depth": 0, "relevance": prior["relevance"]})
            target = arxiv_version_url(seed.get("fetch_url")) or prior["reviewed_version_url"]
            seeds[key] = {**seed, "fetch_url": target}
        old_keys = {identity(r) for r in old.rows} | set(self.pinned_sources) | self.known_keys
        for row in old.rows:
            key = identity(row)
            if key == ecosystem.SPACE_URL or key.startswith(ecosystem.SPACE_URL + "/blob/"):
                continue
            seeds.setdefault(key, {"url": row.get("url", key), "title": row.get("title", key), "topic": row.get("topic", "ecosystem-artifact"), "relation": row.get("relation", "adjacent"), "relevance": row.get("relevance", "Previously recorded public source."), "discovered_from": row.get("discovered_from", []), "discovery_depth": row.get("discovery_depth", 0)})
        visited, new_attempts = set(), 0
        original = ecosystem.fetch
        ecosystem.fetch = self.fetcher.fetch
        try:
            for depth in (0, 1):
                batch = []
                for key, seed in sorted(seeds.items()):
                    if key in visited or seed.get("discovery_depth", 0) > depth:
                        continue
                    if self.policy and self.policy.exclusion(key):
                        self.curation_excluded.add(key)
                        continue
                    if key not in old_keys:
                        if max_new is not None and new_attempts >= max_new:
                            continue
                        new_attempts += 1
                    batch.append(seed)
                    visited.add(key)
                if smoke:
                    batch = batch[:8]
                print(json.dumps({"phase": "ecosystem", "depth": depth, "documents": len(batch)}), flush=True)
                with cf.ThreadPoolExecutor(max_workers=self.workers) as pool:
                    futures = {pool.submit(self.audit_source, seed): seed for seed in batch}
                    for i, future in enumerate(cf.as_completed(futures), 1):
                        seed = futures[future]
                        try:
                            observations, children = future.result()
                            for row in observations:
                                if row.get("verification_level") == "metadata_only":
                                    self.error(seed["url"], row.get("status", "content_unavailable"))
                                if ecosystem.eligible(row):
                                    records.append(row)
                                else:
                                    self.excluded += 1
                            for child in children:
                                try:
                                    key = canonical_source(child["url"])
                                    child["url"] = key
                                    seeds.setdefault(key, child)
                                except FetchError:
                                    self.excluded += 1
                        except (FetchError, ValueError, TypeError, KeyError, AttributeError) as e:
                            self.error(seed["url"], "document_failed:" + safe_exception_code(e))
                        if i % 200 == 0:
                            print(json.dumps({"phase": "ecosystem", "completed": i}), flush=True)
        finally:
            ecosystem.fetch = original
        return records

    def query(self, topic, query, provider):
        if provider == "openalex_api":
            url = research.OPENALEX_API + "?" + urllib.parse.urlencode({"filter": "title.search:" + query, "per-page": 200, "select": "id,doi,title,authorships,publication_year,abstract_inverted_index,primary_location,locations"})
        else:
            url = research.API + "?" + urllib.parse.urlencode({"q": query, "limit": 120})
        with self.api_gate:
            delay = max(0, self.next_api_request - time.monotonic())
            if delay:
                time.sleep(delay)
            self.next_api_request = time.monotonic() + .4
        try:
            raw, final, _ = self.fetcher.fetch(url)
            data = json.loads(raw)
            if provider == "openalex_api":
                data = research.convert_openalex(data.get("results", []))
            if not isinstance(data, list):
                raise ValueError("invalid_paper_response")
            clean = []
            for item in data:
                if not isinstance(item, dict):
                    continue
                paper = item.get("paper", item)
                if not isinstance(paper, dict):
                    continue
                paper = dict(paper)
                for key in ("title", "summary"):
                    paper[key] = paper.get(key) if isinstance(paper.get(key), str) else ""
                paper["authors"] = [{"name": a["name"]} for a in as_list(paper.get("authors")) if isinstance(a, dict) and isinstance(a.get("name"), str)]
                clean.append({"paper": paper})
            with self.lock:
                self.successful_queries += 1
            return topic, query, {"data": clean, "provider": provider, "retrieval_url": final, "retrieved_at": now(), "http_status": 200}
        except (FetchError, ValueError, TypeError, KeyError, AttributeError) as e:
            self.error(url, "paper_query_failed:" + safe_exception_code(e))
            return topic, query, {"data": []}

    def scan_research(self, smoke=False):
        jobs = [("direct", q, research.PROVIDER) for q in DIRECT_QUERIES]
        background = [(t, q, research.PROVIDER) for t, queries in research.QUERIES.items() for q in queries]
        background += [(t, q, "openalex_api") for t, queries in research.OPENALEX_QUERIES.items() for q in queries]
        jobs += background[:2] if smoke else background
        with cf.ThreadPoolExecutor(max_workers=min(self.workers, 3)) as pool:
            results = list(pool.map(lambda args: self.query(*args), jobs))
        records, _ = research.build_records(results)
        for row in records:
            row.pop("_rank", None)
        direct = []
        for _, query, wrapper in results:
            for item in wrapper.get("data", []):
                paper = item.get("paper", item)
                pid = re.sub(r"v\d+$", "", str(paper.get("id", "")))
                title = " ".join(str(paper.get("title", "")).split())
                abstract = " ".join(str(paper.get("summary", "")).split())
                text = title + " " + abstract
                if not direct_paper(title, abstract) or len(abstract.split()) < 30 or not re.fullmatch(r"\d{4}\.\d{4,5}", pid):
                    continue
                direct.append({"url": "https://arxiv.org/abs/" + pid, "title": title, "authors": [a.get("name", "") for a in paper.get("authors", []) if a.get("name")], "published_at": paper.get("publishedAt"), "topic": "direct-decision-research", "relation": "direct", "verification_level": "abstract_checked", "status": "screened", "retrieval_status": "success", "http_status": 200, "editorial_reviewed": False, "retrieved_at": wrapper["retrieved_at"], "retrieval_url": wrapper["retrieval_url"], "abstract_provider": wrapper["provider"], "abstract_sha256": research.sha(abstract), "abstract_word_count": len(abstract.split()), "evidence_excerpt": research.evidence(abstract, ["Jev", "decision"]), "relevance": "Original abstract explicitly discusses Jev or typed decision models; findings remain author-reported.", "screening_method": "Direct Jev/typed-decision title-and-abstract rules; no full-paper review or reproduction.", "full_text_reviewed": False, "canonical_page_separately_fetched": False, "discovery_queries": [query]})
        return records, direct


def as_list(value):
    return value if isinstance(value, list) else []


def direct_paper(title, abstract):
    text = title + " " + abstract
    explicit = bool(re.search(r"typesafe|typed[- ]decision|system[- ]one models?|\brlcd\b", text, re.I))
    if re.search(r"japanese encephalitis|encephalitis virus", text, re.I) and not re.search(r"typesafe", text, re.I):
        return False
    if explicit:
        return bool(re.search(r"decision|probabilit|calibrat", text, re.I))
    return bool(re.search(r"\bjev\b", text, re.I) and re.search(r"\bllms?\b|language models?|artificial intelligence|neural (?:model|network)", text, re.I) and re.search(r"decision|probabilit|calibrat", text, re.I))


def pending_reviews(previous, observed, current_rows):
    """Carry unresolved human review across provider failures; compare capped semantics."""
    current = {identity(r): r for r in current_rows}
    def resolved(item):
        row = current.get(item.get("url"))
        if row is None:
            return True
        if item.get("review_kind") == "pinned_arxiv_abstract":
            version = item.get("observed_version_url")
            if version and arxiv_version_url(row.get("reviewed_version_url")) != version:
                return False
            abstract = item.get("observed_abstract_sha256")
            return (row.get("abstract_sha256") == abstract if abstract else
                    row.get("abstract_page_sha256") == item.get("observed_abstract_page_sha256"))
        return content_hash(row) == item.get("observed_content_sha256")
    def signature(item):
        return (item.get("url"), item.get("old_content_sha256"), item.get("observed_content_sha256"),
                item.get("review_kind"), item.get("old_reviewed_version_url"), item.get("observed_version_url"))
    def pinned_version_number(item):
        version = arxiv_version_url(item.get("observed_version_url"))
        if item.get("review_kind") != "pinned_arxiv_abstract" or not version:
            return 0
        return int(version.rsplit("v", 1)[1])
    pending = {}
    for item in previous.get("editorial_refresh_candidates", []):
        if isinstance(item, dict) and item.get("url") in current and not resolved(item):
            pending[item["url"]] = item
    for item in observed:
        prior = pending.get(item["url"])
        if prior and signature(prior) == signature(item):
            continue
        if prior and pinned_version_number(prior) > pinned_version_number(item):
            # A stale or versionless provider response after a failed latest-page
            # probe cannot erase an already observed, unresolved newer revision.
            continue
        pending[item["url"]] = item
    result = [pending[k] for k in sorted(pending)][:100]
    def semantic(items):
        return sorted(signature(r) for r in items)[:100]
    changed = semantic(result) != semantic(previous.get("editorial_refresh_candidates", []))
    return result, changed, len(pending)


def write_if_changed(path, text):
    if path.exists() and path.read_bytes() == text.encode("utf-8"):
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".refresh-tmp")
    temp.write_text(text, encoding="utf-8", newline="\n")
    temp.replace(path)
    return True


def prune_promoted_exclusions(excluded: Ledger, accepted_rows) -> tuple[Ledger, list[str]]:
    """Drop exclusion-screen rows for sources that a later screen accepted.

    Keeping both would record two opposite decisions about one source.
    """
    accepted = {identity(row) for row in accepted_rows}
    kept = [(row, line) for row, line in zip(excluded.rows, excluded.lines) if identity(row) not in accepted]
    pruned = sorted({identity(row) for row in excluded.rows} & accepted)
    return Ledger([row for row, _ in kept], [line for _, line in kept]), pruned


def publish_summary(report):
    text = "\n".join(["## Public source scan", "", "Status: **" + report["status"] + "**.", f"Added: {report['added_count']}; updated: {report['changed_count']}; source changes awaiting review: {report['editorial_review_required_count']}.", f"Provider/document issues: {report['error_count']}. Earlier evidence was retained on failures.", f"Diagnostic examples stored: {report['error_examples_count']} of {report['error_count']}; error_code_counts covers all issues.", *([f"Retry budget exhausted: no requests were sent after {report['retry_budget_seconds'] // 60} minutes; unscanned sources keep their earlier evidence."] if report.get("retry_budget_exhausted") else []), "","Automated source screening is not scientific review or reproduction. No source instructions or downloaded code were executed.", ""])
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as f:
            f.write(text)
    if os.environ.get("GITHUB_OUTPUT"):
        with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as f:
            f.write("changed=" + str(report["changed"]).lower() + "\n")
            for key in ("added_count", "changed_count", "editorial_review_required_count", "error_count"):
                f.write(key + "=" + str(report[key]) + "\n")


def main(argv=None):
    started_at = now()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workers", type=int, default=8, help="Public document fetch concurrency (1–16); scholarly API concurrency is at most 3")
    parser.add_argument("--max-new", type=int, default=None, help="Optional cap on newly added records; existing records are retained")
    parser.add_argument("--smoke", action="store_true", help="Small real-network dry-run; do not write ledgers, generated files or scan report")
    args = parser.parse_args(argv)
    if not 1 <= args.workers <= 16 or args.max_new is not None and args.max_new < 0:
        parser.error("workers must be 1–16 and max-new nonnegative")
    paths = [ROOT / "data/ecosystem-sources.jsonl", ROOT / "data/research-sources.jsonl"]
    originals = [Ledger.read(path) for path in paths]
    policy = load_policy(ROOT / "data/source-curation.json", index.canonical)
    try:
        curated_seeds = curated_paper_seeds(ROOT / "site/papers.json")
    except ValueError as error:
        parser.error(str(error))
    fetcher = PublicFetcher()
    pinned_sources = {identity(row): row for ledger in originals for row in ledger.rows if pinned_primary_abstract(row)}
    scan = Scan(fetcher, args.workers, curated_seeds=curated_seeds, policy=policy, pinned_sources=pinned_sources,
                known_keys={identity(row) for ledger in originals for row in ledger.rows})
    limit = min(args.max_new, 5) if args.smoke and args.max_new is not None else 5 if args.smoke else args.max_new
    ecosystem_rows = scan.scan_ecosystem(originals[0], limit, args.smoke)
    research_rows, direct = scan.scan_research(args.smoke)
    ecosystem_input, research_input = route_observations(originals, ecosystem_rows + direct, research_rows)
    merged_ecosystem, ec = merge_records(originals[0], ecosystem_input, limit, policy=policy)
    remaining = None if limit is None else max(0, limit - len(ec["added"]))
    merged_research, rc = merge_records(originals[1], research_input, remaining, policy=policy)
    changes = {k: ec[k] + rc[k] for k in ("added", "changed", "editorial_review_required")}
    report_path = ROOT / "data/scan-latest.json"
    previous = json.loads(report_path.read_text(encoding="utf-8")) if report_path.exists() else {}
    pending, pending_changed, pending_count = pending_reviews(previous, changes["editorial_review_required"], merged_ecosystem.rows + merged_research.rows)
    changed = bool(changes["added"] or changes["changed"] or pending_changed)
    successful_content = sum(r.get("verification_level") != "metadata_only" for r in ecosystem_rows) + scan.successful_queries
    status = "failed" if not successful_content else "partial" if scan.errors or fetcher.budget_exhausted else "success"
    if status == "failed":
        changed = False
    excluded_path = ROOT / "data/ecosystem-sources.excluded.jsonl"
    excluded, promoted = prune_promoted_exclusions(Ledger.read(excluded_path), merged_ecosystem.rows + merged_research.rows)
    if not args.smoke:
        for path, ledger in zip(paths, (merged_ecosystem, merged_research)):
            write_if_changed(path, "".join(ledger.lines))
        if promoted:
            write_if_changed(excluded_path, "".join(excluded.lines))
        subprocess.run([sys.executable, str(ROOT / "scripts/build_source_index.py")], cwd=ROOT, check=True)
        counts = json.loads((ROOT / "data/source-counts.json").read_text(encoding="utf-8"))["counts"]
    else:
        counts = json.loads((ROOT / "data/source-counts.json").read_text(encoding="utf-8"))["counts"]
    report = {"schema_version": 1, "started_at": started_at, "completed_at": now(), "status": status, "changed": changed, "dry_run": args.smoke, "added_count": len(changes["added"]), "changed_count": len(changes["changed"]), "editorial_review_required_count": pending_count, "added_urls": changes["added"][:100], "changed_urls": changes["changed"][:100], "editorial_refresh_candidates": pending, "editorial_examples_truncated": pending_count > 100, **error_report(scan.errors), "counts": counts, "index_revision": scan.index_revision, "network_requests": fetcher.requests, "retry_budget_exhausted": fetcher.budget_exhausted, "retry_budget_seconds": fetcher.budget,"excluded_discoveries": scan.excluded, "preserved_after_failure": ec["preserved_after_failure"] + rc["preserved_after_failure"], "duplicate_candidates_skipped": ec["duplicates"] + rc["duplicates"], "privacy_rejected_records": ec["rejected"] + rc["rejected"], "verification_note": "Public document or original-abstract machine screening only. Pinned primary abstracts and editorial records are preserved; their source changes require maintainer review. Metadata-only records do not count as checked sources."}
    report["curation_excluded_count"] = len(set(ec["curation_excluded"] + rc["curation_excluded"]) | scan.curation_excluded)
    # Report every attempt, including failures. The publisher must gate on
    # report.changed, not this report's timestamp or a raw git-diff count.
    if not args.smoke:
        write_if_changed(report_path, json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    publish_summary(report)
    print(json.dumps(report, ensure_ascii=False, indent=2), flush=True)
    return 1 if status == "failed" else 0


if __name__ == "__main__":
    raise SystemExit(main())
