#!/usr/bin/env python3
"""Collect and machine-screen related research from public scholarly APIs.

The Hugging Face Papers API returns publisher/arXiv metadata and abstracts.
An accepted record means its returned title AND abstract were processed by the
explicit topic rules below. It does not mean a person read its full paper, that
the paper was peer reviewed, or that its claims have been independently tested.
Canonical arXiv links are identifiers, not claims of separate page retrieval.

Only short evidence excerpts and abstract hashes enter the repository. Raw API
responses are cached in the operating-system temporary directory, outside it.
No account, token, email address, or private source is used.

The output ledger is replaced wholesale. --offline re-screens only a complete
cache from an earlier online run; it stops without writing if any query is
uncached, and every run stops without writing if no record qualifies.

Usage: python3 scripts/collect_research.py --target 0 --with-openalex
"""

from __future__ import annotations

import argparse
import concurrent.futures
import datetime as dt
import hashlib
import json
import re
import sys
import tempfile
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path


PROVIDER = "huggingface_papers_api"
API = "https://huggingface.co/api/papers/search"
OPENALEX_API = "https://api.openalex.org/works"
USER_AGENT = "Awesome-Jev-Research-Corpus/1.0 (public scholarly metadata collection)"

# Queries discover candidates. Separate rules determine inclusion, irrespective
# of which search returned a paper. Queries are intentionally scoped to the
# decision interfaces and evaluation questions raised by Jev.
QUERIES = {
    "probability_calibration": [
        "probability calibration classification", "confidence calibration neural networks",
        "language model calibration", "temperature scaling calibration",
        "calibration error reliability diagrams", "multicalibration prediction",
        "calibrated language model probabilities", "post hoc calibration classifiers",
    ],
    "proper_scoring_rules": [
        "proper scoring rules probabilistic prediction", "strictly proper scoring rule",
        "Brier score calibration", "proper losses probability estimation",
        "scoring rules language models",
    ],
    "selective_prediction": [
        "selective prediction", "selective classification", "classification reject option",
        "risk coverage abstention", "language models abstention",
        "learning to defer classification", "selective generation language models",
        "confidence rejection classifier",
    ],
    "uncertainty_distribution_shift": [
        "uncertainty estimation distribution shift", "predictive uncertainty classification",
        "epistemic uncertainty language models", "conformal prediction language models",
        "conformal classification", "conformal prediction covariate shift",
        "uncertainty out of distribution calibration", "uncertainty selective prediction",
    ],
    "structured_constrained_decoding": [
        "grammar constrained decoding", "structured output language models",
        "structured generation JSON schema", "constrained language model decoding",
        "finite state constrained decoding", "type safe language model outputs",
        "grammar aligned decoding", "constrained generation language models",
    ],
    "language_model_programming": [
        "language model programming", "DSPy language model programs", "LMQL",
        "language model workflow optimization", "modular language model pipelines",
        "prompt optimization language model programs", "structured language model programs",
    ],
    "judge_reliability": [
        "LLM as a judge calibration", "language model judge reliability",
        "LLM judge bias", "LLM judges uncertainty", "calibrating language model evaluators",
        "LLM judge consistency", "rubric language model evaluation",
        "language model self evaluation confidence",
    ],
    "efficient_routing_cascades": [
        "LLM model routing", "language model cascades", "classifier cascade",
        "early exit neural classification", "adaptive inference language models",
        "cost sensitive classification", "model routing calibrated confidence",
        "learning to route language models", "efficient classifier early exit",
    ],
}

OPENALEX_QUERIES = {
    "proper_scoring_rules": ["proper scoring rules", "proper scoring rule"],
    "selective_prediction": ["selective classification", "selective prediction"],
    "probability_calibration": ["probability calibration", "confidence calibration"],
    "efficient_routing_cascades": ["early exit neural", "classifier cascade", "language model routing"],
}

TOPIC_RELEVANCE = {
    "probability_calibration": "Background for checking whether reported decision probabilities agree with observed outcomes.",
    "proper_scoring_rules": "Background for evaluating probability distributions and incentives for truthful probability reporting.",
    "selective_prediction": "Background for confidence thresholds, abstention, deferral, and the risk versus coverage trade-off.",
    "uncertainty_distribution_shift": "Background for uncertainty estimates and prediction guarantees when inputs or task distributions change.",
    "structured_constrained_decoding": "Comparison background for schema-constrained outputs and the distinction between structural validity and semantic correctness.",
    "language_model_programming": "Comparison background for composing model calls inside explicit programs, modules, and workflows.",
    "judge_reliability": "Background for evaluating the reliability, bias, consistency, or uncertainty of model-based judgments.",
    "efficient_routing_cascades": "Comparison background for allocating prediction work across classifiers or models under accuracy and compute constraints.",
}

ML = r"(?:language models?|\bllms?\b|neural|classifier|classification|machine learning|deep learning|predictive|probabilistic)"
LM = r"(?:language models?|\bllms?\b|text generation|\blmql\b|\bdspy\b|\bsglang\b)"
RULES = {
    "probability_calibration": [
        r"(?:confidence|probability|probabilistic|predictive|prediction|uncertainty|classifier|classification|neural network|model)[- ]calibrat|calibrat(?:ed|ion|ing|e).{0,50}(?:probabilit|confidence|uncertaint)|expected calibration|multicalibrat|temperature scal|reliability diagram|calibration error|(?:well|poorly)[- ]calibrated|miscalibrat",
        ML,
        r"probabilit|confidence|uncertaint|classif|prediction",
    ],
    "proper_scoring_rules": [
        r"proper scoring|strictly proper|brier score|scoring rules?|proper loss",
        r"probabilit|predict|calibrat|uncertaint|forecast|classification",
    ],
    "selective_prediction": [
        r"selective (?:prediction|classification|generation)|reject option|risk[- ]coverage|learning to defer|abstain|abstention",
        ML,
    ],
    "uncertainty_distribution_shift": [
        r"(?:uncertainty|uncertainties|conformal prediction|conformal classification)",
        r"(?:distribution(?:al)? shift|out[- ]of[- ]distribution|covariate shift|epistemic|aleatoric|conformal|predictive uncertainty)",
        ML,
    ],
    "structured_constrained_decoding": [
        r"constrained (?:decoding|generation)|structured (?:output|generation)|grammar[- ](?:constrained|aligned|guided)|json schema|type[- ]safe|type safety|\bxgrammar\b",
        LM,
    ],
    "language_model_programming": [
        LM,
        r"language model program|llm program|\blmql\b|\bdspy\b|\bsglang\b|programmatic|workflow optimization|optimiz.{0,40}(?:workflow|pipeline|program)|prompt optim|automatic prompt|modular.{0,30}(?:language model|llm)|computational graph|declarative",
    ],
    "judge_reliability": [
        LM,
        r"(?:llm|model)[ -](?:as[ -]a[ -])?judg|llm-as-a-judge|(?:language models?|llms?).{0,40}(?:as|for) (?:a |an )?(?:judge|evaluator)|(?:llm|language model)[- ]based evaluat|self[- ]evaluat|self[- ]assessment|rubric",
        r"calibrat|reliab|uncertaint|confidence|bias|consisten|evaluat|judg",
    ],
    "efficient_routing_cascades": [
        r"(?:model|llm|classifier|classification) (?:routing|cascad)|language model cascades?|classifier cascades?|cascaded classifier|early[- ]exit|adaptive (?:inference|computation)|dynamic inference|cost[- ]sensitive classification|learning to route",
        ML,
    ],
}
COMPILED = {k: [re.compile(x, re.I) for x in v] for k, v in RULES.items()}
DIRECT = re.compile(r"\bjev\b|system one models?", re.I)


def now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")


def normalize_title(title: str) -> str:
    return re.sub(r"[^a-z0-9]", "", title.lower())


def sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def evidence(abstract: str, matches: list[str]) -> str:
    """At most 20 words; never store the full copyrighted abstract."""
    words = abstract.split()
    position = 0
    for term in matches:
        offset = abstract.lower().find(term.lower())
        if offset >= 0:
            position = len(abstract[:offset].split())
            break
    start = max(0, position - 5)
    excerpt = " ".join(words[start : start + 20])
    return ("… " if start else "") + excerpt + (" …" if start + 20 < len(words) else "")


def screen(title: str, abstract: str) -> dict[str, list[str]]:
    if len(abstract.split()) < 30:
        return {}
    text = title + "\n" + abstract
    if DIRECT.search(text):
        return {}
    topics = {}
    for topic, patterns in COMPILED.items():
        hits = [pattern.search(text) for pattern in patterns]
        if all(hits):
            # A single incidental mention is insufficient in these categories.
            # Require the core concept in the title or at least two abstract
            # occurrences. This filters papers that merely use a tool or metric.
            if topic in {"proper_scoring_rules", "structured_constrained_decoding", "selective_prediction", "language_model_programming", "judge_reliability"}:
                core = patterns[1 if topic in {"language_model_programming", "judge_reliability"} else 0]
                if not core.search(title) and len(core.findall(abstract)) < 2:
                    continue
            topics[topic] = list(dict.fromkeys(hit.group(0) for hit in hits if hit))
    return topics


class Collector:
    def __init__(self, cache: Path, workers: int, offline: bool = False):
        self.cache = cache
        self.cache.mkdir(parents=True, exist_ok=True)
        self.workers = workers
        self.offline = offline
        self.gate = threading.Lock()
        self.next_request = 0.0
        self.failures: list[dict] = []

    def fetch(self, topic: str, query: str, provider: str = PROVIDER) -> tuple[str, str, dict]:
        if provider == "openalex_api":
            url = OPENALEX_API + "?" + urllib.parse.urlencode({
                "filter": "title.search:" + query,
                "per-page": 200,
                "select": "id,doi,title,authorships,publication_year,abstract_inverted_index,primary_location,locations",
            })
        else:
            url = API + "?" + urllib.parse.urlencode({"q": query, "limit": 120})
        cached = self.cache / (sha(url) + ".json")
        if cached.exists():
            return topic, query, json.loads(cached.read_text())
        if self.offline:
            failure = {"query": query, "url": url, "retrieval_status": "not_in_cache"}
            with self.gate:
                self.failures.append(failure)
            return topic, query, {"data": [], **failure}
        last_error = ""
        for attempt in range(4):
            # Global pacing plus bounded concurrency; respect a Retry-After
            # response when the provider applies a more restrictive limit.
            with self.gate:
                delay = max(0, self.next_request - time.monotonic())
                if delay:
                    time.sleep(delay)
                self.next_request = time.monotonic() + 0.4
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
            try:
                with urllib.request.urlopen(req, timeout=20) as response:
                    raw = response.read()
                    wrapper = {
                        "retrieval_url": url,
                        "retrieved_at": now(),
                        "http_status": response.status,
                        "response_sha256": hashlib.sha256(raw).hexdigest(),
                        "data": json.loads(raw),
                        "provider": provider,
                    }
                if provider == "openalex_api":
                    wrapper["data"] = convert_openalex(wrapper["data"].get("results", []))
                cached.write_text(json.dumps(wrapper, ensure_ascii=False))
                return topic, query, wrapper
            except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as exc:
                last_error = str(exc)
                if isinstance(exc, urllib.error.HTTPError) and exc.code not in (429, 500, 502, 503, 504):
                    break
                retry_after = getattr(exc, "headers", {}).get("Retry-After", "")
                delay = float(retry_after) if retry_after.isdigit() else 2 ** (attempt + 1)
                time.sleep(min(delay, 30))
        failure = {"query": query, "url": url, "retrieval_status": "failed", "error": last_error}
        with self.gate:
            self.failures.append(failure)
        return topic, query, {"data": [], **failure}

    def run(self, with_openalex: bool = False) -> list[tuple[str, str, dict]]:
        jobs = [(topic, q, PROVIDER) for topic, queries in QUERIES.items() for q in queries]
        if with_openalex:
            jobs.extend((topic, q, "openalex_api") for topic, queries in OPENALEX_QUERIES.items() for q in queries)
        output = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.workers) as executor:
            futures = [executor.submit(self.fetch, *job) for job in jobs]
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                output.append(result)
                print(json.dumps({"query_finished": result[1], "candidates": len(result[2].get("data", [])), "finished": len(output), "total_queries": len(jobs)}), flush=True)
        return sorted(output, key=lambda x: (x[0], x[1]))


def convert_openalex(works: list[dict]) -> list[dict]:
    """Reconstruct indexed abstracts; do not substitute titles for missing text."""
    output = []
    for work in works:
        index = work.get("abstract_inverted_index") or {}
        positions = {position: word for word, offsets in index.items() for position in offsets}
        abstract = " ".join(positions[p] for p in sorted(positions))
        primary = work.get("primary_location") or {}
        locations = work.get("locations") or []
        urls = [loc.get("landing_page_url") or "" for loc in [primary] + locations]
        arxiv_ids = [m.group(1) for url in urls if (m := re.search(r"arxiv\.org/(?:abs|pdf)/(\d{4}\.\d{4,5}|[a-z.-]+/\d{7})", url, re.I))]
        arxiv_id = arxiv_ids[0] if arxiv_ids else None
        doi = work.get("doi")
        canonical = "https://arxiv.org/abs/" + arxiv_id if arxiv_id else doi or primary.get("landing_page_url") or work["id"]
        record_id = "arxiv:" + arxiv_id if arxiv_id else ("doi:" + doi.removeprefix("https://doi.org/") if doi else "openalex:" + work["id"].rsplit("/", 1)[-1])
        output.append({"paper": {
            "id": arxiv_id or record_id,
            "_record_id": record_id,
            "_canonical_url": canonical,
            "title": work.get("title") or "",
            "summary": abstract,
            "authors": [{"name": a.get("author", {}).get("display_name", "")} for a in work.get("authorships", [])],
            "publishedAt": str(work.get("publication_year") or ""),
        }})
    return output


def build_records(results: list[tuple[str, str, dict]]) -> tuple[list[dict], dict]:
    records = {}
    title_ids = {}
    stats = Counter()
    direct = {}
    for query_topic, query, wrapper in results:
        for rank, item in enumerate(wrapper.get("data", [])):
            paper = item.get("paper", item)
            paper_id = str(paper.get("id", ""))
            if not paper.get("_record_id") and not re.fullmatch(r"(?:\d{4}\.\d{4,5}|[a-z.-]+/\d{7})(?:v\d+)?", paper_id, re.I):
                stats["invalid_or_missing_arxiv_id"] += 1
                continue
            paper_id = re.sub(r"v\d+$", "", paper_id)
            title = " ".join(str(paper.get("title", "")).split())
            abstract = " ".join(str(paper.get("summary", "")).split())
            stats["candidate_appearances"] += 1
            if DIRECT.search(title + "\n" + abstract):
                direct[paper_id] = title
                stats["direct_jev_appearances_excluded"] += 1
                continue
            matched = screen(title, abstract)
            if not matched:
                stats["topic_screen_rejected_appearances"] += 1
                continue
            title_key = normalize_title(title)
            existing_id = title_ids.get(title_key, paper_id)
            if existing_id in records:
                previous = records[existing_id]
                previous["discovery_queries"] = sorted(set(previous["discovery_queries"] + [query]))
                previous["matched_topics"] = sorted(set(previous["matched_topics"]) | set(matched))
                previous["_rank"] = min(previous["_rank"], rank)
                stats["deduplicated_appearances"] += 1
                continue
            primary_topic = query_topic if query_topic in matched else next(iter(matched))
            published = str(paper.get("publishedAt", ""))
            record = {
                "id": paper.get("_record_id") or "arxiv:" + paper_id,
                "canonical_url": paper.get("_canonical_url") or "https://arxiv.org/abs/" + paper_id,
                "title": title,
                "authors": [a.get("name", "") for a in paper.get("authors", []) if a.get("name")],
                "year": int(published[:4]) if re.match(r"\d{4}", published) else None,
                "published_at": published or None,
                "topic": primary_topic,
                "matched_topics": sorted(matched),
                "relation": "background",
                "source_type": "scholarly_work",
                "verification_level": "abstract_checked",
                "screening_method": "programmatic_title_abstract_rules_v1",
                "editorial_reviewed": False,
                "full_text_reviewed": False,
                "canonical_page_separately_fetched": False,
                "retrieved_at": wrapper["retrieved_at"],
                "retrieval_status": "success",
                "http_status": wrapper["http_status"],
                "abstract_provider": wrapper.get("provider", PROVIDER),
                "abstract_origin": "abstract_inverted_index reconstructed from OpenAlex public metadata; original publisher/repository text not independently retrieved" if wrapper.get("provider") == "openalex_api" else "original paper abstract mirrored by Hugging Face Papers; not the AI-generated summary",
                "retrieval_url": wrapper["retrieval_url"],
                "discovery_queries": [query],
                "abstract_sha256": sha(abstract),
                "abstract_word_count": len(abstract.split()),
                "evidence_terms": matched[primary_topic],
                "evidence_excerpt": evidence(abstract, matched[primary_topic]),
                "relevance": TOPIC_RELEVANCE[primary_topic],
                "limitations": "Machine-screened background relevance only; no claim about Jev implementation, paper validity, peer-review status, or reproduced results.",
                "_rank": rank,
            }
            records[paper_id] = record
            title_ids[title_key] = paper_id
    stats["distinct_screened_candidates"] = len(records)
    return list(records.values()), {"counts": dict(stats), "direct_jev_discoveries": direct}


def select_balanced(records: list[dict], target: int) -> list[dict]:
    buckets = defaultdict(list)
    for record in records:
        buckets[record["topic"]].append(record)
    for bucket in buckets.values():
        bucket.sort(key=lambda r: (r["_rank"], -len(r["discovery_queries"]), r["id"]))
    selected = []
    # Round-robin selection prevents a broad, well-indexed topic from consuming
    # the entire corpus. Exhausted categories yield their remaining allocation.
    while len(selected) < target and any(buckets.values()):
        for topic in QUERIES:
            if buckets[topic] and len(selected) < target:
                selected.append(buckets[topic].pop(0))
    for record in selected:
        record.pop("_rank", None)
    return sorted(selected, key=lambda r: (r["topic"], r["id"]))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", type=int, default=0, help="Maximum accepted records to emit; 0 retains every qualified distinct source")
    parser.add_argument("--workers", type=int, default=3)
    parser.add_argument("--offline", action="store_true", help="Re-screen a complete cache from an earlier online run without network calls")
    parser.add_argument("--with-openalex", action="store_true", help="Supplement arXiv-focused discovery with older published foundational work via OpenAlex")
    parser.add_argument("--output", type=Path, default=Path("data/research-sources.jsonl"))
    parser.add_argument("--cache-dir", type=Path, default=Path(tempfile.gettempdir()) / "awesome-jev-research-api-cache")
    args = parser.parse_args()
    if args.target < 0 or not 1 <= args.workers <= 4:
        parser.error("target must be nonnegative; workers must be between 1 and 4")
    collector = Collector(args.cache_dir, args.workers, args.offline)
    results = collector.run(args.with_openalex)
    # The output replaces the ledger wholesale: never overwrite it with a
    # partial or empty re-screen while reporting success.
    uncached = sum(f["retrieval_status"] == "not_in_cache" for f in collector.failures)
    if uncached:
        sys.exit(f"Offline re-screen stopped: {uncached} of {len(results)} queries have no cached response, "
                 f"so {args.output} was not changed. --offline needs the cache from an earlier online run "
                 "on this machine (see --cache-dir).")
    candidates, audit = build_records(results)
    records = select_balanced(candidates, args.target or len(candidates))
    if not records:
        sys.exit(f"Research collection stopped: no records qualified ({len(collector.failures)} failed queries), "
                 f"so {args.output} was not changed.")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("".join(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n" for r in records))
    audit.update({
        "emitted_records": len(records),
        "requested_target": args.target,
        "topic_counts": dict(Counter(r["topic"] for r in records)),
        "failed_queries": collector.failures,
        "verification_note": "Abstracts retrieved and programmatically screened; no editorial or full-text review is implied.",
    })
    # This audit contains no full abstracts or machine-specific cache paths.
    print(json.dumps(audit, ensure_ascii=False, indent=2), flush=True)


if __name__ == "__main__":
    main()
