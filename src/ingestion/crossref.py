from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import date
from html import unescape
import json
import logging
from pathlib import Path
import re
import time

import requests

from core.config import Settings


@dataclass(frozen=True)
class PaperRecord:
    paper_id: str
    title: str
    summary: str
    authors: list[str]
    categories: list[str]
    primary_category: str
    published: str
    updated: str
    abs_url: str
    pdf_url: str
    comment: str


def parse_crossref_payload(payload: dict) -> list[PaperRecord]:
    """Parse a works payload without mutating it; skip items lacking DOI/title.

    Optional metadata defaults to empty values. Partial dates use January/day 1.
    Malformed payload envelopes raise ValueError so fetching can use a snapshot.
    """
    def clean(value: object) -> str:
        if not isinstance(value, str):
            return ""
        return " ".join(unescape(re.sub(r"<[^>]+>", " ", value)).split())

    def strings(value: object) -> list[str]:
        values = value if isinstance(value, list) else [value]
        return [text for entry in values if (text := clean(entry))]

    def record_date(value: object) -> str:
        if not isinstance(value, dict):
            return ""
        parts = value.get("date-parts")
        if isinstance(parts, list) and parts and isinstance(parts[0], list):
            try:
                components = parts[0]
                return date(*[int(part) for part in (components + [1, 1])[:3]]).isoformat() if components else ""
            except (TypeError, ValueError, OverflowError):
                pass
        timestamp = value.get("date-time")
        if isinstance(timestamp, str):
            try:
                return date.fromisoformat(timestamp[:10]).isoformat()
            except ValueError:
                pass
        return ""

    message = payload.get("message") if isinstance(payload, dict) else None
    if not isinstance(message, dict) or not isinstance(message.get("items"), list):
        raise ValueError("Crossref payload must contain message.items as a list.")

    records = []
    for item in message["items"]:
        if not isinstance(item, dict):
            continue
        paper_id = clean(item.get("DOI"))
        titles = strings(item.get("title"))
        if not paper_id or not titles:
            continue
        authors = []
        for author in item.get("author") or []:
            if isinstance(author, dict):
                name = clean(author.get("name")) or " ".join(
                    part for key in ("given", "family") if (part := clean(author.get(key)))
                )
                if name:
                    authors.append(name)
        categories = strings(item.get("subject"))
        published = next((value for key in ("published", "published-online", "published-print", "issued", "created")
                          if (value := record_date(item.get(key)))), "")
        updated = next((value for key in ("indexed", "deposited", "created")
                        if (value := record_date(item.get(key)))), published)
        abs_url = clean(item.get("URL")) or f"https://doi.org/{paper_id}"
        pdf_url = next((clean(link.get("URL")) for link in item.get("link") or []
                        if isinstance(link, dict) and link.get("content-type") == "application/pdf"
                        and clean(link.get("URL"))), abs_url)
        records.append(PaperRecord(
            paper_id=paper_id, title=titles[0], summary=clean(item.get("abstract")),
            authors=authors, categories=categories,
            primary_category=categories[0] if categories else "",
            published=published, updated=updated, abs_url=abs_url, pdf_url=pdf_url,
            comment=f"Crossref record {paper_id}",
        ))
    return records


def fetch_source_records(settings: Settings) -> list[PaperRecord]:
    """Fetch works with bounded retries, preserving the original JSON bytes.

    On network, HTTP, or invalid-payload errors, use the existing raw snapshot
    without overwriting it. Fail explicitly if no usable snapshot is available.
    """
    params = {"query": settings.source_query, "filter": settings.source_filter,
              "rows": settings.max_results}
    raw_path = settings.paths.raw_api_response
    raw_content = None
    try:
        for attempt in range(3):
            try:
                with requests.get(
                    "https://api.crossref.org/works", params=params, timeout=(5, 20),
                    headers={"Accept": "application/json", "User-Agent": "DataObservabilityLab/0.1"},
                ) as response:
                    response.raise_for_status()
                    records = parse_crossref_payload(response.json())
                    raw_content = response.content
                break
            except (requests.ConnectionError, requests.Timeout, requests.HTTPError) as exc:
                status = exc.response.status_code if exc.response is not None else None
                if attempt == 2 or (status is not None and status not in {429, 500, 502, 503, 504}):
                    raise
                time.sleep(2 ** attempt)
    except (requests.RequestException, ValueError) as exc:
        logging.getLogger(__name__).warning("Crossref request failed; using snapshot %s: %s", raw_path, exc)
        try:
            records = parse_crossref_payload(json.loads(raw_path.read_bytes()))
        except (OSError, ValueError) as snapshot_error:
            raise RuntimeError(f"Crossref unavailable and no usable snapshot at {raw_path}") from snapshot_error

    if raw_content is not None:
        raw_path.parent.mkdir(parents=True, exist_ok=True)
        raw_path.write_bytes(raw_content)
    records_path = settings.paths.raw_records_json
    records_path.parent.mkdir(parents=True, exist_ok=True)
    records_path.write_text(
        json.dumps([asdict(record) for record in records], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return records


def load_raw_records(path: Path) -> list[PaperRecord]:
    """Load the parsed-record JSON snapshot into PaperRecord objects."""
    payload = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(payload, list):
        raise ValueError(f"Expected a JSON list of paper records in {path}")

    records = []
    for index, item in enumerate(payload):
        if not isinstance(item, dict):
            raise ValueError(f"Invalid paper record at index {index} in {path}: expected an object")
        try:
            records.append(PaperRecord(**item))
        except TypeError as exc:
            raise ValueError(f"Invalid paper record at index {index} in {path}: {exc}") from exc
    return records
