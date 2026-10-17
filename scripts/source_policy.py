#!/usr/bin/env python3
"""Evidence-backed source exclusions and display-only metadata annotations.

URL canonicalization is supplied by the caller to avoid circular imports and
keep policy matching identical to the public index's document identities.
Verification levels, evidence hashes, and provider snapshots are never editable
through this policy.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
import ipaddress
import json
from pathlib import Path
import re
from typing import Callable
from urllib.parse import parse_qsl, urlsplit

DISPLAY_FIELDS = frozenset({"title", "first_submitted", "topic", "relation", "relevance"})
EVIDENCE_FIELDS = frozenset({"url", "note", "evidence_url", "reviewed_at"})
EXCLUSION_FIELDS = frozenset({"url", "reason", "evidence_url", "reviewed_at"})
# Query parameter names that carry a credential or signed-request material,
# shared by the collectors, the scheduled scan and the validator. Matched
# case-insensitively: the long words anywhere in a name (X-Amz-Signature,
# x-amz-security-token), Azure's short "sig" only as the whole name, because
# as a substring it would also match ordinary names such as "design".
CREDENTIAL_QUERY_KEY = re.compile(r"token|api.?key|passw(?:or)?d|secret|signature|credential|authorization|^sig$", re.I)


class PolicyError(ValueError):
    pass


def credential_query(query: str) -> bool:
    """True when any query parameter name looks like a credential."""
    return any(CREDENTIAL_QUERY_KEY.search(key) for key, _ in parse_qsl(query, keep_blank_values=True))


def _public_url(value: object) -> bool:
    if not isinstance(value, str) or re.search(r"[\x00-\x20\\]", value):
        return False
    try:
        parsed = urlsplit(value)
        host = parsed.hostname or ""
        if parsed.scheme not in {"http", "https"} or not host or parsed.username is not None or parsed.password is not None:
            return False
        if host == "localhost" or host.endswith((".local", ".internal", ".localhost")):
            return False
        try:
            if not ipaddress.ip_address(host).is_global:
                return False
        except ValueError:
            if "." not in host:
                return False
        return not credential_query(parsed.query)
    except ValueError:
        return False


@dataclass
class SourcePolicy:
    exclusions: dict[str, dict]
    annotations: dict[str, dict]
    canonicalize: Callable[[str], str]

    def exclusion(self, url: str) -> dict | None:
        return self.exclusions.get(self.canonicalize(url))

    def apply(self, row: dict) -> tuple[dict, dict | None]:
        """Return an overlay and explicit provenance; leave the raw row intact."""
        url = row.get("canonical_url", row.get("url", ""))
        annotation = self.annotations.get(self.canonicalize(url))
        if not annotation:
            return dict(row), None
        overrides = {key: annotation[key] for key in sorted(DISPLAY_FIELDS) if key in annotation}
        metadata = {
            "note": annotation["note"],
            "evidence_url": annotation["evidence_url"],
            "reviewed_at": annotation["reviewed_at"],
            "overrides": overrides,
            "provider_title": row.get("title", ""),
            "provider_published_at": row.get("published_at"),
        }
        return {**row, **overrides}, metadata


def load_policy(path: Path, canonicalize: Callable[[str], str]) -> SourcePolicy:
    if not path.exists():
        return SourcePolicy({}, {}, canonicalize)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValueError):
        raise PolicyError("Source curation must be readable UTF-8 JSON.") from None
    if not isinstance(data, dict) or set(data) != {"schema_version", "exclusions", "annotations"} or type(data["schema_version"]) is not int or data["schema_version"] != 1:
        raise PolicyError("Unsupported source-curation schema.")
    groups = {}
    for group in ("exclusions", "annotations"):
        values = data[group]
        if not isinstance(values, list):
            raise PolicyError("Source-curation entries must be lists.")
        allowed = EXCLUSION_FIELDS if group == "exclusions" else EVIDENCE_FIELDS | DISPLAY_FIELDS
        required = EXCLUSION_FIELDS if group == "exclusions" else EVIDENCE_FIELDS
        entries = {}
        for row in values:
            if not isinstance(row, dict) or not required.issubset(row) or not set(row).issubset(allowed):
                raise PolicyError("Unapproved or missing source-curation fields; evidence grades and hashes cannot be overridden.")
            if any(not isinstance(value, str) or not value.strip() for value in row.values()):
                raise PolicyError("Source-curation fields must be nonempty strings.")
            if not _public_url(row["url"]) or not _public_url(row["evidence_url"]):
                raise PolicyError("Source-curation URLs must be public and credential-free.")
            try:
                reviewed = datetime.fromisoformat(row["reviewed_at"].replace("Z", "+00:00"))
                if reviewed.tzinfo is None:
                    raise ValueError("timezone")
                if "first_submitted" in row:
                    if len(row["first_submitted"]) != 10:
                        raise ValueError("date")
                    date.fromisoformat(row["first_submitted"])
            except ValueError:
                raise PolicyError("Curation requires an ISO timestamp with timezone and date-only first_submitted.") from None
            if "relation" in row and row["relation"] not in {"direct", "adjacent", "background"}:
                raise PolicyError("Unknown curated source relationship.")
            key = canonicalize(row["url"])
            if key in entries:
                raise PolicyError("Duplicate canonical source in curation policy.")
            entries[key] = dict(row)
        groups[group] = entries
    if set(groups["exclusions"]) & set(groups["annotations"]):
        raise PolicyError("An excluded source cannot also have display annotations.")
    return SourcePolicy(groups["exclusions"], groups["annotations"], canonicalize)
