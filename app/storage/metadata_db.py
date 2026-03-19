"""SQLite metadata database helpers."""

from __future__ import annotations

import sqlite3
from pathlib import Path


def get_connection(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(conn: sqlite3.Connection) -> None:
    cur = conn.cursor()
    cur.executescript(
        """
        CREATE TABLE IF NOT EXISTS sources (
            source_id TEXT PRIMARY KEY,
            source_type TEXT NOT NULL,
            url TEXT,
            file_name TEXT,
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS documents (
            doc_id TEXT PRIMARY KEY,
            source_id TEXT NOT NULL,
            title TEXT NOT NULL,
            url TEXT,
            file_name TEXT,
            source_type TEXT NOT NULL,
            content_type TEXT NOT NULL,
            document_hash TEXT NOT NULL,
            indexed_at TEXT,
            last_status TEXT NOT NULL,
            FOREIGN KEY(source_id) REFERENCES sources(source_id)
        );

        CREATE TABLE IF NOT EXISTS sync_runs (
            sync_run_id TEXT PRIMARY KEY,
            started_at TEXT NOT NULL,
            finished_at TEXT,
            total_items INTEGER NOT NULL,
            indexed_count INTEGER NOT NULL,
            skipped_count INTEGER NOT NULL,
            failed_count INTEGER NOT NULL
        );

        CREATE TABLE IF NOT EXISTS sync_items (
            sync_item_id TEXT PRIMARY KEY,
            sync_run_id TEXT NOT NULL,
            doc_id TEXT,
            source_ref TEXT NOT NULL,
            status TEXT NOT NULL,
            message TEXT NOT NULL,
            FOREIGN KEY(sync_run_id) REFERENCES sync_runs(sync_run_id)
        );
        """
    )
    conn.commit()
