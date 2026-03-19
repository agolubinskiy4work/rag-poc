# Indexing Layer Workflow

## Goal
Define embedding generation, Qdrant upsert flow, and manual sync orchestration.

## Files

### `app/indexing/embeddings.py`
Responsibilities:
- call Ollama embedding endpoint,
- generate embeddings for chunks,
- generate embeddings for user queries,
- batch embedding requests when helpful.

Requirements:
- use configurable embedding model,
- handle local Ollama failures cleanly,
- expose reusable methods for chunk and query embeddings.

### `app/indexing/qdrant_store.py`
Responsibilities:
- create and manage Qdrant collection,
- upsert chunk points,
- delete/update points for reindexed documents,
- run vector search,
- optionally support payload-based filtering.

Payload fields to store:
- doc_id
- chunk_id
- text
- title
- url
- source_type
- section_title
- document_hash
- chunk_index

### `app/indexing/dedup.py`
Responsibilities:
- compare document hashes,
- detect unchanged documents,
- skip unnecessary reindex,
- mark changed documents for re-upsert.

### `app/indexing/sync_service.py`
Responsibilities:
- orchestrate full manual sync flow,
- receive source inputs from UI,
- call fetch/parse/clean/chunk steps,
- deduplicate against existing metadata,
- call embedding generation,
- write points to Qdrant,
- update local metadata,
- return sync summary to UI.

## Manual Sync Workflow
1. Receive list of URLs and uploaded files.
2. Build normalized source input list.
3. Fetch or read each source.
4. Parse source to document.
5. Clean text.
6. Hash normalized document.
7. Skip if unchanged.
8. Chunk document.
9. Generate embeddings.
10. Upsert chunks to Qdrant.
11. Update metadata DB.
12. Return sync summary.

## Requirements
- manual trigger only,
- local-only,
- safe reindex behavior,
- clear reporting for indexed/skipped/failed items.

## Deliverable
Implement sync service as the single entry point for indexing from the UI.