"""Manual sync orchestration from source inputs to indexed chunks."""

from __future__ import annotations

from datetime import datetime

from app.ingest.chunker import chunk_text
from app.ingest.cleaner import clean_text
from app.ingest.fetcher import fetch_url
from app.ingest.models import RawSource
from app.ingest.parsers import parse_raw_source
from app.indexing.dedup import should_skip_indexing
from app.indexing.embeddings import OllamaEmbeddingClient
from app.indexing.qdrant_store import QdrantStore
from app.shared.config import SETTINGS
from app.shared.logging_utils import get_logger
from app.shared.schemas import SourceInput, SyncItemResult, SyncResult
from app.shared.utils import normalize_text, now_utc_iso, stable_hash
from app.storage import repositories
from app.storage.metadata_db import get_connection, init_db

logger = get_logger(__name__)


class SyncService:
    def __init__(self) -> None:
        self.conn = get_connection(SETTINGS.sqlite_path)
        init_db(self.conn)
        self.embedder = OllamaEmbeddingClient(SETTINGS.ollama_base_url, SETTINGS.embedding_model)
        self.qdrant = QdrantStore(
            SETTINGS.qdrant_host,
            SETTINGS.qdrant_port,
            SETTINGS.qdrant_collection,
            SETTINGS.embedding_dim,
        )
        self.qdrant.ensure_collection()

    def _source_to_raw(self, source: SourceInput) -> RawSource:
        if source.source_type == "url":
            return fetch_url(source.value)

        # file source
        content_type = "text/plain"
        file_name = source.file_name or source.value
        try:
            with open(source.value, "r", encoding="utf-8", errors="ignore") as f:
                raw_text = f.read()
        except OSError:
            raw_text = ""
        return RawSource(
            source_type="file",
            source_ref=source.value,
            content_type=content_type,
            raw_text=raw_text,
            file_name=file_name,
        )

    def run_sync(self, sources: list[SourceInput]) -> SyncResult:
        sync_run_id = stable_hash(now_utc_iso())[:16]
        repositories.create_sync_run(self.conn, sync_run_id, now_utc_iso(), len(sources))

        indexed_count = 0
        skipped_count = 0
        failed_count = 0
        item_results: list[SyncItemResult] = []

        for source in sources:
            source_ref = source.value
            source_id = stable_hash(f"{source.source_type}:{source_ref}")[:24]
            doc_id = stable_hash(f"doc:{source.source_type}:{source_ref}")[:24]

            try:
                repositories.upsert_source(
                    self.conn,
                    source_id=source_id,
                    source_type=source.source_type,
                    url=source_ref if source.source_type == "url" else None,
                    file_name=source.file_name,
                    created_at=now_utc_iso(),
                )

                raw = self._source_to_raw(source)
                parsed = parse_raw_source(raw)
                cleaned = clean_text(parsed.text)
                normalized = normalize_text(cleaned)
                doc_hash = stable_hash(normalized)

                existing_hash = repositories.get_document_hash(self.conn, doc_id)
                if should_skip_indexing(existing_hash, doc_hash):
                    skipped_count += 1
                    message = "Skipped unchanged document"
                    item = SyncItemResult(source_ref=source_ref, status="skipped", message=message, doc_id=doc_id)
                    item_results.append(item)
                    repositories.add_sync_item(
                        self.conn,
                        sync_item_id=stable_hash(f"{sync_run_id}:{source_ref}:skipped")[:24],
                        sync_run_id=sync_run_id,
                        doc_id=doc_id,
                        source_ref=source_ref,
                        status="skipped",
                        message=message,
                    )
                    continue

                chunks = chunk_text(
                    doc_id=doc_id,
                    title=parsed.title,
                    source_type=parsed.source_type,
                    url=parsed.source_ref if parsed.source_type == "url" else None,
                    text=normalized,
                    document_hash=doc_hash,
                    chunk_size=SETTINGS.chunk_size,
                    chunk_overlap=SETTINGS.chunk_overlap,
                )
                if not chunks:
                    raise ValueError("No chunks produced from source")

                vectors = self.embedder.embed_texts([c.text for c in chunks])
                self.qdrant.delete_doc_chunks(doc_id)
                self.qdrant.upsert_chunks(chunks, vectors)

                repositories.upsert_document(
                    self.conn,
                    doc_id=doc_id,
                    source_id=source_id,
                    title=parsed.title,
                    url=parsed.source_ref if parsed.source_type == "url" else None,
                    file_name=parsed.file_name,
                    source_type=parsed.source_type,
                    content_type=parsed.content_type,
                    document_hash=doc_hash,
                    indexed_at=now_utc_iso(),
                    last_status="indexed",
                )

                indexed_count += 1
                message = f"Indexed {len(chunks)} chunks"
                item = SyncItemResult(source_ref=source_ref, status="indexed", message=message, doc_id=doc_id)
                item_results.append(item)
                repositories.add_sync_item(
                    self.conn,
                    sync_item_id=stable_hash(f"{sync_run_id}:{source_ref}:indexed")[:24],
                    sync_run_id=sync_run_id,
                    doc_id=doc_id,
                    source_ref=source_ref,
                    status="indexed",
                    message=message,
                )
            except Exception as exc:  # MVP broad guard to keep partial progress
                logger.exception("Failed to sync source %s", source_ref)
                failed_count += 1
                message = f"Failed: {exc}"
                item = SyncItemResult(source_ref=source_ref, status="failed", message=message, doc_id=doc_id)
                item_results.append(item)
                repositories.add_sync_item(
                    self.conn,
                    sync_item_id=stable_hash(f"{sync_run_id}:{source_ref}:failed:{datetime.now().timestamp()}")[:24],
                    sync_run_id=sync_run_id,
                    doc_id=doc_id,
                    source_ref=source_ref,
                    status="failed",
                    message=message,
                )

        repositories.finalize_sync_run(
            self.conn,
            sync_run_id=sync_run_id,
            finished_at=now_utc_iso(),
            indexed_count=indexed_count,
            skipped_count=skipped_count,
            failed_count=failed_count,
        )
        return SyncResult(
            total_sources=len(sources),
            indexed_count=indexed_count,
            skipped_count=skipped_count,
            failed_count=failed_count,
            items=item_results,
        )
