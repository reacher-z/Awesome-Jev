#!/usr/bin/env python3
"""Screen public Jev Decision Index sources and one-hop research dependencies.

Uses public, unauthenticated HTTP only. Stores concise evidence, provenance and
content hashes, never downloaded full texts or credentials. `content_screened`
means the complete retrieved document passed the explicit automated checks below;
it does not mean manual peer review, correctness validation or reproduction.
"""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import hashlib
import html
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path

try:
    from .build_source_index import identifying_query
except ImportError:
    from build_source_index import identifying_query

SPACE ="multimodalart/jev-decision-index"
SPACE_URL = "https://huggingface.co/spaces/" + SPACE
KEYWORDS = {
    "Jev": r"\bjev\b|openjev|jev[-_]",
    "TypeSafe AI": r"typesafe(?:\.ai|[-_ ]ai)|typesafe_sdk|@typesafe-ai",
    "typed decisions": r"typed.decision|decision.model|decision.engine|decision.head",
    "calibration": r"calibrat|\brlcd\b",
    "probability readout": r"probabilit|logits|log.prob",
    "evaluation": r"benchmark|evaluation|\beval\b",
    "training": r"fine.tun|training|lora",
    "routing": r"routing|router|tool.call",
    "vision": r"vision|visual|multimodal",
}
BLOCKED_HOSTS = {
    "x.com", "twitter.com", "www.linkedin.com", "discord.gg", "discord.com",
    "fonts.googleapis.com", "fonts.gstatic.com", "www.w3.org", "api.codiv.ai",
    "api.openai.com", "api.typesafe.ai", "wandb.ai", "www.youtube.com", "youtu.be",
}
SKIP_GH = {"huggingface/transformers", "huggingface/huggingface_hub", "pytorch/pytorch"}
# Site routes whose first path segment is not an owner or namespace; for
# example README image embeds under github.com/user-attachments/assets/<id>.
GH_RESERVED = {
    "topics", "orgs", "settings", "features", "sponsors", "user-attachments", "apps", "marketplace",
    "login", "about", "pricing", "enterprise", "security", "search", "explore", "trending",
    "advisories", "customer-stories",
}
HF_RESERVED = {
    "docs", "collections", "organizations", "blog", "join", "settings", "api", "tasks", "learn",
    "models", "new", "pricing", "login", "chat", "posts", "search",
}
REQ_HEADERS = {"User-Agent": "Awesome-Jev-public-source-audit/1.0", "Accept": "text/plain,text/html,application/json"}
NOW = lambda: datetime.now(timezone.utc).isoformat(timespec="seconds")


def fetch(url: str):
    req = urllib.request.Request(url, headers=REQ_HEADERS)
    with urllib.request.urlopen(req, timeout=25) as r:
        raw = r.read(6_000_001)
        if len(raw) > 6_000_000:
            raise ValueError("document_exceeds_6MB_limit")
        content_type = r.headers.get("Content-Type", "")
        if raw.startswith(b"%PDF") or any(x in content_type for x in ("image/", "application/octet-stream")):
            raise ValueError("unsupported_binary_document")
        return raw, r.geturl(), content_type


class ReadableHTML(HTMLParser):
    def __init__(self):
        super().__init__()
        self.skip = 0
        self.title_mode = False
        self.title = []
        self.parts = []
    def handle_starttag(self, tag, attrs):
        if tag in {"script", "style", "nav", "footer", "noscript"}:
            self.skip += 1
        if tag == "title":
            self.title_mode = True
    def handle_endtag(self, tag):
        if tag in {"script", "style", "nav", "footer", "noscript"} and self.skip:
            self.skip -= 1
        if tag == "title":
            self.title_mode = False
    def handle_data(self, data):
        if self.title_mode:
            self.title.append(data)
        if not self.skip:
            self.parts.append(data)


def readable(raw: bytes, kind: str):
    text = raw.decode("utf-8", errors="replace")
    title = ""
    if kind == "html":
        p = ReadableHTML()
        p.feed(text)
        title = " ".join(p.title).strip()
        text = " ".join(p.parts)
    else:
        m = re.search(r"^#\s+(.+)$", text, re.M)
        if m:
            title = m.group(1).strip()
        text = re.sub(r"!\[[^\]]*\]\([^)]*\)", " ", text)
        text = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", text)
    return re.sub(r"\s+", " ", html.unescape(text)).strip(), title


def canonical(url: str):
    url = html.unescape(url).strip().rstrip(".,;)]}")
    try:
        p = urllib.parse.urlsplit(url)
    except ValueError:
        return None
    host = p.netloc.lower()
    if p.scheme not in {"http", "https"} or host in BLOCKED_HOSTS or "@" in host:
        return None
    path = re.sub(r"/+", "/", p.path).rstrip("/")
    if host in {"arxiv.org", "www.arxiv.org", "export.arxiv.org"}:
        m = re.search(r"(?:abs|pdf|html)/(\d{4}\.\d{4,5})(?:v\d+)?", path)
        return "https://arxiv.org/abs/" + m.group(1) if m else None
    if host in {"github.com", "www.github.com", "raw.githubusercontent.com"}:
        seg = path.strip("/").split("/")
        if len(seg) < 2 or seg[0].lower() in GH_RESERVED:
            return None
        owner = re.match(r"[A-Za-z0-9_.-]+", seg[0])
        name = re.match(r"[A-Za-z0-9_.-]+", seg[1])
        if not owner or not name:
            return None
        repo = owner[0] + "/" + name[0].removesuffix(".git")
        if repo.lower() in SKIP_GH:
            return None
        return "https://github.com/" + repo.lower()
    if host in {"huggingface.co", "www.huggingface.co", "hf.co"}:
        seg = path.strip("/").split("/")
        if len(seg) < 2 or seg[0] in HF_RESERVED:
            return None
        if seg[0] == "papers":
            if re.fullmatch(r"\d{4}\.\d{4,5}", seg[1]):
                return "https://arxiv.org/abs/" + seg[1]
            return None
        if seg[0] in {"datasets", "spaces"}:
            if len(seg) < 3:
                return None
            parts = seg[:3]
        else:
            parts = seg[:2]
        parts = [re.match(r"[A-Za-z0-9_.-]+", s)[0] if re.match(r"[A-Za-z0-9_.-]+", s) else "" for s in parts]
        if not all(parts) or parts == ["spaces", "Chunte", "HFBA"]:
            return None
        return "https://huggingface.co/" + "/".join(parts)
    if path.lower().endswith((".png", ".jpg", ".svg", ".gif", ".woff", ".zip", ".tar.gz", ".mp4")):
        return None
    # A PDF has one scholarly landing-page identity when the provider supports it.
    if host == "aclanthology.org":
        path = path.removesuffix(".pdf")
    # Keep identifying parameters (OpenReview id, CiteSeer doi) as the source index does.
    return urllib.parse.urlunsplit(("https", host, path or "/", identifying_query(p.query), ""))


def links(text: str):
    return re.findall(r"https?://[^\s\"'<>\\`\]\)]+", text)


def eligible(record: dict):
    """Prevent general software dependencies from inflating the Jev corpus."""
    if record.get("discovery_depth", 0) == 0:
        return True
    if record["topic"] in {"training-dataset", "research-paper"}:
        return True
    # One-hop repository/model entries must have explicit decision/Jev content.
    return bool(set(record.get("matched_topics", [])) & {"Jev", "TypeSafe AI", "typed decisions"})


def repo_target(url: str):
    p = urllib.parse.urlsplit(url)
    seg = p.path.strip("/").split("/")
    if p.netloc == "huggingface.co":
        return "hf", "/".join(seg), [url + "/raw/main/README.md"]
    if p.netloc == "github.com":
        repo = "/".join(seg[:2])
        return "github", repo, ["https://raw.githubusercontent.com/" + repo + "/" + branch + "/" + filename
            for branch in ("main", "master") for filename in ("README.md", "readme.md", "README.rst")]
    return "web", "", [url]


def audit(seed: dict):
    url = seed["url"]
    typ, ident, candidates = repo_target(url)
    errors = []
    payload = None
    for candidate in candidates:
        try:
            raw, final_url, ct = fetch(candidate)
            payload = raw, final_url, ct
            break
        except Exception as e:
            errors.append(type(e).__name__ + ": " + str(e)[:100])
    base = dict(seed)
    base.update({"retrieved_at": NOW(), "checked_via": "public unauthenticated HTTP; automated full-document content screening"})
    if payload is None:
        base.update({"verification_level": "metadata_only", "status": "unavailable", "evidence": "Linked from the specified source; document content could not be retrieved.", "fetch_errors": errors[-2:]})
        return base, []
    raw, final_url, ct = payload
    source_text = raw.decode("utf-8", errors="replace")
    is_html = "text/html" in ct or source_text.lstrip().lower().startswith("<!doctype html")
    text, title = readable(raw, "html" if is_html else "markdown")
    matches = [label for label, pat in KEYWORDS.items() if re.search(pat, text, re.I)]
    headings = re.findall(r"^#{1,3}\s+(.+)$", source_text, re.M)[:6] if not is_html else []
    structural = bool(len(text) >= 240 and len(text.split()) >= 35)
    topical = bool(matches or seed["topic"] in {"benchmark-source", "training-dataset", "research-paper", "reference-baseline"})
    # Direct references still require substantive readable content, never merely a card title.
    ok = structural and topical and not any(z in text[:500].lower() for z in ["access denied", "verify you are human", "this repository is empty"])
    base.update({
        "title": (title or seed.get("title") or ident or url)[:200],
        "verification_level": "content_screened" if ok else "metadata_only",
        "status": "screened" if ok else "insufficient_content",
        "retrieved_url": final_url,
        "content_sha256": hashlib.sha256(raw).hexdigest(),
        "content_bytes": len(raw),
        "readable_characters": len(text),
        "matched_topics": matches,
        "section_headings": [re.sub(r"[<>{}]", "", h)[:90] for h in headings],
        "evidence": ("Retrieved and screened substantive " + ("model/dataset card" if typ == "hf" else "repository README" if typ == "github" else "source page") + "; discusses " + ", ".join(matches[:5]) + ".") if ok and matches else ("Retrieved and screened substantive content for a directly cited evaluation or training resource." if ok else "Retrieved page lacks sufficient readable topical content for content-screened status."),
        "screening_method": "v1: readable body >=240 characters and >=35 words; explicit topic terms or direct benchmark/training provenance; no access-denial marker; SHA-256 over retrieved bytes. Not editorial review or reproduction.",
    })
    children = []
    if ok and seed["relation"] == "direct":
        for u in links(source_text):
            c = canonical(u)
            if not c or c == url:
                continue
            # Keep only identifiable scholarly and implementation artifacts on the
            # dependency hop; no broad browsing or arbitrary links from articles.
            if c.startswith("https://huggingface.co/datasets/"):
                topic = "training-dataset"
            elif c.startswith("https://github.com/"):
                topic = "implementation-repository"
            elif c.startswith(("https://arxiv.org/abs/", "https://aclanthology.org/")):
                topic = "research-paper"
            elif typ == "github" and c.startswith("https://huggingface.co/"):
                # Only Jev/decision-named linked weights, avoiding generic base variants.
                if not re.search(r"jev|decid|decision|rlcd|system.one|laya|nimble|glide|gliner|winnow|\bkev", c, re.I):
                    continue
                topic = "decision-model-card"
            else:
                continue
            children.append({"url": c, "title": c.rsplit("/", 1)[-1], "topic": topic,
                "relation": "adjacent", "relevance": "Direct scholarly, training-data, or implementation dependency linked by an index-listed artifact; not a claim about TypeSafe internals.",
                "discovered_from": [url], "discovery_depth": seed.get("discovery_depth", 0) + 1})
    return base, children


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output", default="data/ecosystem-sources.jsonl")
    ap.add_argument("--workers", type=int, default=12)
    ap.add_argument("--max-depth", type=int, default=1)
    ap.add_argument("--resume", action="store_true", help="Reuse already retrieved dependency content records; rescreen their relevance.")
    args = ap.parse_args()
    info = json.loads(fetch("https://huggingface.co/api/spaces/" + SPACE)[0])
    revision = info["sha"]
    root = SPACE_URL + "/raw/" + revision + "/"
    files = {}
    for f in ["README.md", "news.html", "data/index.json", "data/methodology.json", "data/vision.json", "data/v03.json"]:
        files[f] = fetch(root + f)[0]
    index = json.loads(files["data/index.json"])
    methodology = json.loads(files["data/methodology.json"])
    seeds = {}
    def add(url, topic, relation, origin, why, depth=0):
        c = canonical(url)
        if not c or c == SPACE_URL:
            return
        if c in seeds:
            if origin not in seeds[c]["discovered_from"]:
                seeds[c]["discovered_from"].append(origin)
            return
        seeds[c] = {"url": c, "title": c.rsplit("/", 1)[-1], "topic": topic,
                    "relation": relation, "relevance": why, "discovered_from": [origin], "discovery_depth": depth}
    readme = files["README.md"].decode()
    frontmatter = readme.split("---")[1]
    for model in re.findall(r"^-\s+([^\s]+/[^\s]+)\s*$", frontmatter, re.M):
        add("https://huggingface.co/" + model, "decision-model-card", "direct", SPACE_URL,
            "Model artifact explicitly listed in the community Jev Decision Index; independent Jev-inspired entry or declared comparison model.")
    for model in index["models"]:
        meta = model.get("meta", {})
        for key, topic in [("model_url", "decision-model-card"), ("code_url", "implementation-repository")]:
            if meta.get(key):
                add(meta[key], topic, "direct", root + "data/index.json", "Entrant artifact linked by the index's evaluated-model metadata.")
    # News is an untrusted static source: extract URLs, never execute its JavaScript.
    for u in links(files["news.html"].decode()):
        add(u, "ecosystem-news-artifact", "direct", root + "news.html", "Artifact linked by the community tracker news corpus; claims require separate validation.")
    for b in methodology.get("benchmarks", []) + methodology.get("added_benchmarks", []):
        for u in links(json.dumps(b)):
            add(u, "benchmark-source", "adjacent", root + "data/methodology.json", "Upstream source cited for Decision Index benchmark " + str(b.get("dataset", b.get("name", b.get("id")))) + ". Adaptation may change the original task.")
    for u in links(files["data/vision.json"].decode()):
        add(u, "vision-decision-artifact", "direct", root + "data/vision.json", "Artifact linked by the Decision Index vision evaluation metadata.")
    add(methodology["reproduce"]["github"], "evaluation-harness", "direct", root + "data/methodology.json", "Public repository designated by the index for evaluation reproduction; private tests remain unreleased.")
    add("https://arxiv.org/abs/2609.35342", "research-paper", "direct", "https://huggingface.co/papers/2609.35342", "Sys1Cal-v1 is a Jev probability-calibration dataset study.")
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    cache = {}
    if args.resume and out.exists():
        for line in out.read_text(encoding="utf-8").split("\n"):
            if not line.strip():
                continue
            old = json.loads(line)
            key = canonical(old["url"])
            if key and old.get("content_sha256") and (key == old["url"] or key.lower() == old["url"].lower()):
                cache[key] = old
    results = {}
    # Source files are distinct datasets/documents, not per-model report URLs.
    for f, raw in files.items():
        url = SPACE_URL if f == "README.md" else SPACE_URL + "/blob/" + revision + "/" + f
        data = json.loads(raw) if f.endswith(".json") else None
        evidence = "Inspected community tracker source; independent implementations are not TypeSafe weights."
        if f == "data/index.json":
            evidence = f"Structured scoreboard contains {len(data['models'])} entrant records and public panel size {data['suite']['panel']}; reference version is {data['suite']['jev_version']}."
        elif f == "data/methodology.json":
            evidence = "Methodology records 37 public benchmarks, chance correction, private-test weighting and a 0.3.2 scoring correction; private tests are not publicly reproducible."
        elif f == "data/v03.json":
            evidence = "Full-score component data specifies public/same-skills/new-domains weights of 0.2/0.5/0.3 and scale-equating parameters."
        elif f == "data/vision.json":
            evidence = "Separate vision scoreboard specifies public/private weights of 0.5/0.5, benchmark composition and model-entry metadata."
        elif f == "news.html":
            evidence = "Static news corpus separates trained models, decoding approaches, prior art and explainers; source links extracted without executing JavaScript."
        results[url] = {"url": url, "title": "Jev Decision Index — " + f, "topic": "community-evaluation-index", "relation": "direct", "verification_level": "editorial_reviewed" if f in {"README.md", "data/index.json", "data/methodology.json", "data/v03.json"} else "content_screened", "status": "screened", "retrieved_at": NOW(), "checked_via": "Public repository source inspection", "retrieved_url": root + f, "resolved_revision": revision, "content_sha256": hashlib.sha256(raw).hexdigest(), "content_bytes": len(raw), "evidence": evidence, "relevance": "User-specified central community source for Jev-inspired implementations and evaluation.", "discovered_from": [SPACE_URL]}
    def save():
        kept = [(u, r) for u, r in sorted(results.items()) if eligible(r)]
        excluded = [dict(r, exclusion_reason="Explicit Jev, TypeSafe AI, or typed-decision content was not established for this one-hop implementation; excluded from checked-source totals.") for u, r in sorted(results.items()) if not eligible(r)]
        out.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for _, r in kept), encoding="utf-8", newline="\n")
        out.with_suffix(".excluded.jsonl").write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in excluded), encoding="utf-8", newline="\n")
    for depth in range(args.max_depth + 1):
        batch = [s for u, s in seeds.items() if u not in results and s["discovery_depth"] == depth]
        print(json.dumps({"phase": "screen", "depth": depth, "pending": len(batch)}, ensure_ascii=False), flush=True)
        candidates = []
        if depth > 0 and args.resume:
            remaining = []
            for seed in batch:
                if seed["url"] in cache:
                    record = dict(cache[seed["url"]])
                    record.update(seed)
                    record["title"] = cache[seed["url"]]["title"]
                    record["relevance_rescreened_at"] = NOW()
                    if "Jev" in record.get("matched_topics", []) or "TypeSafe AI" in record.get("matched_topics", []):
                        record["relation"] = "direct"
                        record["relevance"] = "An index-linked community resource whose retrieved content explicitly discusses Jev or TypeSafe AI; independent ecosystem evidence, not a vendor endorsement."
                    results[record["url"]] = record
                else:
                    remaining.append(seed)
            batch = remaining
            save()
            print(json.dumps({"reused": len(results), "pending_after_reuse": len(batch)}), flush=True)
        with cf.ThreadPoolExecutor(max_workers=args.workers) as pool:
            futures = {pool.submit(audit, s): s for s in batch}
            for i, fut in enumerate(cf.as_completed(futures), 1):
                seed = futures[fut]
                try:
                    record, children = fut.result()
                except Exception as e:
                    record = dict(seed, retrieved_at=NOW(), verification_level="metadata_only", status="audit_error", evidence=str(e)[:200])
                    children = []
                results[record["url"]] = record
                if record.get("discovery_depth", 0) > 0 and set(record.get("matched_topics", [])) & {"Jev", "TypeSafe AI"}:
                    record["relation"] = "direct"
                    record["relevance"] = "An index-linked community resource whose retrieved content explicitly discusses Jev or TypeSafe AI; independent ecosystem evidence, not a vendor endorsement."
                candidates.extend(children)
                if i % 30 == 0:
                    save()
                    print(json.dumps({"completed": len(results), "levels": dict(Counter(r["verification_level"] for r in results.values()))}), flush=True)
        for s in candidates:
            if s["url"] not in seeds:
                seeds[s["url"]] = s
            elif s["discovered_from"][0] not in seeds[s["url"]]["discovered_from"]:
                seeds[s["url"]]["discovered_from"].extend(s["discovered_from"])
        save()
    kept = [r for r in results.values() if eligible(r)]
    checked = [r for r in kept if r["verification_level"] != "metadata_only"]
    summary = {"generated_at": NOW(), "index_revision": revision, "index_edition": index["suite"]["label"], "public_panel": index["suite"]["panel"], "records": len(kept), "verification_levels": dict(Counter(r["verification_level"] for r in kept)), "statuses": dict(Counter(r["status"] for r in kept)), "relations": dict(Counter(r["relation"] for r in kept)), "distinct_checked_content_hashes": len({r["content_sha256"] for r in checked}), "excluded_scope": len(results)-len(kept), "discovered_not_screened": len([u for u in seeds if u not in results]), "method": "One-hop public primary-artifact discovery. Full retrieved text screened automatically; editorial_reviewed is reserved for manually inspected index sources. Dependency implementation pages require explicit Jev/TypeSafe/typed-decision content. metadata_only and excluded-scope records are excluded from content-checked totals. No experiment reproduced."}
    # Report this run on stdout only. Scans and reviewed additions change the
    # ledger afterwards, so a committed copy would go stale; current counts are
    # generated and checked by build_source_index.py (data/source-counts.json).
    print(json.dumps(summary, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
