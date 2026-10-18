#!/usr/bin/env python3
"""Manually notify IndexNow of changed Awesome Jev pages; dry-run by default.

Protocol: https://www.indexnow.org/documentation
The public verification key is never printed. A receipt is not an indexing claim.
"""
from __future__ import annotations

import argparse
from html.parser import HTMLParser
import http.client
import json
from pathlib import Path
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
HOST = "awesomejev.github.io"
SITE = "https://" + HOST
ENDPOINT = "https://api.indexnow.org/indexnow"
KEY_LOCATION = SITE + "/indexnow-key.txt"
MAX_PAGE_BYTES = 2_000_000


class SubmissionError(Exception):
    """Safe error text that never includes request or response payloads."""


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def site_url(value):
    try:
        parsed = urllib.parse.urlsplit(value)
        if (parsed.scheme != "https" or parsed.netloc != HOST or
                parsed.username is not None or parsed.password is not None or
                parsed.query or parsed.fragment or re.search(r"[\x00-\x20\\]", value)):
            raise SubmissionError("Only query-free canonical HTTPS pages on the fixed site are allowed.")
        return value
    except (ValueError, TypeError):
        raise SubmissionError("Invalid canonical site URL.") from None


def changed_urls(sitemap, selected=None):
    try:
        root = ET.fromstring(sitemap.read_bytes())
    except (OSError, ET.ParseError):
        raise SubmissionError("Cannot read the generated site sitemap.") from None
    ns = "{http://www.sitemaps.org/schemas/sitemap/0.9}"
    pages = [site_url((node.text or "").strip()) for node in root.findall(ns + "url/" + ns + "loc")]
    if not 1 <= len(pages) <= 1000 or len(set(pages)) != len(pages):
        raise SubmissionError("Expected 1–1000 unique canonical pages in the generated sitemap.")
    urls = list(dict.fromkeys(site_url(url) for url in selected)) if selected else pages
    if not urls or any(url not in pages for url in urls):
        raise SubmissionError("Selected changed pages must belong to the generated sitemap.")
    return urls


def local_key(path):
    try:
        key = path.read_text(encoding="utf-8").strip()
    except OSError:
        raise SubmissionError("Publish the local IndexNow verification file before submitting.") from None
    if not re.fullmatch(r"[A-Za-z0-9-]{8,128}", key):
        raise SubmissionError("The IndexNow verification file has an invalid key format.")
    return key


def get_text(url, opener, limit=MAX_PAGE_BYTES):
    request = urllib.request.Request(url, headers={"User-Agent": "AwesomeJev-IndexNow-Verification/1.0"}, method="GET")
    try:
        with opener.open(request, timeout=20) as response:
            if response.status != 200:
                raise SubmissionError("A live verification request did not return HTTP 200.")
            body = response.read(limit + 1)
        if len(body) > limit:
            raise SubmissionError("A live verification response exceeded the size limit.")
        return body.decode("utf-8")
    except urllib.error.HTTPError as error:
        raise SubmissionError(f"Live verification failed with HTTP {error.code}; no submission was sent.") from None
    # urllib does not wrap errors raised while reading the status line or body
    # (RemoteDisconnected, IncompleteRead, ConnectionResetError).
    except (urllib.error.URLError, TimeoutError, http.client.HTTPException, OSError, UnicodeError):
        raise SubmissionError("Live verification failed; no submission was sent.") from None


class CanonicalLinks(HTMLParser):
    def __init__(self):
        super().__init__()
        self.urls = []

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if tag == "link" and "canonical" in (values.get("rel") or "").lower().split():
            self.urls.append(values.get("href"))


def submit(urls, key, opener):
    # The custom root key location covers every selected page on this host.
    if get_text(KEY_LOCATION, opener, 512).strip() != key:
        raise SubmissionError("The deployed verification file does not match the local key; no submission was sent.")
    for url in urls:
        site_url(url)
        parser = CanonicalLinks()
        parser.feed(get_text(url, opener))
        if parser.urls != [url]:
            raise SubmissionError("A selected live page lacks a unique self-referencing canonical URL; no submission was sent.")
    payload = {"host": HOST, "key": key, "keyLocation": KEY_LOCATION, "urlList": urls}
    request = urllib.request.Request(ENDPOINT, data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json; charset=utf-8", "User-Agent": "AwesomeJev-IndexNow-Submission/1.0"}, method="POST")
    # Exactly one POST. Never automatically retry a failed or rate-limited notice.
    try:
        with opener.open(request, timeout=20) as response:
            return response.status
    except urllib.error.HTTPError as error:
        return error.code
    except (urllib.error.URLError, TimeoutError, http.client.HTTPException, OSError):
        raise SubmissionError("The single submission request failed; receipt is unconfirmed. No automatic retry was attempted.") from None


def status_message(status):
    messages = {
        200: "IndexNow received the URLs. This does not mean they are indexed.",
        202: "URLs received; IndexNow key validation is pending. This does not mean they are indexed.",
        400: "IndexNow rejected the request format.",
        403: "IndexNow did not validate the key.",
        422: "IndexNow rejected the host, URL or key schema.",
        429: "IndexNow rate-limited the request. No automatic retry was attempted.",
    }
    return messages.get(status, "IndexNow returned an unexpected status. No automatic retry was attempted.")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--submit", action="store_true", help="Verify live pages/key and send one actual IndexNow notification")
    parser.add_argument("--url", action="append", help="Changed sitemap URL to include (repeatable); default is all generated sitemap pages")
    args = parser.parse_args(argv)
    try:
        urls = changed_urls(ROOT / "site/sitemap.xml", args.url)
        if not args.submit:
            print(json.dumps({"mode": "dry-run", "endpoint": ENDPOINT, "changed_urls": urls,
                "note": "No network requests sent. Use --submit only for pages actually added or changed."}, indent=2))
            return 0
        key = local_key(ROOT / "site/indexnow-key.txt")
        opener = urllib.request.build_opener(NoRedirect())
        status = submit(urls, key, opener)
        print(json.dumps({"mode": "submitted", "http_status": status, "url_count": len(urls), "message": status_message(status)}, indent=2))
        return 0 if status in {200, 202} else 1
    except SubmissionError as error:
        print(str(error), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
