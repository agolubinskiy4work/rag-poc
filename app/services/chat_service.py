"""Service layer for indexed and page-aware chat flows."""

from __future__ import annotations

from time import perf_counter

from bs4 import BeautifulSoup

from app.generation.answer_builder import build_answer
from app.ingest.cleaner import clean_text
from app.retrieval.search import retrieve
from app.shared.logging_utils import get_logger
from app.shared.schemas import AnswerPayload, RetrievalCandidate
from app.shared.utils import normalize_text, stable_hash

logger = get_logger(__name__)


class ChatService:
    """Expose chat use-cases for API/UI clients."""

    def chat(self, question: str) -> AnswerPayload:
        started = perf_counter()
        candidates, evidence_ok, reason = retrieve(question)
        answer = build_answer(question, candidates, evidence_ok, reason)
        logger.info(
            "chat completed question_len=%s candidates=%s evidence_ok=%s elapsed_ms=%s",
            len(question),
            len(candidates),
            evidence_ok,
            int((perf_counter() - started) * 1000),
        )
        return answer

    def chat_page(self, question: str, page_url: str, page_html: str) -> tuple[AnswerPayload, dict[str, int]]:
        started = perf_counter()
        candidates, evidence_ok, reason = retrieve(question)

        page_candidate, page_error = self._build_page_candidate(page_url, page_html)
        page_used = 0
        if page_candidate is not None:
            page_used = 1
            candidates = [page_candidate, *candidates]
            evidence_ok = True
            reason = None

        answer = build_answer(question, candidates, evidence_ok, reason or page_error)
        logger.info(
            "chat_page completed question_len=%s index_candidates=%s page_used=%s elapsed_ms=%s",
            len(question),
            len(candidates) - page_used,
            page_used,
            int((perf_counter() - started) * 1000),
        )
        return answer, {"page": page_used, "index": max(0, len(candidates) - page_used)}

    def _build_page_candidate(self, page_url: str, page_html: str) -> tuple[RetrievalCandidate | None, str | None]:
        if not page_html.strip():
            return None, "Empty page_html payload"

        try:
            soup = BeautifulSoup(page_html, "html.parser")
            title = (soup.title.string.strip() if soup.title and soup.title.string else page_url) or "Current page"
            text = normalize_text(clean_text(soup.get_text("\n", strip=True)))
        except Exception as exc:  # broad guard for malformed HTML
            logger.exception("Failed to parse page HTML for %s", page_url)
            return None, f"Invalid page_html payload: {exc}"

        if not text:
            return None, "No readable text extracted from page_html"

        return (
            RetrievalCandidate(
                chunk_id=stable_hash(f"page:{page_url}:{text[:128]}")[:24],
                doc_id=stable_hash(f"page-doc:{page_url}")[:24],
                text=text[:4000],
                title=title,
                url=page_url,
                source_type="page",
                section_title=None,
                dense_score=1.0,
                lexical_score=1.0,
                fused_score=1.0,
                rank=1,
            ),
            None,
        )
