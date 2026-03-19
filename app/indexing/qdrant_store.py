"""Qdrant vector store wrapper for chunk upsert/search."""

from __future__ import annotations

from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels

from app.shared.schemas import ChunkRecord
from app.shared.utils import stable_uuid_from_text


class QdrantStore:
    def __init__(self, host: str, port: int, collection: str, vector_size: int) -> None:
        self.collection = collection
        self.client = QdrantClient(host=host, port=port)
        self.vector_size = vector_size

    def ensure_collection(self) -> None:
        collections = [c.name for c in self.client.get_collections().collections]
        if self.collection in collections:
            return
        self.client.recreate_collection(
            collection_name=self.collection,
            vectors_config=qmodels.VectorParams(size=self.vector_size, distance=qmodels.Distance.COSINE),
        )

    def upsert_chunks(self, chunks: list[ChunkRecord], vectors: list[list[float]]) -> None:
        points: list[qmodels.PointStruct] = []
        for chunk, vector in zip(chunks, vectors, strict=False):
            point_id = stable_uuid_from_text(chunk.chunk_id)
            points.append(
                qmodels.PointStruct(
                    id=point_id,
                    vector=vector,
                    payload={
                        "doc_id": chunk.doc_id,
                        "chunk_id": chunk.chunk_id,
                        "text": chunk.text,
                        "title": chunk.title,
                        "url": chunk.url,
                        "source_type": chunk.source_type,
                        "section_title": chunk.section_title,
                        "document_hash": chunk.document_hash,
                        "chunk_index": chunk.chunk_index,
                    },
                )
            )
        if points:
            self.client.upsert(collection_name=self.collection, points=points)

    def delete_doc_chunks(self, doc_id: str) -> None:
        self.client.delete(
            collection_name=self.collection,
            points_selector=qmodels.FilterSelector(
                filter=qmodels.Filter(
                    must=[qmodels.FieldCondition(key="doc_id", match=qmodels.MatchValue(value=doc_id))]
                )
            ),
        )

    def dense_search(self, query_vector: list[float], limit: int) -> list[dict]:
        # qdrant-client>=1.17 uses query_points(); older versions exposed search().
        if hasattr(self.client, "query_points"):
            response = self.client.query_points(
                collection_name=self.collection,
                query=query_vector,
                limit=limit,
                with_payload=True,
            )
            results = response.points
        else:
            results = self.client.search(
                collection_name=self.collection,
                query_vector=query_vector,
                limit=limit,
                with_payload=True,
            )
        rows: list[dict] = []
        for point in results:
            payload = point.payload or {}
            rows.append({"score": float(point.score), **payload})
        return rows

    def scroll_all(self, limit: int = 5000) -> list[dict]:
        points, _ = self.client.scroll(collection_name=self.collection, with_payload=True, limit=limit)
        return [p.payload or {} for p in points]
