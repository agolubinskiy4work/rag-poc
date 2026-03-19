"""Repository helpers for metadata CRUD operations."""

from __future__ import annotations

import sqlite3
from typing import Any


def upsert_source(
    conn: sqlite3.Connection,
    source_id: str,
    source_type: str,
    url: str | None,
    file_name: str | None,
    created_at: str,
) -> None:
    conn.execute(
        """
        INSERT INTO sources (source_id, source_type, url, file_name, created_at)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(source_id) DO UPDATE SET
            source_type=excluded.source_type,
            url=excluded.url,
            file_name=excluded.file_name
        """,
        (source_id, source_type, url, file_name, created_at),
    )
    conn.commit()


def upsert_document(
    conn: sqlite3.Connection,
    *,
    doc_id: str,
    source_id: str,
    title: str,
    url: str | None,
    file_name: str | None,
    source_type: str,
    content_type: str,
    document_hash: str,
    indexed_at: str | None,
    last_status: str,
) -> None:
    conn.execute(
        """
        INSERT INTO documents (
            doc_id, source_id, title, url, file_name, source_type,
            content_type, document_hash, indexed_at, last_status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(doc_id) DO UPDATE SET
            source_id=excluded.source_id,
            title=excluded.title,
            url=excluded.url,
            file_name=excluded.file_name,
            source_type=excluded.source_type,
            content_type=excluded.content_type,
            document_hash=excluded.document_hash,
            indexed_at=excluded.indexed_at,
            last_status=excluded.last_status
        """,
        (
            doc_id,
            source_id,
            title,
            url,
            file_name,
            source_type,
            content_type,
            document_hash,
            indexed_at,
            last_status,
        ),
    )
    conn.commit()


def get_document_by_doc_id(conn: sqlite3.Connection, doc_id: str) -> dict[str, Any] | None:
    row = conn.execute("SELECT * FROM documents WHERE doc_id = ?", (doc_id,)).fetchone()
    return dict(row) if row else None


def get_document_hash(conn: sqlite3.Connection, doc_id: str) -> str | None:
    row = conn.execute(
        "SELECT document_hash FROM documents WHERE doc_id = ?", (doc_id,)
    ).fetchone()
    return row["document_hash"] if row else None


def create_sync_run(conn: sqlite3.Connection, sync_run_id: str, started_at: str, total_items: int) -> None:
    conn.execute(
        """
        INSERT INTO sync_runs (
            sync_run_id, started_at, finished_at,
            total_items, indexed_count, skipped_count, failed_count
        ) VALUES (?, ?, NULL, ?, 0, 0, 0)
        """,
        (sync_run_id, started_at, total_items),
    )
    conn.commit()


def finalize_sync_run(
    conn: sqlite3.Connection,
    sync_run_id: str,
    finished_at: str,
    indexed_count: int,
    skipped_count: int,
    failed_count: int,
) -> None:
    conn.execute(
        """
        UPDATE sync_runs
        SET finished_at = ?, indexed_count = ?, skipped_count = ?, failed_count = ?
        WHERE sync_run_id = ?
        """,
        (finished_at, indexed_count, skipped_count, failed_count, sync_run_id),
    )
    conn.commit()


def add_sync_item(
    conn: sqlite3.Connection,
    sync_item_id: str,
    sync_run_id: str,
    doc_id: str | None,
    source_ref: str,
    status: str,
    message: str,
) -> None:
    conn.execute(
        """
        INSERT INTO sync_items (sync_item_id, sync_run_id, doc_id, source_ref, status, message)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (sync_item_id, sync_run_id, doc_id, source_ref, status, message),
    )
    conn.commit()
