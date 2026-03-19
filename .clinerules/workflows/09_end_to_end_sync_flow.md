# End-to-End Sync Flow Workflow

## Goal
Describe the full manual ingestion and indexing sequence.

## Entry Point
Triggered by the Streamlit Sync / Reindex button.

## Flow

1. Read raw URL list from UI.
2. Read uploaded files from UI.
3. Normalize source input objects.
4. For each URL:
   - fetch raw content,
   - parse HTML,
   - clean body text,
   - compute document hash,
   - compare with existing stored hash,
   - skip if unchanged,
   - chunk clean text,
   - embed chunks,
   - upsert chunks into Qdrant,
   - update metadata storage.
5. For each uploaded file:
   - read file content,
   - parse text,
   - normalize content,
   - compute document hash,
   - compare with existing stored hash,
   - skip if unchanged,
   - chunk text,
   - embed chunks,
   - upsert chunks into Qdrant,
   - update metadata storage.
6. Build sync summary.
7. Return sync summary to UI.

## Required Sync Summary
- total sources
- indexed count
- skipped count
- failed count
- per-source status messages

## Error Handling
- individual source failures must not abort the whole sync,
- failed sources must be reported cleanly,
- partial success is acceptable for MVP.

## Deliverable
Implement sync as a single user-triggered pipeline with clear status reporting.