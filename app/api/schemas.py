"""HTTP request/response schemas for FastAPI endpoints."""

from __future__ import annotations

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    service: str
    status: str
    generation_model: str
    embedding_model: str


class SourceInputDto(BaseModel):
    source_type: str = Field(description="url | file")
    value: str
    file_name: str | None = None


class SyncRequest(BaseModel):
    sources: list[SourceInputDto] = Field(default_factory=list)


class SyncItemDto(BaseModel):
    source_ref: str
    status: str
    message: str
    doc_id: str | None = None


class SyncResponse(BaseModel):
    total_sources: int
    indexed_count: int
    skipped_count: int
    failed_count: int
    items: list[SyncItemDto]


class ChatRequest(BaseModel):
    question: str


class ChatPageRequest(BaseModel):
    question: str
    page_url: str
    page_html: str
    page_title: str | None = None
    timestamp: str | None = None


class CitationDto(BaseModel):
    title: str
    url_or_path: str
    section_title: str | None
    snippet: str
    source_type: str | None = None


class ChatResponse(BaseModel):
    answer_text: str
    confidence: str
    fallback_used: bool
    fallback_reason: str | None
    citations: list[CitationDto]
    evidence_source_counts: dict[str, int] = Field(default_factory=dict)
