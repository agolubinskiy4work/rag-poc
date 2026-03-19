"""Ingestion-specific intermediate models."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class RawSource:
    source_type: str
    source_ref: str
    content_type: str
    raw_text: str
    title: str | None = None
    file_name: str | None = None


@dataclass
class ParsedDocument:
    source_type: str
    source_ref: str
    title: str
    content_type: str
    text: str
    file_name: str | None = None


@dataclass
class ChunkingInput:
    doc_id: str
    source_type: str
    source_ref: str
    title: str
    text: str
    document_hash: str
