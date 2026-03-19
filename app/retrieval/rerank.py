"""Lightweight reranking for MVP laptop execution."""

from __future__ import annotations

import re

from app.shared.schemas import RetrievalCandidate


def _tokenize(text: str) -> set[str]:
    return {t for t in re.findall(r"[a-zA-Z0-9]+", text.lower()) if len(t) > 1}


def rerank_candidates(query: str, candidates: list[RetrievalCandidate]) -> list[RetrievalCandidate]:
    q_terms = _tokenize(query)
    if not q_terms:
        return candidates

    for cand in candidates:
        text_terms = _tokenize(cand.text)
        title_terms = _tokenize(cand.title)
        overlap = len(q_terms.intersection(text_terms))
        title_overlap = len(q_terms.intersection(title_terms))
        bonus = 0.02 * overlap + 0.04 * title_overlap
        cand.fused_score += bonus

    ranked = sorted(candidates, key=lambda c: c.fused_score, reverse=True)
    for rank, cand in enumerate(ranked, start=1):
        cand.rank = rank
    return ranked
