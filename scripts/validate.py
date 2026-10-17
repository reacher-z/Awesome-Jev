#!/usr/bin/env python3
"""Offline repository checks using only Python's standard library and Node.js.

Checks links, source provenance/schema, deterministic index counts, syntax, and
common publication leaks. These checks do not establish scientific validity or
replace a maintainer's review. No external source URLs are requested.
"""

from __future__ import annotations

import ast
import collections
import html
from html.parser import HTMLParser
import ipaddress
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
from urllib.parse import parse_qsl, unquote, urlsplit

try:
    from . import build_source_index as source_index
    from .source_policy import load_policy, PolicyError
except ImportError:
    import build_source_index as source_index
    from source_policy import load_policy, PolicyError

ROOT = Path(__file__).resolve().parents[1]
SKIP = {".git", "node_modules", ".venv", "__pycache__", ".cache", "tmp", "artifacts"}
TEXT_SUFFIXES = {".md", ".py", ".js", ".mjs", ".json", ".jsonl", ".yml", ".yaml", ".html", ".css", ".svg", ".xml", ".bib", ".txt"}
LEVELS = {"metadata_only", "abstract_checked", "content_screened", "editorial_reviewed"}
CHECKED = LEVELS - {"metadata_only"}
HASH = re.compile(r"^[0-9a-f]{64}$")
HTML_ENTITY = re.compile(r"&(?:amp|lt|gt|quot|apos|#\d+|#x[0-9a-f]+);", re.I)
LEAK_PATTERNS = {
    "personal filesystem path": re.compile(r"(?:/Users/[A-Za-z0-9_.-]+/|/home/[A-Za-z0-9_.-]+/|[A-Z]:\\Users\\[^\\\s]+\\)"),
    "GitHub credential": re.compile(r"(?:gh[pousr]_[A-Za-z0-9]{30,255}|github_pat_[A-Za-z0-9_]{40,255})"),
    "model API credential": re.compile(r"(?:\bhf_[A-Za-z0-9]{30,100}\b|\bsk-(?:proj-)?[A-Za-z0-9_-]{24,255}\b)"),
    "cloud access key": re.compile(r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b"),
    "private key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "credential-bearing URL": re.compile(r"https?://[^\s/@:]+:[^\s/@]+@[^\s/]+"),
}
errors: list[str] = []


def fail(location: str, message: str) -> None:
    # Never print a matched credential or the offending source line.
    for pattern in LEAK_PATTERNS.values():
        location = pattern.sub("[redacted]", location)
    errors.append(f"{location}: {message}")


def files() -> list[Path]:
    return sorted(p for p in ROOT.rglob("*") if p.is_file() and not any(part in SKIP for part in p.relative_to(ROOT).parts))


def check_symlinks() -> None:
    # files() keeps only regular files, so a symlinked directory, which the Pages
    # artifact dereferences, or a dangling link would escape the rule and leak scan.
    for directory, names, filenames in os.walk(ROOT):
        names[:] = sorted(name for name in names if name not in SKIP)
        for name in names + sorted(filenames):
            path = Path(directory, name)
            if path.is_symlink() and not path.is_file():
                fail(str(path.relative_to(ROOT)), "symlinks are not supported in the published artifact")


def public_url(value: object) -> bool:
    if not isinstance(value, str):
        return False
    try:
        p = urlsplit(value)
        if p.scheme not in {"http", "https"} or not p.hostname or p.username or p.password:
            return False
        if p.hostname in {"localhost", "localhost.localdomain"} or p.hostname.endswith((".local", ".internal")):
            return False
        try:
            if not ipaddress.ip_address(p.hostname).is_global:
                return False
        except ValueError:
            if "." not in p.hostname:
                return False
        return not any(k.casefold() in {"api_key", "apikey", "access_token", "token", "signature"} for k, _ in parse_qsl(p.query))
    except ValueError:
        return False


class Markup(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[str] = []
        self.ids: set[str] = set()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        for key, value in attrs:
            if key in {"href", "src", "xlink:href"} and value:
                self.links.append(value)
            if key in {"id", "name"} and value:
                self.ids.add(value)


def anchors(path: Path) -> set[str]:
    text = path.read_text(encoding="utf-8")
    if path.suffix == ".md":
        # Fenced examples are not rendered, so their comments and tags define no anchors.
        text = re.sub(r"```.*?```|~~~.*?~~~", "", text, flags=re.S)
    parser = Markup()
    parser.feed(text)
    result = parser.ids
    seen: collections.Counter[str] = collections.Counter()
    if path.suffix == ".md":
        for heading in re.findall(r"^ {0,3}#{1,6}\s+(.+?)\s*#*\s*$", text, re.M):
            heading = re.sub(r"<[^>]+>", "", html.unescape(heading))
            heading = re.sub(r"\[([^]]+)\]\([^)]*\)", r"\1", heading)
            slug = re.sub(r"[^\w\- ]", "", heading.casefold()).replace(" ", "-")
            suffix = f"-{seen[slug]}" if seen[slug] else ""
            result.add(slug + suffix)
            seen[slug] += 1
    return result


# Absolute links to this project's own website (served from site/) and repository
# tree are checked like local links; every other external URL stays offline.
OWN_LINKS = (
    (re.compile(r"https://awesomejev\.github\.io(?=[/?#]|$)", re.I), "site"),
    (re.compile(r"https://github\.com/reacher-z/Awesome-Jev/(?:blob|tree)/main(?=[/?#]|$)", re.I), ""),
)


def own_link(value: str) -> tuple[Path, str] | None:
    for pattern, folder in OWN_LINKS:
        if match := pattern.match(value):
            return ROOT / folder, "/" + value[match.end():].lstrip("/")
    return None


def local_link(path: Path, value: str) -> None:
    value = html.unescape(value.strip().strip("<>"))
    base, link = own_link(value) or (ROOT / "site" if "site" in path.relative_to(ROOT).parts else ROOT, value)
    parsed = urlsplit(link)
    if parsed.scheme or parsed.netloc or not value or value == "#" or value.startswith("{{"):
        return
    target = ((base / parsed.path.lstrip("/")) if parsed.path.startswith("/") else (path.parent / unquote(parsed.path))).resolve() if parsed.path else path
    if not target.is_relative_to(ROOT):
        fail(str(path.relative_to(ROOT)), "local link escapes repository")
        return
    if target.is_dir():
        target = next((target / n for n in ("index.html", "README.md") if (target / n).is_file()), target)
    if not target.exists():
        fail(str(path.relative_to(ROOT)), f"missing local target: {value}")
    elif parsed.fragment and target.is_file() and target.suffix in {".md", ".html", ".svg"}:
        if unquote(parsed.fragment) not in anchors(target):
            fail(str(path.relative_to(ROOT)), f"missing local anchor: {value}")


def check_text(path: Path, text: str) -> None:
    relative = str(path.relative_to(ROOT))
    is_html_template = path.suffix == ".html" and "templates" in path.relative_to(ROOT).parts
    for label, pattern in LEAK_PATTERNS.items():
        if pattern.search(text):
            fail(relative, f"possible {label}; inspect locally (value redacted)")
    if path.suffix in {".md", ".html", ".svg"} and not is_html_template:
        parser = Markup()
        parser.feed(text)
        for link in parser.links:
            local_link(path, link)
        if path.suffix == ".md":
            # Fenced examples are not rendered links.
            rendered = re.sub(r"```.*?```|~~~.*?~~~", "", text, flags=re.S)
            for link in re.findall(r"\[[^\]]*\]\(\s*(<[^>]+>|[^\s)]+)(?:\s+[^)]*)?\)", rendered):
                local_link(path, link)
            for link in re.findall(r"^\s*\[[^]]+\]:\s*(\S+)", rendered, re.M):
                local_link(path, link)
    if path.suffix in {".css", ".html"} and not is_html_template:
        for link in re.findall(r"url\(\s*['\"]?([^)'\"]+)['\"]?\s*\)", text):
            local_link(path, link.strip())
    if path.suffix == ".py":
        try:
            ast.parse(text, filename=relative)
        except SyntaxError as exc:
            fail(relative, f"Python syntax error at line {exc.lineno}")


def check_json(path: Path, text: str) -> None:
    # Published data files must parse even when no script reads them.
    relative = path.relative_to(ROOT).as_posix()

    def reject_constant(value: str) -> None:
        raise ValueError(value)

    try:
        json.loads(text, parse_constant=reject_constant)
    except json.JSONDecodeError as exc:
        fail(relative, f"invalid JSON at line {exc.lineno}, column {exc.colno}")
    except ValueError as exc:
        fail(relative, f"invalid JSON constant {exc}")


def check_ledger(path: Path, policy=None) -> list[dict]:
    result: list[dict] = []
    urls: set[str] = set()
    for number, line in enumerate(path.read_text(encoding="utf-8").split("\n"), 1):
        if not line.strip():
            continue
        location = f"{path.relative_to(ROOT)}:{number}"
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            fail(location, "invalid JSON record")
            continue
        if not isinstance(row, dict):
            fail(location, "record must be an object")
            continue
        result.append(row)
        url = row.get("canonical_url", row.get("url"))
        if policy and isinstance(url, str) and ".excluded." not in path.name and policy.exclusion(url):
            fail(location, "source is explicitly excluded by data/source-curation.json")
        if not public_url(url):
            fail(location, "canonical URL must be public HTTP(S), without credentials")
        elif url in urls:
            fail(location, "duplicate canonical URL in ledger")
        else:
            urls.add(url)
        for key in ("title", "topic", "relation", "retrieved_at", "verification_level", "relevance"):
            if not isinstance(row.get(key), str) or not row[key].strip():
                fail(location, f"missing nonempty {key}")
        if row.get("verification_level") not in LEVELS:
            fail(location, "unknown verification level")
        for key in ("retrieval_url", "retrieved_url"):
            if row.get(key) and not public_url(row[key]):
                fail(location, f"invalid public {key}")
        for key in ("url", "canonical_url", "retrieval_url", "retrieved_url"):
            if isinstance(row.get(key), str) and HTML_ENTITY.search(row[key]):
                fail(location, f"{key} contains an HTML entity; store the unescaped URL")
        for key in ("abstract_sha256", "content_sha256"):
            if row.get(key) and (not isinstance(row[key], str) or not HASH.fullmatch(row[key])):
                fail(location, f"invalid {key}")
        if row.get("verification_level") == "abstract_checked":
            if not HASH.fullmatch(str(row.get("abstract_sha256", ""))) or not isinstance(row.get("abstract_word_count"), int) or row["abstract_word_count"] < 30:
                fail(location, "abstract screening requires a substantive abstract and SHA-256")
            if row.get("retrieval_status") != "success" or row.get("http_status") != 200:
                fail(location, "abstract screening requires successful retrieval")
            if not row.get("screening_method") or not isinstance(row.get("abstract_provider"), str) or not row["abstract_provider"] or "editorial_reviewed" not in row:
                fail(location, "missing abstract provenance or review scope")
            if str(row.get("abstract_provider", "")).startswith("arxiv_primary"):
                if row["abstract_provider"] != "arxiv_primary_abstract_page":
                    fail(location, "primary arXiv abstracts must use the version-protected provider schema")
                version_url = row.get("reviewed_version_url")
                version = re.fullmatch(r"https://arxiv\.org/abs/(\d{4}\.\d{4,5})(v[1-9]\d*)", version_url) if isinstance(version_url, str) else None
                if (not version or not public_url(url)
                        or source_index.canonical(url) != "https://arxiv.org/abs/" + version[1]
                        or row.get("reviewed_version") != version[2]):
                    fail(location, "primary arXiv abstract requires a matching paper identity and reviewed version URL")
                if version and "url" in row and (not public_url(row["url"])
                        or source_index.canonical(row["url"]) != "https://arxiv.org/abs/" + version[1]):
                    fail(location, "primary arXiv URL and canonical identity must match the reviewed paper")
                page_hash = row.get("abstract_page_sha256")
                if (not isinstance(page_hash, str) or not HASH.fullmatch(page_hash)
                        or row.get("canonical_page_separately_fetched") is not True):
                    fail(location, "primary arXiv abstract requires fetched primary-page evidence")
        if row.get("verification_level") in {"content_screened", "editorial_reviewed"}:
            if not HASH.fullmatch(str(row.get("content_sha256", ""))) or row.get("status") != "screened":
                fail(location, "content screening requires retrieved content hash and screened status")
        if row.get("verification_level") == "metadata_only" and row.get("status") == "screened":
            fail(location, "metadata-only record must not claim content-screened status")
        if any(key in row for key in ("abstract", "full_text", "raw_html", "raw_response")):
            fail(location, "bulk source text must stay outside the public ledger")
    return result


def check_index(expected_raw_records: int) -> None:
    index_path = ROOT / "site/data/source-index.json"
    count_path = ROOT / "data/source-counts.json"
    if not index_path.exists() or not count_path.exists():
        fail("source index", "run python3 scripts/build_source_index.py")
        return
    try:
        payload = json.loads(index_path.read_text(encoding="utf-8"))
        snapshot = json.loads(count_path.read_text(encoding="utf-8"))
        rows, counts = payload["sources"], payload["counts"]
        if counts["raw_records"] != expected_raw_records:
            fail("source index", "not all nonexcluded source ledger records are accounted for")
        required = {"title", "url", "category", "description", "year", "status", "relation", "verification_level", "content_sha256"}
        if any(not required.issubset(row) for row in rows):
            fail("source index", "missing website source fields")
        levels = collections.Counter(row["verification_level"] for row in rows)
        if counts["unique_records"] != len(rows) or len({r["url"] for r in rows}) != len(rows):
            fail("source index", "unique source count or URL deduplication mismatch")
        if counts["raw_records"] != counts["unique_records"] + counts["duplicate_records"]:
            fail("source index", "raw, unique, and duplicate counts do not reconcile")
        if counts["duplicate_records"] != len(payload["duplicates"]):
            fail("source index", "duplicate audit count mismatch")
        if any(counts.get(level, 0) != levels.get(level, 0) for level in LEVELS):
            fail("source index", "verification-level counts do not reconcile")
        checked = sum(levels[level] for level in CHECKED)
        if counts["checked_sources"] != checked or checked <= 1500:
            fail("source index", "checked source count must reconcile and exceed 1,500")
        if snapshot != {"generated_at": payload["generated_at"], "counts": counts}:
            fail("data/source-counts.json", "count snapshot is stale")
        if not all(public_url(row["url"]) for row in rows):
            fail("source index", "invalid public source URL")
        result = subprocess.run([sys.executable, "scripts/build_source_index.py", "--check"], cwd=ROOT, capture_output=True, text=True)
        if result.returncode:
            fail("source index", "generated index is stale; run python3 scripts/build_source_index.py")
    except (KeyError, TypeError, ValueError, json.JSONDecodeError):
        fail("source index", "invalid index or count-snapshot schema")


def bib_fields(body: str) -> list[tuple[str, str]] | None:
    """Split an entry body at top-level commas into (field, value) pairs; None if malformed."""
    parts, current, depth, quoted = [], [], 0, False
    for char in body:
        depth += {"{": 1, "}": -1}.get(char, 0)
        quoted = not quoted if char == '"' and depth == 0 else quoted
        if char == "," and depth == 0 and not quoted:
            parts.append("".join(current))
            current = []
        else:
            current.append(char)
    parts.append("".join(current))
    fields = []
    for part in parts:
        name, separator, value = part.partition("=")
        if not separator and part.strip():
            return None
        if separator:
            fields.append((name.strip().casefold(), value.strip()))
    return fields


def check_bibtex(path: Path) -> None:
    # The published bibliography must load in BibTeX/biber: one balanced entry per
    # "@type{key," block, unique keys, and the fields every citation style needs.
    relative = str(path.relative_to(ROOT))
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return  # Already reported by the text check.
    starts = [match.start() for match in re.finditer(r"^[ \t]*@", text, re.M)]
    if not starts:
        fail(relative, "no BibTeX entries")
    keys: set[str] = set()
    for start, end in zip(starts, starts[1:] + [len(text)]):
        line = text.count("\n", 0, start) + 1
        location = f"{relative}:{line}"
        chunk = text[start:end]
        if re.match(r"\s*@(?:comment|preamble|string)\b", chunk, re.I):
            continue
        head = re.match(r"\s*@(\w+)\s*\{\s*([^\s,{}]+)\s*,", chunk)
        if not head:
            fail(location, "malformed BibTeX entry header")
            continue
        key = head[2]
        if key.casefold() in keys:
            fail(location, f"duplicate BibTeX key {key}")
        keys.add(key.casefold())
        depth, close = 0, None
        for position in range(chunk.index("{"), len(chunk)):
            depth += {"{": 1, "}": -1}.get(chunk[position], 0)
            if depth == 0:
                close = position
                break
        trailing = chunk[close + 1:] if close is not None else ""
        if close is None or any(line.strip() and not line.lstrip().startswith("%") for line in trailing.splitlines()):
            fail(location, f"unbalanced braces in BibTeX entry {key}")
            continue
        fields = bib_fields(chunk[head.end():close])
        if fields is None:
            fail(location, f"malformed field in BibTeX entry {key}")
            continue
        values = {name: value.strip('{}" \t\n') for name, value in fields}
        for name in ("title", "author", "year"):
            if not values.get(name):
                fail(location, f"BibTeX entry {key} is missing {name}")
        if values.get("year") and not re.fullmatch(r"\d{4}", values["year"]):
            fail(location, f"BibTeX entry {key} needs a four-digit year")


def main() -> int:
    all_files = files()
    check_symlinks()
    try:
        policy = load_policy(ROOT / "data/source-curation.json", source_index.canonical)
    except PolicyError as exc:
        fail("data/source-curation.json", str(exc))
        policy = None
    ledgers = []
    for path in all_files:
        relative = path.relative_to(ROOT)
        if any(pattern.search(str(relative)) for pattern in LEAK_PATTERNS.values()):
            fail(str(relative), "possible private value in filename")
        if path.name in {".env", ".npmrc", ".netrc"} or (path.name.startswith(".env.") and path.name != ".env.example") or path.suffix in {".pem", ".key"}:
            fail(str(relative), "private configuration or key file must not be published")
        if path.is_symlink():
            fail(str(relative), "symlinks are not supported in the published artifact")
            continue
        if path.suffix in TEXT_SUFFIXES or path.name in {"LICENSE", ".gitignore"}:
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                fail(str(relative), "expected UTF-8 text")
                continue
            check_text(path, text)
            if path.suffix == ".json":
                check_json(path, text)
        if path.suffix == ".jsonl" and path.parent == ROOT / "data":
            rows = check_ledger(path, policy)
            if ".excluded." not in path.name:
                ledgers.extend(rows)
    if not ledgers:
        fail("data", "no source ledger records")
    node = shutil.which("node")
    if not node:
        fail("JavaScript", "Node.js is required for syntax validation")
    else:
        for path in all_files:
            if path.suffix in {".js", ".mjs"}:
                result = subprocess.run([node, "--check", str(path.relative_to(ROOT))], cwd=ROOT, capture_output=True)
                if result.returncode:
                    fail(str(path.relative_to(ROOT)), "JavaScript syntax check failed")
    check_index(len(ledgers))
    for path in all_files:
        if path.suffix == ".bib" and not path.is_symlink():
            check_bibtex(path)
    if errors:
        print("Validation failed:")
        for error in errors[:80]:
            print("- " + error)
        if len(errors) > 80:
            print(f"- {len(errors) - 80} additional errors")
        return 1
    print(f"Validated {len(all_files)} files and {len(ledgers)} source ledger records: links, assets, provenance, counts, syntax, and publication hygiene.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
