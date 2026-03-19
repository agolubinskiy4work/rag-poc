# Storage Layer Workflow

## Goal
Define local metadata persistence responsibilities outside Qdrant.

## Scope
This layer stores local metadata required for:
- sync tracking,
- source registry,
- document hashes,
- indexing timestamps,
- file references,
- sync logs.

Qdrant is the retrieval database, but local metadata storage is still needed.

## Files

### `app/storage/metadata_db.py`
Responsibilities:
- initialize local SQLite database,
- define schema creation,
- expose DB connection/session helpers.

Suggested tables:
- sources
- documents
- sync_runs
- sync_items

### `app/storage/repositories.py`
Responsibilities:
- CRUD operations for metadata entities,
- read/write document hashes,
- upsert source metadata,
- store sync summaries,
- lookup documents by doc_id or source,
- mark documents as indexed.

## Suggested Metadata Tables

### `sources`
Fields:
- source_id
- source_type
- url
- file_name
- created_at

### `documents`
Fields:
- doc_id
- source_id
- title
- url
- file_name
- source_type
- content_type
- document_hash
- indexed_at
- last_status

### `sync_runs`
Fields:
- sync_run_id
- started_at
- finished_at
- total_items
- indexed_count
- skipped_count
- failed_count

### `sync_items`
Fields:
- sync_item_id
- sync_run_id
- doc_id
- source_ref
- status
- message

## Requirements
- keep storage simple,
- support local-only execution,
- store enough metadata to explain what happened during sync,
- support skipping unchanged documents during manual reindex.

## Deliverable
Implement a minimal SQLite-backed metadata layer with repository helpers.