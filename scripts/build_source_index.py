#!/usr/bin/env python3
"""Build the public browser index from provenance-preserving source ledgers."""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import re
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

try:
    from .source_policy import load_policy, PolicyError
except ImportError:
    from source_policy import load_policy, PolicyError

ROOT = Path(__file__).resolve().parents[1]
CHECKED = {"content_screened", "editorial_reviewed", "abstract_checked"}
# Only real HTML elements: paper titles such as "Entropy After </Think>" or
# "Cut <Taxes> Hair" contain angle brackets that are part of the title.
HTML_TAG = re.compile(r"</?(?:a|b|br|center|div|em|h[1-6]|i|img|p|picture|source|span|strong|sub|sup)\b[^>]*>", re.I)
SITE_SUFFIX = re.compile(r"\s+[-|]\s+(?:ACL Anthology|Zenodo|DEV Community\b.*)$")


def clean_title(title: str) -> str:
    """Plain display text for an extracted heading; the ledger keeps the raw value."""
    title = re.split(r"\\n|\n", title, maxsplit=1)[0]
    title = re.sub(r"\[!\[[^\]]*\]\([^)]*\)\]\([^)]*\)", " ", title)  # linked badges
    # Ledger titles are capped at 200 characters, which can cut a badge short.
    title = re.sub(r"\[!\[.*$", " ", title)
    title = re.sub(r"!\[[^\]]*\]\([^)]*\)", " ", title)  # images
    title = re.sub(r"!\[.*$", " ", title)
    title = re.sub(r"\[\[[^\]]*\]\([^)]*\)\]", " ", title)  # "[[Project Website](...)]"
    title = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", title)  # unwrap links
    title = HTML_TAG.sub(" ", title)
    title = re.sub(r"^\s*\[\d{4}\.\d{4,5}(?:v\d+)?\]\s*", "", title)  # arXiv page prefix
    return SITE_SUFFIX.sub("", re.sub(r"\s+", " ", title).strip())


def canonical(url: str) -> str:
    p = urlsplit(url.strip())
    host = p.netloc.lower().removeprefix("www.")
    path = p.path.rstrip("/")
    if host in {"arxiv.org", "export.arxiv.org"}:
        host = "arxiv.org"
        path = re.sub(r"^/(pdf|html)/", "/abs/", path)
        path = re.sub(r"v\d+(?:\.pdf)?$", "", path).removesuffix(".pdf")
    if host == "huggingface.co" and path.startswith("/papers/"):
        host, path = "arxiv.org", "/abs/" + path.split("/")[-1]
        path = re.sub(r"v\d+$", "", path)
    # Verified Hub redirects: a renamed repository stays one resource even
    # after its README changes. Match a whole repository path, not a prefix of
    # an unrelated model name. Evidence is retained in the source review files.
    hub_aliases = {
        "/spaces/multimodalart/jev-reproductions-tracker": "/spaces/multimodalart/jev-decision-index",
        "/lihe07/span-02": "/respanai/span-02",
    }
    if host == "huggingface.co":
        for legacy, current in hub_aliases.items():
            if path == legacy or path.startswith(legacy + "/"):
                path = current + path[len(legacy):]
                break
    if host == "github.com":
        path = re.sub(r"/blob/[^/]+/(?:README(?:\.[a-zA-Z-]+)?(?:\.md|\.rst|\.txt)?)$", "", path, flags=re.I)
        path = path.removesuffix(".git")
        # GitHub owner and repository names are case-insensitive, and the
        # scanner stores them lowercased; later path segments keep their case.
        repository = "/".join(path.split("/")[:3])
        path = repository.lower() + path[len(repository):]
    # Query parameters can identify a paper (OpenReview id, CiteSeer doi)
    # or a model report. Strip tracking parameters, never resource identity.
    query = urlencode(sorted((key, value) for key, value in parse_qsl(p.query, keep_blank_values=True)
                             if not key.lower().startswith("utm_")
                             and key.lower() not in {"fbclid", "gclid", "msclkid"}))
    return urlunsplit(("https", host, path, query, ""))


def category(row: dict) -> str:
    if row.get("relation") == "background":
        return "Research foundations"
    if row.get("source_type") == "hf_repository" and row.get("topic") == "implementation-repository":
        return "Projects"
    url = row.get("url", row.get("canonical_url", ""))
    if "arxiv.org" in url or "huggingface.co/papers/" in url:
        return "Papers"
    if "huggingface.co/datasets/" in url:
        return "Datasets"
    if "huggingface.co/" in url and "/spaces/" not in url:
        return "Models"
    if "github.com" in url:
        return "Projects"
    if row.get("source_type") == "anonymous_repository" and row.get("topic") == "implementation-repository":
        return "Projects"
    return "Guides and evaluations"


def build() -> dict:
    policy = load_policy(ROOT / "data/source-curation.json", canonical)
    raw = []
    for name in ("ecosystem-sources.jsonl", "research-sources.jsonl"):
        source = ROOT / "data" / name
        if source.exists():
            for line in source.read_text(encoding="utf-8").split("\n"):
                if line.strip():
                    row = json.loads(line)
                    row["ledger"] = name
                    raw.append(row)
    # Preserve the strongest verification record when multiple discovery paths converge.
    rank = {"editorial_reviewed": 0, "content_screened": 1, "abstract_checked": 2, "metadata_only": 3}
    raw.sort(key=lambda r: (rank.get(r.get("verification_level"), 9), r.get("url", r.get("canonical_url", ""))))
    urls, hashes, titles = set(), set(), set()
    rows, duplicates = [], []
    for row in raw:
        url = canonical(row.get("url", row.get("canonical_url", "")))
        if not urlsplit(url).netloc:
            raise ValueError("Missing source URL")
        if policy.exclusion(url):
            raise PolicyError("An explicitly excluded source remains in an accepted ledger; remove it through a reviewed change.")
        display, curation = policy.apply(row)
        level = row.get("verification_level", "metadata_only")
        content_hash = row.get("content_sha256", row.get("abstract_sha256", ""))
        title = clean_title(display.get("title", url))
        if not title or re.match(r"^(?:pip install|git clone|1\.\s*encoder|\{|Start the server)", title, re.I) or re.sub(r"[^a-z]", "", title.casefold()) in {"citation", "acknowledgments", "acknowledgements", "license", "usage", "installation", "readme", "introduction", "modelcard", "datasetcard", "datasetcardfordatasetname", "datasplits", "quickstart", "macmlx"}:
            title = urlsplit(url).path.strip("/").removeprefix("datasets/").removeprefix("spaces/") or urlsplit(url).netloc
        title_key = re.sub(r"\W+", "", title.casefold())
        is_paper = display.get("relation") == "background" or "arxiv.org/abs/" in url
        reason = "canonical_url" if url in urls else "content_hash" if content_hash and content_hash in hashes else "paper_title" if is_paper and len(title_key) > 20 and title_key in titles else None
        if reason:
            duplicates.append({"url": url, "reason": reason, "ledger": row["ledger"]})
            continue
        urls.add(url)
        if content_hash:
            hashes.add(content_hash)
        if is_paper:
            titles.add(title_key)
        date = display.get("first_submitted") or row.get("published_at", "")
        labels = {"editorial_reviewed": "Editorially reviewed", "content_screened": "Content screened", "abstract_checked": "Abstract screened", "metadata_only": "Metadata only"}
        entry = {
            "id": hashlib.sha256(url.encode()).hexdigest()[:12],
            "title": title,
            "url": url,
            "category": category(display),
            "topic": display.get("topic", ""),
            "description": display.get("relevance", row.get("evidence", "")),
            "year": str(date)[:4] if date else "",
            "status": labels.get(level, level),
            "relation": display.get("relation", "adjacent"),
            "verification_level": level,
            "content_sha256": content_hash,
            "retrieved_at": row.get("retrieved_at", ""),
            "ledger": row["ledger"],
        }
        if curation:
            entry["curation"] = curation
        rows.append(entry)
    counts = dict(collections.Counter(row["verification_level"] for row in rows))
    counts.update(raw_records=len(raw), unique_records=len(rows), duplicate_records=len(duplicates), checked_sources=sum(row["verification_level"] in CHECKED for row in rows))
    generated = max((r["retrieved_at"] for r in rows), default="")
    rows.sort(key=lambda r: (r["relation"] == "background", r["category"], r["title"].casefold()))
    return {"generated_at": generated, "counts": counts, "sources": rows, "duplicates": duplicates}


def outputs(payload: dict) -> dict[str, str]:
    """Render every file this script owns, keyed by repository-relative path."""
    badge = {"schemaVersion": 1, "label": "source checks", "message": f"{payload['counts']['checked_sources']:,} sources", "color": "6B7280", "labelColor": "374151"}
    return {
        "site/data/source-index.json": json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n",
        "data/source-counts.json": json.dumps({"generated_at": payload["generated_at"], "counts": payload["counts"]}, indent=2) + "\n",
        "site/data/source-badge.json": json.dumps(badge) + "\n",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="Fail if any committed generated file is stale")
    args = parser.parse_args()
    payload = build()
    files = outputs(payload)
    if args.check:
        # The README badge reads source-badge.json directly, so every output is
        # compared, not only the index that validate.py reconciles.
        stale = [name for name, text in files.items()
                 if not (ROOT / name).exists() or (ROOT / name).read_text(encoding="utf-8") != text]
        if stale:
            raise SystemExit(f"Stale generated source files ({', '.join(stale)}): run python3 scripts/build_source_index.py")
    else:
        for name, text in files.items():
            destination = ROOT / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(text, encoding="utf-8", newline="\n")
    print(json.dumps(payload["counts"], indent=2))


if __name__ == "__main__":
    main()
