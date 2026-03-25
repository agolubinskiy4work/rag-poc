"""FastAPI routes exposing sync and chat endpoints."""

from __future__ import annotations

from time import perf_counter

from fastapi import APIRouter, HTTPException

from app.api.schemas import (
    ChatPageRequest,
    ChatRequest,
    ChatResponse,
    CitationDto,
    HealthResponse,
    SyncItemDto,
    SyncRequest,
    SyncResponse,
)
from app.services.chat_service import ChatService
from app.services.sync_service import SyncService
from app.shared.config import SETTINGS
from app.shared.logging_utils import get_logger
from app.shared.schemas import SourceInput

router = APIRouter()
logger = get_logger(__name__)


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(
        service="local-rag-api",
        status="ok",
        generation_model=SETTINGS.generation_model,
        embedding_model=SETTINGS.embedding_model,
    )


@router.post("/api/sync", response_model=SyncResponse)
def sync_sources(payload: SyncRequest) -> SyncResponse:
    if not payload.sources:
        raise HTTPException(status_code=400, detail="At least one source is required")

    started = perf_counter()
    service = SyncService()
    sources = [
        SourceInput(source_type=source.source_type, value=source.value, file_name=source.file_name)
        for source in payload.sources
    ]
    result = service.run_sync(sources)
    logger.info(
        "sync completed total=%s indexed=%s skipped=%s failed=%s elapsed_ms=%s",
        result.total_sources,
        result.indexed_count,
        result.skipped_count,
        result.failed_count,
        int((perf_counter() - started) * 1000),
    )
    return SyncResponse(
        total_sources=result.total_sources,
        indexed_count=result.indexed_count,
        skipped_count=result.skipped_count,
        failed_count=result.failed_count,
        items=[
            SyncItemDto(
                source_ref=item.source_ref,
                status=item.status,
                message=item.message,
                doc_id=item.doc_id,
            )
            for item in result.items
        ],
    )


def _to_chat_response(answer_text: str, confidence: str, fallback_used: bool, fallback_reason: str | None, citations: list[dict[str, str | None]], evidence_counts: dict[str, int]) -> ChatResponse:
    return ChatResponse(
        answer_text=answer_text,
        confidence=confidence,
        fallback_used=fallback_used,
        fallback_reason=fallback_reason,
        citations=[
            CitationDto(
                title=str(citation.get("title", "Untitled")),
                url_or_path=str(citation.get("url_or_path", "")),
                section_title=citation.get("section_title"),
                snippet=str(citation.get("snippet", "")),
            )
            for citation in citations
        ],
        evidence_source_counts=evidence_counts,
    )


@router.post("/api/chat", response_model=ChatResponse)
def chat(payload: ChatRequest) -> ChatResponse:
    question = payload.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="question must not be empty")

    service = ChatService()
    answer = service.chat(question)
    return _to_chat_response(
        answer_text=answer.answer_text,
        confidence=answer.confidence,
        fallback_used=answer.fallback_used,
        fallback_reason=answer.fallback_reason,
        citations=[
            {
                "title": c.title,
                "url_or_path": c.url_or_path,
                "section_title": c.section_title,
                "snippet": c.snippet,
            }
            for c in answer.citations
        ],
        evidence_counts={"index": len(answer.citations), "page": 0},
    )


@router.post("/api/chat/page", response_model=ChatResponse)
def chat_page(payload: ChatPageRequest) -> ChatResponse:
    question = payload.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="question must not be empty")

    service = ChatService()
    answer, counts = service.chat_page(question, payload.page_url.strip(), payload.page_html)
    return _to_chat_response(
        answer_text=answer.answer_text,
        confidence=answer.confidence,
        fallback_used=answer.fallback_used,
        fallback_reason=answer.fallback_reason,
        citations=[
            {
                "title": c.title,
                "url_or_path": c.url_or_path,
                "section_title": c.section_title,
                "snippet": c.snippet,
            }
            for c in answer.citations
        ],
        evidence_counts=counts,
    )
