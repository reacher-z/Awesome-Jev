#!/usr/bin/env python3
"""Audit a manually published expansion against a frozen public-source baseline.

This report is an explicit maintenance artifact, not a scheduled scanner output.
It counts only evidence-checked resources that were absent from the whole known
collection. A new discovery is not a scientific endorsement or reproduced result.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
from urllib.parse import urlsplit

try:
    from .build_source_index import canonical, CHECKED
except ImportError:
    from build_source_index import canonical, CHECKED

ROOT = Path(__file__).resolve().parents[1]
BASELINE = ROOT / "data/expansion-baseline-2026-10-16.json"
REPORT = ROOT / "data/expansion-progress-2026-10-16.json"
DIRECTORY = ROOT / "docs/expansion-2026-10-16.md"
INTAKE = ROOT / "data/expansion-intake-2026-10-16.json"
SUPPLEMENT = ROOT / "data/expansion-baseline-supplement-2026-10-16.json"


def source_key(url):
    value = canonical(url)
    parsed = urlsplit(value)
    parts = parsed.path.strip("/").split("/")
    if parsed.netloc in {"github.com", "raw.githubusercontent.com"} and len(parts) >= 2 and parts[0] not in {"topics", "orgs", "settings", "features", "sponsors"}:
        return "https://github.com/" + "/".join(parts[:2]).removesuffix(".git").lower()
    if parsed.netloc in {"huggingface.co", "hf.co"}:
        if parts[0] in {"datasets", "spaces"} and len(parts) >= 3:
            return "https://huggingface.co/" + "/".join(parts[:3])
        if len(parts) >= 2 and parts[0] not in {"docs", "blog", "papers", "collections", "organizations", "join", "settings"}:
            return "https://huggingface.co/" + "/".join(parts[:2])
    if parsed.netloc == "doi.org":
        match = re.fullmatch(r"/10\.48550/arxiv\.(\d{4}\.\d{4,5})(?:v\d+)?", parsed.path, re.I)
        if match:
            return "https://arxiv.org/abs/" + match[1]
    return value


def supplemented_baseline(raw, supplement):
    baseline = json.loads(raw)
    if supplement.get("baseline_commit") != baseline["baseline_commit"] or supplement.get("original_baseline_sha256") != hashlib.sha256(raw).hexdigest():
        raise ValueError("Baseline supplement does not match the immutable original baseline.")
    return {**baseline,
            "known_urls": baseline["known_urls"] + supplement["additional_known_urls"],
            "known_paper_titles": baseline["known_paper_titles"] + supplement["additional_known_paper_titles"]}


def title_key(title):
    return re.sub(r"\W+", "", re.sub(r"^\[\d{4}\.\d{4,5}\]\s*", "", title).casefold())


def assess(baseline, current, approved_urls):
    known_urls = {source_key(url) for url in baseline["known_urls"]}
    known_hashes = set(baseline["known_evidence_hashes"])
    known_titles = set(baseline["known_paper_titles"])
    approved = {source_key(url) for url in approved_urls}
    additions, excluded = [], []
    for source in sorted(current["sources"], key=lambda row: source_key(row["url"])):
        url = source_key(source["url"])
        if url in known_urls:
            continue
        evidence = source.get("content_sha256", "")
        paper = source.get("category") in {"Papers", "Research foundations"}
        title = title_key(source["title"])
        reason = None
        if url not in approved:
            reason = "not_in_reviewed_intake"
        elif source.get("verification_level") not in CHECKED:
            reason = "metadata_only_does_not_count"
        elif not re.fullmatch(r"[0-9a-f]{64}", evidence):
            reason = "missing_evidence_hash"
        elif evidence in known_hashes:
            reason = "previous_or_duplicate_evidence"
        elif paper and len(title) > 20 and title in known_titles:
            reason = "previous_or_duplicate_paper_title"
        if reason:
            excluded.append({"url": url, "reason": reason})
            continue
        additions.append({key: source[key] for key in (
            "title", "url", "category", "topic", "description", "relation",
            "verification_level", "content_sha256", "retrieved_at", "ledger",
        )})
        known_urls.add(url)
        known_hashes.add(evidence)
        if paper:
            known_titles.add(title)
    additions.sort(key=lambda row: (row["relation"] == "background", row["category"], row["title"].casefold()))
    return {
        "schema_version": 1,
        "baseline_commit": baseline["baseline_commit"],
        "baseline_source_index_sha256": baseline["baseline_source_index_sha256"],
        "target_new_sources": baseline["target_new_sources"],
        "accepted_new_sources": len(additions),
        "remaining_to_target": max(0, baseline["target_new_sources"] - len(additions)),
        "target_count_reached": len(additions) >= baseline["target_new_sources"],
        "current_index_counts": current["counts"],
        "by_category": dict(sorted(Counter(row["category"] for row in additions).items())),
        "by_relation": dict(sorted(Counter(row["relation"] for row in additions).items())),
        "by_verification_level": dict(sorted(Counter(row["verification_level"] for row in additions).items())),
        "verification_note": "Evidence depth is labeled per source. Content screening and abstract checks do not establish full-paper review, peer review, endorsement, or experimental reproduction.",
        "additions": additions,
        "excluded_from_target": excluded,
    }


def cell(value):
    return str(value).replace("|", "\\|").replace("\n", " ").replace("[", "\\[").replace("]", "\\]")


def directory(report):
    count, target = report["accepted_new_sources"], report["target_new_sources"]
    lines = [
        "<!-- Generated by scripts/build_expansion_report.py; do not edit by hand. Edit data/expansion-intake-2026-10-16.json or the source ledgers and rebuild. -->",
        "# Resource expansion — 16 October 2026", "",
        f"**{count} newly added, evidence-checked sources / target: at least {target}.**", "",
        "[Main collection](../README.md) · [Website source search](https://awesomejev.github.io/#corpus) · [Machine-readable progress](../data/expansion-progress-2026-10-16.json) · [Frozen baseline](../data/expansion-baseline-2026-10-16.json) · [Prior-citation supplement](../data/expansion-baseline-supplement-2026-10-16.json)", "",
        f"The baseline is [commit {report['baseline_commit'][:7]}](https://github.com/reacher-z/Awesome-Jev/tree/{report['baseline_commit']}). Prior ledger entries, curated resources and cited links are excluded. Canonical URL aliases, repeated content hashes and duplicate paper titles do not count again. Metadata-only discoveries do not count toward the target.", "",
        "Only sources in the [reviewed intake](../data/expansion-intake-2026-10-16.json) count toward this expansion. This is a discovery directory with explicit screening levels. **Direct** sources concern Jev or typed decision systems; **adjacent** resources implement closely related methods; **background** papers provide research context. Listing is not an endorsement or independent reproduction. The short descriptions explain relevance, not a universal recommendation.", "",
        f"**中文：本轮已新增 {count} 项有核查证据的资源，目标至少 {target} 项。** 已有台账、精选与引用链接、重复正文或论文题名均不重复计数，仅元数据条目不计入目标。下表区分直接相关、邻近方法与背景研究；自动内容筛查或摘要检查不等于全文评审，也不代表实验复现。", "",
        "| Resource type | Newly added |", "| --- | ---: |",
    ]
    lines.extend(f"| {cell(category)} | {number} |" for category, number in report["by_category"].items())
    if not report["additions"]:
        lines += ["", "No additions have been accepted into this release yet. Candidate discovery is not counted as completion."]
    for category in report["by_category"]:
        lines += ["", f"## {category}", "", "| Resource | Relationship / evidence | Relevance |", "| --- | --- | --- |"]
        for row in report["additions"]:
            if row["category"] == category:
                lines.append(f"| [{cell(row['title'])}]({row['url']}) | {row['relation']} · `{row['verification_level']}` | {cell(row['description'])} |")
    lines += ["", "Hashes, retrieval timestamps and discovery provenance remain in the public source ledgers. The progress report is rebuilt explicitly during reviewed expansion releases; scheduled scans do not silently rewrite this review directory.", ""]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    baseline = supplemented_baseline(BASELINE.read_bytes(), json.loads(SUPPLEMENT.read_text(encoding="utf-8")))
    intake = json.loads(INTAKE.read_text(encoding="utf-8"))
    if intake.get("baseline_commit") != baseline["baseline_commit"]:
        raise SystemExit("Expansion intake does not match the frozen baseline.")
    approved_urls = [url for batch in intake["batches"] for url in batch["accepted_urls"]]
    current = json.loads((ROOT / "site/data/source-index.json").read_text(encoding="utf-8"))
    report = assess(baseline, current, approved_urls)
    outputs = {REPORT: json.dumps(report, ensure_ascii=False, indent=2) + "\n", DIRECTORY: directory(report)}
    for path, text in outputs.items():
        if args.check:
            if not path.exists() or path.read_text(encoding="utf-8") != text:
                raise SystemExit("Expansion report differs from the current index; rebuild during the next reviewed expansion release.")
        else:
            path.write_text(text, encoding="utf-8", newline="\n")
    print(json.dumps({key: report[key] for key in ("accepted_new_sources", "target_new_sources", "remaining_to_target", "by_category")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
