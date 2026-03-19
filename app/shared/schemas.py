"""Shared typed schemas for the local RAG MVP."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class SourceInput:
    source_type: str  # url | file
    value: str
    file_name: str | None = None


@dataclass
class DocumentRecord:
    doc_id: str
    source_type: str
    title: str
    url: str | None
    file_name: str | None
    content_type: str
    clean_text: str
    document_hash: str
    indexed_at: datetime | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ChunkRecord:
    chunk_id: str
    doc_id: str
    chunk_index: int
    text: str
    title: str
    url: str | None
    source_type: str
    section_title: str | None
    token_count: int
    document_hash: str


@dataclass
class SyncItemResult:
    source_ref: str
    status: str  # indexed | skipped | failed
    message: str
    doc_id: str | None = None


@dataclass
class SyncResult:
    total_sources: int
    indexed_count: int
    skipped_count: int
    failed_count: int
    items: list[SyncItemResult]


@dataclass
class RetrievalCandidate:
    chunk_id: str
    doc_id: str
    text: str
    title: str
    url: str | None
    source_type: str
    dense_score: float = 0.0
    lexical_score: float = 0.0
    fused_score: float = 0.0
    rank: int = 0
    section_title: str | None = None


@dataclass
class SourceCitation:
    title: str
    url_or_path: str
    section_title: str | None
    snippet: str


@dataclass
class AnswerPayload:
    answer_text: str
    confidence: str
    fallback_used: bool
    fallback_reason: str | None
    citations: list[SourceCitation]
    used_chunk_ids: list[str]
