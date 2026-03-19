"""URL fetcher for manual ingestion."""

from __future__ import annotations

import requests

from app.ingest.models import RawSource


def fetch_url(url: str, timeout: int = 20) -> RawSource:
    response = requests.get(url, timeout=timeout)
    response.raise_for_status()
    content_type = response.headers.get("Content-Type", "text/html").split(";")[0].strip()
    return RawSource(
        source_type="url",
        source_ref=url,
        content_type=content_type,
        raw_text=response.text,
    )
