"""Parsers for URL HTML and uploaded text-like files."""

from __future__ import annotations

from bs4 import BeautifulSoup

from app.ingest.models import ParsedDocument, RawSource


def parse_raw_source(raw: RawSource) -> ParsedDocument:
    if raw.source_type == "url":
        soup = BeautifulSoup(raw.raw_text, "html.parser")
        title = (soup.title.string.strip() if soup.title and soup.title.string else raw.source_ref)
        body_text = soup.get_text("\n", strip=True)
        return ParsedDocument(
            source_type="url",
            source_ref=raw.source_ref,
            title=title,
            content_type=raw.content_type,
            text=body_text,
        )

    title = raw.file_name or raw.source_ref
    return ParsedDocument(
        source_type="file",
        source_ref=raw.source_ref,
        title=title,
        content_type=raw.content_type,
        text=raw.raw_text,
        file_name=raw.file_name,
    )
