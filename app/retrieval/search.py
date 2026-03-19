"""Top-level retrieval API implementing dense + lexical + fusion flow."""

from __future__ import annotations

import re

from app.indexing.embeddings import OllamaEmbeddingClient
from app.indexing.qdrant_store import QdrantStore
from app.retrieval.hybrid import fuse_candidates
from app.retrieval.rerank import rerank_candidates
from app.retrieval.thresholds import evaluate_evidence
from app.shared.config import SETTINGS
from app.shared.schemas import RetrievalCandidate


def _tokenize(text: str) -> set[str]:
    return {t for t in re.findall(r"[a-zA-Z0-9]+", text.lower()) if len(t) > 1}


def _dense_candidates(qdrant: QdrantStore, embedder: OllamaEmbeddingClient, query: str) -> list[RetrievalCandidate]:
    qv = embedder.embed_query(query)
    rows = qdrant.dense_search(qv, SETTINGS.dense_top_k)
    out: list[RetrievalCandidate] = []
    for row in rows:
        out.append(
            RetrievalCandidate(
                chunk_id=str(row.get("chunk_id", "")),
                doc_id=str(row.get("doc_id", "")),
                text=str(row.get("text", "")),
                title=str(row.get("title", "Untitled")),
                url=row.get("url"),
                source_type=str(row.get("source_type", "unknown")),
                section_title=row.get("section_title"),
                dense_score=float(row.get("score", 0.0)),
                fused_score=float(row.get("score", 0.0)),
            )
        )
    return out


def _lexical_candidates(qdrant: QdrantStore, query: str) -> list[RetrievalCandidate]:
    q_terms = _tokenize(query)
    rows = qdrant.scroll_all()
    scored: list[RetrievalCandidate] = []
    for row in rows:
        text = str(row.get("text", ""))
        text_terms = _tokenize(text)
        overlap = len(q_terms.intersection(text_terms))
        if overlap <= 0:
            continue
        score = overlap / max(1, len(q_terms))
        scored.append(
            RetrievalCandidate(
                chunk_id=str(row.get("chunk_id", "")),
                doc_id=str(row.get("doc_id", "")),
                text=text,
                title=str(row.get("title", "Untitled")),
                url=row.get("url"),
                source_type=str(row.get("source_type", "unknown")),
                section_title=row.get("section_title"),
                lexical_score=score,
                fused_score=score,
            )
        )

    scored.sort(key=lambda c: c.lexical_score, reverse=True)
    return scored[: SETTINGS.lexical_top_k]


def retrieve(query: str) -> tuple[list[RetrievalCandidate], bool, str | None]:
    embedder = OllamaEmbeddingClient(SETTINGS.ollama_base_url, SETTINGS.embedding_model)
    qdrant = QdrantStore(
        SETTINGS.qdrant_host,
        SETTINGS.qdrant_port,
        SETTINGS.qdrant_collection,
        SETTINGS.embedding_dim,
    )
    dense = _dense_candidates(qdrant, embedder, query)
    lexical = _lexical_candidates(qdrant, query)
    fused = fuse_candidates(dense, lexical, SETTINGS.final_top_k)
    reranked = rerank_candidates(query, fused)
    ok, reason = evaluate_evidence(
        query,
        reranked,
        min_fused_score=SETTINGS.min_fused_score,
        min_term_overlap=SETTINGS.min_term_overlap,
    )
    return reranked[: SETTINGS.final_top_k], ok, reason
