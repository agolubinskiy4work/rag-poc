"""Build final answer payload from retrieval evidence and generation result."""

from __future__ import annotations

from app.generation.ollama_client import OllamaGenerationClient
from app.generation.prompts import SYSTEM_PROMPT, build_user_prompt
from app.shared.config import SETTINGS
from app.shared.schemas import AnswerPayload, RetrievalCandidate, SourceCitation
from app.shared.utils import safe_truncate


def _build_citations(candidates: list[RetrievalCandidate]) -> list[SourceCitation]:
    citations: list[SourceCitation] = []
    seen: set[str] = set()
    for candidate in candidates:
        key = candidate.url or f"file:{candidate.title}"
        if key in seen:
            continue
        seen.add(key)
        citations.append(
            SourceCitation(
                title=candidate.title,
                url_or_path=candidate.url or candidate.title,
                section_title=candidate.section_title,
                snippet=safe_truncate(candidate.text, 180),
            )
        )
    return citations


def build_answer(question: str, candidates: list[RetrievalCandidate], evidence_ok: bool, fallback_reason: str | None) -> AnswerPayload:
    citations = _build_citations(candidates)
    used_chunk_ids = [candidate.chunk_id for candidate in candidates]

    if not evidence_ok:
        reason = fallback_reason or "Insufficient evidence"
        return AnswerPayload(
            answer_text=(
                "I could not find enough reliable evidence in the indexed sources "
                "to answer this confidently."
            ),
            confidence="Insufficient evidence",
            fallback_used=True,
            fallback_reason=reason,
            citations=citations,
            used_chunk_ids=used_chunk_ids,
        )

    context_blocks = [
        f"Title: {candidate.title}\nSource: {candidate.url or candidate.title}\nText: {candidate.text}"
        for candidate in candidates
    ]
    prompt = build_user_prompt(question, context_blocks)
    client = OllamaGenerationClient(SETTINGS.ollama_base_url, SETTINGS.generation_model)
    answer = client.generate(prompt=prompt, system_prompt=SYSTEM_PROMPT)

    confidence = "High"
    if candidates and candidates[0].fused_score < 0.2:
        confidence = "Medium"
    if candidates and candidates[0].fused_score < 0.12:
        confidence = "Low"

    return AnswerPayload(
        answer_text=answer,
        confidence=confidence,
        fallback_used=False,
        fallback_reason=None,
        citations=citations,
        used_chunk_ids=used_chunk_ids,
    )
