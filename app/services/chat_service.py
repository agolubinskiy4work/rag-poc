"""Service layer for indexed and page-aware chat flows."""

from __future__ import annotations

from time import perf_counter

from app.generation.answer_builder import build_answer
from app.ingest.page_parser import ParsedLink
from app.ingest.page_parser import parse_page_html
from app.retrieval.search import retrieve
from app.shared.config import SETTINGS
from app.shared.logging_utils import get_logger
from app.shared.schemas import AnswerPayload, RetrievalCandidate, SourceCitation
from app.shared.utils import stable_hash

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
        index_candidates, evidence_ok, reason = retrieve(question)

        page_candidates, page_link_citations, page_error = self._build_page_candidates(page_url, page_html)
        merged_candidates = [*page_candidates, *index_candidates]
        page_used = len(page_candidates)
        if page_used > 0:
            evidence_ok = True
            reason = None

        answer = build_answer(question, merged_candidates, evidence_ok, reason or page_error)
        if page_link_citations:
            answer.citations = self._merge_citations(page_link_citations, answer.citations)

        logger.info(
            "chat_page completed question_len=%s index_candidates=%s page_candidates=%s page_links=%s elapsed_ms=%s",
            len(question),
            len(index_candidates),
            page_used,
            len(page_link_citations),
            int((perf_counter() - started) * 1000),
        )
        return answer, {"page": page_used, "index": len(index_candidates)}

    def _build_page_candidates(
        self,
        page_url: str,
        page_html: str,
    ) -> tuple[list[RetrievalCandidate], list[SourceCitation], str | None]:
        if not page_html.strip():
            return [], [], "Empty page_html payload"

        if len(page_html) > SETTINGS.page_html_max_chars:
            return [], [], f"page_html exceeds max size ({SETTINGS.page_html_max_chars} chars)"

        try:
            parsed = parse_page_html(page_url, page_html)
        except Exception as exc:  # broad guard for malformed HTML
            logger.exception("Failed to parse page HTML for %s", page_url)
            return [], [], f"Invalid page_html payload: {exc}"

        if not parsed.text_blocks:
            return [], self._link_citations(parsed.links), "No readable text extracted from page_html"

        page_doc_id = stable_hash(f"page-doc:{page_url}")[:24]
        page_candidates = [
            RetrievalCandidate(
                chunk_id=stable_hash(f"page:{page_url}:{idx}:{text[:64]}")[:24],
                doc_id=page_doc_id,
                text=text[:4000],
                title=parsed.title,
                url=page_url,
                source_type="page",
                section_title=f"Page block {idx + 1}",
                dense_score=1.0,
                lexical_score=1.0,
                fused_score=1.0,
                rank=idx + 1,
            )
            for idx, text in enumerate(parsed.text_blocks)
        ]
        return page_candidates, self._link_citations(parsed.links), None

    def _link_citations(self, links: list[ParsedLink]) -> list[SourceCitation]:
        citations: list[SourceCitation] = []
        for link in links[:8]:
            citations.append(
                SourceCitation(
                    title=link.title or link.url,
                    url_or_path=link.url,
                    section_title=None,
                    snippet=link.snippet,
                    source_type="page",
                )
            )
        return citations

    def _merge_citations(self, page_citations: list[SourceCitation], existing: list[SourceCitation]) -> list[SourceCitation]:
        merged: list[SourceCitation] = []
        seen: set[str] = set()
        for citation in [*page_citations, *existing]:
            key = citation.url_or_path.strip()
            if not key or key in seen:
                continue
            seen.add(key)
            merged.append(citation)
        return merged
