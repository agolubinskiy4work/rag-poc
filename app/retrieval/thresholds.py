"""Evidence threshold evaluation for fallback decisions."""

from __future__ import annotations

import re

from app.shared.schemas import RetrievalCandidate


def _tokenize(text: str) -> set[str]:
    return {t for t in re.findall(r"[a-zA-Z0-9]+", text.lower()) if len(t) > 1}


def evaluate_evidence(
    query: str,
    candidates: list[RetrievalCandidate],
    min_fused_score: float,
    min_term_overlap: int,
) -> tuple[bool, str | None]:
    if not candidates:
        return False, "No retrieval candidates found"

    top = candidates[0]
    if top.fused_score < min_fused_score:
        return False, "Top candidate score below threshold"

    q_terms = _tokenize(query)
    text_terms = _tokenize(top.text)
    overlap = len(q_terms.intersection(text_terms))
    if overlap < min_term_overlap:
        return False, "Weak lexical overlap with question"

    return True, None
