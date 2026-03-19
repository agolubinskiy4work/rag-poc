"""Text chunking logic for retrieval-ready chunks."""

from __future__ import annotations

from app.shared.schemas import ChunkRecord


def chunk_text(
    *,
    doc_id: str,
    title: str,
    source_type: str,
    url: str | None,
    text: str,
    document_hash: str,
    chunk_size: int,
    chunk_overlap: int,
) -> list[ChunkRecord]:
    if not text:
        return []

    chunks: list[ChunkRecord] = []
    start = 0
    idx = 0
    step = max(1, chunk_size - chunk_overlap)
    while start < len(text):
        piece = text[start : start + chunk_size].strip()
        if piece:
            chunks.append(
                ChunkRecord(
                    chunk_id=f"{doc_id}:{idx}",
                    doc_id=doc_id,
                    chunk_index=idx,
                    text=piece,
                    title=title,
                    url=url,
                    source_type=source_type,
                    section_title=None,
                    token_count=max(1, len(piece.split())),
                    document_hash=document_hash,
                )
            )
            idx += 1
        start += step
    return chunks
