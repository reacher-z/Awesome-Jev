"""Parse the public arXiv Atom search feed as untrusted discovery metadata."""
from __future__ import annotations

from datetime import datetime
import re
import urllib.parse
import xml.etree.ElementTree as ET

API = "https://export.arxiv.org/api/query"
QUERY = 'ti:Jev OR abs:Jev OR ti:"typed decision" OR abs:"typed decision" OR ti:"System One model" OR abs:"System One model" OR ti:RLCD OR abs:RLCD'
PAGE_SIZE = 200
NAMESPACES = {"atom": "http://www.w3.org/2005/Atom", "os": "http://a9.com/-/spec/opensearch/1.1/"}
VERSION_URL = re.compile(r"https?://arxiv\.org/abs/(\d{4}\.\d{4,5}|[a-z-]+(?:\.[A-Z]{2})?/\d{7})(v[1-9]\d*)")


def query_url(start=0, size=PAGE_SIZE):
    return API + "?" + urllib.parse.urlencode({"search_query": QUERY, "start": start,
        "max_results": size, "sortBy": "lastUpdatedDate", "sortOrder": "descending"})


def api_host(url):
    parsed = urllib.parse.urlsplit(url)
    return (parsed.hostname in {"export.arxiv.org", "arxiv.org", "www.arxiv.org"}
            and parsed.path.startswith("/api/"))


def parse_feed(raw, expected_start, requested_size):
    """Return a complete page; malformed/error/truncated feeds are never successes."""
    try:
        text = raw.decode("utf-8")
        if "\x00" in text or re.search(r"<!\s*(?:DOCTYPE|ENTITY)\b", text, re.I):
            raise ValueError
        root = ET.fromstring(text)
        if root.tag != "{http://www.w3.org/2005/Atom}feed":
            raise ValueError
        def field(element, name):
            return " ".join((element.findtext(name, namespaces=NAMESPACES) or "").split())
        def number(name):
            value = field(root, name)
            if not re.fullmatch(r"[0-9]{1,9}", value):
                raise ValueError
            return int(value)
        total, start, size = number("os:totalResults"), number("os:startIndex"), number("os:itemsPerPage")
        entries = root.findall("atom:entry", NAMESPACES)
        if start != expected_start or size > requested_size or len(entries) != min(requested_size, max(0, total-start)):
            raise ValueError
        papers, seen = [], set()
        for entry in entries:
            version = VERSION_URL.fullmatch(field(entry, "atom:id"))
            title, abstract = field(entry, "atom:title"), field(entry, "atom:summary")
            authors = [field(author, "atom:name") for author in entry.findall("atom:author", NAMESPACES)]
            published, updated = field(entry, "atom:published"), field(entry, "atom:updated")
            dates = [datetime.fromisoformat(value.replace("Z", "+00:00")) for value in (published, updated)]
            if (not version or version[1] in seen or not 1 <= len(title) <= 500
                    or not abstract or not authors or not all(authors)
                    or any(date.tzinfo is None for date in dates) or dates[0] > dates[1]):
                raise ValueError
            seen.add(version[1])
            papers.append({"id": version[1], "url": "https://arxiv.org/abs/" + version[1],
                "version_url": "https://arxiv.org/abs/" + version[1] + version[2],
                "title": title, "abstract": abstract, "authors": authors,
                "published_at": dates[0].date().isoformat(), "updated_at": dates[1].date().isoformat()})
        return papers, total
    except (UnicodeError, ET.ParseError, ValueError, TypeError, OverflowError):
        raise ValueError("invalid_arxiv_api_feed") from None
