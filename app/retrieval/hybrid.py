"""Hybrid fusion logic for dense + lexical retrieval."""

from __future__ import annotations

from app.shared.schemas import RetrievalCandidate


def fuse_candidates(
    dense: list[RetrievalCandidate], lexical: list[RetrievalCandidate], final_top_k: int
) -> list[RetrievalCandidate]:
    by_chunk: dict[str, RetrievalCandidate] = {}

    for idx, cand in enumerate(dense, start=1):
        current = by_chunk.get(cand.chunk_id, cand)
        current.dense_score = max(current.dense_score, cand.dense_score)
        current.fused_score += 1.0 / (50 + idx)
        by_chunk[cand.chunk_id] = current

    for idx, cand in enumerate(lexical, start=1):
        current = by_chunk.get(cand.chunk_id, cand)
        current.lexical_score = max(current.lexical_score, cand.lexical_score)
        current.fused_score += 1.0 / (50 + idx)
        by_chunk[cand.chunk_id] = current

    merged = sorted(by_chunk.values(), key=lambda c: c.fused_score, reverse=True)
    for rank, cand in enumerate(merged, start=1):
        cand.rank = rank
    return merged[:final_top_k]
